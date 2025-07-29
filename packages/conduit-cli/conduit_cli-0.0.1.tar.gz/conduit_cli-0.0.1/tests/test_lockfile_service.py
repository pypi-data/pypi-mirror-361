"""
Tests for lockfile service.

This module tests the LockfileService that handles lockfile generation,
serialization, and metadata calculation for Conduit manifests.
"""

from pathlib import Path

import pytest
import yaml

from conduit.handlers.factory import HandlerFactory
from src.conduit.core.models import LockFile, LockFileArtifact, Manifest
from src.conduit.services.cache import CacheResolver
from src.conduit.services.lockfile import LockfileError, LockfileService

from .conftest import API_VERSION


@pytest.fixture
def lockfile_service() -> LockfileService:
    """Provides a LockfileService instance."""
    return LockfileService()


@pytest.fixture
def handler_factory_with_cache(tmp_path: Path) -> HandlerFactory:
    """Provides a HandlerFactory with a CacheResolver."""
    cache_dir = tmp_path / "lockfile_service_test_cache"
    cache_dir.mkdir(exist_ok=True, parents=True)
    cache_service = CacheResolver(cache_dir=cache_dir)
    return HandlerFactory(cache_service=cache_service)


def create_test_file_at(tmp_path: Path, content: str, filename: str) -> str:
    """
    Helper to create a test file with the given content in a specific tmp_path.
    """
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_calculate_manifest_hash_consistency(lockfile_service: LockfileService):
    """Test that manifest hash calculation is consistent."""
    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "test"},
        "artifacts": [
            {"name": "test-file", "origin": "test.txt", "target": "output.txt"}
        ],
    }
    manifest = Manifest(**manifest_data)

    hash1 = lockfile_service.calculate_manifest_hash(manifest)
    hash2 = lockfile_service.calculate_manifest_hash(manifest)

    assert hash1 == hash2
    assert hash1.startswith("sha256:")


def test_calculate_manifest_hash_different_manifests(lockfile_service: LockfileService):
    """Test that different manifests produce different hashes."""
    manifest1_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "test1"},
        "artifacts": [
            {"name": "test-file", "origin": "test.txt", "target": "output.txt"}
        ],
    }
    manifest2_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "test2"},
        "artifacts": [
            {"name": "test-file", "origin": "test.txt", "target": "output.txt"}
        ],
    }

    manifest1 = Manifest(**manifest1_data)
    manifest2 = Manifest(**manifest2_data)

    hash1 = lockfile_service.calculate_manifest_hash(manifest1)
    hash2 = lockfile_service.calculate_manifest_hash(manifest2)

    assert hash1 != hash2


def test_determine_lockfile_name_with_metadata(lockfile_service: LockfileService):
    """Test lockfile name determination when manifest has metadata name."""
    manifest_data = {
        "apiVersion": API_VERSION,
        "kind": "Manifest",
        "metadata": {"name": "my-app", "version": "1.0.0"},
        "artifacts": [],
    }
    manifest = Manifest(**manifest_data)
    result = lockfile_service.determine_lockfile_filename(manifest)
    assert result == "my-app-1.0.0.conduit.lock.yaml"


def test_determine_lockfile_name_invalid_metadata_name(
    lockfile_service: LockfileService,
):
    """Test lockfile name determination with invalid metadata name."""
    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "", "version": "1.0.0"},  # Empty name
        "artifacts": [],
    }
    manifest = Manifest(**manifest_data)
    result = lockfile_service.determine_lockfile_filename(manifest)
    assert result == "conduit.lock.yaml"


@pytest.mark.asyncio
async def test_generate_lockfile_from_manifest_single_artifact(
    lockfile_service: LockfileService,
    handler_factory_with_cache: HandlerFactory,
    tmp_path: Path,
):
    """Test lockfile generation from manifest with single artifact."""
    content = "Test file content"
    source_file = create_test_file_at(tmp_path, content, "source.txt")

    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "test-manifest", "version": "1.0.0"},
        "artifacts": [
            {"name": "test-file", "origin": source_file, "target": "output.txt"}
        ],
    }
    manifest = Manifest(**manifest_data)

    # Set the base_path on the handler factory for resolving relative paths
    manifest_path = str(tmp_path / "manifest.yaml")
    manifest_dir = Path(manifest_path).parent
    handler_factory_with_cache.base_path = str(manifest_dir)

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest,
        handler_factory_with_cache,
        manifest_path=manifest_path,
    )

    assert isinstance(lockfile, LockFile)
    assert lockfile.manifestHash.startswith("sha256:")
    assert len(lockfile.artifacts) == 1
    artifact = lockfile.artifacts[0]
    assert artifact.name == "test-file"
    assert artifact.type == "file"
    # action is a required field in LockfileArtifact, so it will be present.
    # No need for `assert "action" in artifact` for a Pydantic model.
    # We can assert its value if needed, e.g., assert artifact.action == "copy_local"
    # For now, just ensuring it's processed is enough.
    assert artifact.origin == source_file
    assert artifact.target == "output.txt"
    assert artifact.checksum.startswith("sha256:")
    assert artifact.size == len(content.encode("utf-8"))


