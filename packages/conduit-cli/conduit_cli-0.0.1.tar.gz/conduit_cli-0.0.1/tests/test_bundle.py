from pathlib import Path
from unittest.mock import patch
import os
import pytest
from click.testing import CliRunner

from conduit.cli.main import main


@pytest.fixture
def runner():
    return CliRunner()


# Helper to create a dummy manifest for testing
@pytest.fixture
def dummy_manifest(tmp_path: Path):
    manifest_content = """apiVersion: conduit.warrical.com/next
kind: Manifest
metadata:
  name: test-bundle
  version: 1.0.0
artifacts:
  - name: dummy-artifact
    origin: dummy.txt
    target: /app/dummy.txt
"""
    manifest_path = tmp_path / "test-manifest.yml"
    manifest_path.write_text(manifest_content)
    (tmp_path / "dummy.txt").write_text("This is a dummy artifact.")
    return manifest_path


# Helper to create a dummy bundle for testing
@pytest.fixture
def dummy_bundle(runner: CliRunner, dummy_manifest: Path, tmp_path: Path):
    # Build a bundle from the dummy manifest
    output_bundle = tmp_path / "test.bundle"
    result = runner.invoke(main, ["bundle", "build", "-m", str(dummy_manifest), "-o", str(output_bundle)])
    assert result.exit_code == 0, f"Failed to create dummy bundle: {result.output}"
    return output_bundle


def test_bundle_apply(runner: CliRunner, dummy_bundle: Path, tmp_path: Path):
    """Test the 'bundle apply' subcommand."""
    output_dir = tmp_path / "applied_bundle"
    result = runner.invoke(main, ["bundle", "apply", str(dummy_bundle), "-o", str(output_dir)])
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert "Bundle applied successfully!" in result.output
    assert output_dir.exists()
    assert (output_dir / "app" / "dummy.txt").exists()


def test_bundle_build(runner: CliRunner, dummy_manifest: Path, tmp_path: Path):
    """Test the 'bundle build' subcommand."""
    output_bundle = tmp_path / "my-built-bundle.bundle"
    result = runner.invoke(main, ["bundle", "build", "-m", str(dummy_manifest), "-o", str(output_bundle)])
    print(f"Bundle output path: {output_bundle}")
    print(output_bundle.stat().st_size / (1024*1024))
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert "Bundle build completed successfully!" in result.output
    assert output_bundle.exists()


def test_bundle_extract(runner: CliRunner, dummy_bundle: Path, tmp_path: Path):
    """Test the 'bundle extract' subcommand."""
    output_dir = tmp_path / "extracted_bundle"
    result = runner.invoke(main, ["bundle", "extract", str(dummy_bundle), str(output_dir), "--format", "oci"])
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert "Extracted to:" in result.output
    assert output_dir.exists()
    assert (output_dir / "oci-layout").exists() # Should extract to OCI layout when --format oci is used


def test_bundle_info(runner: CliRunner, dummy_bundle: Path):
    """Test the 'bundle info' subcommand."""
    result = runner.invoke(main, ["bundle", "info", str(dummy_bundle)])
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert "Bundle Info:" in result.output
    assert "Name: test-bundle" in result.output
    assert "Version: 1.0.0" in result.output

@pytest.mark.parametrize("bundle_name, bundle_version, has_entrypoint, number_of_artifacts", [("my-test-bundle", "1.0.0", True, 1), ("test-bundle", "latest", False, 1)])
def test_bundle_init(runner: CliRunner, tmp_path: Path, bundle_name: str, bundle_version: str, has_entrypoint: bool, number_of_artifacts: int):
    """Test the 'bundle init' subcommand."""
    # init command creates files in the current directory, so we isolate it
    with runner.isolated_filesystem(temp_dir=tmp_path):
        entrypoint_option = "y" if has_entrypoint else "n"
        result = runner.invoke(main, ["bundle", "init"], input=f"{bundle_name}\n{bundle_version}\nTest bundle description\n{entrypoint_option}\n{number_of_artifacts}\nL\n")
        expected_manifest_path = Path.cwd() / bundle_name / f"{bundle_name}.conduit.yml"
        content = expected_manifest_path.read_text()
        print()
        print(f"Result Output: \n{result.output}")
        print(f"List Dir: {os.listdir(tmp_path)}")
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "✅ Created manifest template:" in result.output
        # entrypoint should not be in the manifest if has_entrypoint is False
        if has_entrypoint:
            assert "entrypoint:" in content, f"Expected entrypoint in manifest but got: {content}"
        else:
            assert "entrypoint:" not in content, f"Expected no entrypoint in manifest but got: {content}"
        # assert that it contains metadata.version = 1.0.0
        print(f"Manifest Path: {expected_manifest_path}")
        print(f"Manifest Content: {expected_manifest_path.read_text()}")
        # assert (tmp_path / ".conduitignore").exists()


def test_bundle_push(runner: CliRunner, dummy_bundle: Path):
    """Test the 'bundle push' subcommand to a local registry."""
    registry_ref = "localhost:8080/test/bundle:latest"
    # Set environment variables for authentication
    os.environ["CONDUIT_REGISTRY_USERNAME"] = "admin"
    # Assuming CONDUIT_REGISTRY_PASSWORD is set in the environment where tests are run
    # If not, this test will fail or prompt for password.
    
    result = runner.invoke(
        main,
        [
            "bundle",
            "push",
            str(dummy_bundle),
            registry_ref,
            "--insecure",
        ],
    )
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert f"Successfully pushed {registry_ref}" in result.output


def test_bundle_pull(runner: CliRunner, tmp_path: Path):
    """Test the 'bundle pull' subcommand from a local registry."""
    registry_ref = "localhost:8080/test/bundle:latest"
    output_bundle = tmp_path / "pulled.bundle"
    
    # Set environment variables for authentication
    os.environ["CONDUIT_REGISTRY_USERNAME"] = "admin"
    # Assuming CONDUIT_REGISTRY_PASSWORD is set in the environment where tests are run

    result = runner.invoke(
        main,
        [
            "bundle",
            "pull",
            registry_ref,
            "-o",
            str(output_bundle),
            "--insecure",
        ],
    )
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert "Bundle pulled successfully!" in result.output
    assert output_bundle.exists()

# Skipped tests for now due to lack of key setup:
# test_bundle_sign
# test_bundle_verify
