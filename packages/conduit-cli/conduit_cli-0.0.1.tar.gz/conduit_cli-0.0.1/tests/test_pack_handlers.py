"""
Tests for pack command handlers.

Tests the PackCommandHandler's ability to create valid OCI bundles from pack commands.
Additional test cases to implement:
- Large artifact sets (1000+ files)
- Binary files and various file types
- Nested directory structures in artifacts
- Invalid lockfile handling
- Missing artifact files
- Insufficient disk space scenarios
- Unicode filenames and paths
"""

import hashlib
import json
import repro_tarfile as tarfile
from pathlib import Path

import pytest

from src.conduit.handlers.pack import PackCommand, PackCommandHandler, PackResult


@pytest.mark.parametrize(
    ("manifest_name", "artifact_count", "expected_layers"),
    [
        # Basic case - single artifact
        ("simple-app", 1, 2),
        # Multiple artifacts - typical app
        ("web-app", 3, 2),
    ],
)
def test_pack_command_handler_creates_valid_bundle(
    pack_manifest_factory,
    pack_lockfile_factory,
    manifest_name,
    artifact_count,
    expected_layers,
    tmp_path,
):
    """Test that PackCommandHandler creates a complete, valid OCI bundle from pack commands."""

    # Setup: Create realistic manifest with actual source files
    manifest_path, _files_dir = pack_manifest_factory(manifest_name, artifact_count)

    # Generate lockfile from manifest (creates real checksums and metadata)
    lockfile, lockfile_path = pack_lockfile_factory(manifest_path)

    # Create pack command
    pack_command = PackCommand(
        lockfile_path=str(lockfile_path), output_path=str(tmp_path / "bundle")
    )

    # Action: Handle pack command (this models the interface we want)
    if PackCommandHandler is None:
        # PackCommandHandler doesn't exist yet - skip test gracefully
        pytest.skip("PackCommandHandler not implemented yet")

    # Command handler with dependency injection
    pack_handler = PackCommandHandler()

    # Handle the command
    result = pack_handler.handle(pack_command)

    # Verify: Command result and OCI structure compliance
    assert isinstance(result, PackResult)
    assert result.bundle_path == pack_command.output_path
    assert result.layers_created == expected_layers
    assert result.artifacts_bundled == len(lockfile.artifacts)

    # OCI compliance verification
    bundle_path = Path(result.bundle_path)

    # Check required OCI directory structure
    assert bundle_path.exists(), f"Bundle path does not exist: {bundle_path}"
    assert (bundle_path / "oci-layout").exists(), "Missing oci-layout file"
    assert (bundle_path / "index.json").exists(), "Missing index.json file"
    assert (bundle_path / "blobs" / "sha256").exists(), "Missing blobs/sha256 directory"

    # Verify oci-layout content
    oci_layout = json.loads((bundle_path / "oci-layout").read_text())
    assert oci_layout["imageLayoutVersion"] == "1.0.0", "Invalid OCI layout version"

    # Verify index.json structure
    index = json.loads((bundle_path / "index.json").read_text())
    assert index["schemaVersion"] == 2, "Invalid index schema version"
    assert index["mediaType"] == "application/vnd.oci.image.index.v1+json", (
        "Invalid index media type"
    )
    assert len(index["manifests"]) == 1, "Should have exactly one manifest"

    # Verify manifest exists and is valid
    manifest_digest = index["manifests"][0]["digest"].replace("sha256:", "")
    manifest_path = bundle_path / "blobs" / "sha256" / manifest_digest
    assert manifest_path.exists(), f"Manifest blob does not exist: {manifest_path}"

    manifest = json.loads(manifest_path.read_text())
    assert manifest["schemaVersion"] == 2, "Invalid manifest schema version"
    assert manifest["mediaType"] == "application/vnd.oci.image.manifest.v1+json", (
        "Invalid manifest media type"
    )
    assert len(manifest["layers"]) == expected_layers, (
        f"Expected {expected_layers} layers, got {len(manifest['layers'])}"
    )

    # Verify config blob exists
    config_digest = manifest["config"]["digest"].replace("sha256:", "")
    config_path = bundle_path / "blobs" / "sha256" / config_digest
    assert config_path.exists(), f"Config blob does not exist: {config_path}"

    # Verify tag annotations in manifest
    assert "com.warrical.conduit.bundle.version" in manifest["annotations"]
    assert manifest["annotations"]["com.warrical.conduit.bundle.version"] == "latest"
    assert (
        manifest["annotations"]["org.opencontainers.artifact.type"]
        == "application/vnd.conduit.bundle.v1+json"
    )

    config = json.loads(config_path.read_text())
    assert "rootfs" in config, "Config missing rootfs"
    assert "history" in config, "Config missing history"
    assert len(config["rootfs"]["diff_ids"]) == expected_layers, (
        "Config diff_ids count mismatch"
    )

    # Verify all layers exist and are valid tar.gz files
    for layer in manifest["layers"]:
        layer_digest = layer["digest"].replace("sha256:", "")
        layer_path = bundle_path / "blobs" / "sha256" / layer_digest
        assert layer_path.exists(), f"Layer blob does not exist: {layer_path}"
        assert layer["mediaType"] == "application/vnd.oci.image.layer.v1.tar+gzip", (
            "Invalid layer media type"
        )

        # Verify layer is valid tar.gz and not empty
        with tarfile.open(layer_path, "r:gz") as tar:
            members = tar.getnames()
            assert len(members) > 0, f"Layer {layer_digest} is empty"

    # Verify blob naming follows content-addressable format
    blobs_dir = bundle_path / "blobs" / "sha256"
    for blob_file in blobs_dir.iterdir():
        if blob_file.is_file():
            # Verify blob name matches its SHA256 content hash
            content = blob_file.read_bytes()
            expected_hash = hashlib.sha256(content).hexdigest()
            assert blob_file.name == expected_hash, (
                f"Blob {blob_file.name} does not match content hash {expected_hash}"
            )


