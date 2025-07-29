"""
Tests for the SchemaValidationService.

This test module validates that the JSON schema validation works correctly
for both manifest and lockfile data, ensuring proper error handling and
detailed error messages.
"""

from unittest.mock import Mock, patch

import pytest

from conduit.services.validation import SchemaValidationError, SchemaValidationService

from .conftest import API_VERSION


class TestSchemaValidationService:
    """Deprecated Test cases for SchemaValidationService."""

    def test_schema_validation_service_initialization(self):
        """Test that SchemaValidationService initializes correctly."""
        service = SchemaValidationService()
        assert service.manifest_schema is not None
        assert service.lockfile_schema is not None
        assert isinstance(service.manifest_schema, dict)
        assert isinstance(service.lockfile_schema, dict)

    def test_validate_valid_minimal_manifest(self):
        """Test validation of a minimal valid manifest."""
        service = SchemaValidationService()

        valid_manifest = {
            "apiVersion": API_VERSION,
            "kind": "Manifest",
            "metadata": {"name": "test-manifest", "version": "1.0.0"},
            "artifacts": [
                {
                    "name": "test-artifact",
                    "origin": "test_source.txt",  # String origin - inferred as file type
                    "target": "test_target.txt",  # String target - inferred as file type
                }
            ],
        }

        # Should not raise any exception
        service.validate_manifest(valid_manifest)

    def test_validate_valid_manifest_with_metadata(self):
        """Test validation of a manifest with metadata."""
        service = SchemaValidationService()

        valid_manifest = {
            "apiVersion": f"{API_VERSION}",
            "kind": "Manifest",
            "metadata": {"name": "test-manifest", "version": "1.0.0"},
            "artifacts": [
                {
                    "name": "test-artifact",
                    "origin": "test_source.txt",
                    "target": "test_target.txt",
                }
            ],
        }

        # Should not raise any exception
        service.validate_manifest(valid_manifest)

    def test_validate_valid_manifest_with_variables(self):
        """Test validation of a manifest with variables."""
        service = SchemaValidationService()

        valid_manifest = {
            "apiVersion": API_VERSION,
            "kind": "Manifest",
            "metadata": {"name": "test-manifest-with-variables", "version": "1.0.0"},
            "variables": {
                "project_name": "test-manifest-with-variables",
                "version": "1.0.0",
            },
            "artifacts": [
                {
                    "name": "test-artifact",
                    "origin": "test_source.txt",
                    "target": "test_target.txt",
                }
            ],
        }

        # Should not raise any exception
        service.validate_manifest(valid_manifest)

    def test_validate_invalid_manifest_missing_required_field(self):
        """Test validation fails for manifest missing required fields."""
        service = SchemaValidationService()

        invalid_manifest = {
            "apiVersion": f"{API_VERSION}",
            "kind": "Manifest",
            # Missing required 'metadata' and 'artifacts' fields
        }

        with pytest.raises(SchemaValidationError) as exc_info:
            service.validate_manifest(invalid_manifest)

        assert "Manifest validation failed" in str(exc_info.value)
        assert "'metadata' is a required property" in str(exc_info.value)

    def test_validate_invalid_manifest_wrong_api_version(self):
        """Test validation fails for manifest with wrong API version."""
        service = SchemaValidationService()

        invalid_manifest = {
            "apiVersion": "invalid/version",
            "kind": "Manifest",
            "artifacts": [
                {
                    "name": "test-artifact",
                    "origin": "test_source.txt",
                    "target": "test_target.txt",
                }
            ],
        }

        with pytest.raises(SchemaValidationError) as exc_info:
            service.validate_manifest(invalid_manifest)

        assert "No module named 'conduit.core.schemas.invalid/version'" in str(
            exc_info.value
        )

    def test_validate_invalid_manifest_empty_artifacts(self):
        """Test validation fails for manifest with empty artifacts array."""
        service = SchemaValidationService()

        invalid_manifest = {
            "apiVersion": f"{API_VERSION}",
            "kind": "Manifest",
            "artifacts": [],  # Empty array should fail minItems validation
        }

        with pytest.raises(SchemaValidationError) as exc_info:
            service.validate_manifest(invalid_manifest)

        assert "Manifest validation failed" in str(exc_info.value)

    def test_validate_valid_minimal_lockfile(self):
        """Test validation of a minimal valid lockfile."""
        service = SchemaValidationService()

        valid_lockfile = {
            "apiVersion": API_VERSION,
            "kind": "ManifestLock",
            "name": "test-lockfile",
            "version": "1.0.0",
            "manifestHash": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "artifacts": [
                {
                    "name": "test-artifact",
                    "type": "file",
                    "action": "copy_local",
                    "origin": "test_source.txt",
                    "target": "test_target.txt",
                    "checksum": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                    "size": 1024,
                }
            ],
        }

        # Should not raise any exception
        service.validate_lockfile(valid_lockfile)

    def test_validate_invalid_lockfile_missing_required_field(self):
        """Test validation fails for lockfile missing required fields."""
        service = SchemaValidationService()

        invalid_lockfile = {
            "apiVersion": f"{API_VERSION}",
            "kind": "ManifestLock",
            # Missing required 'manifestHash' and 'artifacts' fields
        }

        with pytest.raises(SchemaValidationError) as exc_info:
            service.validate_lockfile(invalid_lockfile)

        assert "Lockfile validation failed" in str(exc_info.value)

    def test_validate_invalid_lockfile_wrong_checksum_format(self):
        """Test validation fails for lockfile with wrong checksum format."""
        service = SchemaValidationService()

        invalid_lockfile = {
            "apiVersion": f"{API_VERSION}",
            "kind": "ManifestLock",
            "manifestHash": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "artifacts": [
                {
                    "name": "test-artifact",
                    "type": "file",
                    "action": "copy_local",
                    "origin": "test_source.txt",
                    "target": "test_target.txt",
                    "checksum": "invalid-checksum-format",  # Wrong format
                    "size": 1024,
                }
            ],
        }

        with pytest.raises(SchemaValidationError) as exc_info:
            service.validate_lockfile(invalid_lockfile)

        assert "Lockfile validation failed" in str(exc_info.value)

    def test_format_validation_error(self):
        """Test error message formatting."""
        service = SchemaValidationService()

        # Create a mock validation error
        mock_error = Mock()
        mock_error.absolute_path = ["artifacts", 0, "name"]
        mock_error.message = "'test' does not match pattern"
        mock_error.context = []

        formatted = service._format_validation_error(mock_error)
        assert "artifacts -> 0 -> name" in formatted
        assert "'test' does not match pattern" in formatted

    def test_format_validation_error_no_path(self):
        """Test error message formatting with no path."""
        service = SchemaValidationService()

        # Create a mock validation error with no path
        mock_error = Mock()
        mock_error.absolute_path = []
        mock_error.message = "Missing required property"
        mock_error.context = []

        formatted = service._format_validation_error(mock_error)
        assert "root" in formatted
        assert "Missing required property" in formatted

    @patch("conduit.services.validation.resources.read_text")
    def test_schema_loading_failure(self, mock_read_text):
        """Test that schema loading failures are handled properly."""
        mock_read_text.side_effect = Exception("Failed to load schema")

        with pytest.raises(SchemaValidationError) as exc_info:
            SchemaValidationService()

        assert "Failed to load schema" in str(exc_info.value)

    def test_validation_error_attributes(self):
        """Test that SchemaValidationError properly stores validation errors."""
        validation_errors = ["Error 1", "Error 2"]
        error = SchemaValidationError("Test message", validation_errors)

        assert str(error) == "Test message"
        assert error.validation_errors == validation_errors

    def test_validation_error_default_errors(self):
        """Test that SchemaValidationError handles default empty error list."""
        error = SchemaValidationError("Test message")

        assert str(error) == "Test message"
        assert error.validation_errors == []
