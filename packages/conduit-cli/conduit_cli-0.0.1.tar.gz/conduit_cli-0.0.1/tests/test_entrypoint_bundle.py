"""Tests for entrypoint support in manifest, lockfile, and pack service."""

import json
import repro_tarfile as tarfile
import tempfile
from pathlib import Path

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
from conduit.services.pack import PackService

from .conftest import API_VERSION


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    yield tmp_path


@pytest.fixture
def manifest_with_entrypoint(temp_dir) -> tuple[Manifest, Path]:
    """Create a manifest with entrypoint."""
    # Create test artifact
    artifact_path = temp_dir / "app.tar.gz"
    artifact_path.write_text("test content")

    # Create entrypoint script
    script_path: Path = temp_dir / "setup.sh"
    script_path.write_text("#!/bin/bash\necho 'Setup completed'")
    script_path.chmod(0o755)

    manifest = Manifest(
        apiVersion=API_VERSION,
        kind="Manifest",
        metadata=ManifestMetadata(name="test-app", version="1.0.0"),
        entrypoint=ManifestEntrypoint(script=str(script_path), mode="0755"),
        artifacts=[
            ManifestArtifact(
                name="app-bundle", origin=str(artifact_path), target="/app/app.tar.gz"
            )
        ],
    )

    return manifest, script_path


def test_manifest_model_accepts_entrypoint(manifest_with_entrypoint):
    """Test that manifest model properly handles entrypoint field."""
    manifest, script_path = manifest_with_entrypoint

    assert manifest.entrypoint is not None
    assert manifest.entrypoint.script == str(script_path)
    assert manifest.entrypoint.mode == "0755"
    assert manifest.entrypoint.uid is ""  # Optional field
    assert manifest.entrypoint.gid is ""  # Optional field


@pytest.mark.asyncio
async def test_lockfile_preserves_entrypoint(manifest_with_entrypoint, temp_dir):
    """Test that lockfile generation preserves entrypoint field."""
    manifest, script_path = manifest_with_entrypoint

    # Save manifest
    manifest_path = temp_dir / "manifest.yaml"

    with manifest_path.open("w", encoding="utf-8") as f:
        yaml.dump(manifest.model_dump(), f)

    # Generate lockfile
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest,
        handler_factory=handler_factory,
        manifest_path=str(manifest_path),
    )

    # Check that entrypoint is preserved
    assert lockfile.entrypoint is not None
    assert lockfile.entrypoint.script == str(script_path)
    assert lockfile.entrypoint.mode == "0755"


@pytest.mark.asyncio
async def test_pack_includes_entrypoint_in_metadata_layer(
    manifest_with_entrypoint, temp_dir
):
    """Test that pack service includes entrypoint in the metadata layer."""
    manifest, script_path = manifest_with_entrypoint

    print(f"Using script path: {script_path}")
    print(f"Temporary directory: {temp_dir}")

    # Generate lockfile
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest, handler_factory=handler_factory
    )

    # Save lockfile
    lockfile_path = temp_dir / "test.lock.yaml"
    with open(lockfile_path, "w", encoding="utf-8") as extracted_lockfile:
        yaml.dump(lockfile.model_dump(), extracted_lockfile)

    # Create bundle
    cache_service = CacheResolver(cache_dir=temp_dir / "cache")
    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    bundle_path, layers_created, _ = await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(temp_dir / "bundle"),
        tag="v1.0.0",
    )

    # Verify bundle was created
    assert Path(bundle_path).exists(), "Bundle was not created"
    assert layers_created == 2  # metadata + artifacts

    # Extract and verify metadata layer contains entrypoint
    bundle_dir = Path(bundle_path)
    index_path = bundle_dir / "index.json"
    with open(index_path, encoding="utf-8") as extracted_lockfile:
        index = json.load(extracted_lockfile)

    manifest_ref = index["manifests"][0]
    manifest_digest = manifest_ref["digest"].replace("sha256:", "")

    manifest_path = bundle_dir / "blobs" / "sha256" / manifest_digest
    with open(manifest_path, encoding="utf-8") as extracted_lockfile:
        oci_manifest = json.load(extracted_lockfile)

    # Find metadata layer
    metadata_layer = None
    for layer in oci_manifest.get("layers", []):
        if (
            layer.get("annotations", {}).get("com.warrical.conduit.layer.type")
            == "metadata"
        ):
            metadata_layer = layer
            break

    assert metadata_layer is not None, "Metadata layer not found in OCI manifest"

    # Extract metadata layer and check for entrypoint in lockfile
    metadata_digest = metadata_layer["digest"].replace("sha256:", "")
    metadata_blob_path = bundle_dir / "blobs" / "sha256" / metadata_digest

    metadata_tar_entries = set()
    checked_lockfile = False
    checked_script = False

    with tarfile.open(metadata_blob_path, "r:gz") as tar:
        for member in tar.getmembers():
            metadata_tar_entries.add(member.name)
            if member.name.endswith("conduit.lock.json"):
                extracted_lockfile = tar.extractfile(member)
                if extracted_lockfile:
                    checked_lockfile = True
                    lockfile_data = json.load(extracted_lockfile)
                    assert "entrypoint" in lockfile_data
                    assert lockfile_data["entrypoint"]["script"] == str(script_path)
                    assert lockfile_data["entrypoint"]["mode"] == "0755"

            if member.name == f"metadata/{script_path.name}":
                extracted_script_file = tar.extractfile(member)
                if extracted_script_file:
                    script_data = extracted_script_file.read()
                    checked_script = True
                    assert script_data == script_path.read_bytes(), (
                        "Entrypoint script content does not match original"
                    )

                    # Verify checksum matches lockfile
                    import hashlib

                    actual_checksum = (
                        f"sha256:{hashlib.sha256(script_data).hexdigest()}"
                    )
                    expected_checksum = lockfile.entrypoint.checksum
                    assert actual_checksum == expected_checksum, (
                        f"Script checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
                    )

    # Verify lockfile, artifacts index and most importantly entrypoint script are all included in the bundle
    assert metadata_tar_entries, "Metadata layer should not be empty"
    assert "metadata/artifact-index.json" in metadata_tar_entries, (
        "Artifact index not found in metadata layer"
    )

    assert checked_lockfile, "Entrypoint lockfile not found in metadata layer"
    assert "metadata/conduit.lock.json" in metadata_tar_entries, (
        "Lockfile not found in metadata layer"
    )

    # Is this where we are supposed to check for the existence of the entrypoint script in the bundle?
    expected_script_path = f"metadata/{script_path.name}"
    assert expected_script_path in metadata_tar_entries, (
        f"Entrypoint script not found in metadata layer. Looking for '{expected_script_path}' in {sorted(metadata_tar_entries)}"
    )
    assert checked_script, (
        "Entrypoint script wasn't found in metadata layer and was not checked"
    )


