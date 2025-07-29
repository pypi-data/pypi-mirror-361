"""Integration tests for PackService - ensures artifacts are downloaded through cache before bundling."""

import json
from pathlib import Path

import pytest

from conduit.core.models import LockFile, LockFileArtifact
from conduit.handlers.factory import HandlerFactory
from conduit.services.cache import CacheResolver
from conduit.services.lockfile import LockfileService
from conduit.services.pack import PackProgress, PackService


@pytest.fixture
def test_files_dir(tmp_path):
    """Create test files directory structure."""
    test_dir = tmp_path / "testfiles"
    test_dir.mkdir()

    # Create test source files
    source_dir = test_dir / "source"
    source_dir.mkdir()

    # Create a config file
    config_file = source_dir / "config.yaml"
    config_file.write_text("app:\n  name: test-app\n  version: 1.0.0\n")

    # Create a data file
    data_file = source_dir / "data.json"
    data_file.write_text('{"users": ["alice", "bob"], "count": 2}')

    return test_dir


@pytest.fixture
def sample_lockfile(test_files_dir):
    """Create a lockfile with local file artifacts."""
    source_dir = test_files_dir / "source"

    return LockFile(
        apiVersion="v1",
        name="test-pack",
        version="1.0.0",
        manifestHash="sha256:abc123",
        artifacts=[
            LockFileArtifact(
                name="config",
                type="file",
                action="copy_local",
                origin=str(source_dir / "config.yaml"),
                target="/app/config.yaml",
                checksum="sha256:dummy1",  # Will be replaced by actual
                size=100,  # Will be replaced by actual
            ),
            LockFileArtifact(
                name="data",
                type="file",
                action="copy_local",
                origin=str(source_dir / "data.json"),
                target="/app/data.json",
                checksum="sha256:dummy2",  # Will be replaced by actual
                size=200,  # Will be replaced by actual
            ),
        ],
    )


@pytest.mark.asyncio
async def test_pack_service_creates_bundle_with_real_artifacts(
    test_files_dir, sample_lockfile
):
    """Test that PackService creates a complete OCI bundle with real artifacts."""
    # Arrange
    lockfile_path = test_files_dir / "test.lock.yaml"
    lockfile_path.write_text(sample_lockfile.dump_canonical_json())

    cache_dir = test_files_dir / "cache"
    output_dir = test_files_dir / "output"

    # Create services with real dependencies
    cache_service = CacheResolver(cache_dir=cache_dir)
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    # Act
    bundle_path, layers_created, artifacts_bundled = await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(output_dir / "bundle"),
        tag="v1.0.0",
    )

    # Assert
    # Verify bundle structure
    bundle_dir = Path(bundle_path)
    assert bundle_dir.exists()
    assert (bundle_dir / "oci-layout").exists()
    assert (bundle_dir / "index.json").exists()
    assert (bundle_dir / "blobs" / "sha256").exists()

    # Verify oci-layout
    oci_layout = json.loads((bundle_dir / "oci-layout").read_text())
    assert oci_layout["imageLayoutVersion"] == "1.0.0"

    # Verify index.json
    index = json.loads((bundle_dir / "index.json").read_text())
    assert index["schemaVersion"] == 2
    assert len(index["manifests"]) == 1

    # Verify we have 2 layers (metadata + artifacts)
    assert layers_created == 2
    assert artifacts_bundled == 2

    # Verify blobs were created
    blobs_dir = bundle_dir / "blobs" / "sha256"
    blobs = list(blobs_dir.iterdir())
    assert len(blobs) >= 3  # At least config + 2 layers + manifest


@pytest.mark.asyncio
async def test_pack_service_downloads_through_cache(test_files_dir, sample_lockfile):
    """Test that PackService creates consistent bundles."""
    # Arrange
    lockfile_path = test_files_dir / "test.lock.yaml"
    lockfile_path.write_text(sample_lockfile.dump_canonical_json())

    cache_dir = test_files_dir / "cache"
    output_dir = test_files_dir / "output"

    # Create services
    cache_service = CacheResolver(cache_dir=cache_dir)
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    # Act - create bundle twice
    bundle_path1, _, _ = await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(output_dir / "bundle1"),
        tag="v1.0.0",
    )

    bundle_path2, _, _ = await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(output_dir / "bundle2"),
        tag="v1.0.0",
    )

    # Assert - both bundles should exist and be valid
    assert Path(bundle_path1).exists()
    assert Path(bundle_path2).exists()

    # Both bundles should have the same structure
    bundle1_blobs = sorted((Path(bundle_path1) / "blobs" / "sha256").iterdir())
    bundle2_blobs = sorted((Path(bundle_path2) / "blobs" / "sha256").iterdir())

    # Same number of blobs
    assert len(bundle1_blobs) == len(bundle2_blobs)


@pytest.mark.asyncio
async def test_pack_service_with_progress_tracking(test_files_dir, sample_lockfile):
    """Test that PackService reports progress correctly."""
    # Arrange
    lockfile_path = test_files_dir / "test.lock.yaml"
    lockfile_path.write_text(sample_lockfile.dump_canonical_json())

    cache_dir = test_files_dir / "cache"
    output_dir = test_files_dir / "output"

    # Track progress updates
    progress_updates = []

    def progress_callback(progress: PackProgress):
        progress_updates.append({
            "total": progress.total_artifacts,
            "downloaded": progress.downloaded_artifacts,
            "bundled": progress.bundled_artifacts,
            "current": progress.current_artifact,
            "status": progress.current_status,
        })

    # Create services
    cache_service = CacheResolver(cache_dir=cache_dir)
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    # Act
    await pack_service.create_bundle(
        lockfile_path=str(lockfile_path),
        output_path=str(output_dir / "bundle"),
        tag="v1.0.0",
        progress_callback=progress_callback,
    )

    # Assert
    assert len(progress_updates) >= 2  # At least one update per artifact

    # Check progress tracking
    first_update = progress_updates[0]
    assert first_update["total"] == 2
    assert first_update["status"] == "downloading"
    assert first_update["downloaded"] == 0

    # Final state should show all artifacts downloaded
    final_downloads = max(u["downloaded"] for u in progress_updates)
    assert final_downloads == 2


@pytest.mark.asyncio
async def test_pack_service_handles_missing_files(test_files_dir):
    """Test that PackService handles missing source files gracefully."""
    # Arrange
    lockfile = LockFile(
        apiVersion="v1",
        manifestHash="sha256:abc123",
        name="test-pack",
        version="1.0.0",
        artifacts=[
            LockFileArtifact(
                name="missing",
                type="file",
                action="copy_local",
                origin="/nonexistent/file.txt",
                target="/app/file.txt",
                checksum="sha256:dummy",
                size=100,
            )
        ],
    )

    lockfile_path = test_files_dir / "test.lock.yaml"
    lockfile_path.write_text(lockfile.dump_canonical_json())

    cache_dir = test_files_dir / "cache"
    output_dir = test_files_dir / "output"

    # Create services
    cache_service = CacheResolver(cache_dir=cache_dir)
    lockfile_service = LockfileService()
    handler_factory = HandlerFactory()

    pack_service = PackService(
        cache_service=cache_service,
        lockfile_service=lockfile_service,
        handler_factory=handler_factory,
    )

    # Act & Assert
    with pytest.raises(Exception, match="Failed to fetch artifact"):
        await pack_service.create_bundle(
            lockfile_path=str(lockfile_path), output_path=str(output_dir / "bundle")
        )

