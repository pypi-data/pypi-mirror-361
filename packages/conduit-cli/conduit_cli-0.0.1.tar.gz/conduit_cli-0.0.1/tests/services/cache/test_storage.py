"""
RED TESTS for Content Addressable Store (Flyweight Pattern).

These tests MUST FAIL initially - no implementation exists yet.
Following TDD: RED -> GREEN -> REFACTOR
"""

import hashlib

import pytest

from conduit.services.cache.storage import ContentAddressableStore


def test_content_store_git_like_structure(tmp_path):
    """Test git-like blob storage structure."""
    store = ContentAddressableStore(tmp_path)
    content_hash = "sha256:abcd1234567890ef"

    # Should generate git-like path: blobs/sha256/ab/cd/abcd1234567890ef
    expected_path = tmp_path / "blobs" / "sha256" / "ab" / "cd" / "abcd1234567890ef"
    actual_path = store.get_content_path(content_hash)
    assert actual_path == expected_path


@pytest.mark.asyncio
async def test_content_store_deduplication(tmp_path):
    """Test Flyweight pattern prevents content duplication."""
    store = ContentAddressableStore(tmp_path)

    # Create identical content in different source files
    content = b"identical content for deduplication test"
    content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"

    file1 = tmp_path / "source1.txt"
    file2 = tmp_path / "source2.txt"
    file1.write_bytes(content)
    file2.write_bytes(content)

    # Store same content twice
    cached_path1 = await store.store_content(file1, content_hash)
    cached_path2 = await store.store_content(file2, content_hash)

    # Should return same cached path (deduplication)
    assert cached_path1 == cached_path2
    assert cached_path1.read_bytes() == content

    # Should only exist once in storage
    assert await store.content_exists(content_hash)


@pytest.mark.asyncio
async def test_content_store_copy_to_target(tmp_path):
    """Test copying cached content to target location."""
    store = ContentAddressableStore(tmp_path)

    # Store content
    content = b"content to copy"
    content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
    source_file = tmp_path / "source.bin"
    source_file.write_bytes(content)

    cached_path = await store.store_content(source_file, content_hash)
    assert cached_path.exists()

    # Copy to target
    target_file = tmp_path / "target.bin"
    success = await store.copy_to_target(content_hash, target_file)

    assert success is True
    assert target_file.exists()
    assert target_file.read_bytes() == content


@pytest.mark.asyncio
async def test_content_store_missing_content(tmp_path):
    """Test handling of missing content."""
    store = ContentAddressableStore(tmp_path)
    missing_hash = "sha256:doesnotexist"

    assert await store.content_exists(missing_hash) is False
    assert await store.get_content(missing_hash) is None

    target = tmp_path / "target.txt"
    success = await store.copy_to_target(missing_hash, target)
    assert success is False
    assert not target.exists()


@pytest.mark.asyncio
async def test_content_store_directory_creation(tmp_path):
    """Test automatic directory creation for nested structure."""
    store = ContentAddressableStore(tmp_path)

    content = b"test content for directory creation"
    content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
    source_file = tmp_path / "source.txt"
    source_file.write_bytes(content)

    # Cache directory shouldn't exist initially
    cache_path = store.get_content_path(content_hash)
    assert not cache_path.parent.exists()

    # Storing should create all necessary directories
    cached_path = await store.store_content(source_file, content_hash)
    assert cached_path.parent.exists()
    assert cached_path.exists()
    assert cached_path.read_bytes() == content


@pytest.mark.parametrize(
    ("hash_input", "expected_structure"),
    [
        ("sha256:abcdef1234567890", "blobs/sha256/ab/cd/abcdef1234567890"),
        ("sha256:123456789abcdef0", "blobs/sha256/12/34/123456789abcdef0"),
        ("sha256:fedcba0987654321", "blobs/sha256/fe/dc/fedcba0987654321"),
    ],
)
def test_content_store_path_structure(tmp_path, hash_input, expected_structure):
    """Test consistent path structure generation."""
    store = ContentAddressableStore(tmp_path)

    actual_path = store.get_content_path(hash_input)
    expected_path = tmp_path / expected_structure

    assert actual_path == expected_path


@pytest.mark.asyncio
async def test_content_store_large_file_handling(tmp_path):
    """Test handling of larger files (basic performance test)."""
    store = ContentAddressableStore(tmp_path)

    # Create a 1MB file
    large_content = b"X" * (1024 * 1024)
    content_hash = f"sha256:{hashlib.sha256(large_content).hexdigest()}"
    large_file = tmp_path / "large.bin"
    large_file.write_bytes(large_content)

    # Should handle large files efficiently
    cached_path = await store.store_content(large_file, content_hash)
    assert cached_path.exists()
    assert cached_path.stat().st_size == len(large_content)

    # Copy to target should work
    target = tmp_path / "large_copy.bin"
    success = await store.copy_to_target(content_hash, target)
    assert success is True
    assert target.stat().st_size == len(large_content)


@pytest.mark.asyncio
async def test_content_store_concurrent_storage(tmp_path):
    """Test concurrent storage of same content."""
    import asyncio

    store = ContentAddressableStore(tmp_path)
    content = b"concurrent test content"
    content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"

    # Create multiple source files
    files = []
    for i in range(3):
        file_path = tmp_path / f"source_{i}.txt"
        file_path.write_bytes(content)
        files.append(file_path)

    # Store concurrently
    tasks = [store.store_content(file_path, content_hash) for file_path in files]
    cached_paths = await asyncio.gather(*tasks)

    # All should return same cached path
    assert all(path == cached_paths[0] for path in cached_paths)
    assert cached_paths[0].read_bytes() == content
