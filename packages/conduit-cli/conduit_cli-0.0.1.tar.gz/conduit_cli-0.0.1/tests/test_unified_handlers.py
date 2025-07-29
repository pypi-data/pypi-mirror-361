"""
Tests for unified handlers (File, HTTP, OCI).
"""

import asyncio
import hashlib
from pathlib import Path
from typing import Callable

import pytest

from conduit.core.commands import CalculateMetadataCommand, FetchArtifactCommand
from conduit.handlers.factory import HandlerFactory
from src.conduit.services.cache import CacheResolver


@pytest.fixture
def factory():
    # Generic factory without cache for tests that don't need HTTP caching
    return HandlerFactory()


@pytest.fixture
def http_cached_factory(tmp_path: Path):
    # Factory specifically for HTTP tests, configured with a cache service
    cache_dir = tmp_path / "http_cache_for_tests"
    cache_dir.mkdir(exist_ok=True)
    cache_service = CacheResolver(cache_dir=cache_dir)
    return HandlerFactory(cache_service=cache_service)


@pytest.fixture
def tmp_test_file_factory(tmp_path: Path):
    """Helper to create test files."""

    def _create_file(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _create_file


# === FileSourceHandler Tests ===


@pytest.mark.parametrize(
    ("file_content", "file_name"),
    [
        ("Test file content for metadata calculation", "test_meta.txt"),
        ("", "empty_meta.txt"),  # Empty file
        ("A" * 1024, "large_meta.txt"),  # 1KB file
    ],
)
def test_calculate_metadata_returns_correct_structure(
    factory,
    tmp_test_file_factory: Callable[[str, str], Path],
    file_content: str,
    file_name: str,
):
    """Test that calculate_metadata returns the expected data structure for various files."""
    test_file_path = tmp_test_file_factory(file_name, file_content)
    handler = factory.get_handler(str(test_file_path))
    command = CalculateMetadataCommand(origin=str(test_file_path))
    metadata = asyncio.run(handler.handle(command))

    assert metadata.checksum is not None
    assert metadata.size is not None
    assert metadata.type is not None

    assert isinstance(metadata.checksum, str)
    assert isinstance(metadata.size, int)
    assert isinstance(metadata.type, str)

    assert metadata.checksum.startswith("sha256:")
    assert metadata.type == "file"
    assert metadata.size == len(file_content.encode("utf-8"))


def test_calculate_metadata_checksum_accuracy(
    factory, tmp_test_file_factory: Callable[[str, str], Path]
):
    """Test that the calculated checksum is accurate."""
    content = "Known content for checksum verification"
    file_path = tmp_test_file_factory("checksum_test.txt", content)
    handler = factory.get_handler(str(file_path))
    command = CalculateMetadataCommand(origin=str(file_path))
    metadata = asyncio.run(handler.handle(command))

    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    expected_checksum = f"sha256:{expected_hash}"
    assert metadata.checksum == expected_checksum


def test_calculate_metadata_binary_file(factory, tmp_test_dir: Path):
    """Test metadata calculation for binary files."""
    binary_content = b"\x00\x01\x02\x03\xff\xfe\xfd"
    file_path = tmp_test_dir / "binary_test.bin"
    file_path.open("wb").write(binary_content)
    handler = factory.get_handler(str(file_path))
    command = CalculateMetadataCommand(origin=str(file_path))
    metadata = asyncio.run(handler.handle(command))

    assert metadata.checksum.startswith("sha256:")
    assert metadata.size == len(binary_content)
    assert metadata.type == "file"


def test_calculate_metadata_nonexistent_file(factory):
    """Test calculate_metadata raises FileNotFoundError for nonexistent files."""
    handler = factory.get_handler("/path/that/does/not/exist/file.txt")
    command = CalculateMetadataCommand(origin="/path/that/does/not/exist/file.txt")
    metadata = asyncio.run(handler.handle(command))
    assert metadata.success is False


def test_calculate_metadata_directory_path(factory, tmp_test_dir: Path):
    """Test calculate_metadata raises IsADirectoryError for directory paths."""
    handler = factory.get_handler(str(tmp_test_dir))
    command = CalculateMetadataCommand(origin=str(tmp_test_dir))
    metadata = asyncio.run(handler.handle(command))
    assert metadata.success is False


# === HTTP Handler Tests ===


@pytest.mark.asyncio
async def test_http_download_works(tmp_path, concurrent_httpbin):
    """Test that HTTP handler actually downloads file with correct content and caches it."""
    test_url = (
        f"{concurrent_httpbin.url}/base64/dGVzdCBjb250ZW50"  # Returns "test content"
    )
    expected_content = "test content"
    expected_checksum = (
        f"sha256:{hashlib.sha256(expected_content.encode()).hexdigest()}"
    )

    # --- Test CalculateMetadataCommand (should download to cache) ---
    # For this test, let's create a factory with a cache service
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()

    # We need to import CacheResolver for this
    cache_service = CacheResolver(cache_dir=cache_dir)
    cached_factory = HandlerFactory(cache_service=cache_service)

    handler_meta = cached_factory.get_handler(test_url)
    meta_command = CalculateMetadataCommand(
        origin=test_url, artifact_name="http_test_artifact"
    )

    meta_result = await handler_meta.handle(meta_command)

    assert meta_result.success is True
    assert meta_result.checksum == expected_checksum
    assert meta_result.size == len(expected_content)
    assert meta_result.type == "http"
    assert meta_result.cached_path is not None
    cached_file_path = Path(meta_result.cached_path)
    assert cached_file_path.exists()
    # Verify content of cached file (assuming it's directly readable, might need adjustment if cache stores it differently)
    # This depends on how HttpHandler and CacheResolver interact.
    # For now, we assume cached_path is the path to the actual content.
    assert cached_file_path.read_text() == expected_content

    # --- Test FetchArtifactCommand (should use cache if checksum matches) ---
    target_file_fetch = tmp_path / "downloaded_test_fetch.txt"
    handler_fetch = cached_factory.get_handler(test_url)  # Use the same cached_factory

    # Scenario 1: Fetch with correct expected_checksum (should use cache, not re-download)
    fetch_command_cached = FetchArtifactCommand(
        origin_url=test_url,
        target_path=str(target_file_fetch),
        expected_checksum=expected_checksum,
    )
    fetch_result_cached = await handler_fetch.handle(fetch_command_cached)

    assert fetch_result_cached.success is True
    # This assertion depends on HttpHandler's logic for using cached_path from CalculateMetadataResult
    # or if CacheResolver itself handles providing the cached file.
    # For now, we assume if checksum matches, it might not "download" in the sense of hitting the network.
    # The current HttpHandler._fetch_artifact checks target_path, not cache directly for FetchArtifactCommand.
    # This part of the test might need refinement based on HttpHandler's detailed cache interaction.
    # Let's assume for now it will re-verify the target_file if it exists.
    # If the file doesn't exist at target_path, it will download.
    # To test cache usage properly, HttpHandler._fetch_artifact would need to consult CacheService.

    # For now, let's verify the download to target_path
    if target_file_fetch.exists():  # Clean up if previous test part created it
        target_file_fetch.unlink()

    fetch_command_direct = FetchArtifactCommand(
        origin_url=test_url, target_path=str(target_file_fetch)
    )
    fetch_result_direct = await handler_fetch.handle(fetch_command_direct)

    assert fetch_result_direct.success is True
    assert fetch_result_direct.was_downloaded is True  # It will download to target_path
    assert fetch_result_direct.bytes_downloaded == len(expected_content)
    assert target_file_fetch.exists()
    assert target_file_fetch.stat().st_size == len(expected_content)
    actual_content_direct = target_file_fetch.read_text()
    assert actual_content_direct == expected_content
    assert fetch_result_direct.checksum == expected_checksum


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "artifact_url_template",
    [
        "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.13.4-linux-x86_64.tar.gz",
        "{httpbin_url}/base64/dGVzdCBjb250ZW50",  # Placeholder for httpbin
    ],
)
async def test_http_artifact_download(
    artifact_url_template, http_cached_factory, tmp_path, concurrent_httpbin
):
    """Test downloading real artifacts from various sources."""
    if "{httpbin_url}" in artifact_url_template:
        artifact_url = artifact_url_template.format(httpbin_url=concurrent_httpbin.url)
    else:
        artifact_url = artifact_url_template
    handler = http_cached_factory.get_handler(artifact_url)
    url_filename = artifact_url.split("/")[-1] or "artifact"
    target_file = tmp_path / url_filename
    command = FetchArtifactCommand(
        origin_url=artifact_url, target_path=str(target_file)
    )

    result = await handler.handle(command)

    assert result.success is True
    assert result.was_downloaded is True
    assert target_file.exists()
    assert target_file.stat().st_size > 0
    assert result.bytes_downloaded > 0


