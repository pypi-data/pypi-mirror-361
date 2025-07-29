"""
Pack Service - Creates OCI bundles from lockfiles with cache integration.

This service coordinates the creation of OCI bundles, ensuring all artifacts
are downloaded through the cache service before bundling.
"""

import asyncio
import gzip
import hashlib
import json
import logging
import os
import shutil
import repro_tarfile as tarfile
import tempfile
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.parse import urlparse

import oras.client
import oras.defaults
import oras.oci
import oras.utils
from oras.provider import Registry
from requests import HTTPError

from ..core.commands import FetchArtifactCommand
from ..core.models import LockFile
from ..core.oci_types import (
    AnnotationKeys,
    CompressionTypes,
    LayerTypes,
    MediaTypes,
    OrasDefaults,
    create_bundle_annotations,
)
from ..handlers.factory import HandlerFactory
from ..services.cache import CacheResolver
from ..services.lockfile import LockfileService

logger = logging.getLogger(__name__)


@dataclass
class PackProgress:
    """Progress information for pack operations."""

    total_artifacts: int
    downloaded_artifacts: int
    bundled_artifacts: int
    current_artifact: Optional[str] = None
    current_status: str = "initializing"


class PackServiceError(Exception):
    """Base exception for PackService errors."""

    pass


class PackService:
    """
    Service for creating OCI bundles from lockfiles.

    Ensures all artifacts are downloaded through the cache service
    before creating the bundle.
    """

    def __init__(
        self,
        cache_service: Optional[CacheResolver] = None,
        lockfile_service: Optional[LockfileService] = None,
        handler_factory: Optional[HandlerFactory] = None,
    ):
        """
        Initialize the pack service.

        Args:
            cache_service: Service for caching artifacts
            lockfile_service: Service for loading lockfiles
            handler_factory: Factory for creating artifact handlers
        """
        self._cache_service = cache_service or CacheResolver()
        self._handler_factory = handler_factory or HandlerFactory(
            cache_service=self._cache_service
        )
        self._lockfile_service = lockfile_service or LockfileService(
            cache_service=self._cache_service, handler_factory=self._handler_factory
        )

    async def create_bundle(
        self,
        lockfile_path: str,
        output_path: str,
        tag: str = "latest",
        push_to_registry: Optional[str] = None,
        registry_username: Optional[str] = None,
        registry_password: Optional[str] = None,
        insecure: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[str, int, int]:
        """
        Create an OCI bundle from a lockfile.

        Args:
            lockfile_path: Path to the lockfile
            output_path: Path where the bundle should be created
            tag: Bundle version tag
            push_to_registry: Optional registry URL to push to (e.g., "ghcr.io/org/bundle:v1.0")
            registry_username: Optional registry username
            registry_password: Optional registry password
            insecure: Allow insecure HTTP connections (for localhost registries)
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (bundle_path, layers_created, artifacts_bundled)
        """
        Path.cwd()
        should_pack = True
        # Check if bundle already exists (idempotency)
        bundle_path_obj = Path(output_path)
        if bundle_path_obj.exists() and (bundle_path_obj / "index.json").exists():
            should_pack = False
            if progress_callback:
                progress_callback({
                    "type": "bundle_exists",
                    "message": f"✓ Bundle already exists at {output_path}",
                    "status": "complete",
                })
            # return str(bundle_path_obj), 2, 0  # Return existing bundle info (2 layers created, 0 artifacts bundled)

        # THIS ONLY HAPPENS IF THE BUNDLE DOES NOT EXIST AND INDEX.JSON IS NOT FOUND

        # Load lockfile
        lockfile = self._lockfile_service.load_lockfile(Path(lockfile_path))

        progress = PackProgress(
            total_artifacts=len(lockfile.artifacts),
            downloaded_artifacts=0,
            bundled_artifacts=0,
        )

        if should_pack:
            if progress_callback:
                progress_callback({
                    "type": "pack_start",
                    "total_artifacts": progress.total_artifacts,
                    "message": f"Starting bundle creation with {progress.total_artifacts} artifacts",
                })

            # Create temporary directory for staging artifacts
            with tempfile.TemporaryDirectory() as staging_dir:
                staging_path = Path(staging_dir)
                logger.debug("Staging directory", extra={"staging_path": staging_path})
                # TODO: Remove this

                # Download all artifacts through cache
                await self._download_artifacts(
                    lockfile, staging_path, progress, progress_callback, lockfile_path
                )

                # Create the OCI bundle
                bundle_path = await self._create_oci_bundle(
                    lockfile,
                    lockfile_path,
                    staging_path,
                    output_path,
                    tag,
                    progress_callback,
                )

                # Push to registry if requested
                if push_to_registry:
                    await self._push_to_registry(
                        bundle_path,
                        push_to_registry,
                        username=registry_username,
                        password=registry_password,
                        insecure=insecure,
                        progress=progress,
                        progress_callback=progress_callback,
                    )

                return (
                    bundle_path,
                    2,
                    len(lockfile.artifacts),
                )  # 2 layers: metadata + artifacts

        elif push_to_registry:
            # We just upload the existing bundle without repacking
            await self._push_to_registry(
                str(bundle_path_obj),
                push_to_registry,
                username=registry_username,
                password=registry_password,
                insecure=insecure,
                progress=progress,
                progress_callback=progress_callback,
            )
        # If we reach here, it means we either repacked or just pushed
        return str(bundle_path_obj), 2, len(lockfile.artifacts)

    async def _download_artifacts(
        self,
        lockfile: LockFile,
        staging_dir: Path,
        progress: PackProgress,
        progress_callback: Optional[Callable] = None,
        lockfile_path: Optional[str] = None,
    ) -> None:
        """
        Download all artifacts through the cache service.

        Args:
            lockfile: The lockfile containing artifacts
            staging_dir: Directory to stage downloaded artifacts
            progress: Progress tracking object
            progress_callback: Optional callback for progress updates
            lockfile_path: Path to lockfile for resolving relative paths
        """
        # Create handler factory with lockfile directory as base path
        base_path = None
        if lockfile_path:
            base_path = str(Path(lockfile_path).parent)

        handler_factory = HandlerFactory(
            base_path=base_path, cache_service=self._cache_service
        )

        # Process all artifacts concurrently
        async def process_artifact(artifact):
            """Process a single artifact with progress tracking."""
            # Create target path in staging directory
            target_path = staging_dir / artifact.target.lstrip("/")
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Report start
            if progress_callback:
                progress_callback({
                    "type": "artifact_start",
                    "name": artifact.target,
                    "origin": artifact.origin,
                    "status": "checking cache",
                })

            # Hybrid approach: Try cache first, fallback to download
            try:
                # Try to resolve from cache first (fast path)
                resolution = await self._cache_service.resolve_artifact(artifact.origin)

                if (
                    resolution.type == "remote"
                    and resolution.cached_metadata
                    and resolution.cached_metadata.content_hash
                ):
                    # Get cached file path from content store
                    content_store = self._cache_service._content_store
                    cached_file_path = content_store.get_content_path(
                        resolution.cached_metadata.content_hash
                    )

                    if cached_file_path.exists():
                        # Copy from cache (fast path)
                        if progress_callback:
                            progress_callback({
                                "type": "artifact_progress",
                                "name": artifact.target,
                                "status": "copying from cache",
                            })

                        shutil.copy2(cached_file_path, target_path)

                        if progress_callback:
                            progress_callback({
                                "type": "artifact_progress",
                                "name": artifact.target,
                                "status": "copied from cache",
                            })
                    else:
                        msg = "Cache file missing, will download"
                        raise Exception(msg)
                else:
                    msg = "Not in cache, will download"
                    raise Exception(msg)

            except Exception:
                # Fallback: Download using lockfile data (resilient path)
                if progress_callback:
                    progress_callback({
                        "type": "artifact_progress",
                        "name": artifact.target,
                        "status": "downloading",
                    })

                handler = handler_factory.get_handler_for_scheme(artifact.type)
                command = FetchArtifactCommand(
                    origin_url=artifact.origin,
                    target_path=str(target_path),
                    expected_checksum=artifact.checksum,
                )

                result = await handler.handle(command)

                if not result.success:
                    msg = f"Failed to fetch artifact {artifact.origin}: {result.error_message}"
                    raise Exception(msg)

            # Verify checksum
            with open(target_path, "rb") as f:
                actual_checksum = f"sha256:{hashlib.sha256(f.read()).hexdigest()}"

            if actual_checksum != artifact.checksum:
                msg = f"Checksum mismatch for {artifact.origin}: expected {artifact.checksum}, got {actual_checksum}"
                raise Exception(msg)

            # Report completion
            if progress_callback:
                progress_callback({
                    "type": "artifact_complete",
                    "name": artifact.target,
                    "status": "complete",
                })

            return artifact

        # Execute all artifact processing concurrently
        completed_artifacts = await asyncio.gather(
            *[process_artifact(artifact) for artifact in lockfile.artifacts],
            return_exceptions=True,
        )

        # Check for errors
        for i, result in enumerate(completed_artifacts):
            if isinstance(result, Exception):
                artifact = lockfile.artifacts[i]
                msg = f"Failed to process {artifact.origin}: {result!s}"
                raise Exception(msg)

        progress.downloaded_artifacts = len(lockfile.artifacts)

        # Report download completion
        if progress_callback:
            progress_callback({
                "type": "download_complete",
                "message": f"All {len(lockfile.artifacts)} artifacts processed",
                "status": "creating bundle",
            })

    async def _create_oci_bundle(
        self,
        lockfile: LockFile,
        lockfile_path: str,
        staging_dir: Path,
        output_path: str,
        tag: str,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Create OCI bundle structure from staged artifacts.

        Args:
            lockfile: The lockfile
            lockfile_path: Path to the original lockfile
            staging_dir: Directory containing staged artifacts
            output_path: Output path for the bundle
            tag: Bundle version tag

        Returns:
            Path to the created bundle
        """
        bundle_path = Path(output_path)
        bundle_path.mkdir(parents=True, exist_ok=True)

        # Create OCI directory structure
        blobs_dir = bundle_path / "blobs" / "sha256"
        blobs_dir.mkdir(parents=True, exist_ok=True)

        # Create oci-layout file
        self._create_oci_layout(bundle_path)

        # Create layers
        layers = []
        source_files = []

        # Create metadata layer
        metadata_layer, metadata_file = await self._create_metadata_layer(
            lockfile, progress_callback, lockfile_path
        )
        layers.append(metadata_layer)
        source_files.append(metadata_file)

        # Create artifacts layer from staging directory
        if staging_dir and any(staging_dir.iterdir()):
            artifacts_layer, artifacts_file = self._create_artifacts_layer(
                staging_dir, lockfile
            )
            layers.append(artifacts_layer)
            source_files.append(artifacts_file)

        # Create config and manifest
        config_obj, _ = self._create_config(layers)
        manifest = self._create_manifest(
            layers, config_obj, lockfile, tag, lockfile_path
        )

        # Write objects to filesystem
        self._write_objects_to_filesystem(
            bundle_path, manifest, config_obj, layers, source_files
        )

        # Create index.json
        manifest_digest = self._write_manifest_and_get_digest(bundle_path, manifest)
        self._create_index(bundle_path, manifest_digest)

        return str(bundle_path)

    def _create_oci_layout(self, bundle_path: Path) -> None:
        """Create the oci-layout file."""
        oci_layout = {"imageLayoutVersion": "1.0.0"}
        with open(bundle_path / "oci-layout", "w", encoding="utf-8") as f:
            json.dump(oci_layout, f)

    async def _create_metadata_layer(
        self, lockfile: LockFile, progress_callback: Optional[Callable] = None, lockfile_path: Optional[str] = None
    ) -> Tuple[dict, str]:
        """Create enhanced metadata layer with lockfile and artifact index."""
        # Create temporary directory for metadata
        base_temp = Path(tempfile.mkdtemp())
        temp_dir = base_temp / "metadata"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Write lockfile JSON
            lockfile_data = lockfile.dump_canonical_json()
            lockfile_json_path = os.path.join(temp_dir, "conduit.lock.json")
            with open(lockfile_json_path, "w", encoding="utf-8") as f:
                f.write(lockfile_data)

            # Create artifact index for quick lookup
            artifact_index = {
                "version": "1.0",
                "artifact_count": len(lockfile.artifacts),
                "artifacts": [
                    {
                        "name": os.path.basename(a.target),
                        "type": a.type,
                        "target": a.target,
                        "origin": a.origin,
                        "checksum": a.checksum,
                        "metadata": getattr(a, "metadata", {}),
                    }
                    for a in lockfile.artifacts
                ],
            }

            index_path = os.path.join(temp_dir, "artifact-index.json")
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(artifact_index, f, indent=2)

            # Include entrypoint script if present
            if lockfile.entrypoint and lockfile.entrypoint.script:
                script_path = Path(lockfile.entrypoint.script)
                
                # Resolve script path relative to current working directory if it's relative
                if not script_path.is_absolute():
                    script_path = Path.cwd() / script_path

                # Report progress
                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_verification",
                        "message": f"Verifying entrypoint script: {script_path.name}",
                        "checksum": lockfile.entrypoint.checksum,
                    })

                # Try cache first
                cached_path = await self._cache_service._content_store.get_content(
                    lockfile.entrypoint.checksum
                )

                if cached_path and cached_path.exists():
                    # Use cached version
                    script_dest = temp_dir / script_path.name
                    shutil.copy2(cached_path, script_dest)
                    logger.info(
                        "Retrieved entrypoint script from cache",
                        extra={"entrypoint_checksum": lockfile.entrypoint.checksum},
                    )

                    if progress_callback:
                        progress_callback({
                            "type": "entrypoint_retrieved",
                            "message": "Entrypoint script retrieved from cache",
                            "source": "cache",
                        })
                elif script_path.exists():
                    # Verify checksum
                    actual_checksum = await self._calculate_file_checksum_async(
                        script_path
                    )
                    if actual_checksum != lockfile.entrypoint.checksum:
                        error_msg = (
                            f"Entrypoint script checksum mismatch: "
                            f"expected {lockfile.entrypoint.checksum}, got {actual_checksum}"
                        )
                        logger.error(error_msg)

                        if progress_callback:
                            progress_callback({
                                "type": "entrypoint_error",
                                "message": error_msg,
                                "error": "checksum_mismatch",
                            })

                        msg = f"Entrypoint script {script_path} has been modified"
                        raise PackServiceError(msg)

                    # Copy and cache
                    script_dest = os.path.join(temp_dir, script_path.name)
                    shutil.copy2(script_path, script_dest)

                    # Cache for future use
                    await self._cache_service._content_store.store_content(
                        script_path, lockfile.entrypoint.checksum
                    )

                    logger.info(f"Entrypoint script verified and cached: {script_path}")

                    if progress_callback:
                        progress_callback({
                            "type": "entrypoint_retrieved",
                            "message": "Entrypoint script verified and cached",
                            "source": "filesystem",
                        })
                else:
                    error_msg = f"Entrypoint script not found: {script_path}"
                    if progress_callback:
                        progress_callback({
                            "type": "entrypoint_error",
                            "message": error_msg,
                            "error": "not_found",
                        })
                    raise PackServiceError(error_msg)

                # Set appropriate permissions based on mode in lockfile
                if lockfile.entrypoint.mode:
                    try:
                        # Convert mode string (e.g., "0755") to octal
                        mode = int(lockfile.entrypoint.mode, 8)
                        os.chmod(script_dest, mode)
                    except (ValueError, OSError):
                        # If mode conversion fails, keep default permissions
                        pass

            # Create tar.gz using deterministic method - archive from base_temp to include metadata/ prefix
            tar_gz_path = self._create_deterministic_targz(Path(base_temp))

            # Create layer descriptor
            layer = oras.oci.NewLayer(
                tar_gz_path,
                is_dir=False,
                media_type=MediaTypes.CONDUIT_METADATA_LAYER,
            )

            # Add enhanced annotations
            layer_contents = "lockfile,artifact-index"
            if lockfile.entrypoint:
                layer_contents += ",entrypoint-script"

            layer["annotations"] = {
                AnnotationKeys.TITLE: "Conduit Bundle Metadata",
                AnnotationKeys.DESCRIPTION: "Lockfile and artifact index for bundle verification",
                AnnotationKeys.LAYER_TYPE: LayerTypes.METADATA,
                AnnotationKeys.LAYER_CONTENTS: layer_contents,
                AnnotationKeys.LOCKFILE_VERSION: lockfile.apiVersion,
                AnnotationKeys.LOCKFILE_ARTIFACT_COUNT: str(len(lockfile.artifacts)),
                AnnotationKeys.METADATA_VERSION_KEY: "1.0",
            }

            return layer, tar_gz_path
        finally:
            shutil.rmtree(base_temp)

    def _create_artifacts_layer(
        self, staging_dir: Path, lockfile: Optional[LockFile] = None
    ) -> Tuple[dict, str]:
        """Create artifacts layer from staged files with enhanced annotations."""
        # Create tar.gz of staging directory with deterministic content
        tar_gz_path = self._create_deterministic_targz(staging_dir)

        # Count and categorize artifacts
        artifact_count = sum(1 for _ in staging_dir.rglob("*") if _.is_file())
        artifact_types = {}

        if lockfile:
            for artifact in lockfile.artifacts:
                artifact_type = artifact.type
                if artifact_type not in artifact_types:
                    artifact_types[artifact_type] = []
                artifact_types[artifact_type].append(os.path.basename(artifact.target))

        # Create layer descriptor
        layer = oras.oci.NewLayer(
            tar_gz_path,
            is_dir=False,
            media_type=MediaTypes.CONDUIT_ARTIFACTS_LAYER,
        )

        # Add comprehensive annotations
        layer["annotations"] = {
            AnnotationKeys.TITLE: "Conduit Artifacts Bundle",
            AnnotationKeys.DESCRIPTION: f"Bundle containing {artifact_count} deployment artifacts",
            OrasDefaults.ANNOTATION_TITLE: "artifacts",
            # Layer metadata
            AnnotationKeys.LAYER_TYPE: LayerTypes.ARTIFACTS,
            AnnotationKeys.LAYER_COMPRESSION: CompressionTypes.GZIP,
            # Artifact counts
            AnnotationKeys.ARTIFACTS_COUNT: str(artifact_count),
        }

        # Add type-specific information if lockfile available
        if lockfile and artifact_types:
            layer["annotations"][AnnotationKeys.ARTIFACTS_COUNT_BY_TYPE] = json.dumps(
                {k: len(v) for k, v in artifact_types.items()}, separators=(",", ":")
            )

            # Add type-specific counts
            for artifact_type, artifacts in artifact_types.items():
                key = AnnotationKeys.artifact_type_count(artifact_type)
                layer["annotations"][key] = str(len(artifacts))

            # Add detailed manifest (first 10 artifacts)
            if lockfile.artifacts:
                layer["annotations"][AnnotationKeys.ARTIFACTS_MANIFEST] = (
                    self._create_layer_artifact_manifest(lockfile.artifacts[:10])
                )

        return layer, tar_gz_path

    def _create_config(self, layers: list) -> Tuple[dict, Optional[str]]:
        """Create OCI v1.1.0 compliant empty config for artifacts."""
        from ..core.oci_types import MediaTypes, OCI_EMPTY_CONFIG_DIGEST, OCI_EMPTY_CONFIG_SIZE
        
        # For OCI v1.1.0 artifacts, return empty config descriptor
        config_obj = {
            "mediaType": MediaTypes.OCI_EMPTY,
            "digest": OCI_EMPTY_CONFIG_DIGEST,  # Already includes sha256: prefix
            "size": OCI_EMPTY_CONFIG_SIZE,
        }
        
        return config_obj, None

    def _create_manifest(
        self,
        layers: list,
        config_obj: dict,
        lockfile: LockFile,
        tag: str,
        lockfile_path: str,
    ) -> dict:
        """Create OCI manifest with proper annotations."""
        manifest = oras.oci.NewManifest()
        manifest["layers"] = layers
        manifest["config"] = config_obj
        
        # Add OCI v1.1.0 artifactType field
        manifest["artifactType"] = MediaTypes.BUNDLE_MANIFEST

        # Determine bundle name
        bundle_name = "conduit-bundle"
        if lockfile_path:
            lockfile_name = Path(lockfile_path).name
            if lockfile_name.endswith(".conduit.lock.yaml"):
                bundle_name = lockfile_name[: -len(".conduit.lock.yaml")]
            elif lockfile_name.endswith(".lock.yaml"):
                bundle_name = lockfile_name[: -len(".lock.yaml")]

        # Calculate total size including config
        config_size = config_obj.get("size", 0) if isinstance(config_obj, dict) else 0
        layers_size = sum(layer.get("size", 0) for layer in layers)
        total_size = layers_size + config_size

        # Generate artifact summary
        artifact_summary = self._generate_artifact_summary(lockfile.artifacts)

        # Create annotations using our standard helper
        annotations = create_bundle_annotations(
            lockfile=lockfile,
            bundle_name=bundle_name,
            bundle_version=tag,
            description=f"Deployment bundle containing {len(lockfile.artifacts)} artifacts from {len(artifact_summary['types'])} sources",
            manifest_hash=getattr(lockfile, "manifestHash", "unknown"),
            lockfile_hash=self._calculate_lockfile_hash(lockfile),
            artifact_count=len(lockfile.artifacts),
            total_size=total_size,
            vendor="Warrical",
            licenses="Apache-2.0",
        )

        # The title is already set by create_bundle_annotations, no need to override

        # Add enhanced annotations
        annotations.update({
            # Conduit schema info
            AnnotationKeys.SCHEMA_VERSION: lockfile.apiVersion,
            AnnotationKeys.LOCKFILE_PATH: os.path.basename(lockfile_path)
            if lockfile_path
            else "unknown",
            # Artifact details
            AnnotationKeys.ARTIFACTS_LIST: self._create_artifact_list_annotation(
                lockfile.artifacts
            ),
            AnnotationKeys.ARTIFACTS_TYPES: ",".join(sorted(artifact_summary["types"])),
            AnnotationKeys.ARTIFACTS_TOTAL_SIZE_BYTES: str(
                artifact_summary["total_size"]
            ),
            AnnotationKeys.ARTIFACTS_TOTAL_SIZE_HUMAN: self._human_readable_size(
                artifact_summary["total_size"]
            ),
            # Source information
            AnnotationKeys.SOURCES_COUNT: str(len(artifact_summary["sources"])),
            AnnotationKeys.SOURCES_DOMAINS: ",".join(
                sorted(artifact_summary["sources"])[:5]
            ),  # Top 5 domains
            # Build information
            AnnotationKeys.BUILD_TOOL: "conduit-pack",
            AnnotationKeys.BUILD_TOOL_VERSION: self._get_conduit_version(),
        })

        # Add layer-specific annotations
        for i, layer in enumerate(layers):
            layer_type = layer.get("annotations", {}).get(
                AnnotationKeys.LAYER_TYPE, "unknown"
            )
            annotations[AnnotationKeys.layer_annotation(i, "type")] = layer_type
            annotations[AnnotationKeys.layer_annotation(i, "size")] = str(
                layer.get("size", 0)
            )

        manifest["annotations"] = annotations
        manifest["mediaType"] = MediaTypes.OCI_MANIFEST

        return manifest

    def _write_objects_to_filesystem(
        self,
        bundle_path: Path,
        manifest: dict,
        config_obj: dict,
        layers: list,
        source_files: list,
    ) -> None:
        """Write OCI objects to filesystem."""
        blobs_dir = bundle_path / "blobs" / "sha256"

        # Write the OCI v1.1.0 empty config blob
        from ..core.oci_types import OCI_EMPTY_CONFIG_DIGEST
        
        empty_config_data = b"{}"
        empty_config_filename = OCI_EMPTY_CONFIG_DIGEST.replace("sha256:", "")
        (blobs_dir / empty_config_filename).write_bytes(empty_config_data)
        
        # Don't update manifest config - it's already set correctly in _create_manifest

        # Write layer blobs
        for layer, source_file in zip(layers, source_files, strict=False):
            if os.path.exists(source_file):
                with open(source_file, "rb") as f:
                    blob_data = f.read()

                layer_digest = layer.get("digest", "").replace("sha256:", "")
                if layer_digest:
                    (blobs_dir / layer_digest).write_bytes(blob_data)

                # Clean up source file
                os.unlink(source_file)

    def _write_manifest_and_get_digest(self, bundle_path: Path, manifest: dict) -> str:
        """Write manifest and return its digest."""
        blobs_dir = bundle_path / "blobs" / "sha256"

        manifest_data = json.dumps(manifest, separators=(",", ":")).encode()
        manifest_digest = self._calculate_sha256(manifest_data)
        (blobs_dir / manifest_digest).write_bytes(manifest_data)

        return f"sha256:{manifest_digest}"

    def _create_index(self, bundle_path: Path, manifest_digest: str) -> None:
        """Create index.json file."""
        blobs_dir = bundle_path / "blobs" / "sha256"
        manifest_blob_path = blobs_dir / manifest_digest.replace("sha256:", "")
        manifest_size = manifest_blob_path.stat().st_size

        index = {
            "schemaVersion": 2,
            "mediaType": MediaTypes.OCI_INDEX,
            "manifests": [
                {
                    "mediaType": MediaTypes.OCI_MANIFEST,
                    "digest": manifest_digest,
                    "size": manifest_size,
                }
            ],
        }

        with open(bundle_path / "index.json", "w", encoding="utf-8") as f:
            json.dump(index, f, separators=(",", ":"))

    def _calculate_sha256(self, data: bytes) -> str:
        """Calculate SHA256 digest of data."""
        return hashlib.sha256(data).hexdigest()

    def _calculate_lockfile_hash(self, lockfile: LockFile) -> str:
        """Calculate hash of the lockfile content."""
        lockfile_json = lockfile.dump_canonical_json()
        return f"sha256:{self._calculate_sha256(lockfile_json.encode())}"

    def _generate_artifact_summary(self, artifacts: list) -> dict:
        """Generate summary statistics about artifacts."""
        summary = {
            "types": set(),
            "sources": set(),
            "total_size": 0,
            "artifacts_by_type": {},
        }

        for artifact in artifacts:
            # Track types
            summary["types"].add(artifact.type)

            # Track source domains
            if artifact.origin.startswith(("http://", "https://")):
                domain = urlparse(artifact.origin).netloc
                summary["sources"].add(domain)
            elif artifact.type == "oci":
                # Extract registry from OCI references
                # Handle both 'registry.io/path' and 'oci://registry.io/path' formats
                origin = artifact.origin
                origin = origin.removeprefix("oci://")  # Remove 'oci://' prefix

                # Extract registry hostname (before first /)
                registry = origin.split("/")[0]

                # Only add if it looks like a valid registry hostname
                if registry and "." in registry:  # e.g., quay.io, docker.io
                    summary["sources"].add(registry)

            # Count by type
            if artifact.type not in summary["artifacts_by_type"]:
                summary["artifacts_by_type"][artifact.type] = 0
            summary["artifacts_by_type"][artifact.type] += 1

            # Add size from artifact
            if hasattr(artifact, "size") and artifact.size:
                summary["total_size"] += int(artifact.size)

        return summary

    def _create_artifact_list_annotation(self, artifacts: list) -> str:
        """Create a compact artifact listing for annotations."""
        # Create a structured but compact representation
        artifact_list = []

        for artifact in artifacts[:20]:  # Limit to first 20 to avoid huge annotations
            # Format: "name@type:target"
            name = os.path.basename(artifact.target)
            entry = f"{name}@{artifact.type}:{artifact.target}"
            artifact_list.append(entry)

        if len(artifacts) > 20:
            artifact_list.append(f"...and {len(artifacts) - 20} more")

        return ";".join(artifact_list)

    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size_float < 1024.0:
                return f"{size_float:.1f}{unit}"
            size_float /= 1024.0
        return f"{size_float:.1f}TB"

    async def _calculate_file_checksum_async(self, file_path: Path) -> str:
        """Calculate SHA256 checksum asynchronously."""

        def calculate():
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)
            return f"sha256:{sha256_hash.hexdigest()}"

        return await asyncio.to_thread(calculate)

    def _get_conduit_version(self) -> str:
        """Get the current conduit version."""
        try:
            return version("conduit")
        except (ImportError, ModuleNotFoundError, Exception):
            logger.warning("Could not determine Conduit version, using 'unknown'")
            return "unknown"

    def _create_layer_artifact_manifest(self, artifacts: list) -> str:
        """Create a detailed manifest of artifacts for layer annotation."""
        manifest_entries = []

        for artifact in artifacts:
            entry = {
                "name": os.path.basename(artifact.target),
                "type": artifact.type,
                "target": artifact.target,
                "checksum": artifact.checksum.split(":")[-1][
                    :12
                ],  # First 12 chars of hash
            }
            manifest_entries.append(entry)

        return json.dumps(manifest_entries, separators=(",", ":"))

    def _create_deterministic_targz(self, source_dir: Path) -> str:
        """
        Create a tar.gz file with deterministic content.

        Unlike oras.utils.make_targz, this ensures:
        - Consistent file ordering
        - No timestamps
        - Proper relative paths
        - Consistent permissions

        Args:
            source_dir: Directory to archive

        Returns:
            Path to created tar.gz file
        """

        # Create temporary tar.gz file
        fd, tar_gz_path = tempfile.mkstemp(suffix=".tar.gz")
        os.close(fd)

        with open(tar_gz_path, "wb") as f, gzip.GzipFile(
            filename="", mode="wb", compresslevel=9, mtime=0, fileobj=f
        ) as gz, tarfile.open(fileobj=gz, mode="w") as tar:
            # Get all files sorted for deterministic ordering
            all_files = sorted(source_dir.rglob("*"))

            for file_path in all_files:
                if file_path.is_file():
                    # Calculate relative path from source_dir
                    rel_path = file_path.relative_to(source_dir)

                    # Create tarinfo with deterministic attributes
                    tarinfo = tar.gettarinfo(
                        str(file_path), arcname=str(rel_path)
                    )

                    # Zero out timestamps for determinism
                    tarinfo.mtime = 0
                    tarinfo.uid = 0
                    tarinfo.gid = 0
                    tarinfo.uname = ""
                    tarinfo.gname = ""

                    # Add file to tar
                    with open(file_path, "rb") as f2:
                        tar.addfile(tarinfo, f2)

        return tar_gz_path

    async def _push_to_registry(
        self,
        bundle_path: str,
        registry_target: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        insecure: bool = False,
        progress: Optional[PackProgress] = None,
        progress_callback: Optional[Callable] = None,
    ) -> None:
        """
        Push the bundle to a registry using ORAS.

        Args:
            bundle_path: Path to the OCI bundle
            registry_target: Registry URL (e.g., "ghcr.io/org/bundle:v1.0")
            username: Optional registry username
            password: Optional registry password
            insecure: Allow insecure HTTP connections
            progress: Progress tracking object
            progress_callback: Optional callback for progress updates
        """
        if progress:
            progress.current_status = "pushing to registry"
        if progress_callback:
            progress_callback({"type": "push_start", "registry": registry_target})

        # Get the manifest digest from the bundle before pushing
        bundle_digest = "unknown"
        try:
            index_path = Path(bundle_path) / "index.json"
            if index_path.exists():
                with open(index_path, encoding="utf-8") as f:
                    index = json.load(f)
                if index.get("manifests") and len(index["manifests"]) > 0:
                    bundle_digest = index["manifests"][0].get("digest", "unknown")
        except Exception as e:
            logger.warning(f"Failed to read bundle digest from {bundle_path}: {e!s}")
            pass  # Continue with "unknown" if we can't read the digest

        # Extract hostname from registry target
        hostname = registry_target.split("/", maxsplit=1)[0]

        # Create ORAS registry directly with basic auth backend for htpasswd registries
        # This avoids the JSON decode error from token auth endpoints that don't exist
        registry_kwargs: Dict[str, Any] = {
            "hostname": hostname,
            "auth_backend": "basic",  # Force basic auth instead of token
            "insecure": insecure,  # Default to secure connections
            "tls_verify": not insecure,  # Use TLS unless insecure is True
        }

        client = Registry(**registry_kwargs)

        # Login if credentials provided
        if username and password:
            try:
                # For Registry, use set_basic_auth on the auth object
                client.auth.set_basic_auth(username, password)
            except Exception as e:
                logger.warning(
                    f"Failed to set basic auth for registry {hostname}: {e!s}"
                )
                # Continue even if auth setup has issues
                pass

        try:
            # Push the bundle - Registry.push expects files parameter
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, lambda: client.push(target=registry_target, files=[bundle_path])
            )
            result.raise_for_status()  # Raise if push failed
            logger.info(f"Pack Push result: {result}")

            # Use the pre-extracted digest instead of trying to parse result
            digest = bundle_digest

            if progress:
                progress.current_status = "push complete"
            if progress_callback:
                progress_callback({"type": "push_complete", "digest": digest})

        except (Exception, HTTPError) as e:
            logged_err_msg = (
                f"HTTPError: {e!s}" if isinstance(e, HTTPError) else f"Error: {e!s}"
            )
            logger.error(f"Failed to push bundle to registry {registry_target}: {e!s}")
            logger.error(f"{logged_err_msg}")

            error_msg = f"push failed: {e!s}"
            if progress:
                progress.current_status = error_msg
            if progress_callback:
                progress_callback({"type": "push_error", "error": str(e)})
            raise
