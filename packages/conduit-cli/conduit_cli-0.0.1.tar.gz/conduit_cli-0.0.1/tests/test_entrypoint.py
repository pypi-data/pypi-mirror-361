"""Consolidated tests for entrypoint functionality in manifest and lockfile generation."""

import hashlib
from pathlib import Path

import pytest
import yaml

from conduit.core.models import LockFileEntrypoint, Manifest, ManifestEntrypoint
from conduit.handlers.factory import HandlerFactory
from conduit.services.lockfile import LockfileService


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test artifact
    artifact = tmp_path / "app.tar.gz"
    artifact.write_text("test app content")

    # Create test scripts
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()

    script1 = scripts_dir / "deploy.sh"
    script1.write_text("#!/bin/bash\necho 'Deploying...'\n")
    script1.chmod(0o755)

    script2 = scripts_dir / "setup.sh"
    script2.write_text("#!/bin/bash\necho 'Setting up...'\nexit 0\n")
    script2.chmod(0o644)

    return tmp_path


@pytest.fixture
def manifest_dict(temp_dir):
    """Base manifest dictionary."""
    return {
        "apiVersion": "conduit.warrical.com/next",
        "kind": "Manifest",
        "metadata": {"name": "test-app", "version": "1.0.0"},
        "artifacts": [
            {
                "name": "app",
                "origin": str(temp_dir / "app.tar.gz"),
                "target": "/app/app.tar.gz",
            }
        ],
    }


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    content = file_path.read_bytes()
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


@pytest.mark.parametrize(
    ("entrypoint_value", "expected_mode", "expected_uid", "expected_gid"),
    [
        # String format uses defaults
        ("scripts/deploy.sh", "0755", None, None),
        # Object format with all fields
        (
            {
                "script": "scripts/setup.sh",
                "mode": "0644",
                "uid": "1000",
                "gid": "1000",
            },
            "0644",
            "1000",
            "1000",
        ),
        # Object format with minimal fields
        ({"script": "scripts/deploy.sh", "mode": "0755"}, "0755", None, None),
        # Absolute path
        ("/usr/local/bin/init.sh", "0755", None, None),
    ],
)
def test_manifest_entrypoint_formats(
    manifest_dict, entrypoint_value, expected_mode, expected_uid, expected_gid
):
    """Test that manifest accepts both string and object entrypoint formats."""
    manifest_dict["entrypoint"] = entrypoint_value
    manifest = Manifest(**manifest_dict)

    # Check manifest parsed correctly
    if isinstance(entrypoint_value, str):
        assert isinstance(manifest.entrypoint, str)
        assert manifest.entrypoint == entrypoint_value
    else:
        assert isinstance(manifest.entrypoint, ManifestEntrypoint)
        assert manifest.entrypoint.script == entrypoint_value["script"]
        assert manifest.entrypoint.mode == expected_mode
        assert manifest.entrypoint.uid == expected_uid
        assert manifest.entrypoint.gid == expected_gid


@pytest.mark.asyncio
async def test_lockfile_generates_entrypoint_metadata(temp_dir, manifest_dict):
    """Test that lockfile generation calculates checksum and size for entrypoint scripts."""
    script_path = temp_dir / "scripts" / "deploy.sh"
    manifest_dict["entrypoint"] = str(script_path)

    manifest = Manifest(**manifest_dict)
    manifest_path = temp_dir / "manifest.yaml"
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest_dict, f)

    # Generate lockfile
    service = LockfileService()
    factory = HandlerFactory()
    lockfile = await service.generate_lockfile_from_manifest_async(
        manifest=manifest, handler_factory=factory, manifest_path=str(manifest_path)
    )

    # Verify entrypoint in lockfile
    assert lockfile.entrypoint is not None
    assert isinstance(lockfile.entrypoint, LockFileEntrypoint)
    assert lockfile.entrypoint.script == str(script_path)
    assert lockfile.entrypoint.mode == "0755"
    assert lockfile.entrypoint.checksum == calculate_checksum(script_path)
    assert lockfile.entrypoint.size == script_path.stat().st_size
    assert lockfile.entrypoint.uid is ""
    assert lockfile.entrypoint.gid is ""


@pytest.mark.asyncio
async def test_lockfile_entrypoint_relative_path_resolution(temp_dir, manifest_dict):
    """Test that relative entrypoint paths are resolved correctly."""
    manifest_dict["entrypoint"] = "scripts/setup.sh"
    manifest = Manifest(**manifest_dict)

    manifest_path = temp_dir / "manifest.yaml"
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest_dict, f)

    service = LockfileService()
    factory = HandlerFactory()
    lockfile = await service.generate_lockfile_from_manifest_async(
        manifest=manifest, handler_factory=factory, manifest_path=str(manifest_path)
    )

    expected_path = temp_dir / "scripts" / "setup.sh"
    assert lockfile.entrypoint is not None
    assert lockfile.entrypoint.script == str(expected_path)
    assert lockfile.entrypoint.checksum == calculate_checksum(expected_path)


@pytest.mark.asyncio
async def test_lockfile_no_entrypoint(temp_dir, manifest_dict):
    """Test lockfile generation without entrypoint."""
    manifest = Manifest(**manifest_dict)

    service = LockfileService()
    factory = HandlerFactory()
    lockfile = await service.generate_lockfile_from_manifest_async(
        manifest=manifest, handler_factory=factory
    )

    assert lockfile.entrypoint is None


@pytest.mark.asyncio
async def test_lockfile_yaml_serialization_with_entrypoint(temp_dir, manifest_dict):
    """Test that lockfile with entrypoint serializes to valid YAML."""
    manifest_dict["entrypoint"] = {
        "script": str(temp_dir / "scripts" / "deploy.sh"),
        "mode": "0700",
        "uid": "root",
        "gid": "root",
    }
    manifest = Manifest(**manifest_dict)
    print(f"\n\nManifest:\n {manifest}")
    print(f"\n\nManifest dict:\n {manifest_dict}")

    service = LockfileService()
    factory = HandlerFactory()
    lockfile = await service.generate_lockfile_from_manifest_async(
        manifest=manifest, handler_factory=factory
    )

    print(f"\n\nLockfile:\n {lockfile}")

    # Serialize to YAML
    yaml_content = service.generate_lockfile_yaml(lockfile)

    # Parse back and verify
    parsed = yaml.safe_load(yaml_content)
    assert "entrypoint" in parsed
    assert parsed["entrypoint"]["script"] == manifest_dict["entrypoint"]["script"]
    assert parsed["entrypoint"]["mode"] == "0700"
    assert parsed["entrypoint"]["uid"] == "root"
    assert parsed["entrypoint"]["gid"] == "root"
    assert "checksum" in parsed["entrypoint"]
    assert "size" in parsed["entrypoint"]
