"""
Tests for manifest variables functionality.

This module tests the implementation of variables in manifest files,
including variable merging between manifest and CLI sources.
"""

import pytest

from conduit.commands.lock import (
    LockError,
    load_manifest_from_file,
    merge_variables,
    parse_variables,
)


class TestVariableParsing:
    """Deprecated Test variable parsing from CLI options."""

    @pytest.mark.parametrize(
        ("var_options", "expected"),
        [
            (("key1=value1",), {"key1": "value1"}),
            (("env=prod", "version=1.2.3"), {"env": "prod", "version": "1.2.3"}),
            (("name=test app", "debug=true"), {"name": "test app", "debug": "true"}),
            ((), {}),
        ],
    )
    def test_parse_variables_success(self, var_options, expected):
        """Test successful variable parsing."""
        result = parse_variables(var_options)
        assert result == expected

    @pytest.mark.parametrize(
        "var_options",
        [("invalid",), ("key1=value1", "invalid"), ("=value",), ("key=",)],
    )
    def test_parse_variables_invalid_format(self, var_options):
        """Test parsing with invalid format raises GenerateError."""
        with pytest.raises(LockError):
            parse_variables(var_options)


class TestVariableMerging:
    """Test variable merging between manifest and CLI sources."""

    @pytest.mark.parametrize(
        ("manifest_vars", "cli_vars", "expected"),
        [
            (
                {"a": "1", "b": "2"},
                {"c": "3"},
                {"a": "1", "b": "2", "c": "3", "variables.a": "1", "variables.b": "2"},
            ),
            (
                {"a": "1", "b": "2"},
                {"b": "override", "c": "3"},
                {
                    "a": "1",
                    "variables.a": "1",
                    "b": "override",
                    "variables.b": "override",
                    "c": "3",
                },
                # {"a": "1", "b": "override", "c": "3"},
            ),
            ({"a": "1"}, None, {"a": "1", "variables.a": "1"}),
            (None, {"a": "1"}, {"a": "1"}),
            (None, None, {}),
            ({}, {}, {}),
        ],
    )
    def test_merge_variables(self, manifest_vars, cli_vars, expected):
        """Test variable merging with various combinations."""
        result = merge_variables(manifest_vars, cli_vars)
        assert result == expected


class TestManifestWithVariables:
    """Test loading manifests that contain variables sections."""

    def test_load_manifest_with_variables_only(self):
        """
        Test loading a manifest with variables section and template substitution.

        This test validates:
        - Manifest variables are parsed correctly
        - Template variables are substituted in artifact paths
        - The final manifest contains resolved paths
        """
        # Use the test manifest file with variables
        manifest_path = "tests/testfiles/test_manifest_with_variables.yaml"

        # Load manifest without CLI variables
        manifest = load_manifest_from_file(manifest_path)

        # Verify manifest variables are loaded
        assert manifest.variables is not None
        # Add explicit check for Pylance and runtime safety
        if manifest.variables:
            assert manifest.variables["project_name"] == "my-project"
            assert manifest.variables["version"] == "1.0.0"
            assert manifest.variables["environment"] == "dev"
        else:
            pytest.fail("manifest.variables should not be None for this test case")

        # Verify template substitution in artifacts
        assert len(manifest.artifacts) == 1
        artifact = manifest.artifacts[0]
        assert artifact.name == "config-file"
        assert artifact.origin == "test_source.txt"
        # Template should be resolved
        assert artifact.target == "output/my-project-1.0.0-dev.txt"

    def test_load_manifest_with_cli_variable_override(self):
        """
        Test loading manifest with CLI variables overriding manifest variables.

        This test validates:
        - CLI variables override manifest variables
        - Template substitution uses the overridden values
        - Both manifest and CLI variables are available
        """
        manifest_path = "tests/testfiles/test_manifest_with_variables.yaml"

        # CLI variables that override some manifest variables
        cli_variables = {"environment": "production", "new_var": "cli_value"}

        # Load manifest with CLI variable override
        manifest = load_manifest_from_file(manifest_path, cli_variables)

        # Verify artifact target uses overridden environment
        artifact = manifest.artifacts[0]
        assert artifact.target == "output/my-project-1.0.0-production.txt"

        # Verify variables contain both manifest and CLI variables
        assert manifest.variables is not None
        if manifest.variables:
            assert manifest.variables["project_name"] == "my-project"  # from manifest
            assert (
                manifest.variables["environment"] == "production"
            )  # overridden by CLI
            assert manifest.variables["new_var"] == "cli_value"  # from CLI only
        else:
            pytest.fail("manifest.variables should not be None for this test case")

    # Additional test cases that would be implemented:
    # def test_load_manifest_with_complex_template_expressions(self):
    #     """Test templates with complex Jinja2 expressions like loops and conditionals."""
    #     pass
    #
    # def test_load_manifest_with_missing_variable_error(self):
    #     """Test that undefined variables cause appropriate errors."""
    #     pass
    #
    # def test_load_manifest_with_nested_variable_references(self):
    #     """Test variables that reference other variables."""
    #     pass
    #
    # def test_variable_type_preservation(self):
    #     """Test that variable types (string, number, boolean) are preserved."""
    #     pass
    #
    # def test_backwards_compatibility_without_variables(self):
    #     """Test that manifests without variables section still work."""
    #     pass
