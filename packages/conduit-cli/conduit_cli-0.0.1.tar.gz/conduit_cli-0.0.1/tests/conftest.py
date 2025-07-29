"""Shared pytest fixtures for the Conduit test suite.

This module provides common fixtures following pytest best practices:
- Factory fixtures for dynamic test data generation
- Shared setup/teardown with yield for cleanup
- Temporary directory management using tmp_path
- Common test data patterns for parametrization
"""

import asyncio  # Add asyncio import
import hashlib
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

import pytest
import yaml
from click.testing import CliRunner

from conduit.services.lock import LockService

# === Pack Command Handler Fixtures ===
from .plugins import concurrent_httpbin

# Import the concurrent_httpbin fixture from the plugin
concurrent_httpbin = concurrent_httpbin.concurrent_httpbin

API_VERSION = "conduit.warrical.com/next"  # Default API version for manifests


@pytest.fixture
def runner(request):
    return CliRunner()


@pytest.fixture
def real_bundle_reference():
    """Provide a real bundle reference for integration testing."""
    return "localhost:8080/jupytertest02/reverse-proxy-manager:0.0.3"


class AppDefaults:
    """Constants used across tests."""

    API_VERSION: str = "conduit.warrical.com/next"
    SCRIPT_MODE: int = 0o755
    ARTIFACT_MODE: int = 0o644


class AppTestUtils:
    """Utility functions for test  setup and validation."""

    @staticmethod
    def checksum_size(file: Path) -> Tuple[str, int]:
        """Calculate the checksum of a file."""
        if not file.exists() or not file.is_file():
            msg = f"File {file} does not exist or is not a file."
            raise FileNotFoundError(msg)

        checksum = hashlib.sha256(file.read_bytes()).hexdigest()
        size = file.stat().st_size
        return checksum, size


@pytest.fixture
def bundle_manifest_factory(tmp_path):
    """Factory for creating test manifests for bundle command testing."""

    def _create_bundle_manifest(
        manifest_name: str = "test-bundle",
        artifact_count: int = 1,
        variables: Optional[Dict[str, str]] = None,
        version: str = "1.0.0",
    ):
        # Create source files directory
        files_dir = tmp_path / "files"
        files_dir.mkdir(exist_ok=True)

        # Create test source file
        source_file = files_dir / "test.txt"
        source_file.write_text("test content for bundle")

        # Create manifest data
        manifest_data = {
            "apiVersion": API_VERSION,
            "kind": "Manifest",
            "metadata": {"name": manifest_name, "version": version},
            "artifacts": [],
        }

        # Add variables if provided
        if variables:
            manifest_data["variables"] = variables

        # Add artifacts based on count
        for i in range(artifact_count):
            manifest_data["artifacts"].append({
                "name": f"artifact-{i}",
                "origin": str(source_file),
                "target": f"target-{i}.txt",
            })

        # Write manifest file
        manifest_path = tmp_path / f"{manifest_name}.yml"
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest_data, f, default_flow_style=False)

        return manifest_path, source_file

    return _create_bundle_manifest


@pytest.fixture
def pack_manifest_factory(tmp_path):
    """Factory for creating realistic test manifests for pack command testing."""

    def _create_manifest(manifest_name: str, artifact_count: int = 3):
        # Create source files directory in tmp_path
        files_dir = tmp_path / "files" / manifest_name
        files_dir.mkdir(parents=True, exist_ok=True)

        # Create realistic dummy source files
        (files_dir / "config.yaml").write_text(
            "server:\n  host: localhost\n  port: 8080"
        )
        (files_dir / "app.conf").write_text("[app]\nversion = 1.0\ndebug = false")
        (files_dir / "binary.bin").write_bytes(b"\x00\x01\x02\x03\x04\x05")

        # Create manifest data similar to soc-nids-suite.yml
        manifest_data = {
            "apiVersion": API_VERSION,
            "kind": "Manifest",
            "metadata": {"name": manifest_name, "version": "1.0.0"},
            "variables": {"target_dir": f"/opt/{manifest_name}"},
            "artifacts": [],
        }

        # Add artifacts based on count
        if artifact_count >= 1:
            manifest_data["artifacts"].append({
                "name": f"{manifest_name}-config",
                "origin": f"files/{manifest_name}/config.yaml",
                "target": "{{variables.target_dir}}/config.yaml",
            })

        if artifact_count >= 2:
            manifest_data["artifacts"].append({
                "name": f"{manifest_name}-app-config",
                "origin": f"files/{manifest_name}/app.conf",
                "target": "{{variables.target_dir}}/app.conf",
            })

        if artifact_count >= 3:
            manifest_data["artifacts"].append({
                "name": f"{manifest_name}-binary",
                "origin": f"files/{manifest_name}/binary.bin",
                "target": "{{variables.target_dir}}/bin/app",
            })

        # Write manifest file
        manifest_path = tmp_path / f"{manifest_name}.manifest.yaml"
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest_data, f, default_flow_style=False)

        return manifest_path, files_dir