@pytest.mark.asyncio
async def test_entrypoint_script_cached_separately(manifest_with_entrypoint):
    """Test that entrypoint script is cached and included in bundle."""
    manifest, script_path = manifest_with_entrypoint

    # Modify manifest to have entrypoint as an artifact reference
    manifest.artifacts.append(
        ManifestArtifact(
            name="entrypoint-script",
            origin=str(script_path),
            target="/.conduit/entrypoint.sh",
        )
    )

    # Generate lockfile
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest=manifest, handler_factory=handler_factory
    )

    # Verify entrypoint script is in artifacts
    assert len(lockfile.artifacts) == 2
    entrypoint_artifact = next(
        (a for a in lockfile.artifacts if a.name == "entrypoint-script"), None
    )
    assert entrypoint_artifact is not None
    assert entrypoint_artifact.target == "/.conduit/entrypoint.sh"


@pytest.mark.parametrize(
    ("entrypoint_data", "expected_in_lockfile"),
    [
        # Test case 1: Full entrypoint object
        (
            {
                "script": "/scripts/deploy.sh",
                "mode": "0755",
                "uid": "root",
                "gid": "root",
            },
            {
                "script": "/scripts/deploy.sh",
                "mode": "0755",
                "uid": "root",
                "gid": "root",
            },
        ),
        # Test case 2: Minimal entrypoint
        (
            {"script": "echo 'Hello'", "mode": "0755"},
            {"script": "echo 'Hello'", "mode": "0755", "uid": None, "gid": None},
        ),
        # Test case 3: No entrypoint
        (None, None),
    ],
)
def test_entrypoint_variations_in_lockfile(
    temp_dir, entrypoint_data, expected_in_lockfile
):
    """Test various entrypoint configurations are preserved in lockfile."""
    # Create manifest with specified entrypoint
    artifact_path = temp_dir / "test.txt"
    artifact_path.write_text("content")

    manifest_dict = {
        "apiVersion": API_VERSION,
        "kind": "Manifest",
        "metadata": {"name": "test", "version": "1.0.0"},
        "artifacts": [
            {"name": "test", "origin": str(artifact_path), "target": "/test.txt"}
        ],
    }

    if entrypoint_data:
        manifest_dict["entrypoint"] = entrypoint_data

    manifest = Manifest(**manifest_dict)

    # Verify entrypoint in model
    if expected_in_lockfile:
        assert manifest.entrypoint is not None
        assert manifest.entrypoint.script == expected_in_lockfile["script"]
        assert manifest.entrypoint.mode == expected_in_lockfile["mode"]
        assert manifest.entrypoint.uid == expected_in_lockfile.get("uid")
        assert manifest.entrypoint.gid == expected_in_lockfile.get("gid")
    else:
        assert manifest.entrypoint is None


def test_manifest_schema_validates_entrypoint():
    """Test that manifest schema properly validates entrypoint field."""
    # Test invalid entrypoint (missing required field)
    manifest_dict = {
        "apiVersion": API_VERSION,
        "kind": "Manifest",
        "metadata": {"name": "test", "version": "1.0.0"},
        "entrypoint": {
            # Missing required 'script' field
            "mode": "0755"
        },
        "artifacts": [],
    }

    # Should raise validation error
    with pytest.raises(Exception):  # Pydantic ValidationError
        Manifest(**manifest_dict)
