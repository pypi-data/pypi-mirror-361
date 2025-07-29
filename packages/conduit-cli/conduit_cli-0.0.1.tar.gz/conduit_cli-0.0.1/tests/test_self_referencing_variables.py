"""
Tests for self-referencing variables functionality.

This module tests the implementation of self-referencing variables using {{.variable_key}} syntax
within manifest variable sections, including resolution order, circular dependency detection,
and interaction with CLI variable overrides.
"""

import pytest

from conduit.commands.lock import (
    LockError,
    load_manifest_from_file,
    resolve_self_referencing_variables,
)


class TestSelfReferencingVariableResolution:
    """
    Deprecated Test the core self-referencing variable resolution functionality.

    Additional test scenarios to implement:
    - Complex chain references (a -> b -> c -> d)
    - Self-reference combined with regular template variables
    - Variables that are numbers, booleans, objects (should not be processed)
    - Partial self-references mixed with literal text
    - Case sensitivity in variable references
    - Special characters in variable names
    - Empty string self-references
    - Multiple self-references within a single variable value
    """

    @pytest.mark.parametrize(
        ("variables", "expected"),
        [
            # Simple self-reference
            (
                {"base": "hello", "full": "{{.base}}-world"},
                {"base": "hello", "full": "hello-world"},
            ),
            # Chain references
            (
                {"a": "start", "b": "{{.a}}-middle", "c": "{{.b}}-end"},
                {"a": "start", "b": "start-middle", "c": "start-middle-end"},
            ),
            # Multiple references in one variable
            (
                {"name": "app", "version": "1.0", "full": "{{.name}}-v{{.version}}"},
                {"name": "app", "version": "1.0", "full": "app-v1.0"},
            ),
            # Mixed types (non-strings should not be processed)
            (
                {
                    "str_var": "text",
                    "num_var": 42,
                    "bool_var": True,
                    "ref_var": "{{.str_var}}-suffix",
                },
                {
                    "str_var": "text",
                    "num_var": 42,
                    "bool_var": True,
                    "ref_var": "text-suffix",
                },
            ),
            # Numeric reference converted to string
            ({"version": 123, "tag": "v{{.version}}"}, {"version": 123, "tag": "v123"}),
            # No self-references (should pass through unchanged)
            ({"a": "hello", "b": "world"}, {"a": "hello", "b": "world"}),
            # Empty variables dict
            ({}, {}),
        ],
    )
    def test_resolve_self_referencing_variables_success(self, variables, expected):
        """Test successful self-referencing variable resolution."""
        result = resolve_self_referencing_variables(variables)
        assert result == expected

    def test_resolve_none_variables(self):
        """Test handling of None variables input."""
        result = resolve_self_referencing_variables(None)
        assert result is None


class TestManifestWithSelfReferencingVariables:
    """
    Test loading manifests with self-referencing variables.

    Additional test scenarios to implement:
    - Self-referencing variables with CLI override interactions
    - Complex manifest with mixed self-references and regular template variables
    - Manifest with self-references in metadata and artifacts sections
    - Performance testing with deep variable chains
    - Unicode and special characters in self-referenced variables
    - Self-references combined with Jinja2 filters and functions
    - Nested object/array variables with string values containing self-references
    """

    def test_load_manifest_with_self_referencing_variables(self):
        """
        Test loading a manifest with self-referencing variables.

        This test validates:
        - Self-references are resolved before template rendering
        - Chain references work correctly (base -> full -> complex)
        - Final artifact paths use the resolved variables
        - The resolved variables are available in the final manifest
        """
        # Use the test manifest file with self-referencing variables
        manifest_path = "tests/testfiles/test_self_referencing_variables.yaml"

        # Load manifest with self-referencing variables
        manifest = load_manifest_from_file(manifest_path)

        # Verify self-references are resolved
        assert manifest.variables is not None
        # Add explicit check for Pylance and runtime safety
        if manifest.variables:
            assert manifest.variables["base_name"] == "my-project"
            assert manifest.variables["version"] == "1.0.0"
            assert manifest.variables["environment"] == "dev"

            # Check resolved chain references
            assert manifest.variables["full_name"] == "my-project-v1.0.0"
            assert manifest.variables["config_file"] == "my-project-v1.0.0-dev.yaml"
            assert (
                manifest.variables["complex_path"]
                == "output/my-project-v1.0.0-dev.yaml"
            )
        else:
            pytest.fail("manifest.variables should not be None for this test case")

        # Verify final artifact uses the resolved path
        assert len(manifest.artifacts) == 1
        artifact = manifest.artifacts[0]
        assert artifact.name == "config-file"
        assert artifact.origin == "test_source.txt"
        # The template should use the resolved complex_path variable
        assert artifact.target == "output/my-project-v1.0.0-dev.yaml"

    def test_load_manifest_with_cli_override_and_self_references(self):
        """
        Test CLI variables overriding self-referencing variables.

        This test validates:
        - CLI variables can override base variables used in self-references
        - Chain reactions work when base variables are overridden
        - Final resolved values reflect the CLI overrides
        """
        manifest_path = "tests/testfiles/test_self_referencing_variables.yaml"

        # Override base variables that are used in self-references
        cli_variables = {"base_name": "overridden-project", "environment": "production"}

        # Load manifest with CLI overrides
        manifest = load_manifest_from_file(manifest_path, cli_variables)

        # Verify CLI overrides are applied
        assert manifest.variables is not None
        if manifest.variables:
            assert manifest.variables["base_name"] == "overridden-project"
            assert manifest.variables["environment"] == "production"

            # Verify chain reactions - self-references should use the CLI overridden values
            # Note: CLI overrides happen BEFORE self-reference resolution (correct behavior)
            assert (
                manifest.variables["full_name"] == "overridden-project-v1.0.0"
            )  # resolved with CLI override
            assert (
                manifest.variables["config_file"]
                == "overridden-project-v1.0.0-production.yaml"
            )  # resolved with CLI override
        else:
            pytest.fail("manifest.variables should not be None for this test case")

        # Final artifact should use the template rendering with CLI overrides
        artifact = manifest.artifacts[0]
        # This will depend on which variables are actually used in the final template
        assert "output/" in artifact.target

    def test_load_manifest_with_circular_dependency_error(self):
        """
        Test that circular dependencies in manifest variables cause appropriate errors.

        This test validates:
        - Circular dependencies are detected during manifest loading
        - Clear error messages are provided
        - The error prevents further processing
        """
        manifest_path = "tests/testfiles/test_circular_dependency.yaml"

        # Loading should fail due to circular dependency
        with pytest.raises(LockError) as exc_info:
            load_manifest_from_file(manifest_path)

        # Verify the error message indicates circular dependency
        error_message = str(exc_info.value)
        assert (
            "Circular dependency detected" in error_message
            or "Circular reference detected" in error_message
        )

    # Additional test cases that would be implemented:
    # def test_self_references_with_complex_jinja2_expressions(self):
    #     """Test self-references combined with Jinja2 filters and functions."""
    #     pass
    #
    # def test_performance_with_deep_variable_chains(self):
    #     """Test performance with very deep chains of variable references."""
    #     pass
    #
    # def test_self_references_with_unicode_characters(self):
    #     """Test self-references work correctly with Unicode variable names and values."""
    #     pass
    #
    # def test_backwards_compatibility_without_self_references(self):
    #     """Test that manifests without self-references continue to work unchanged."""
    #     pass
