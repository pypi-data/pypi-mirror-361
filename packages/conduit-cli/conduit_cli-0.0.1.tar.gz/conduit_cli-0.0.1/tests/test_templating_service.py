"""
Tests for templating service.

This module tests the TemplatingService that handles variable processing,
merging, and Jinja2 template rendering for Conduit manifests.
"""

import pytest

from src.conduit.services.templating import TemplatingService


class TestTemplatingService:
    """Deprecated Test class for TemplatingService functionality."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.service = TemplatingService()

    def test_parse_variables_valid_format(self):
        """Test parsing of properly formatted CLI variables."""
        var_options = ("key1=value1", "key2=value2", "key3=value3")

        result = self.service.parse_variables(var_options)

        expected = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert result == expected

    def test_parse_variables_empty_tuple(self):
        """Test parsing empty variable tuple."""
        result = self.service.parse_variables(())

        assert result == {}

    def test_parse_variables_with_equals_in_value(self):
        """Test parsing variables where value contains equals signs."""
        var_options = ("url=https://example.com/path?param=value",)

        result = self.service.parse_variables(var_options)

        assert result == {"url": "https://example.com/path?param=value"}

    def test_parse_variables_malformed_no_equals(self):
        """Test error handling for variables without equals sign."""
        var_options = ("malformed_variable",)

        with pytest.raises(Exception) as exc_info:
            self.service.parse_variables(var_options)

        assert "Invalid variable format" in str(exc_info.value)

    def test_parse_variables_empty_key(self):
        """Test error handling for empty variable key."""
        var_options = ("=value",)

        with pytest.raises(Exception) as exc_info:
            self.service.parse_variables(var_options)

        assert "Empty variable key" in str(exc_info.value)

    def test_parse_variables_empty_value(self):
        """Test error handling for empty variable value."""
        var_options = ("key=",)

        with pytest.raises(Exception) as exc_info:
            self.service.parse_variables(var_options)

        assert "Empty variable value" in str(exc_info.value)

    def test_merge_variables_manifest_only(self):
        """Test merging when only manifest variables are provided."""
        manifest_vars = {"key1": "value1", "key2": 42, "key3": True}
        cli_vars = None
        expected = {
            "key1": "value1",
            "variables.key1": "value1",
            "key2": 42,
            "variables.key2": 42,
            "key3": True,
            "variables.key3": True,
        }

        result = self.service.merge_variables(None, manifest_vars, cli_vars)

        assert result == expected

    def test_merge_variables_cli_only(self):
        """Test merging when only CLI variables are provided."""
        manifest_vars = None
        cli_vars = {"key1": "cli_value1", "key2": "cli_value2"}

        result = self.service.merge_variables(None, manifest_vars, cli_vars)

        assert result == cli_vars

    def test_merge_variables_both_provided(self):
        """Test merging when both manifest and CLI variables are provided."""
        manifest_vars = {
            "variables.key1": "manifest_value",
            "key1": "manifest_value",
            "key2": 42,
            "key3": True,
        }
        cli_vars = {"key1": "cli_value", "key4": "new_value"}

        result = self.service.merge_variables(None, manifest_vars, cli_vars)

        expected = {
            "key1": "cli_value",
            "key2": 42,
            "key3": True,
            "key4": "new_value",
            "variables.key1": "cli_value",
            "variables.key2": 42,
            "variables.key3": True,
            "variables.variables.key1": "manifest_value",
        }
        assert result == expected

    def test_merge_variables_both_none(self):
        """Test merging when both inputs are None."""
        result = self.service.merge_variables(None, None)

        assert result == {}

    def test_resolve_self_referencing_variables_simple(self):
        """Test resolving simple self-referencing variables."""
        variables = {
            "base_url": "https://example.com",
            "api_url": "{{.base_url}}/api",
            "health_url": "{{.api_url}}/health",
        }

        result = self.service.resolve_self_referencing_variables(variables)

        expected = {
            "base_url": "https://example.com",
            "api_url": "https://example.com/api",
            "health_url": "https://example.com/api/health",
        }
        assert result == expected

    def test_resolve_self_referencing_variables_no_references(self):
        """Test resolving variables with no self-references."""
        variables = {"key1": "value1", "key2": "value2", "key3": 42}

        result = self.service.resolve_self_referencing_variables(variables)

        assert result == variables

    def test_resolve_self_referencing_variables_empty_dict(self):
        """Test resolving empty variables dictionary."""
        result = self.service.resolve_self_referencing_variables({})

        assert result == {}

    def test_resolve_self_referencing_variables_none_input(self):
        """Test resolving None variables input."""
        result = self.service.resolve_self_referencing_variables(None)

        assert result is None

    def test_resolve_self_referencing_variables_circular_dependency(self):
        """Test error handling for circular dependencies."""
        variables = {"var1": "{{.var2}}", "var2": "{{.var1}}"}

        with pytest.raises(Exception) as exc_info:
            self.service.resolve_self_referencing_variables(variables)

        assert "Circular" in str(exc_info.value)

    def test_resolve_self_referencing_variables_undefined_reference(self):
        """Test error handling for undefined variable references."""
        variables = {"var1": "{{.undefined_var}}"}

        with pytest.raises(Exception) as exc_info:
            self.service.resolve_self_referencing_variables(variables)

        assert "Undefined variable reference" in str(exc_info.value)

    def test_render_template_simple(self):
        """Test simple template rendering."""
        template_content = "Hello {{name}}, welcome to {{project}}!"
        variables = {"name": "Alice", "project": "Conduit"}

        result = self.service.render_template(template_content, variables)

        assert result == "Hello Alice, welcome to Conduit!"

    def test_render_template_with_variables_namespace(self):
        """Test template rendering using variables namespace."""
        template_content = (
            "Project: {{variables.project}}, Version: {{variables.version}}"
        )
        variables = {"project": "Conduit", "version": "1.0.0"}

        result = self.service.render_template(template_content, variables)

        assert result == "Project: Conduit, Version: 1.0.0"

    def test_render_template_no_variables(self):
        """Test template rendering with no variables."""
        template_content = "Static content with no templates"
        variables = {}

        result = self.service.render_template(template_content, variables)

        assert result == template_content

    def test_render_template_undefined_variable(self):
        """Test error handling for undefined template variables."""
        template_content = "Hello {{undefined_var}}!"
        variables = {"name": "Alice"}

        with pytest.raises(Exception) as exc_info:
            self.service.render_template(template_content, variables)

        assert "Template rendering failed" in str(exc_info.value)

    def test_render_template_invalid_syntax(self):
        """Test error handling for invalid template syntax."""
        template_content = "Hello {{unclosed_template"
        variables = {"name": "Alice"}

        with pytest.raises(Exception) as exc_info:
            self.service.render_template(template_content, variables)

        assert "Template rendering failed" in str(exc_info.value)

    def test_process_manifest_variables_full_workflow(self):
        """Test the complete workflow of processing manifest variables."""
        # Test the workflow: merge first, then resolve self-references
        manifest_vars = {
            "env": "dev",
            "base_url": "https://{{.env}}.example.com",
            "api_url": "{{.base_url}}/api",
        }
        cli_variables = {"env": "production"}

        # Step 1: Merge CLI variables with manifest variables first
        merged_vars = self.service.merge_variables(None, manifest_vars, cli_variables)

        # Step 2: Then resolve self-referencing variables in the merged result
        final_vars = self.service.resolve_self_referencing_variables(merged_vars) or {}

        # Step 3: Render template with final variables
        template_content = """artifacts:
- name: config
  origin: config.txt
  target: {{variables.env}}/config.txt
variables:
  api_url: {{variables.api_url}}
  base_url: {{variables.base_url}}
  env: {{variables.env}}
"""

        rendered_content = self.service.render_template(template_content, final_vars)

        # Verify the complete workflow worked
        assert "production" in rendered_content
        assert "https://production.example.com" in rendered_content

        # Verify that CLI variable overrode manifest variable
        assert final_vars["env"] == "production"

        # Verify that self-references were resolved with the merged values
        assert final_vars["base_url"] == "https://production.example.com"
        assert final_vars["api_url"] == "https://production.example.com/api"

    def test_service_consistency(self):
        """Test that service methods return consistent results."""
        var_options = ("key=value",)

        result1 = self.service.parse_variables(var_options)
        result2 = self.service.parse_variables(var_options)

        assert result1 == result2

        variables = {"key": "value"}

        result3 = self.service.merge_variables(None, variables, None)
        result4 = self.service.merge_variables(None, variables, None)

        assert result3 == result4
