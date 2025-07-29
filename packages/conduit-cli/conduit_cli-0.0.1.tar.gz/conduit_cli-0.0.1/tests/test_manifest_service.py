"""
Tests for manifest service.

This module tests the ManifestService that handles manifest loading,
validation, and processing for Conduit workflows.
"""

import os
import tempfile

import pytest

from src.conduit.core.models import Manifest
from src.conduit.services.manifest import ManifestService
from src.conduit.services.templating import TemplatingService

from .conftest import API_VERSION


class TestManifestService:
    """Deprecated Test class for ManifestService functionality."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.service = ManifestService()
        self.templating_service = TemplatingService()

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

    def test_load_manifest_from_file_simple(self):
        """Test loading a simple manifest without templating."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: simple-test
  version: 1.0.0
artifacts:
  - name: test-file
    origin: input.txt
    target: output.txt
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.conduit.yaml"
            )

            manifest = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )

            assert isinstance(manifest, Manifest)
            assert manifest.metadata.name == "simple-test"
            assert len(manifest.artifacts) == 1
            assert manifest.artifacts[0].name == "test-file"
            assert manifest.artifacts[0].origin == "input.txt"
            assert manifest.artifacts[0].target == "output.txt"

    def test_load_manifest_from_file_with_variables(self):
        """Test loading manifest with variables section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: variables-test
  version: 1.0.0
variables:
  env: development
  project: myapp
artifacts:
  - name: config-file
    origin: config.txt
    target: "{{variables.env}}/{{variables.project}}/config.txt"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.conduit.yaml"
            )

            manifest = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )

            assert manifest.metadata.name == "variables-test"
            assert manifest.variables, "Variables should not be empty"
            assert manifest.variables["env"] == "development"
            assert manifest.variables["project"] == "myapp"
            assert manifest.artifacts[0].target == "development/myapp/config.txt"

    def test_load_manifest_from_file_with_cli_variables(self):
        """Test loading manifest with CLI variable overrides."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # TODO: The variable resolution is only about 1 level deep for the self referencing variables (e.g. variables and metadata keys when referring to other variables in the same section)
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: cli-vars-test
  version: 1.0.0
variables:
  version: "1.0.0"
  splash:
    text: "Hello, World!"
  splash_version: "{{.version}}"
artifacts:
  - name: app-file-v{{variables.version}}
    origin: app.jar
    target: "deploy/{{variables.env}}/app-{{metadata.insert}}-{{metadata.version}}.jar"
  - name: splash-file-{{variables.splash_version}}
    origin: splash.{{metadata.insert}}.txt
    target: "{{variables.splash.text}}"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.conduit.yaml"
            )
            cli_variables = {
                "env": "production",
                "version": "2.0.0",
                "metadata.version": "3.0.0",
                "metadata.insert": "test",
            }

            manifest = self.service.load_manifest_from_file(
                manifest_file, self.templating_service, cli_variables
            )

            assert manifest, "Manifest should not be None"
            assert manifest.metadata, "Metadata should not be empty"
            assert manifest.variables, "Variables should not be empty"
            assert manifest.variables["env"] == "production", (
                "Env should have been set through the cli variables"
            )
            assert (
                manifest.variables["metadata.insert"]
                == cli_variables["metadata.insert"]
            ), (
                "Insert should have been set through the cli variables even though it is a metadata key"
            )
            assert manifest.variables["version"] == "2.0.0", (
                "Version should have been set through the cli variables"
            )
            assert manifest.variables["splash_version"] == "2.0.0", (
                "Splash version should have been set through the cli variables"
            )
            assert manifest.metadata.version == "3.0.0", (
                "Metadata version should have been set through the cli variables"
            )
            assert manifest.metadata.version != manifest.variables.get("version"), (
                "Metadata version should be different from the variables version"
            )
            assert (
                manifest.artifacts[0].name
                == f"app-file-v{manifest.variables.get('version')}"
            )
            assert (
                manifest.artifacts[0].target
                == f"deploy/{manifest.variables.get('env')}/app-test-{manifest.metadata.version}.jar"
            )
            assert (
                manifest.artifacts[1].name
                == f"splash-file-{manifest.variables.get('splash_version')}"
            ), "Splash file name should have been set by resolving the version variable"
            assert manifest.artifacts[1].target == "Hello, World!"
            assert (
                manifest.artifacts[1].origin
                == f"splash.{cli_variables['metadata.insert']}.txt"
            )

    def test_load_manifest_from_file_self_referencing_variables(self):
        """Test loading manifest with self-referencing variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: self-ref-test
  version: 1.0.0
variables:
  env: staging
  base_url: "https://{{.env}}.example.com"
  api_url: "{{.base_url}}/api"
artifacts:
  - name: config
    origin: config.json
    target: "{{variables.env}}/config.json"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "manifest.conduit.yaml"
            )

            manifest = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )

            assert manifest, "Manifest should not be None"
            assert manifest.variables, "Variables should not be empty"
            assert manifest.variables["env"] == "staging"
            assert manifest.variables["base_url"] == "https://staging.example.com"
            assert manifest.variables["api_url"] == "https://staging.example.com/api"
            assert manifest.artifacts[0].target == "staging/config.json"

    def test_load_manifest_from_file_nonexistent(self):
        """Test error handling for nonexistent manifest file."""
        with pytest.raises(Exception) as exc_info:
            self.service.load_manifest_from_file(
                "/nonexistent/manifest.yaml", self.templating_service
            )

        assert "not found" in str(exc_info.value).lower()

    def test_load_manifest_from_file_invalid_yaml(self):
        """Test error handling for invalid YAML syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_yaml = f"""apiVersion: {API_VERSION}
kind: Manifest
  invalid: yaml: structure
  - missing: proper indentation
"""
            manifest_file = self.create_test_file(
                invalid_yaml, temp_dir, "invalid.conduit.yaml"
            )

            with pytest.raises(Exception) as exc_info:
                self.service.load_manifest_from_file(
                    manifest_file, self.templating_service
                )

            assert (
                "yaml" in str(exc_info.value).lower()
                or "syntax" in str(exc_info.value).lower()
            )

    def test_load_manifest_from_file_invalid_structure(self):
        """Test error handling for manifests with invalid structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_manifest = """apiVersion: wrong/version
