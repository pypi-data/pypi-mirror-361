"""Tests for generate service.

This module tests the GenerateService that orchestrates the complete
manifest processing and lockfile generation workflow using handlers and services.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pytest
import yaml

from conduit.services.lock import LockError, LockService

from .conftest import API_VERSION, ManifestScenario  # Import the NamedTuple

# Test data for parametrized success scenarios
GENERATE_SUCCESS_SCENARIOS_PARAMS = [
    # manifest_name, source_content, expected_artifact_name, artifacts_def, manifest_variables, cli_variables, expected_target_path
    (
        "simple-generate-test",
        "Simple test content",
        "test-file",
        [
            {
                "name": "test-file",
                "origin_placeholder": "{source_file}",
                "target": "output.txt",
            }
        ],
        None,
        None,
        "output.txt",
    ),
    (
        "variable-test",
        "Variable test content",
        "config-file",
        [
            {
                "name": "config-file",
                "origin_placeholder": "{source_file}",
                "target": "{{variables.env}}/{{variables.project}}/config.txt",
            }
        ],
        {"env": "development", "project": "myapp"},
        None,
        "development/myapp/config.txt",
    ),
    (
        "cli-var-test",
        "CLI variable test content",
        "app-file",
        [
            {
                "name": "app-file",
                "origin_placeholder": "{source_file}",
                "target": "deploy/{{variables.env}}/app-{{variables.version}}.jar",
            }
        ],
        {"env": "development", "version": "1.0.0"},
        ("env=production", "version=2.0.0"),
        "deploy/production/app-2.0.0.jar",
    ),
    (
        "self-ref-test",
        "Self-referencing test",
        "config",
        [
            {
                "name": "config",
                "origin_placeholder": "{source_file}",
                "target": "{{variables.env}}/config.json",
            }
        ],
        {
            "env": "staging",
            "base_url": "https://{{.env}}.example.com",
            "api_url": "{{.base_url}}/api",
        },
        None,
        "staging/config.json",
    ),
    (
        "integration-test",
        "Integration test content",
        "application",
        [
            {
                "name": "application",
                "origin_placeholder": "{source_file}",
                "target": "{{variables.deploy_path}}/app.jar",
            }
        ],
        {
            "app_name": "myapp",
            "env": "{{.app_name}}-staging",
            "deploy_path": "/opt/{{.app_name}}/{{.env}}",
        },
        ("app_name=webapp",),
        "/opt/webapp/webapp-staging/app.jar",
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prepared_manifest_scenario",
    GENERATE_SUCCESS_SCENARIOS_PARAMS,
    indirect=["prepared_manifest_scenario"],
)
async def test_lock_lockfile_success_scenarios(
    lock_service: LockService, prepared_manifest_scenario: ManifestScenario
):
    """Test various successful lockfile generation scenarios using indirect fixture."""
    scenario = prepared_manifest_scenario

    lockfile_path_str, _ = await lock_service.generate_lockfile_async(
        str(scenario.manifest_path),
        cli_variables=scenario.cli_variables,
        output_path=str(scenario.expected_lockfile_path),
    )
    lockfile_path = Path(lockfile_path_str)

    assert lockfile_path.exists()
    assert lockfile_path == scenario.expected_lockfile_path

    lockfile_content = yaml.safe_load(lockfile_path.read_text())

    assert "manifestHash" in lockfile_content
    assert lockfile_content["manifestHash"].startswith("sha256:")
    assert len(lockfile_content["artifacts"]) == 1

    artifact = lockfile_content["artifacts"][0]
    assert artifact["name"] == scenario.expected_artifact_name
    # Origin should now be relative to lockfile location
    # In test scenarios, source file is typically in same dir as lockfile, so just filename
    expected_origin = Path(scenario.source_file_path).name
    assert artifact["origin"] == expected_origin
    assert artifact["target"] == scenario.expected_target_path
    assert artifact["checksum"].startswith("sha256:")
    assert artifact["size"] == len(scenario.source_content.encode("utf-8"))
    assert artifact["type"] == "file"
    # Action might be different with unified handlers, let's check if it exists
    assert "action" in artifact


@pytest.mark.asyncio
async def test_lock_lockfile_custom_output_path(
    lock_service: LockService,
    tmp_test_dir: Path,
    sample_manifest_factory: Callable[[Dict[str, Any]], Path],
    manifest_data_factory: Callable[..., Dict[str, Any]],
):
    """Test generating lockfile with custom output path."""
    source_content = "Custom output test"
    source_file = tmp_test_dir / "source.txt"
    source_file.write_text(source_content)

    manifest_data = manifest_data_factory(
        manifest_name="custom-output-test",
        artifacts=[
            {"name": "test-file", "origin": str(source_file), "target": "output.txt"}
        ],
    )
    manifest_file = sample_manifest_factory(manifest_data)
    custom_output = tmp_test_dir / "custom.lock.yaml"

    lockfile_path_str, _ = await lock_service.generate_lockfile_async(
        str(manifest_file), output_path=str(custom_output)
    )
    lockfile_path = Path(lockfile_path_str)

    assert lockfile_path == custom_output
    assert lockfile_path.exists()


# Test data for error scenarios
GENERATE_ERROR_SCENARIOS = [
    (
        None,  # manifest_data (for nonexistent manifest)
        "not found",  # expected_error_message_part
    ),
    (
        {
            "apiVersion": "wrong/version",
            "kind": "WrongKind",
            "metadata": {"name": "invalid-test", "version": "1.0.0"},
        },
        "validation",
    ),
    (
        {
            "apiVersion": f"{API_VERSION}",
            "kind": "Manifest",
            "metadata": {"name": "missing-source-test", "version": "1.0.0"},
            "artifacts": [
                {
                    "name": "missing-file",
                    "origin": "/nonexistent/source.txt",
                    "target": "output.txt",
                }
            ],
        },
        "not found",  # This will be caught by handler when checking source
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("manifest_data", "expected_error_message_part"), GENERATE_ERROR_SCENARIOS
)
async def test_lock_lockfile_error_handling(
    lock_service: LockService,
    tmp_test_dir: Path,
    sample_manifest_factory: Callable[[Dict[str, Any]], Path],
    manifest_data: Optional[Dict[str, Any]],
    expected_error_message_part: str,
):
    """Test error handling for various invalid manifest scenarios."""
    manifest_path_str = ""
    if manifest_data:
        if manifest_data.get("metadata", {}).get("name") == "missing-source-test":
            dummy_source = tmp_test_dir / "dummy_source_for_validation.txt"
            dummy_source.write_text("dummy")

        manifest_path = sample_manifest_factory(manifest_data)
        manifest_path_str = str(manifest_path)
    else:
        manifest_path_str = str(tmp_test_dir / "nonexistent_manifest.yaml")

    with pytest.raises(LockError) as exc_info:
        await lock_service.generate_lockfile_async(manifest_path_str)

    assert expected_error_message_part in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_lock_lockfile_multiple_artifacts(
    lock_service: LockService,
    tmp_test_dir: Path,
    sample_manifest_factory: Callable[[Dict[str, Any]], Path],
    manifest_data_factory: Callable[..., Dict[str, Any]],
):
    """Test generating lockfile with multiple artifacts."""
    content1 = "First file content"
    content2 = "Second file content"
    source1 = tmp_test_dir / "file1.txt"
    source1.write_text(content1)
    source2 = tmp_test_dir / "file2.txt"
    source2.write_text(content2)

    manifest_data = manifest_data_factory(
        manifest_name="multi-artifact-test",
        artifacts=[
            {"name": "first-file", "origin": str(source1), "target": "output1.txt"},
            {"name": "second-file", "origin": str(source2), "target": "output2.txt"},
        ],
    )
    manifest_file = sample_manifest_factory(manifest_data)
    expected_lockfile_path = tmp_test_dir / "multi-artifact-test.conduit.lock.yaml"

    lockfile_path_str, _ = await lock_service.generate_lockfile_async(
        str(manifest_file), output_path=str(expected_lockfile_path)
    )
    lockfile_path = Path(lockfile_path_str)

    assert lockfile_path.exists()
    assert lockfile_path == expected_lockfile_path

    lockfile_content = yaml.safe_load(lockfile_path.read_text())

    assert len(lockfile_content["artifacts"]) == 2

    artifacts_by_name = {a["name"]: a for a in lockfile_content["artifacts"]}
    assert "first-file" in artifacts_by_name
    assert "second-file" in artifacts_by_name

    # Origins should now be relative to lockfile location
    assert artifacts_by_name["first-file"]["origin"] == Path(source1).name
    assert artifacts_by_name["second-file"]["origin"] == Path(source2).name


@pytest.mark.asyncio
async def test_lock_service_consistency(
    lock_service: LockService,
    tmp_test_dir: Path,
    sample_manifest_factory: Callable[[Dict[str, Any]], Path],
    manifest_data_factory: Callable[..., Dict[str, Any]],
):
    """Test that generate service produces consistent results."""
    source_content = "Consistency test"
    source_file = tmp_test_dir / "test.txt"
    source_file.write_text(source_content)

    manifest_data = manifest_data_factory(
        manifest_name="consistency-test",
        artifacts=[
            {"name": "test-file", "origin": str(source_file), "target": "output.txt"}
        ],
    )
    manifest_file = sample_manifest_factory(manifest_data)
    expected_lockfile_path1 = tmp_test_dir / "consistency-test-1.conduit.lock.yaml"
    expected_lockfile_path2 = tmp_test_dir / "consistency-test-2.conduit.lock.yaml"

    lockfile_path1_str, _ = await lock_service.generate_lockfile_async(
        str(manifest_file), output_path=str(expected_lockfile_path1)
    )
    lockfile_path2_str, _ = await lock_service.generate_lockfile_async(
        str(manifest_file), output_path=str(expected_lockfile_path2)
    )
    lockfile_path1 = Path(lockfile_path1_str)
    lockfile_path2 = Path(lockfile_path2_str)

    lockfile1 = yaml.safe_load(lockfile_path1.read_text())
    lockfile2 = yaml.safe_load(lockfile_path2.read_text())

    assert lockfile1["manifestHash"] == lockfile2["manifestHash"]
    assert (
        lockfile1["artifacts"][0]["checksum"] == lockfile2["artifacts"][0]["checksum"]
    )
    assert lockfile1["artifacts"][0]["size"] == lockfile2["artifacts"][0]["size"]


class TestGenerateOutputRefactor:
    """Test class for enhanced output argument handling."""

    @pytest.fixture(scope="class")
    def service(self) -> LockService:
        return LockService()

    def create_test_file(self, content: str, temp_dir: str, filename: str) -> str:
        """
        Create a test file with the given content.
        """
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    @pytest.mark.asyncio
    async def test_output_directory_with_trailing_slash(self, service: LockService):
        """Test --output with directory ending in slash creates lockfile in that directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_content = "Directory test content"
            source_file = self.create_test_file(source_content, temp_dir, "source.txt")
            manifest_content = f"""apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: directory-test
  version: 1.0.0
artifacts:
  - name: test-file
    origin: {source_file!s}
    target: output.txt
"""
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.yaml"
            )
            output_dir = Path(temp_dir) / "builds/"
            os.makedirs(output_dir, exist_ok=True)
            output_path_with_slash = str(output_dir) + "/"

            lockfile_path, _ = await service.generate_lockfile_async(
                manifest_file, output_path=output_path_with_slash
            )
            expected_path = os.path.join(
                output_dir, "directory-test-1.0.0.conduit.lock.yaml"
            )
            assert lockfile_path == expected_path
            assert os.path.exists(expected_path)

    @pytest.mark.asyncio
    async def test_output_existing_directory_without_slash(self, service: LockService):
        """Test --output with existing directory (no slash) creates lockfile in that directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_content = "Directory test content"
            source_file = self.create_test_file(source_content, temp_dir, "source.txt")
            manifest_content = f"""apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: existing-dir-test
  version: 1.0.0
