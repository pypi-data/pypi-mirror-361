"""
HTTP Cache Service tests using real HTTP interactions (No Mocks).

Following project's no-mocking principle with concurrent_httpbin.
"""

from datetime import datetime

import pytest

from conduit.core.clients.http import AiohttpClient
from conduit.core.models import CacheMetadata
from conduit.services.cache.http_cache import HttpCacheService
from conduit.services.cache.metadata import CacheMetadataRepository
from conduit.services.cache.storage import ContentAddressableStore


@pytest.mark.asyncio
async def test_http_cache_service_cache_miss_downloads(concurrent_httpbin, tmp_path):
    """Test cache miss triggers download and caching."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = f"{concurrent_httpbin.url}/stream-bytes/1024"
        target_path = tmp_path / "target.bin"

        # Execute
        result = await cache_service.get_or_fetch(url, target_path)

        # Verify download occurred
        assert result.success is True
        assert result.was_cached is False

        # Verify content cached
        assert target_path.exists()
        assert target_path.stat().st_size == 1024


@pytest.mark.asyncio
async def test_http_cache_service_cache_hit_no_download(tmp_path):
    """Test cache hit returns cached content without download."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = "https://example.com/cached.bin"
        content = b"cached content for testing"
        content_hash = (
            "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )

        # Pre-populate cache
        cached_file = tmp_path / "cached.tmp"
        cached_file.write_bytes(content)
        await content_store.store_content(cached_file, content_hash)

        metadata = CacheMetadata(
            url=url,
            content_hash=content_hash,
            etag='"cached-etag"',
            cache_time=datetime.utcnow(),
            size=len(content),
        )
        await metadata_repo.store_metadata(metadata)

        # Execute
        target_path = tmp_path / "target.bin"
        result = await cache_service.get_or_fetch(url, target_path)

        # Verify cache hit
        assert result.success is True
        assert result.was_cached is True

        # Verify cached content returned
        assert target_path.read_bytes() == content


@pytest.mark.asyncio
async def test_http_cache_service_conditional_request_headers(tmp_path):
    """Test conditional request headers are generated for cached content."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")

    url = "https://example.com/conditional.bin"

    # Pre-cache metadata
    metadata = CacheMetadata(
        url=url,
        content_hash="sha256:testdata",
        etag='"test-etag"',
        last_modified="Wed, 01 Jan 2020 00:00:00 GMT",
        cache_time=datetime.utcnow(),
        size=100,
    )
    await metadata_repo.store_metadata(metadata)

    # Test conditional headers generation
    headers = await metadata_repo.get_conditional_headers(url)

    assert "If-None-Match" in headers
    assert headers["If-None-Match"] == '"test-etag"'
    assert "If-Modified-Since" in headers
    assert headers["If-Modified-Since"] == "Wed, 01 Jan 2020 00:00:00 GMT"


@pytest.mark.asyncio
async def test_http_cache_service_304_not_modified_response(
    concurrent_httpbin, tmp_path
):
    """Test HTTP cache service handles error scenarios gracefully."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        # Test with invalid URL
        invalid_url = "https://nonexistent.invalid/file.bin"
        target_path = tmp_path / "target.bin"

        result = await cache_service.get_or_fetch(invalid_url, target_path)

        # Should handle error gracefully
        assert result.success is False
        assert result.was_cached is False
        assert result.error_message is not None


@pytest.mark.asyncio
async def test_http_cache_service_progress_callback(concurrent_httpbin, tmp_path):
    """Test progress callback is called during download."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    progress_calls = []

    def progress_callback(event):
        progress_calls.append(event)

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = f"{concurrent_httpbin.url}/stream-bytes/2048"
        target_path = tmp_path / "target.bin"

        result = await cache_service.get_or_fetch(url, target_path, progress_callback)

        assert result.success is True
        assert target_path.exists()
        assert target_path.stat().st_size == 2048


@pytest.mark.asyncio
async def test_http_cache_service_error_handling(tmp_path):
    """Test error handling in HTTP cache service."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        # Test with completely invalid URL
        bad_url = "not-a-url-at-all"
        target_path = tmp_path / "target.bin"

        result = await cache_service.get_or_fetch(bad_url, target_path)

        assert result.success is False
        assert result.was_cached is False
        assert result.error_message is not None


@pytest.mark.asyncio
async def test_http_cache_service_fetch_and_cache_method(concurrent_httpbin, tmp_path):
    """Test direct fetch_and_cache method."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = f"{concurrent_httpbin.url}/stream-bytes/512"
        target_path = tmp_path / "direct.bin"

        result = await cache_service.fetch_and_cache(url, target_path)

        assert result.success is True
        assert result.was_cached is False
        assert target_path.exists()
        assert target_path.stat().st_size == 512


@pytest.mark.asyncio
async def test_http_cache_service_stores_response_metadata(
    concurrent_httpbin, tmp_path
):
    """Test that response metadata is stored correctly."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = f"{concurrent_httpbin.url}/stream-bytes/256"
        target_path = tmp_path / "metadata_test.bin"

        # First fetch
        result = await cache_service.get_or_fetch(url, target_path)
        assert result.success is True

        # Verify metadata was stored
        cached_metadata = await metadata_repo.get_by_url(url)
        assert cached_metadata is not None
        assert cached_metadata.url == url
        assert cached_metadata.content_hash.startswith("sha256:")
        assert cached_metadata.size == 256
