"""
Unpack service - Extracts artifacts from OCI bundles in registries.

This service handles pulling OCI bundles from registries and extracting
their artifacts to the local filesystem with checksum verification.
"""

import asyncio
import json
import subprocess
import repro_tarfile as tarfile
import tempfile
from pathlib import Path
from typing import Callable, Optional, Tuple

import yaml
from oras.provider import Registry

from ..core.models import LockFile


class UnpackService:
    """Service for unpacking OCI bundles from registries."""

    async def unpack_from_registry(
        self,
        registry_url: str,
        output_path: str,
        registry_username: Optional[str] = None,
        registry_password: Optional[str] = None,
        insecure: bool = False,
        progress_callback: Optional[Callable] = None,
        auto_execute_entrypoint: bool = True,
    ) -> Tuple[str, int]:
        """
        Unpack an OCI bundle from a registry.

        Args:
            registry_url: OCI registry URL (e.g., "oci://ghcr.io/org/bundle:v1.0")
            output_path: Directory to extract artifacts to
            registry_username: Optional registry username
            registry_password: Optional registry password
            insecure: Allow insecure HTTP connections
            progress_callback: Optional callback for progress updates
            auto_execute_entrypoint: Whether to execute the entrypoint script

        Returns:
            Tuple of (output_path, artifacts_extracted_count)
        """
        # Validate registry URL
        if not registry_url.startswith(("oci://", "file://")):
            msg = "Invalid OCI registry URL format. Expected: oci://registry/repo:tag"
            raise ValueError(msg)

        if registry_url.startswith("oci://"):
            # Check it has more than just oci://
            remaining = registry_url[6:]  # Remove oci://
            if not remaining or "/" not in remaining:
                msg = (
                    "Invalid OCI registry URL format. Expected: oci://registry/repo:tag"
                )
                raise ValueError(msg)

        # Report start
        if progress_callback:
            progress_callback({
                "type": "unpack_start",
                "registry": registry_url,
                "message": f"Pulling bundle from {registry_url}",
            })

        # For file:// URLs (testing), handle differently
        if registry_url.startswith("file://"):
            bundle_path = registry_url.replace("file://", "")
            return await self.unpack_local_bundle(
                bundle_path, output_path, progress_callback
            )

        # Parse registry URL
        url_parts = registry_url.replace("oci://", "")
        hostname = url_parts.split("/")[0]

        # Create registry client
        registry_kwargs = {
            "hostname": hostname,
            "insecure": insecure,
            "auth_backend": "basic",  # Always use basic auth
            "tls_verify": not insecure,
        }

        registry = Registry(**registry_kwargs)

        if registry_username and registry_password:
            registry.auth.set_basic_auth(registry_username, registry_password)

        # Pull bundle to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Report pulling
            if progress_callback:
                progress_callback({
                    "type": "pull_start",
                    "message": "Pulling bundle from registry",
                })

            # Pull using ORAS
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, lambda: registry.pull(target=url_parts, outdir=str(temp_path))
                )

                # ORAS returns a list of extracted paths
                if result and isinstance(result, list) and len(result) > 0:
                    # Use the first path returned
                    bundle_dir = result[0]
                else:
                    # Fallback to temp_path
                    bundle_dir = str(temp_path)

            except Exception as e:
                msg = f"Failed to pull bundle: {e!s}"
                raise Exception(msg)

            if progress_callback:
                progress_callback({
                    "type": "pull_complete",
                    "message": "Bundle pulled successfully",
                })

            # Unpack the pulled bundle
            return await self.unpack_local_bundle(
                bundle_dir, output_path, progress_callback, auto_execute_entrypoint
            )

    async def unpack_local_bundle(
        self,
        bundle_path: str,
        output_path: str,
        progress_callback: Optional[Callable] = None,
        auto_execute_entrypoint: bool = True,
    ) -> Tuple[str, int]:
        """Unpack a local OCI bundle."""
        bundle_dir = Path(bundle_path)
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read index.json
        index_path = bundle_dir / "index.json"
        if not index_path.exists():
            msg = f"No index.json found in bundle at {bundle_path}"
            raise FileNotFoundError(msg)

        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)

        # Get manifest
        if not index.get("manifests"):
            msg = "No manifests found in bundle index"
            raise ValueError(msg)

        manifest_ref = index["manifests"][0]
        manifest_digest = manifest_ref["digest"].replace("sha256:", "")

        # Read manifest
        manifest_path = bundle_dir / "blobs" / "sha256" / manifest_digest
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        # Find metadata and artifacts layers
        metadata_layer = None
        artifacts_layer = None

        for layer in manifest.get("layers", []):
            layer_type = layer.get("annotations", {}).get(
                "com.warrical.conduit.layer.type"
            )
            if layer_type == "metadata":
                metadata_layer = layer
            elif layer_type == "artifacts":
                artifacts_layer = layer

        if not metadata_layer:
            msg = "No metadata layer found in bundle"
            raise ValueError(msg)
        if not artifacts_layer:
            msg = "No artifacts layer found in bundle"
            raise ValueError(msg)

        # Extract metadata layer to read lockfile
        if progress_callback:
            progress_callback({
                "type": "extract_metadata",
                "message": "Reading bundle metadata",
            })

        metadata_digest = metadata_layer["digest"].replace("sha256:", "")
        metadata_blob_path = bundle_dir / "blobs" / "sha256" / metadata_digest

        metadata_contents = metadata_layer.get("annotations", {}).get(
            "com.warrical.conduit.layer.contents"
        )
        has_entrypoint = "entrypoint" in metadata_contents

        lockfile_data = None
        entrypoint_data = None
        with tarfile.open(metadata_blob_path, "r:gz") as tar:
            for member in tar.getmembers():
                if lockfile_data and (not has_entrypoint or entrypoint_data):
                    break
                if lockfile_data and has_entrypoint and entrypoint_data:
                    break

                if member.name.endswith("conduit.lock.json"):
                    f = tar.extractfile(member)
                    if f:
                        lockfile_data = json.load(f)
                        continue

                if has_entrypoint and lockfile_data and lockfile_data.get("entrypoint", {}).get("script"):
                    expected_script_name = Path(lockfile_data["entrypoint"]["script"]).name
                    if member.name.endswith(expected_script_name):
                        f = tar.extractfile(member)
                        if f:
                            entrypoint_data = f.read()
                            continue

        if not lockfile_data:
            msg = "No lockfile found in metadata layer"
            raise ValueError(msg)

        # Parse lockfile
        lockfile = LockFile(**lockfile_data)

        # Write lockfile to output directory as YAML
        lockfile_name = "conduit.lock.yaml"
        if lockfile.name and lockfile.version:
            lockfile_name = f"{lockfile.name}-{lockfile.version}.conduit.lock.yaml"
        elif lockfile.name:
            lockfile_name = f"{lockfile.name}.conduit.lock.yaml"

        lockfile_path = output_dir / lockfile_name
        lockfile_yaml = lockfile.to_yaml()
        lockfile_path.write_text(lockfile_yaml)

        # Report lockfile extraction
        if progress_callback:
            progress_callback({
                "type": "lockfile_extracted",
                "name": lockfile_name,
                "message": "Extracted lockfile",
            })

        # Extract entrypoint script if present
        if entrypoint_data:
            entrypoint_filename = "entrypoint.sh"
            if lockfile.entrypoint and lockfile.entrypoint.script:
                # Use the original filename from the lockfile
                entrypoint_filename = Path(lockfile.entrypoint.script).name

            entrypoint_path = output_dir / entrypoint_filename
            entrypoint_path.write_bytes(entrypoint_data)

            # Set executable permissions if specified in lockfile
            if lockfile.entrypoint and lockfile.entrypoint.mode:
                try:
                    mode = int(lockfile.entrypoint.mode, 8)
                    entrypoint_path.chmod(mode)
                except (ValueError, OSError):
                    # If mode conversion fails, set basic executable permissions
                    entrypoint_path.chmod(0o755)
            else:
                # Default executable permissions
                entrypoint_path.chmod(0o755)

            if progress_callback:
                progress_callback({
                    "type": "entrypoint_extracted",
                    "name": entrypoint_filename,
                    "message": "Extracted entrypoint script",
                })

        # Extract artifacts layer
        if progress_callback:
            progress_callback({
                "type": "extract_artifacts",
                "message": f"Extracting {len(lockfile.artifacts)} artifacts",
                "total": len(lockfile.artifacts),
            })

        artifacts_digest = artifacts_layer["digest"].replace("sha256:", "")
        artifacts_blob_path = bundle_dir / "blobs" / "sha256" / artifacts_digest

        extracted_count = 0
        missing_artifacts = []
        with tarfile.open(artifacts_blob_path, "r:gz") as tar:
            for artifact in lockfile.artifacts:
                # Find corresponding file in tar
                target_path = artifact.target.lstrip("/")

                # Look for the file in the tar
                member = None
                for m in tar.getmembers():
                    if m.name.endswith(target_path) or m.name == f"./{target_path}":
                        member = m
                        break

                if not member:
                    missing_artifacts.append(artifact.target)
                    if progress_callback:
                        progress_callback({
                            "type": "artifact_missing",
                            "name": artifact.target,
                            "message": f"Artifact {artifact.target} not found in bundle",
                        })
                    continue

                # Extract to output directory
                output_file = output_dir / target_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

                # Extract file
                f = tar.extractfile(member)
                if f:
                    content = f.read()

                    # Verify checksum
                    import hashlib

                    actual_checksum = f"sha256:{hashlib.sha256(content).hexdigest()}"

                    if actual_checksum != artifact.checksum:
                        if progress_callback:
                            progress_callback({
                                "type": "checksum_error",
                                "name": artifact.target,
                                "expected": artifact.checksum,
                                "actual": actual_checksum,
                            })
                        msg = f"Checksum mismatch for {artifact.target}"
                        raise ValueError(msg)

                    # Write file
                    output_file.write_bytes(content)

                    # Set executable bit if needed
                    if member.mode & 0o111:
                        output_file.chmod(output_file.stat().st_mode | 0o111)

                    extracted_count += 1

                    if progress_callback:
                        progress_callback({
                            "type": "artifact_extracted",
                            "name": artifact.target,
                            "size": len(content),
                            "count": extracted_count,
                            "total": len(lockfile.artifacts),
                        })

        # Verify that ALL artifacts were extracted successfully
        if missing_artifacts:
            msg = f"Failed to extract {len(missing_artifacts)} artifacts: {', '.join(missing_artifacts)}"
            raise ValueError(msg)

        # Verify that the extracted count matches the expected count
        if extracted_count != len(lockfile.artifacts):
            msg = f"Expected to extract {len(lockfile.artifacts)} artifacts, but only extracted {extracted_count}"
            raise ValueError(msg)

        # Execute entrypoint script if present and auto_execute_entrypoint is enabled
        if entrypoint_data and auto_execute_entrypoint:
            entrypoint_filename = "entrypoint.sh"
            if lockfile.entrypoint and lockfile.entrypoint.script:
                # Use the original filename from the lockfile
                entrypoint_filename = Path(lockfile.entrypoint.script).name

            entrypoint_path = output_dir / entrypoint_filename

            if progress_callback:
                progress_callback({
                    "type": "entrypoint_execution",
                    "name": entrypoint_filename,
                    "message": "Executing entrypoint script",
                })

            try:
                # Run the entrypoint script and capture output
                result = subprocess.run(
                    [str(entrypoint_path.absolute())],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=str(output_dir),  # Run from the output directory
                )

                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_completed",
                        "name": entrypoint_filename,
                        "message": "Entrypoint script executed successfully",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    })

            except subprocess.CalledProcessError as e:
                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_error",
                        "name": entrypoint_filename,
                        "message": f"Entrypoint script execution failed: {e}",
                        "stdout": e.stdout,
                        "stderr": e.stderr,
                        "returncode": e.returncode,
                    })
                msg = f"Entrypoint script execution failed with return code {e.returncode}: {e.stderr}"
                raise Exception(msg)
            except FileNotFoundError:
                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_error",
                        "name": entrypoint_filename,
                        "message": "Entrypoint script not found or not executable",
                    })
                msg = (
                    f"Entrypoint script not found or not executable: {entrypoint_path}"
                )
                raise Exception(msg)

        if progress_callback:
            progress_callback({
                "type": "unpack_complete",
                "message": f"Successfully extracted {extracted_count} artifacts and lockfile",
                "count": extracted_count + 1,
            })

        return str(output_dir), extracted_count + 1