artifacts:
  - name: test-file
    origin: {source_file}
    target: output.txt
"""
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.yaml"
            )
            output_dir = Path(temp_dir) / "deploy"
            output_dir = os.path.join(temp_dir, "deploy")
            os.makedirs(output_dir, exist_ok=True)

            lockfile_path, _ = await service.generate_lockfile_async(
                manifest_file, output_path=output_dir
            )
            expected_path = os.path.join(
                output_dir, "existing-dir-test-1.0.0.conduit.lock.yaml"
            )
            assert lockfile_path == expected_path
            assert os.path.exists(expected_path)

    @pytest.mark.asyncio
    async def test_output_nonexistent_directory_creates_parent_dirs(
        self, service: LockService
    ):
        """Test --output with non-existent directory creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_content = "Parent dir test content"
            source_file = self.create_test_file(source_content, temp_dir, "source.txt")
            manifest_content = f"""apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: parent-dir-test
  version: 1.0.0
artifacts:
  - name: test-file
    origin: {source_file}
    target: output.txt
"""
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.yaml"
            )
            output_dir = os.path.join(temp_dir, "build", "artifacts", "staging")
            output_path_with_slash = output_dir + "/"

            lockfile_path, _ = await service.generate_lockfile_async(
                manifest_file, output_path=output_path_with_slash
            )
            expected_path = os.path.join(
                output_dir, "parent-dir-test-1.0.0.conduit.lock.yaml"
            )
            assert lockfile_path == expected_path
            assert os.path.exists(expected_path)
            assert os.path.isdir(output_dir)

    @pytest.mark.asyncio
    async def test_output_relative_directory(self, service: LockService):
        """Test --output with relative directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                source_content = "Relative dir test content"
                # source_file needs to be an absolute path or relative to the new CWD (temp_dir)
                source_file_abs = os.path.join(temp_dir, "source.txt")
                with open(source_file_abs, "w", encoding="utf-8") as f:
                    f.write(source_content)

                manifest_content = f"""apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: relative-dir-test
  version: 1.0.0