@pytest.mark.asyncio
async def test_generate_lockfile_from_manifest_multiple_artifacts(
    lockfile_service: LockfileService,
    handler_factory_with_cache: HandlerFactory,
    tmp_path: Path,
):
    """Test lockfile generation from manifest with multiple artifacts."""
    file1_content = "File 1 content"
    file2_content = "File 2 content with different length"
    source_file1 = create_test_file_at(tmp_path, file1_content, "source1.txt")
    source_file2 = create_test_file_at(tmp_path, file2_content, "source2.txt")

    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "multi-artifact", "version": "1.0.0"},
        "artifacts": [
            {"name": "file1", "origin": source_file1, "target": "output1.txt"},
            {"name": "file2", "origin": source_file2, "target": "output2.txt"},
        ],
    }
    manifest = Manifest(**manifest_data)

    # Set the base_path on the handler factory for resolving relative paths
    manifest_path = str(tmp_path / "manifest.yaml")
    manifest_dir = Path(manifest_path).parent
    handler_factory_with_cache.base_path = str(manifest_dir)

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest,
        handler_factory_with_cache,
        manifest_path=manifest_path,
    )

    assert len(lockfile.artifacts) == 2
    artifacts_by_name = {a.name: a for a in lockfile.artifacts}
    file1_artifact = artifacts_by_name["file1"]
    assert file1_artifact.origin == source_file1
    assert file1_artifact.size == len(file1_content.encode("utf-8"))
    file2_artifact = artifacts_by_name["file2"]
    assert file2_artifact.origin == source_file2
    assert file2_artifact.size == len(file2_content.encode("utf-8"))


@pytest.mark.asyncio
async def test_generate_lockfile_from_manifest_nonexistent_file(
    lockfile_service: LockfileService, handler_factory_with_cache: HandlerFactory
):
    """Test error handling when source file doesn't exist."""
    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "test", "version": "1.0.0"},
        "artifacts": [
            {
                "name": "missing",
                "origin": "/nonexistent/file.txt",
                "target": "output.txt",
            }
        ],
    }
    manifest = Manifest(**manifest_data)

    with pytest.raises(LockfileError):
        await lockfile_service.generate_lockfile_from_manifest_async(
            manifest, handler_factory_with_cache
        )


def test_generate_lockfile_yaml_serialization(lockfile_service: LockfileService):
    """Test YAML serialization of lockfile."""
    lockfile_artifact = LockFileArtifact(
        name="test-file",
        type="file",
        action="copy_local",
        origin="source.txt",
        target="target.txt",
        checksum="sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        size=100,
    )
    lockfile_model = LockFile(
        apiVersion=f"{API_VERSION}",
        name="test-lockfile.yaml",
        version="1.0.0",
        manifestHash="sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        artifacts=[lockfile_artifact],
    )
    yaml_content = lockfile_service.generate_lockfile_yaml(lockfile_model)
    assert (
        "manifestHash: sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        in yaml_content
    )
    assert "artifacts:" in yaml_content
    assert "name: test-file" in yaml_content
    assert (
        "checksum: sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        in yaml_content
    )
    assert "size: 100" in yaml_content


@pytest.mark.asyncio
async def test_service_integration_with_handlers(
    lockfile_service: LockfileService,
    handler_factory_with_cache: HandlerFactory,
    tmp_path: Path,
):
    """Test that lockfile service properly integrates with handler factory."""
    content = "Integration test of content and two artifacts files with and without file:// URI."
    source_file_uri = create_test_file_at(tmp_path, content, "integration_uri.txt")
    source_file_plain = create_test_file_at(tmp_path, content, "integration_plain.txt")

    artifact_source_one = {
        "name": "integration-file-1",
        "origin": f"file://{source_file_uri}",
        "target": "output_uri.txt",
    }
    artifact_source_two = {
        "name": "integration-file-2",
        "origin": source_file_plain,
        "target": "output_plain.txt",
    }
    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "integration-test", "version": "1.0.0"},
        "artifacts": [artifact_source_one, artifact_source_two],
    }
    manifest = Manifest(**manifest_data)
    manifest_file_path = str(tmp_path / "integration_manifest.yaml")
    with open(manifest_file_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest_data, f)

    # Set the base_path on the handler factory for resolving relative paths
    manifest_dir = Path(manifest_file_path).parent
    handler_factory_with_cache.base_path = str(manifest_dir)

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest, handler_factory_with_cache, manifest_path=manifest_file_path
    )

    assert len(lockfile.artifacts) == 2
    for artifact in lockfile.artifacts:
        assert artifact.type == "file"
        assert artifact.checksum.startswith("sha256:")
        assert artifact.size == len(content.encode("utf-8"))
        if artifact.name == "integration-file-1":
            assert (
                Path(artifact.origin).name == Path(source_file_uri).name
                or artifact.origin == source_file_uri
            )
        elif artifact.name == "integration-file-2":
            assert (
                Path(artifact.origin).name == Path(source_file_plain).name
                or artifact.origin == source_file_plain
            )


def test_lockfile_service_consistency(lockfile_service: LockfileService):
    """Test that lockfile service methods are returning consistent results."""
    manifest_data = {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "metadata": {"name": "consistency-test", "version": "1.0.0"},
        "artifacts": [],
    }
    manifest = Manifest(**manifest_data)
    hash1 = lockfile_service.calculate_manifest_hash(manifest)
    hash2 = lockfile_service.calculate_manifest_hash(manifest)
    assert hash1 == hash2
    name1 = lockfile_service.determine_lockfile_filename(manifest)
    name2 = lockfile_service.determine_lockfile_filename(manifest)
    assert name1 == name2
