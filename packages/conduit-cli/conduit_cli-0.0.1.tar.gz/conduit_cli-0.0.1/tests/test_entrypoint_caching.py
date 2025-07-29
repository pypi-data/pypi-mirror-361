"""Tests for entrypoint script caching and security."""

import json
import repro_tarfile as tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, NamedTuple

import pytest
import yaml

from conduit.core.models import (
    Manifest,
    ManifestArtifact,
    ManifestEntrypoint,
    ManifestMetadata,
)
from conduit.handlers.factory import HandlerFactory
from conduit.services.cache import CacheResolver
from conduit.services.lockfile import LockfileService
from conduit.services.pack import PackService, PackServiceError

from .conftest import AppDefaults


class EntrypointParams(NamedTuple):
    """Parameters for entrypoint script tests."""

    test_id: str = "caching-entrypoint"
    version: str = "1.0.0"
    artifact_mode: int = AppDefaults.ARTIFACT_MODE
    script_mode: int = AppDefaults.SCRIPT_MODE


@dataclass
class EntrypointScenario:
    temp_dir: Path
    artifact_path: Path
    lockfile_path: Path
    bundle_output_dir: Path
    bundle_version: str
    script_object: Dict[str, str]
    manifest: Manifest
    cache_service: CacheResolver
    handler_factory: HandlerFactory
    lockfile_service: LockfileService
    pack_service: PackService


@pytest.fixture
def entrypoint_scenario(request, temp_dir):
    """Create a scenario for entrypoint testing."""

    params: EntrypointParams = (
        request.param
        if request and hasattr(request, "param") and request.param
        else EntrypointParams()
    )

    # Create artifact directory and artifact file
    artifact_dir = temp_dir / f"{params.test_id}-artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "app.tar.gz"
    artifact_path.write_text("test content")

    # Create script directory
    script_dir = temp_dir / f"{params.test_id}-scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / f"{params.test_id}.sh"

    # Create test artifact

    # Create entrypoint script
    original_content = "#!/bin/bash\necho 'Original deployment script'"
    script_path.write_text(original_content)
    script_path.chmod(0o755)

    cache_dir = temp_dir / f"{params.test_id}-cache"
    lockfile_path = temp_dir / f"{params.test_id}.lock.yaml"
    bundle_output_dir = temp_dir / f"{params.test_id}-output" / "bundle"

    # Create manifest
    manifest = Manifest(
        apiVersion=AppDefaults.API_VERSION,
        kind="Manifest",
        metadata=ManifestMetadata(
            name=f"{params.test_id}-bundle", version=params.version
        ),
        entrypoint=ManifestEntrypoint(script=str(script_path), mode="0755"),
        artifacts=[
            ManifestArtifact(
                name=f"{params.test_id}-artifact",
                origin=str(artifact_path),
                target="/app/app.tar.gz",
            )
        ],
    )

    cache_service = CacheResolver(cache_dir=cache_dir)
    handler_factory = HandlerFactory(cache_service=cache_service)
    lockfile_service = LockfileService(
        cache_service=cache_service, handler_factory=handler_factory
    )
    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    return EntrypointScenario(
        temp_dir=temp_dir,
        artifact_path=artifact_path,
        lockfile_path=lockfile_path,
        bundle_output_dir=bundle_output_dir,
        bundle_version=f"v{params.version}",
        script_object={"path": script_path, "original_content": original_content},
        manifest=manifest,
        cache_service=cache_service,
        handler_factory=handler_factory,
        lockfile_service=lockfile_service,
        pack_service=pack_service,
    )


@pytest.fixture
def malicious_content():
    """Create a malicious entrypoint script for testing."""
    return str("#!/bin/bash\necho 'MALICIOUS CODE HERE!'")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.asyncio(
    "entrypoint_params",
    [EntrypointParams(test_id="clear-cache")],
    ids=lambda p: p.test_id,
    indirect=True,
)
@pytest.mark.asyncio
async def test_entrypoint_script_caching_prevents_tampering(
    entrypoint_scenario, malicious_content
):
    """Test that cached entrypoint scripts prevent tampering between lock and pack commands.
    by ensuring that the entrypoint script is not modified after it has been cached.
    """
    # INITIALIZE
    script_path = entrypoint_scenario.script_object.get("path")
    entrypoint_scenario.script_object.get("original_content")
    manifest = entrypoint_scenario.manifest
    cache_service = entrypoint_scenario.cache_service
    lockfile_service = entrypoint_scenario.lockfile_service
    lockfile_path = entrypoint_scenario.lockfile_path
    bundle_output_dir = entrypoint_scenario.bundle_output_dir
    bundle_version = entrypoint_scenario.bundle_version

    # ARRANGE
    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest
    )
    with open(lockfile_path, "w", encoding="utf-8") as f:
        yaml.dump(lockfile.model_dump(), f)
    script_path.write_text(malicious_content)
    cache_service.clear_cache()

    # Re-initialize pack_service after clearing cache
    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=entrypoint_scenario.handler_factory,
    )

    # ASSERT
    with pytest.raises(PackServiceError) as exc_info:
        await pack_service.create_bundle(
            lockfile_path=str(lockfile_path),
            output_path=str(bundle_output_dir),
            tag=bundle_version,
        )

    assert "has been modified" in str(exc_info.value), (
        "Expected tampering error not raised"
    )