@pytest.fixture
def pack_lockfile_factory(
    tmp_path, lock_service: LockService
):  # Added type hint for generate_service
    """Factory for creating realistic lockfiles from manifests for pack testing."""

    def _create_lockfile(manifest_path: Path):
        # Generate lockfile from manifest using LockService
        lockfile_path = tmp_path / "test.conduit.lock.yaml"

        # Use existing LockService to create realistic lockfile
        # Pass empty CLI variables and explicit output path
        # Call the async version using asyncio.run() as this fixture is synchronous
        lockfile_path, lockfile = asyncio.run(
            lock_service.generate_lockfile_async(
                str(manifest_path),
                cli_variables=None,  # No CLI variables needed for test
                output_path=str(lockfile_path),
            )
        )
        return lockfile, lockfile_path

    return _create_lockfile


@pytest.fixture
def tmp_test_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test files with automatic cleanup.

    Uses pytest's built-in tmp_path fixture for proper cleanup.
    Follows Rule 17: Use tmp_path fixture for temporary file operations.
    """
    return tmp_path


@pytest.fixture
def sample_manifest_factory(tmp_test_dir: Path) -> Callable[[Dict[str, Any]], Path]:
    """Factory fixture for creating test manifest files.

    Returns a function that creates manifest files with custom content.
    Follows Rule 9: Create factory fixtures for flexible test data.
    """

    def _create_manifest(content: Dict[str, Any]) -> Path:
        manifest_path = tmp_test_dir / "manifest.yaml"
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(content, f)
        return manifest_path

    return _create_manifest


@pytest.fixture
def sample_lockfile_factory(tmp_test_dir: Path) -> Callable[[Dict[str, Any]], Path]:
    """Factory fixture for creating test lockfile files.

    Returns a function that creates lockfile files with custom content.
    Follows Rule 9: Create factory fixtures for flexible test data.
    """

    def _create_lockfile(content: Dict[str, Any]) -> Path:
        lockfile_path = tmp_test_dir / "conduit.lock.yaml"
        with open(lockfile_path, "w", encoding="utf-8") as f:
            yaml.dump(content, f)
        return lockfile_path

    return _create_lockfile


@pytest.fixture
def basic_manifest_content() -> Dict[str, Any]:
    """Provide basic manifest content for tests.

    Follows Rule 6: Return configuration functions from fixtures.
    """
    return {
        "apiVersion": f"{API_VERSION}",
        "kind": "Manifest",
        "artifacts": [
            {
                "name": "test-artifact",
                "origin": "test_source.txt",
                "target": "test_target.txt",
            }
        ],
    }


@pytest.fixture
def basic_lockfile_content() -> Dict[str, Any]:
    """Provide basic lockfile content for tests.

    Follows Rule 6: Return configuration functions from fixtures.
    """
    return {
        "apiVersion": f"{API_VERSION}",
        "kind": "Lockfile",
        "metadata": {"generation": 1},
        "operations": [
            {
                "type": "copy",
                "source": "test_source.txt",
                "destination": "test_target.txt",
            }
        ],
    }


@pytest.fixture
def manifest_data_string_factory() -> Callable[..., str]:
    """Factory to create manifest data strings for tests."""

    def _create_manifest_data(
        manifest_name: str,
        artifacts: List[Dict[str, str]],
        variables: Optional[Dict[str, Any]] = None,
        api_version: str = API_VERSION,
        kind: str = "Manifest",
        entrypoint: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
    ) -> str:
        if variables is None:
            variables = {"dummy_test_var": "dummy_test_value"}
        manifest_data = {
            "apiVersion": api_version,
            "kind": kind,
            "metadata": {"name": manifest_name, "version": version},
            "artifacts": artifacts,
        }
        if variables:
            manifest_data["variables"] = variables
        if entrypoint:
            manifest_data["entrypoint"] = entrypoint
        return yaml.dump(manifest_data, default_flow_style=True, indent=4)

    return _create_manifest_data


@pytest.fixture
def manifest_data_factory() -> Callable[..., Dict[str, Any]]:
    """Factory to create manifest data structures for tests.

    Allows customization of manifest name, artifacts, and variables.
    """

    def _create_manifest_data(
        manifest_name: str,
        artifacts: List[Dict[str, str]],
        variables: Optional[Dict[str, Any]] = None,
        api_version: str = API_VERSION,
        kind: str = "Manifest",
        entrypoint: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
    ) -> Dict[str, Any]:
        if variables is None:
            variables = {"dummy_test_var": "dummy_test_value"}
        manifest_data = {
            "apiVersion": api_version,
            "kind": kind,
            "metadata": {"name": manifest_name, "version": version},
            "artifacts": artifacts,
        }
        if variables:
            manifest_data["variables"] = variables
        if entrypoint:
            manifest_data["entrypoint"] = entrypoint
        return manifest_data

    return _create_manifest_data


@pytest.fixture
def lock_service() -> LockService:
    """Provide a LockServices instance for tests."""
    return LockService()


@pytest.fixture
def oci_registry_config():
    """Provide OCI registry configuration for testing."""
    import os
    return {
        "url": "localhost:8080",
        "repo": "ocinative-test", 
        "username": os.getenv("CONDUIT_REGISTRY_USERNAME"),
        "password": os.getenv("CONDUIT_REGISTRY_PASSWORD"),
        "skip_tls": True
    }


class ManifestScenario(NamedTuple):
    manifest_path: Path
    expected_lockfile_path: Path
    cli_variables: Optional[Tuple[str, ...]]
    expected_target_path: str
    expected_artifact_name: str
    source_file_path: Path
    source_content: str
    manifest_name: str


@pytest.fixture
def prepared_manifest_scenario(
    request: pytest.FixtureRequest,
    tmp_test_dir: Path,
    sample_manifest_factory: Callable[[Dict[str, Any]], Path],
    manifest_data_factory: Callable[..., Dict[str, Any]],
) -> ManifestScenario:
    """Fixture to prepare a manifest test scenario using indirect parametrization.

    This fixture receives parameters via request.param and sets up the necessary
    files and data for a test case.
    """
    (
        manifest_name,
        source_content,
        expected_artifact_name,
        artifacts_def,
        manifest_variables,
        cli_variables,
        expected_target_path,
    ) = request.param

    source_file = tmp_test_dir / "source.txt"
    source_file.write_text(source_content)

    processed_artifacts = []
    for art_def in artifacts_def:
        art_copy = art_def.copy()
        # Always replace {source_file} with the actual path
        art_copy["origin"] = art_def["origin_placeholder"].format(
            source_file=str(source_file)
        )
        if "origin_placeholder" in art_copy:
            del art_copy["origin_placeholder"]
        processed_artifacts.append(art_copy)

    manifest_data = manifest_data_factory(
        manifest_name=manifest_name,
        artifacts=processed_artifacts,
        variables=manifest_variables,
    )
    manifest_path = sample_manifest_factory(manifest_data)
    expected_lockfile_path = tmp_test_dir / f"{manifest_name}.conduit.lock.yaml"

    return ManifestScenario(
        manifest_path=manifest_path,
        expected_lockfile_path=expected_lockfile_path,
        cli_variables=cli_variables,
        expected_target_path=expected_target_path,
        expected_artifact_name=expected_artifact_name,
        source_file_path=source_file,
        source_content=source_content,
        manifest_name=manifest_name,
    )
