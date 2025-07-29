"""Test relative path handling in manifest generation.

This module tests that relative paths in manifests are correctly resolved
relative to the manifest file location, not the current working directory.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from conduit.services.lock import LockService

from .conftest import AppDefaults


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace with standard directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create standard directories
        (base / "config").mkdir()
        (base / "sources").mkdir()
        (base / "output").mkdir()
        (base / "config" / "nested" / "deep").mkdir(parents=True)

        # Create test source file
        source_file = base / "sources" / "test_source.txt"
        source_file.write_text("Test content for relative path testing")

        yield base


@pytest.fixture
def manifest_factory(temp_workspace):
    """Factory to create manifest files with given content."""

    def _create_manifest(subdir: str, artifacts: list, name: str = "test"):
        manifest_content = {
            "apiVersion": AppDefaults.API_VERSION,
            "kind": "Manifest",
            "metadata": {"name": name, "version": "1.0.0"},
            "artifacts": artifacts,
        }

        manifest_path = temp_workspace / subdir / f"{name}.conduit.yaml"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest_content, f)

        return str(manifest_path)

    return _create_manifest


@pytest.fixture
def generate_service():
    """Provide a GenerateService instance."""
    return LockService()


@pytest.mark.parametrize(
    ("manifest_subdir", "origin_path", "target_path", "working_dir"),
    [
        # Manifest in config/, files relative to it
        ("config", "../sources/test_source.txt", "../output/test_output.txt", ""),
        # Manifest in nested dir, files relative to it
        (
            "config/nested/deep",
            "../../../sources/test_source.txt",
            "../../../output/test_output.txt",
            "output",
        ),
        # Current directory references
        ("config", "./sibling.txt", "../output/out.txt", "sources"),
    ],
)
async def test_relative_paths_resolved_from_manifest_directory(  # Changed to async def
    temp_workspace,
    manifest_factory,
    generate_service,
    manifest_subdir,
    origin_path,
    target_path,
    working_dir,
):
    """Test that relative paths are resolved from manifest directory, not CWD."""
    # Create a sibling file if needed
    if "./sibling.txt" in origin_path:
        sibling = temp_workspace / manifest_subdir / "sibling.txt"
        sibling.write_text("Sibling content")

    # Create manifest
    artifacts = [
        {"name": "test-artifact", "origin": origin_path, "target": target_path}
    ]
    manifest_path = manifest_factory(manifest_subdir, artifacts)

    # Change working directory if specified
    original_cwd = Path.cwd()
    try:
        if working_dir:
            os.chdir(temp_workspace / working_dir)

        # Generate lockfile
        lockfile_path, lockfile = await generate_service.generate_lockfile_async(
            manifest_path
        )  # Changed to await async version

        # Verify success
        assert Path(lockfile_path).exists()
        assert len(lockfile.artifacts) == 1

        # Origin should be relative path from lockfile to source
        # Target path should be preserved as-is
        # Note: "./sibling.txt" becomes "sibling.txt" (normalized)
        expected_origin = (
            origin_path.lstrip("./") if origin_path.startswith("./") else origin_path
        )
        assert lockfile.artifacts[0].origin == expected_origin
        assert lockfile.artifacts[0].target == target_path

        # File was found and processed
        assert lockfile.artifacts[0].checksum.startswith("sha256:")
        assert lockfile.artifacts[0].size > 0

    finally:
        os.chdir(original_cwd)


async def test_absolute_paths_work_unchanged(  # Changed to async def
    temp_workspace, manifest_factory, generate_service
):
    """Test that absolute paths work as expected."""
    source_path = temp_workspace / "sources" / "test_source.txt"
    target_path = temp_workspace / "output" / "test_output.txt"

    artifacts = [
        {
            "name": "test-artifact",
            "origin": str(source_path),
            "target": str(target_path),
        }
    ]

    manifest_path = manifest_factory("config", artifacts, name="absolute")
    lockfile_path, lockfile = await generate_service.generate_lockfile_async(
        manifest_path
    )  # Changed to await async version

    # Verify success with absolute paths preserved
    assert Path(lockfile_path).exists()
    assert lockfile.artifacts[0].origin == str(source_path)
    assert lockfile.artifacts[0].target == str(target_path)
    assert lockfile.artifacts[0].checksum.startswith("sha256:")