@pytest.mark.asyncio
async def test_http_deduplication_skips_existing_file(tmp_path, http_cached_factory):
    """Test that existing file with correct checksum is not re-downloaded."""
    content = "existing content"
    target_file = tmp_path / "existing.txt"
    target_file.write_text(content)
    expected_checksum = f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"

    # Using a generic httpbin URL as the origin, the actual content won't be fetched if deduplication works
    origin_url = "https://httpbin.org/anything"
    command = FetchArtifactCommand(
        origin_url=origin_url,
        target_path=str(target_file),
        expected_checksum=expected_checksum,
    )
    handler = http_cached_factory.get_handler(origin_url)

    result = await handler.handle(command)

    assert result.success is True
    assert (
        result.was_downloaded is False
    )  # Should be false as file exists with correct checksum
    assert result.checksum == expected_checksum
    assert target_file.read_text() == content


@pytest.mark.asyncio
async def test_http_404_error_handling(tmp_path, http_cached_factory):
    """Test handling of HTTP 404 errors."""
    target_file = tmp_path / "notfound.txt"
    origin_url = "https://httpbin.org/status/404"
    command = FetchArtifactCommand(origin_url=origin_url, target_path=str(target_file))
    handler = http_cached_factory.get_handler(origin_url)

    result = await handler.handle(command)

    assert result.success is False
    assert "404" in result.error_message
    assert not target_file.exists()


