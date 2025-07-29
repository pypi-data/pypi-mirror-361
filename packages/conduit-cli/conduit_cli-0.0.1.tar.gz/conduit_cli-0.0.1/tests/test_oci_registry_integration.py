"""Tests for OCI registry integration - fetch and push functionality."""

from pathlib import Path

import pytest

from conduit.core.commands import CalculateMetadataCommand, CalculateMetadataResult
from conduit.core.models import (
    Manifest,
    ManifestArtifact,
    ManifestMetadata,
)  # Added ManifestMetadata
from conduit.handlers.factory import HandlerFactory  # Changed import
from conduit.handlers.oci import OciHandler  # Changed import
from conduit.handlers.pack import PackCommandHandler

from .conftest import API_VERSION  # Import API_VERSION from conftest


@pytest.fixture
def oci_handler():  # Renamed fixture
    """Fixture providing OCI handler."""
    return OciHandler()


@pytest.fixture
def pack_handler():
    """Fixture providing pack command handler."""
    return PackCommandHandler()


@pytest.fixture
def sample_manifest_with_oci():
    """Sample manifest with OCI image references."""
    return Manifest(
        apiVersion=f"{API_VERSION}",
        kind="Manifest",
        metadata=ManifestMetadata(name="sample-oci-manifest"),  # Added ManifestMetadata
        artifacts=[
            ManifestArtifact(
                name="nginx-image",
                origin="oci://docker.io/nginx:1.25",
                target="./images/nginx.tar",
            ),
            ManifestArtifact(
                name="alpine-image",
                origin="oci://ghcr.io/alpine/alpine:latest",
                target="./images/alpine.tar",
            ),
            ManifestArtifact(
                name="local-config",
                origin="./config/nginx.conf",
                target="./config/nginx.conf",
            ),
        ],
    )


@pytest.mark.asyncio
async def test_oci_handler_pulls_docker_image(
    oci_handler: OciHandler, tmp_path: Path
):  # Renamed, use unified handler
    """Test OCI handler can process OCI images (placeholder logic)."""
    origin = "oci://docker.io/library/nginx:1.25"
    command = CalculateMetadataCommand(origin=origin)

    # Current OciHandler._calculate_metadata uses placeholder logic and does not call _pull_to_cache
    # So, no need to mock OrasClient for this test of placeholder behavior.
    metadata_result = await oci_handler.handle(command)

    assert isinstance(metadata_result, CalculateMetadataResult)
    assert metadata_result.success is True
    assert metadata_result.type == "oci"  # Standardized to "oci"
    assert metadata_result.checksum is not None
    assert metadata_result.checksum.startswith("sha256:")
    assert metadata_result.size is not None
    assert metadata_result.metadata is not None
    # Ensure metadata is not None for type checker before using .get()
    oci_meta = metadata_result.metadata
    assert oci_meta.get("repository") == "library/nginx"


@pytest.mark.parametrize(
    ("registry_url", "expected_host"),
    [
        ("oci://docker.io/library/nginx:1.25", "docker.io"),
        ("oci://ghcr.io/owner/repo:latest", "ghcr.io"),
        ("oci://registry.example.com:5000/app:v1", "registry.example.com:5000"),
    ],
)
def test_oci_handler_parses_registry_urls(
    oci_handler: OciHandler, registry_url: str, expected_host: str
):  # Renamed
    """Test OCI handler correctly parses registry URLs."""
    parsed = oci_handler._parse_oci_reference(
        registry_url
    )  # _parse_oci_reference is on OciHandler

    assert parsed["registry"] == expected_host
    assert "repository" in parsed
    assert "tag" in parsed


def test_handler_factory_supports_oci_scheme():  # Renamed test
    """Test unified handler factory includes OCI scheme in supported schemes."""
    factory = HandlerFactory()
    supported_schemes = factory.supported_schemes  # Use property
    assert "oci" in supported_schemes

    oci_handler_instance = factory.get_handler(
        "oci://docker.io/nginx:latest"
    )  # Use get_handler
    assert isinstance(oci_handler_instance, OciHandler)  # Check type
    assert hasattr(oci_handler_instance, "handle")  # Handlers have 'handle'
