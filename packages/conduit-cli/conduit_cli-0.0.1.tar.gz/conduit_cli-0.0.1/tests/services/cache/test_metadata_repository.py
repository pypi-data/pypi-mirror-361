"""
RED TESTS for Cache Metadata Repository.

These tests MUST FAIL initially - no implementation exists yet.
Following TDD: RED -> GREEN -> REFACTOR
"""

from datetime import datetime

import pytest

from conduit.services.cache.metadata import CacheMetadata, CacheMetadataRepository


@pytest.mark.parametrize(
    ("url", "content_hash", "etag"),
    [
        ("https://example.com/file.tar.gz", "sha256:abc123", '"etag-abc"'),
        ("https://test.org/artifact.zip", "sha256:def456", '"etag-def"'),
    ],
)
@pytest.mark.asyncio
async def test_metadata_repository_store_and_get_by_url(
    tmp_path, url, content_hash, etag
):
    """Test storing metadata and retrieving by URL (primary use case)."""
    repo = CacheMetadataRepository(tmp_path)

    metadata = CacheMetadata(
        url=url,
        content_hash=content_hash,
        etag=etag,
        last_modified="Wed, 21 Oct 2015 07:28:00 GMT",
        cache_time=datetime.utcnow(),
        size=1024,
    )

    # Store metadata
    await repo.store_metadata(metadata)

    # Should be able to retrieve by URL
    retrieved = await repo.get_by_url(url)
    assert retrieved is not None
    assert retrieved.url == url
    assert retrieved.content_hash == content_hash
    assert retrieved.etag == etag


@pytest.mark.asyncio
async def test_metadata_repository_url_only_lookup_before_checksum(tmp_path):
    """Test URL-only lookup before checksum is known (core requirement)."""
    repo = CacheMetadataRepository(tmp_path)
    url = "https://example.com/unknown-checksum.tar.gz"

    # Initially no metadata
    assert await repo.get_by_url(url) is None

    # Store with known checksum
    metadata = CacheMetadata(
        url=url,
        content_hash="sha256:computed-later",
        cache_time=datetime.utcnow(),
        size=2048,
    )
    await repo.store_metadata(metadata)

    # Should find by URL even without knowing checksum
    cached = await repo.get_by_url(url)
    assert cached is not None
    assert cached.content_hash == "sha256:computed-later"


@pytest.mark.asyncio
async def test_metadata_repository_conditional_headers(tmp_path):
    """Test generation of conditional request headers."""
    repo = CacheMetadataRepository(tmp_path)
    url = "https://example.com/conditional.tar.gz"

    # No headers for uncached URL
    headers = await repo.get_conditional_headers(url)
    assert headers == {}

    # Store metadata with ETag and Last-Modified
    metadata = CacheMetadata(
        url=url,
        content_hash="sha256:cached",
        etag='"strong-etag"',
        last_modified="Thu, 22 Oct 2015 08:30:00 GMT",
        cache_time=datetime.utcnow(),
    )
    await repo.store_metadata(metadata)

    # Should generate conditional headers
    headers = await repo.get_conditional_headers(url)
    assert headers["If-None-Match"] == '"strong-etag"'
    assert headers["If-Modified-Since"] == "Thu, 22 Oct 2015 08:30:00 GMT"


@pytest.mark.asyncio
async def test_metadata_repository_persistence(tmp_path):
    """Test metadata persists across repository instances."""
    url = "https://example.com/persistent.tar.gz"
    metadata = CacheMetadata(
        url=url,
        content_hash="sha256:persistent",
        etag='"persist-etag"',
        cache_time=datetime.utcnow(),
        size=512,
    )

    # Store in first instance
    repo1 = CacheMetadataRepository(tmp_path)
    await repo1.store_metadata(metadata)

    # Retrieve from new instance
    repo2 = CacheMetadataRepository(tmp_path)
    retrieved = await repo2.get_by_url(url)
    assert retrieved is not None
    assert retrieved.content_hash == "sha256:persistent"
    assert retrieved.etag == '"persist-etag"'


@pytest.mark.asyncio
async def test_metadata_repository_get_by_hash(tmp_path):
    """Test retrieving metadata by content hash."""
    repo = CacheMetadataRepository(tmp_path)
    url = "https://example.com/test.tar.gz"
    content_hash = "sha256:test123"

    metadata = CacheMetadata(
        url=url,
        content_hash=content_hash,
        etag='"hash-etag"',
        cache_time=datetime.utcnow(),
        size=256,
    )

    await repo.store_metadata(metadata)

    # Should be able to retrieve by hash
    retrieved = await repo.get_by_hash(content_hash)
    assert retrieved is not None
    assert retrieved.url == url
    assert retrieved.content_hash == content_hash


@pytest.mark.asyncio
async def test_metadata_repository_dual_indexing(tmp_path):
    """Test that both URL and hash indexing work simultaneously."""
    repo = CacheMetadataRepository(tmp_path)

    url1 = "https://example.com/file1.tar.gz"
    url2 = "https://example.com/file2.tar.gz"
    same_hash = "sha256:identical-content"

    # Store two URLs with same content hash (deduplication scenario)
    metadata1 = CacheMetadata(
        url=url1,
        content_hash=same_hash,
        etag='"etag1"',
        cache_time=datetime.utcnow(),
        size=100,
    )
    metadata2 = CacheMetadata(
        url=url2,
        content_hash=same_hash,
        etag='"etag2"',
        cache_time=datetime.utcnow(),
        size=100,
    )

    await repo.store_metadata(metadata1)
    await repo.store_metadata(metadata2)

    # Should be able to find both by URL
    found1 = await repo.get_by_url(url1)
    found2 = await repo.get_by_url(url2)
    assert found1.etag == '"etag1"' if found1 else False
    assert found2.etag == '"etag2"' if found2 else False

    # Finding by hash should return one of them (implementation detail)
    found_by_hash = await repo.get_by_hash(same_hash)
    assert found_by_hash is not None
    assert found_by_hash.content_hash == same_hash