kind: WrongKind
metadata:
  name: invalid-test
  version: 1.0.0
"""
            manifest_file = self.create_test_file(
                invalid_manifest, temp_dir, "invalid-structure.conduit.yaml"
            )

            with pytest.raises(Exception) as exc_info:
                self.service.load_manifest_from_file(
                    manifest_file, self.templating_service
                )

            assert (
                "validation" in str(exc_info.value).lower()
                or "invalid" in str(exc_info.value).lower()
            )

    def test_load_manifest_from_file_empty_file(self):
        """Test error handling for empty manifest file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_file = self.create_test_file("", temp_dir, "empty.conduit.yaml")

            with pytest.raises(Exception) as exc_info:
                self.service.load_manifest_from_file(
                    manifest_file, self.templating_service
                )

            assert "empty" in str(exc_info.value).lower()

    def test_load_manifest_from_file_template_error(self):
        """Test error handling for template rendering errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: template-error-test
  version: 1.0.0
artifacts:
  - name: test
    origin: input.txt
    target: "{{undefined_variable}}/output.txt"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "template-error.conduit.yaml"
            )

            with pytest.raises(Exception) as exc_info:
                self.service.load_manifest_from_file(
                    manifest_file, self.templating_service
                )

            assert (
                "template" in str(exc_info.value).lower()
                or "undefined" in str(exc_info.value).lower()
            )

    def test_load_manifest_from_file_circular_variables(self):
        """Test error handling for circular variable dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: circular-test
  version: 1.0.0
variables:
  var1: "{{.var2}}"
  var2: "{{.var1}}"
artifacts:
  - name: test
    origin: input.txt
    target: output.txt
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "circular.conduit.yaml"
            )

            with pytest.raises(Exception) as exc_info:
                self.service.load_manifest_from_file(
                    manifest_file, self.templating_service
                )

            assert "circular" in str(exc_info.value).lower()

    def test_load_manifest_from_file_no_variables_no_templating(self):
        """Test loading manifest without variables section and no templating."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: no-vars-test
  version: 1.0.0
artifacts:
  - name: simple-file
    origin: source.txt
    target: dest.txt
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "no-vars.conduit.yaml"
            )

            manifest = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )

            assert manifest.metadata.name == "no-vars-test"
            assert manifest.variables == {}
            assert len(manifest.artifacts) == 1

    def test_load_manifest_from_file_consistency(self):
        """Test that loading the same manifest multiple times produces consistent results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: consistency-test
  version: 1.0.0
variables:
  value: consistent
artifacts:
  - name: test-file
    origin: "{{variables.value}}.txt"
    target: "output-{{variables.value}}.txt"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "consistency.conduit.yaml"
            )

            manifest1 = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )
            manifest2 = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )

            # Results should be identical
            assert manifest1.metadata.name == manifest2.metadata.name
            assert manifest1.variables == manifest2.variables
            assert len(manifest1.artifacts) == len(manifest2.artifacts)
            assert manifest1.artifacts[0].origin == manifest2.artifacts[0].origin
            assert manifest1.artifacts[0].target == manifest2.artifacts[0].target

    def test_service_integration_with_templating_service(self):
        """Test that manifest service properly integrates with templating service."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_content = (
                "apiVersion: "
                + API_VERSION
                + """
kind: Manifest
metadata:
  name: integration-test
  version: 1.0.0
variables:
  component: database
  env: "{{.component}}-staging"
  config_path: "/etc/{{.component}}/{{.env}}"
artifacts:
  - name: db-config
    origin: "configs/{{variables.component}}.yaml"
    target: "{{variables.config_path}}/config.yaml"
"""
            )
            manifest_file = self.create_test_file(
                manifest_content, temp_dir, "integration.conduit.yaml"
            )

            manifest = self.service.load_manifest_from_file(
                manifest_file, self.templating_service
            )

            # Verify complex variable resolution worked
            assert manifest.variables, "Variables should not be empty"
            assert manifest.variables["component"] == "database", (
                "Component variable should be 'database'"
            )
            assert manifest.variables["env"] == "database-staging", (
                "Env variable should be 'database-staging'"
            )
            assert (
                manifest.variables["config_path"] == "/etc/database/database-staging"
            ), "Config path variable should be '/etc/database/database-staging'"
            assert manifest.artifacts[0].origin == "configs/database.yaml", (
                "Origin should resolve to 'configs/database.yaml'"
            )
            assert (
                manifest.artifacts[0].target
                == "/etc/database/database-staging/config.yaml"
            ), "Target should resolve to '/etc/database/database-staging/config.yaml'"