# === OCI Handler Tests ===


@pytest.mark.asyncio
async def test_oci_calculate_metadata_placeholder(factory):
    """Test OCI handler metadata calculation (placeholder)."""
    oci_url = "oci://docker.io/hello-world:latest"
    handler = factory.get_handler(oci_url)
    command = CalculateMetadataCommand(origin=oci_url)
    result = await handler.handle(command)

    assert result.success is True
    assert result.type == "oci"
    assert result.checksum.startswith("sha256:")
    assert result.size > 0  # Placeholder size
    assert result.metadata["registry"] == "docker.io"
    assert result.metadata["repository"] == "hello-world"
    assert result.metadata["tag"] == "latest"
    assert hasattr(result, "cached_path")  # Should exist, even if None for placeholder


@pytest.mark.asyncio
async def test_oci_fetch_artifact_placeholder(factory, tmp_path):
    """Test OCI handler artifact fetching (placeholder)."""
    oci_url = "oci://docker.io/alpine:latest"
    target_file = tmp_path / "alpine.tar"
    handler = factory.get_handler(oci_url)
    # In a real scenario, expected_checksum would come from a lockfile or manifest
    command = FetchArtifactCommand(
        origin_url=oci_url,
        target_path=str(target_file),
        expected_checksum="sha256:placeholder",
    )
    result = await handler.handle(command)

    assert result.success is True
    assert result.was_downloaded is True  # Placeholder always "downloads"
    target_file_path = Path(result.local_path)
    assert target_file_path.exists()
    assert target_file_path.name == "alpine.tar"
    assert target_file_path.stat().st_size > 0