@pytest.mark.parametrize(
    ("manifest_name", "artifact_count"),
    [
        # Test determinism with single artifact
        ("simple-app", 1),
        # Test determinism with multiple artifacts
        ("web-app", 3),
    ],
)
def test_identical_lockfiles_produce_identical_bundles(
    pack_manifest_factory,
    pack_lockfile_factory,
    manifest_name,
    artifact_count,
    tmp_path,
):
    """Test that identical lockfiles produce bit-for-bit identical bundles."""
    # Use existing factory to create manifest and lockfile
    manifest_path, _files_dir = pack_manifest_factory(manifest_name, artifact_count)
    _lockfile, lockfile_path = pack_lockfile_factory(manifest_path)

    # Create first bundle
    bundle1_path = tmp_path / "bundle1"
    command1 = PackCommand(
        lockfile_path=str(lockfile_path), output_path=str(bundle1_path)
    )

    handler = PackCommandHandler()
    result1 = handler.handle(command1)

    # Create second bundle from same lockfile
    bundle2_path = tmp_path / "bundle2"
    command2 = PackCommand(
        lockfile_path=str(lockfile_path), output_path=str(bundle2_path)
    )

    result2 = handler.handle(command2)

    # Verify both bundles were created successfully
    assert Path(result1.bundle_path).exists()
    assert Path(result2.bundle_path).exists()

    # Compare all blob files - they should be identical
    blobs1_dir = Path(bundle1_path) / "blobs" / "sha256"
    blobs2_dir = Path(bundle2_path) / "blobs" / "sha256"

    blobs1 = {f.name: f.read_bytes() for f in blobs1_dir.iterdir() if f.is_file()}
    blobs2 = {f.name: f.read_bytes() for f in blobs2_dir.iterdir() if f.is_file()}

    # Should have identical blob digests and content
    assert blobs1.keys() == blobs2.keys(), "Bundle blob digests should be identical"

    for digest in blobs1:
        assert blobs1[digest] == blobs2[digest], f"Blob content differs for {digest}"

    # Compare index.json files
    index1 = json.loads((Path(bundle1_path) / "index.json").read_text())
    index2 = json.loads((Path(bundle2_path) / "index.json").read_text())
    assert index1 == index2, "index.json files should be identical"

    # Compare oci-layout files
    layout1 = json.loads((Path(bundle1_path) / "oci-layout").read_text())
    layout2 = json.loads((Path(bundle2_path) / "oci-layout").read_text())
    assert layout1 == layout2, "oci-layout files should be identical"

