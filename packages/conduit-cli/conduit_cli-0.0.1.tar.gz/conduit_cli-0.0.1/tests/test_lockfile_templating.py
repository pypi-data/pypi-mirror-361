"""
Tests for the `conduit generate` command with Jinja2 templating support.
"""

import os
from pathlib import Path
from typing import Any, Dict

from click.testing import CliRunner

from conduit.commands.lock import lock
from conduit.services.lockfile import LockfileService

from .conftest import API_VERSION


class TestGenerateTemplating:
    """Deprecated Test class for generate command templating functionality."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.runner = CliRunner()

    def create_test_file(self, content: str, temp_dir: str, filename: str) -> str:
        """
        Create a test file with the given content.

        Args:
            content: Content to write to the file
            temp_dir: Temporary directory path
            filename: Name of the file

        Returns:
            Path to the created file
        """
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def load_lockfile(self, lockfile_path: Path) -> Dict[str, Any]:
        """
        Load a lockfile and return its content as a dictionary.

        Args:
            lockfile_path: Path to the lockfile

        Returns:
            Lockfile content as a dictionary
        """
        lockfile_service = LockfileService()
        return lockfile_service.load_lockfile_data(lockfile_path)

    def test_basic_templating(self, tmp_path):
        """Test basic templating with a single variable."""
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a source file
            source_content = "This is a test file for basic templating."
            self.create_test_file(source_content, ".", "source.txt")

            # Create a templated manifest
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: test-{{ env }}
  version: 1.0.0
artifacts:
  - name: config-file
    origin: source.txt
    target: "{{ target_dir }}/output.txt"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "manifest.yaml"
            )

            # Run the generate command with template variables
            result = self.runner.invoke(
                lock,
                [
                    manifest_file,
                    "--var",
                    "env=production",
                    "--var",
                    "target_dir=deploy",
                ],
            )
            # Check that the command succeeded
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert (
                "Using template variables: env=production, target_dir=deploy"
                in result.output
            )
            assert "✓ Lock file generated:" in result.output
            assert "1 artifact(s) processed" in result.output
            # Check that the lockfile was created with the correct name
            current_dir = Path.cwd()
            expected_lockfile = (
                current_dir / "output" / "test-production-1.0.0.conduit.lock.yaml"
            )
            assert expected_lockfile.exists(), "Lockfile was not created"

            # Load and verify the lockfile content
            lockfile_data = self.load_lockfile(expected_lockfile)

            # Verify the artifact target was templated correctly
            assert len(lockfile_data["artifacts"]) == 1
            artifact = lockfile_data["artifacts"][0]
            assert artifact["name"] == "config-file"
            assert str(artifact["origin"]).endswith("source.txt")
            assert artifact["target"] == "deploy/output.txt"
            assert artifact["action"] == "copy_local"
            assert artifact["type"] == "file"
            assert "checksum" in artifact
            assert "size" in artifact

    def test_multiple_variables_in_manifest(self):
        """Test templating with multiple variables affecting different parts of the manifest."""
        with self.runner.isolated_filesystem():
            # Create a source file
            source_content = "Multi-variable test content."
            self.create_test_file(source_content, ".", "app.conf")

            # Create a complex templated manifest
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: "{{ app_name }}"
  version: "{{ version }}"
artifacts:
  - name: "{{ app_name }}-config"
    origin: "app.conf"
    target: "{{ deploy_path }}/{{ app_name }}/config/{{ env }}.conf"
  - name: "{{ app_name }}-backup"
    origin: "app.conf"
    target: "{{ backup_path }}/{{ app_name }}-{{ version }}.backup"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "complex-manifest.yaml"
            )

            # Run the generate command with multiple template variables
            result = self.runner.invoke(
                lock,
                [
                    manifest_file,
                    "--var",
                    "app_name=myapp",
                    "--var",
                    "version=v1.2.3",
                    "--var",
                    "env=staging",
                    "--var",
                    "deploy_path=/opt/deploy",
                    "--var",
                    "backup_path=/var/backups",
                ],
            )

            # Check that the command succeeded
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "✓ Lock file generated:" in result.output
            assert "2 artifact(s) processed" in result.output

            # Check that the lockfile was created with the correct templated name
            current_dir = Path.cwd()
            expected_lockfile = current_dir / "output" / "myapp-1.2.3.conduit.lock.yaml"
            assert expected_lockfile.exists(), "Lockfile was not created"

            # Load and verify the lockfile content
            lockfile_data = self.load_lockfile(expected_lockfile)

            # Verify both artifacts were templated correctly
            assert len(lockfile_data["artifacts"]) == 2

            # Check first artifact
            config_artifact = next(
                a for a in lockfile_data["artifacts"] if a["name"] == "myapp-config"
            )
            assert str(config_artifact["origin"]).endswith("app.conf")
            assert config_artifact["target"] == "/opt/deploy/myapp/config/staging.conf"

            # Check second artifact
            backup_artifact = next(
                a for a in lockfile_data["artifacts"] if a["name"] == "myapp-backup"
            )
            assert str(backup_artifact["origin"]).endswith("app.conf")
            assert backup_artifact["target"] == "/var/backups/myapp-v1.2.3.backup"

    def test_no_templating_variables(self):
        """Test that the command works normally when no template variables are provided."""
        with self.runner.isolated_filesystem():
            # Create a source file
            source_content = "No templating test."
            self.create_test_file(source_content, ".", "plain.txt")

            # Create a regular manifest (no template variables)
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: plain-test
  version: 1.0.0
artifacts:
  - name: plain-file
    origin: plain.txt
    target: output.txt
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "plain-manifest.yaml"
            )

            # Run the generate command without template variables
            result = self.runner.invoke(lock, [manifest_file])

            # Check that the command succeeded
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Using template variables:" not in result.output
            assert "✓ Lock file generated:" in result.output
            assert "1 artifact(s) processed" in result.output

            # Check that the lockfile was created
            current_dir = Path.cwd()
            expected_lockfile = (
                current_dir / "output" / "plain-test-1.0.0.conduit.lock.yaml"
            )
            assert expected_lockfile.exists(), "Lockfile was not created"

    def test_malformed_variable_format(self):
        """Test error handling for malformed --var options."""
        with self.runner.isolated_filesystem():
            # Create a minimal manifest
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: test
  version: 1.0.0
artifacts: []
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "manifest.yaml"
            )

            # Test various malformed variable formats
            malformed_vars = [
                "noequals",  # Missing =
                "=nokey",  # Empty key
            ]

            for var in malformed_vars:
                result = self.runner.invoke(lock, [manifest_file, "--var", var])

                assert result.exit_code != 0, (
                    f"Command should have failed for var: {var}"
                )
                assert "Unexpected error:" in result.output

    def test_template_rendering_error(self):
        """Test error handling for Jinja2 template rendering errors."""
        with self.runner.isolated_filesystem():
            # Create a source file
            source_content = "Template error test."
            self.create_test_file(source_content, ".", "source.txt")

            # Create a manifest with invalid Jinja2 syntax
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: "{{ unclosed_template"
artifacts:
  - name: test
    origin: source.txt
    target: output.txt
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "bad-template.yaml"
            )

            # Run the generate command
            result = self.runner.invoke(lock, [manifest_file, "--var", "test=value"])

            # Check that the command failed with a template error
            assert result.exit_code != 0, (
                "Command should have failed due to template error"
            )
            assert "Unexpected error:" in result.output
            assert "Template rendering failed" in result.output

    def test_undefined_template_variable(self):
        """Test error handling when a template references an undefined variable."""
        with self.runner.isolated_filesystem():
            # Create a source file
            source_content = "Undefined variable test."
            self.create_test_file(source_content, ".", "source.txt")

            # Create a manifest that references an undefined variable
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: "test-{{ undefined_var }}"
  version: 1.0.0
artifacts:
  - name: test
    origin: source.txt
    target: output.txt
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "undefined-var.yaml"
            )

            # Run the generate command without providing the required variable
            result = self.runner.invoke(
                lock, [manifest_file, "--var", "other_var=value"]
            )

            # Check that the command failed due to undefined variable
            assert result.exit_code != 0, (
                "Command should have failed due to undefined variable"
            )
            assert "Unexpected error:" in result.output

    def test_special_characters_in_variables(self):
        """Test that special characters in variable values are handled correctly."""
        with self.runner.isolated_filesystem():
            # Create a source file
            source_content = "Special chars test."
            self.create_test_file(source_content, ".", "source.txt")

            # Create a templated manifest
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: "{{ project_name }}"
  version: 1.0.0
artifacts:
  - name: config
    origin: source.txt
    target: "{{ path }}/config.txt"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, ".", "special-chars.yaml"
            )

            # Run the generate command with special characters in variables
            result = self.runner.invoke(
                lock,
                [
                    manifest_file,
                    "--var",
                    "project_name=my-app_v1.0",
                    "--var",
                    "path=/opt/my-app/config",
                ],
            )

            # Check that the command succeeded
            assert result.exit_code == 0, f"Command failed: {result.output}"

            # Check that the lockfile was created
            current_dir = Path.cwd()
            expected_lockfile = (
                current_dir / "output" / "my-app_v1.0-1.0.0.conduit.lock.yaml"
            )
            assert expected_lockfile.exists(), "Lockfile was not created"

            # Verify the artifact target uses special characters correctly
            lockfile_data = self.load_lockfile(expected_lockfile)
            assert (
                lockfile_data["artifacts"][0]["target"]
                == "/opt/my-app/config/config.txt"
            )
