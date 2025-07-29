"""
Tests for the `conduit init` command.

This module tests the init command functionality including template generation,
file creation, and CLI options.
"""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from conduit.commands.init import init
from conduit.cli.context import ConduitContext


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_init_creates_project_directory_and_manifest(runner: CliRunner):
    """Test that `conduit init <name>` creates a directory and manifest."""
    with runner.isolated_filesystem() as fs:
        result = runner.invoke(init, ["my-app", "--yes"], obj=ConduitContext(calling_dir=Path(fs)))

        assert result.exit_code == 0, result.output
        assert "✅ Created manifest template: my-app/my-app.conduit.yml" in result.output

        project_dir = Path(fs) / "my-app"
        manifest_file = project_dir / "my-app.conduit.yml"
        assert project_dir.is_dir()
        assert manifest_file.exists()

        content = manifest_file.read_text()
        assert 'name: "my-app"' in content


def test_init_in_current_directory(runner: CliRunner):
    """Test that `conduit init` initializes in the current directory."""
    with runner.isolated_filesystem() as fs:
        result = runner.invoke(init, ["--yes"], obj=ConduitContext(calling_dir=Path(fs)))

        assert result.exit_code == 0, result.output
        assert "✅ Created manifest template: manifest.conduit.yml" in result.output

        manifest_file = Path(fs) / "manifest.conduit.yml"
        assert manifest_file.exists()

        content = manifest_file.read_text()
        assert 'name: "manifest"' in content


def test_init_with_directory_option(runner: CliRunner):
    """Test that `conduit init -C <dir> <name>` works correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        fs = Path(temp_dir)
        target_dir = fs / "projects"
        target_dir.mkdir()

        result = runner.invoke(
            init, ["-C", str(target_dir), "new-bundle", "--yes"], obj=ConduitContext(calling_dir=fs)
        )

        assert result.exit_code == 0, result.output

        project_dir = target_dir / "new-bundle"
        manifest_file = project_dir / "new-bundle.conduit.yml"

        assert f"✅ Created manifest template: {manifest_file.relative_to(fs)}" in result.output
        assert project_dir.is_dir()
        assert manifest_file.exists()

        content = manifest_file.read_text()
        assert 'name: "new-bundle"' in content


def test_init_in_specific_directory_no_name(runner: CliRunner):
    """Test that `conduit init -C <dir>` initializes in that directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        fs = Path(temp_dir)
        target_dir = fs / "projects"
        target_dir.mkdir()

        result = runner.invoke(init, ["-C", str(target_dir), "--yes"], obj=ConduitContext(calling_dir=fs))

        assert result.exit_code == 0, result.output

        manifest_file = target_dir / "projects.conduit.yml"
        assert f"✅ Created manifest template: {manifest_file.relative_to(fs)}" in result.output
        assert manifest_file.exists()

        content = manifest_file.read_text()
        assert 'name: "projects"' in content


def test_init_with_entrypoint(runner: CliRunner):
    """Test that entrypoint script is created correctly."""
    with runner.isolated_filesystem() as fs:
        result = runner.invoke(
            init, ["my-app", "--template", "basic-entrypoint", "--yes"], obj=ConduitContext(calling_dir=Path(fs))
        )

        assert result.exit_code == 0, result.output
        assert "✅ Created manifest template: my-app/my-app.conduit.yml" in result.output
        assert "✅ Created entrypoint script: my-app/scripts/install.sh" in result.output

        entrypoint_file = Path(fs) / "my-app/scripts/install.sh"
        assert entrypoint_file.exists()
        assert entrypoint_file.stat().st_mode & 0o111  # Check for execute permissions


def test_init_force_behavior(runner: CliRunner):
    """Test that init respects --force flag."""
    with runner.isolated_filesystem() as fs:
        # Create an existing file
        manifest_file = Path(fs) / "my-app/my-app.conduit.yml"
        manifest_file.parent.mkdir()
        manifest_file.write_text("existing content")

        # Should fail without --force
        result = runner.invoke(init, ["my-app", "--yes"], obj=ConduitContext(calling_dir=Path(fs)))
        assert result.exit_code != 0
        assert "already exists. Use --force to overwrite." in result.output

        # Should succeed with --force
        result = runner.invoke(init, ["my-app", "--yes", "--force"], obj=ConduitContext(calling_dir=Path(fs)))
        assert result.exit_code == 0, result.output
        assert "✅ Created manifest template: my-app/my-app.conduit.yml" in result.output
        content = manifest_file.read_text()
        assert "existing content" not in content
        assert "apiVersion: conduit.warrical.com/next" in content


def test_init_directory_option_does_not_exist(runner: CliRunner):
    """Test that `init -C` fails if the directory does not exist."""
    with runner.isolated_filesystem() as fs:
        result = runner.invoke(init, ["-C", "nonexistent-dir", "my-app", "--yes"], obj=ConduitContext(calling_dir=Path(fs)))
        assert result.exit_code != 0
        assert "Directory 'nonexistent-dir' does not exist" in result.output


def test_init_help_output(runner: CliRunner):
    """Test that help output includes the new options."""
    result = runner.invoke(init, ["--help"])

    assert result.exit_code == 0
    assert "Scaffold a starter manifest file" in result.output
    assert "-C, --directory" in result.output
    assert "conduit init my-app" in result.output


@pytest.mark.parametrize(
    ("options", "expected_file", "expected_name"),
    [
        (["my-bundle"], "my-bundle/my-bundle.conduit.yml", "my-bundle"),
        ([], "manifest.conduit.yml", "manifest"),
    ],
)
def test_init_creates_valid_manifest(runner: CliRunner, options, expected_file, expected_name):
    """Test that init creates a manifest file that can be parsed."""
    with runner.isolated_filesystem() as fs:
        result = runner.invoke(init, [*options, "--yes"], obj=ConduitContext(calling_dir=Path(fs)))
        assert result.exit_code == 0, result.output

        manifest_file = Path(fs) / expected_file
        assert manifest_file.exists()

        with open(manifest_file) as f:
            data = yaml.safe_load(f)

        assert data["apiVersion"] == "conduit.warrical.com/next"
        assert data["kind"] == "Manifest"
        assert data["metadata"]["name"] == expected_name
        assert "artifacts" in data
        