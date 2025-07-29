"""
Integration tests for HTTP Cache Service (No Mocks).

These tests use real HTTP interactions with concurrent_httpbin.
Following the project's no-mocking principle.
"""

import pytest

from conduit.core.clients.http import AiohttpClient
from conduit.services.cache.http_cache import HttpCacheService
from conduit.services.cache.metadata import CacheMetadataRepository
from conduit.services.cache.storage import ContentAddressableStore


@pytest.mark.asyncio
async def test_http_cache_service_real_download(concurrent_httpbin, tmp_path):
    """Test cache service with real HTTP download."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = f"{concurrent_httpbin.url}/stream-bytes/1024"
        target_path = tmp_path / "downloaded.bin"

        result = await cache_service.get_or_fetch(url, target_path)

        assert result.success is True
        assert result.was_cached is False
        assert target_path.exists()
        assert target_path.stat().st_size == 1024


@pytest.mark.asyncio
async def test_http_cache_service_cache_hit(concurrent_httpbin, tmp_path):
    """Test cache hit scenario with real cached content."""
    metadata_repo = CacheMetadataRepository(tmp_path / "metadata")
    content_store = ContentAddressableStore(tmp_path / "content")

    async with AiohttpClient() as http_client:
        cache_service = HttpCacheService(metadata_repo, content_store, http_client)

        url = f"{concurrent_httpbin.url}/stream-bytes/2048"

        # First download - cache miss
        target_path1 = tmp_path / "first.bin"
        result1 = await cache_service.get_or_fetch(url, target_path1)
        assert result1.success is True
        assert result1.was_cached is False

        # Second download - cache hit
        target_path2 = tmp_path / "second.bin"
        result2 = await cache_service.get_or_fetch(url, target_path2)
        assert result2.success is True
        assert result2.was_cached is True

        assert target_path1.read_bytes() == target_path2.read_bytes()
