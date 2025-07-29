"""Tests for lockfile generation with OCI artifacts."""

from pathlib import Path

import pytest
import yaml

from conduit.core.commands import CalculateMetadataCommand, CalculateMetadataResult
from conduit.core.models import (
    Manifest,
    ManifestArtifact,
    ManifestMetadata,
)
from conduit.handlers.factory import HandlerFactory
from conduit.handlers.oci import OciHandler
from conduit.services.cache import CacheResolver
from conduit.services.lockfile import LockfileService

from .conftest import API_VERSION


@pytest.mark.parametrize(
    ("oci_ref", "oci_name", "oci_target"),
    [("docker.io/library/nginx:1.25", "nginx-image", "./images/nginx.tar")],
)
@pytest.mark.asyncio
async def test_generate_lockfile_with_oci_artifacts(
    tmp_path: Path, oci_ref: str, oci_name: str, oci_target: str
):
    """Test lockfile generation includes OCI image artifacts."""
    manifest = Manifest(
        apiVersion=f"{API_VERSION}",
        kind="Manifest",
        metadata=ManifestMetadata(
            name="test-oci-manifest"
        ),  # Wrapped in ManifestMetadata
        artifacts=[
            ManifestArtifact(
                name=oci_name,
                origin=f"oci://{oci_ref}",
                target=oci_target,
            ),
            ManifestArtifact(
                name="local-config", origin="./config.txt", target="./config/app.txt"
            ),
        ],
    )

    config_file = tmp_path / "config.txt"
    config_file.write_text("test config")

    manifest_file_on_disk = tmp_path / "manifest.yaml"
    with open(manifest_file_on_disk, "w", encoding="utf-8") as f:
        yaml.dump(manifest.model_dump(), f)

    lockfile_service = LockfileService()

    cache_dir = tmp_path / "oci_test_cache"
    cache_dir.mkdir(exist_ok=True)
    cache_service = CacheResolver(cache_dir=cache_dir)
    # Pass manifest_file_on_disk's parent as base_path for relative local artifact resolution
    handler_factory = HandlerFactory(
        base_path=str(manifest_file_on_disk.parent), cache_service=cache_service
    )

    lockfile = await lockfile_service.generate_lockfile_from_manifest_async(
        manifest, handler_factory, manifest_path=str(manifest_file_on_disk)
    )

    assert len(lockfile.artifacts) == 2

    oci_artifact = next(a for a in lockfile.artifacts if a.name == oci_name)
    assert oci_artifact.type == "oci"
    assert oci_artifact.origin == f"oci://{oci_ref}"
    assert oci_artifact.checksum.startswith("sha256:")

    local_artifact = next(a for a in lockfile.artifacts if a.name == "local-config")
    assert local_artifact.type == "file"
    assert local_artifact.checksum.startswith("sha256:")


@pytest.mark.parametrize("oci_ref", ["oci://ghcr.io/linuxcontainers/alpine:latest"])
@pytest.mark.asyncio
async def test_oci_handler_metadata_structure(oci_ref: str):
    """Test OCI handler returns proper metadata structure."""
    handler = OciHandler()
    command = CalculateMetadataCommand(origin=oci_ref)

    base_result = await handler.handle(command)

    assert isinstance(base_result, CalculateMetadataResult)
    metadata_result: CalculateMetadataResult = base_result
    # This is the one that should work because I just grabbed it without being authenticated

    assert metadata_result.success is True
    assert metadata_result.checksum is not None
    assert metadata_result.size is not None
    assert metadata_result.type is not None
    assert metadata_result.type == "oci"

    assert metadata_result.metadata is not None
    assert "registry" in metadata_result.metadata
    assert "repository" in metadata_result.metadata
    assert "tag" in metadata_result.metadata


@pytest.mark.parametrize(
    ("oci_ref", "expected"),
    [
        (
            "oci://docker.io/nginx:1.25",
            {"registry": "docker.io", "repository": "nginx", "tag": "1.25"},
        ),
        (
            "oci://ghcr.io/owner/repo:latest",
            {"registry": "ghcr.io", "repository": "owner/repo", "tag": "latest"},
        ),
        (
            "oci://registry.example.com:5000/app/service:v1",
            {
                "registry": "registry.example.com:5000",
                "repository": "app/service",
                "tag": "v1",
            },
        ),
        (
            "oci://docker.io/library/ubuntu",
            {"registry": "docker.io", "repository": "library/ubuntu", "tag": "latest"},
        ),
    ],
)
def test_oci_reference_parsing(oci_ref, expected):
    """Test OCI reference parsing handles various formats."""
    handler = OciHandler()
    parsed = handler._parse_oci_reference(oci_ref)

    assert parsed["registry"] == expected["registry"]
    assert parsed["repository"] == expected["repository"]
    assert parsed["tag"] == expected["tag"]