artifacts:
  - name: test-file
    origin: {source_file_abs} # Use absolute path for origin in manifest
    target: output.txt
"""
                manifest_file_abs = os.path.join(temp_dir, "manifest.yaml")
                with open(manifest_file_abs, "w", encoding="utf-8") as f:
                    f.write(manifest_content)

                relative_output = "./output/"
                lockfile_path, _ = await service.generate_lockfile_async(
                    manifest_file_abs, output_path=relative_output
                )
                expected_relative_path = (
                    "output/relative-dir-test-1.0.0.conduit.lock.yaml"
                )
                assert lockfile_path == expected_relative_path
                assert os.path.exists(
                    expected_relative_path
                )  # This checks relative to current CWD (temp_dir)
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_output_full_file_path_backward_compatibility(
        self, service: LockService
    ):
        """Test that existing full file path behavior still works (backward compatibility)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_content = "Backward compatibility test"
            source_file = self.create_test_file(source_content, temp_dir, "source.txt")
            manifest_content = f"""apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: backward-compat-test
  version: 1.0.0
artifacts:
  - name: test-file
    origin: {source_file!s}
    target: output.txt
"""
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.yaml"
            )
            custom_lockfile_path = os.path.join(
                temp_dir, "custom-name.conduit.lock.yaml"
            )
            lockfile_path, _ = await service.generate_lockfile_async(
                manifest_file, output_path=custom_lockfile_path
            )
            assert lockfile_path == custom_lockfile_path
            assert os.path.exists(custom_lockfile_path)