@pytest.mark.asyncio(
    "entrypoint_params",
    [EntrypointParams(test_id="use-cache-ignore-tampered")],
    ids=lambda p: p.test_id,
    indirect=True,
)
@pytest.mark.asyncio
async def test_entrypoint_uses_cache_ignoring_tampered_file(
    entrypoint_scenario, malicious_content
):
    """Test that pack uses cached entrypoint even if file is tampered."""

    # INITIALIZE
    script_path = entrypoint_scenario.script_object.get("path")
    script_original_content = entrypoint_scenario.script_object.get("original_content")
    manifest = entrypoint_scenario.manifest
    lockfile_service = entrypoint_scenario.lockfile_service
    lockfile_path = entrypoint_scenario.lockfile_path
    bundle_output_dir = entrypoint_scenario.bundle_output_dir
    bundle_version = entrypoint_scenario.bundle_version
    pack_service = entrypoint_scenario.pack_service  # (SUT)
    events = []

    def progress_callback(event):
        events.append(event)

    # ARRANGE
    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest
    )
    with open(lockfile_path, "w", encoding="utf-8") as f:
        yaml.dump(lockfile.model_dump(), f)
    script_path.write_text(malicious_content)
    bundle_path, layers_created, _ = await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(bundle_output_dir),
        tag=bundle_version,
        progress_callback=progress_callback,
    )

    #
    # Verify bundle was created successfully
    assert Path(bundle_path).exists(), "Bundle was not created successfully"
    assert layers_created == 2, f"Expected 2 layers to be created, got {layers_created}"

    # Check that it used cache
    retrieved_event = next(
        (e for e in events if e.get("type") == "entrypoint_retrieved"), None
    )
    assert retrieved_event is not None, "Expected entrypoint retrieval event not found"
    assert retrieved_event["source"] == "cache", (
        "Expected entrypoint to be retrieved from cache"
    )

    # Verify the ORIGINAL content is in the bundle (not the tampered content)
    bundle_dir = Path(bundle_path)
    index_path = bundle_dir / "index.json"
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    manifest_ref = index["manifests"][0]
    manifest_digest = manifest_ref["digest"].replace("sha256:", "")

    manifest_path = bundle_dir / "blobs" / "sha256" / manifest_digest
    with open(manifest_path, encoding="utf-8") as f:
        oci_manifest = json.load(f)

    # Find metadata layer
    metadata_layer = None
    for layer in oci_manifest.get("layers", []):
        if (
            layer.get("annotations", {}).get("com.warrical.conduit.layer.type")
            == "metadata"
        ):
            metadata_layer = layer
            break

    assert metadata_layer is not None

    # Extract and verify script content
    metadata_digest = metadata_layer["digest"].replace("sha256:", "")
    metadata_blob_path = bundle_dir / "blobs" / "sha256" / metadata_digest

    with tarfile.open(metadata_blob_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name == f"metadata/{script_path.name}":
                extracted_file = tar.extractfile(member)
                if extracted_file:
                    content = extracted_file.read().decode()
                    assert content == script_original_content  # Original, not tampered!
                    assert "MALICIOUS" not in content
                    break
        else:
            pytest.fail("Entrypoint script not found in metadata layer")


@pytest.mark.asyncio(
    "entrypoint_params",
    [EntrypointParams(test_id="cached-even-if-deleted")],
    ids=lambda p: p.test_id,
    indirect=True,
)
@pytest.mark.asyncio
async def test_entrypoint_script_from_cache_when_file_deleted(
    entrypoint_scenario, malicious_content
):
    """Test that pack can use cached entrypoint script even if original is deleted."""
    script_path = entrypoint_scenario.script_object.get("path")
    script_original_content = entrypoint_scenario.script_object.get("original_content")
    manifest = entrypoint_scenario.manifest
    temp_dir = entrypoint_scenario.temp_dir
    lockfile_service = entrypoint_scenario.lockfile_service
    lockfile_path = entrypoint_scenario.lockfile_path
    pack_service = entrypoint_scenario.pack_service  # (SUT)

    # ARRANGE
    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest
    )
    with open(lockfile_path, "w", encoding="utf-8") as f:
        yaml.dump(lockfile.model_dump(), f)
    script_path.write_text(malicious_content)
    bundle_path, layers_created, _ = await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(temp_dir / "bundle"),
        tag="v1.0.0",
    )

    # Verify bundle was created successfully
    assert Path(bundle_path).exists()
    assert layers_created == 2

    bundle_dir = Path(bundle_path)
    index_path = bundle_dir / "index.json"
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    manifest_ref = index["manifests"][0]
    manifest_digest = manifest_ref["digest"].replace("sha256:", "")

    manifest_path = bundle_dir / "blobs" / "sha256" / manifest_digest
    with open(manifest_path, encoding="utf-8") as f:
        oci_manifest = json.load(f)

    # Find metadata layer
    metadata_layer = None
    for layer in oci_manifest.get("layers", []):
        if (
            layer.get("annotations", {}).get("com.warrical.conduit.layer.type")
            == "metadata"
        ):
            metadata_layer = layer
            break

    assert metadata_layer is not None

    # Extract and verify script content
    metadata_digest = metadata_layer["digest"].replace("sha256:", "")
    metadata_blob_path = bundle_dir / "blobs" / "sha256" / metadata_digest

    with tarfile.open(metadata_blob_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name == f"metadata/{script_path.name}":
                extracted_file = tar.extractfile(member)
                if extracted_file:
                    content = extracted_file.read().decode()
                    assert content == script_original_content  # Original, not tampered!
                    assert "MALICIOUS" not in content
                    break
        else:
            pytest.fail("Entrypoint script not found in metadata layer")


@pytest.mark.asyncio
async def test_entrypoint_progress_callbacks(temp_dir):
    """Test that entrypoint caching reports progress correctly."""
    # Create test files
    artifact_path = temp_dir / "app.tar.gz"
    artifact_path.write_text("test content")

    script_path = temp_dir / "setup.sh"
    script_path.write_text("#!/bin/bash\necho 'Setup'")
    script_path.chmod(0o755)

    manifest = Manifest(
        apiVersion=AppDefaults.API_VERSION,
        kind="Manifest",
        metadata=ManifestMetadata(name="progress-app", version="1.0.0"),
        entrypoint=ManifestEntrypoint(script=str(script_path), mode="0755"),
        artifacts=[
            ManifestArtifact(
                name="app", origin=str(artifact_path), target="/app.tar.gz"
            )
        ],
    )

    # Track progress events
    events = []

    def progress_callback(event):
        events.append(event)

    # Generate lockfile with progress tracking
    cache_service = CacheResolver(cache_dir=temp_dir / "cache")
    lockfile_service = LockfileService(cache_service=cache_service)
    handler_factory = HandlerFactory(cache_service=cache_service)

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest,
        handler_factory=handler_factory,
        progress_callback=progress_callback,
    )

    # Check for entrypoint caching events
    entrypoint_events = [
        e for e in events if e.get("type", "").startswith("entrypoint_")
    ]
    assert len(entrypoint_events) >= 2

    caching_event = next(
        (e for e in entrypoint_events if e["type"] == "entrypoint_caching"), None
    )
    assert caching_event is not None
    assert "setup.sh" in caching_event["message"]
    assert lockfile.entrypoint is not None, "Lockfile should have entrypoint defined"
    assert caching_event["checksum"] == lockfile.entrypoint.checksum, (
        "Checksum should match lockfile entrypoint checksum"
    )

    cached_event = next(
        (e for e in entrypoint_events if e["type"] == "entrypoint_cached"), None
    )
    assert cached_event is not None, "Expected entrypoint cached event not found"
    assert "successfully" in cached_event["message"], (
        "Expected success message in entrypoint cached event"
    )

    # Save lockfile
    lockfile_path = temp_dir / "progress.lock.yaml"
    with open(lockfile_path, "w", encoding="utf-8") as f:
        yaml.dump(lockfile.model_dump(), f)

    # Clear events and pack with progress tracking
    events.clear()

    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(temp_dir / "bundle"),
        tag="v1.0.0",
        progress_callback=progress_callback,
    )

    # Check for entrypoint verification events during pack
    pack_entrypoint_events = [
        e for e in events if e.get("type", "").startswith("entrypoint_")
    ]
    assert len(pack_entrypoint_events) >= 2

    verification_event = next(
        (e for e in pack_entrypoint_events if e["type"] == "entrypoint_verification"),
        None,
    )
    assert verification_event is not None
    assert "setup.sh" in verification_event["message"]

    retrieved_event = next(
        (e for e in pack_entrypoint_events if e["type"] == "entrypoint_retrieved"), None
    )
    assert retrieved_event is not None
    assert retrieved_event["source"] in ["cache", "filesystem"]
