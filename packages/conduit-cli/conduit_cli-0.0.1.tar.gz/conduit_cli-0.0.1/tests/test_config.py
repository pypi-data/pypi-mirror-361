"""Test configuration system."""


import pytest
import yaml
from click.testing import CliRunner

from conduit.services.config import ConfigService
from conduit.services.validation import SchemaValidationService
from conduit.cli.main import main

from .conftest import API_VERSION


@pytest.fixture
def config_file(tmp_path):
    """Create a test config file."""
    config_path = tmp_path / "config.yaml"
    config_data = {
        "apiVersion": "conduit.warrical.com/next",
        "kind": "Config",
        "registry": {
            "default": "test.registry.io",
            "auth": {
                "test.registry.io": {"username": "testuser", "password": "testpass"}
            },
        },
        "sbom": {"enabled": True, "format": "spdx"},
    }
    config_path.write_text(yaml.dump(config_data))
    return config_path


@pytest.fixture
def env_vars(monkeypatch):
    """Set test environment variables."""
    monkeypatch.setenv("CONDUIT_REGISTRY_DEFAULT", "env.registry.io")
    monkeypatch.setenv("CONDUIT_SBOM_ENABLED", "false")


import os

def test_default_config(monkeypatch):
    """Test default configuration values."""
    monkeypatch.setenv("CONDUIT_REGISTRY_DEFAULT", "env.registry.io")
    monkeypatch.setenv("CONDUIT_SBOM_ENABLED", "false")

    # Use the new ConfigService
    config_service = ConfigService(validation_service=SchemaValidationService())
    config_data = config_service.list()

    # Check that environment variables take precedence
    assert config_data.get("registry.default") == "env.registry.io"
    assert config_data.get("sbom.enabled") is False


def test_load_config_from_file(config_file):
    """Test loading configuration from file."""
    config_service = ConfigService(
        config_file=config_file, validation_service=SchemaValidationService()
    )
    config_data = config_service.list()

    assert config_data.get("registry.default") == "test.registry.io"
    assert config_data.get("sbom.enabled") is True


def test_missing_config_file_returns_defaults():
    """Test that missing config file returns defaults."""
    config_service = ConfigService(validation_service=SchemaValidationService())
    config_data = config_service.list()

    # Should have schema defaults
    assert config_data.get("build.workers") == 4
    assert config_data.get("security.verify_signatures") is True
    assert config_data.get("logging.level") == "info"


def test_missing_config_file_returns_proper_xdg_defaults(monkeypatch):
    """Test that missing config file returns proper XDG defaults."""
    monkeypatch.setenv("XDG_DATA_HOME", "/tmp/test-data")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/test-config")
    monkeypatch.setenv("XDG_STATE_HOME", "/tmp/test-state")

    config_service = ConfigService(validation_service=SchemaValidationService())
    config_data = config_service.list()

    # Should have XDG defaults
    assert config_data.get("paths.data_dir") == "/tmp/test-data/conduit"
    assert config_data.get("paths.cache_dir") == "/tmp/test-data/conduit/cache"
    assert config_data.get("paths.config_dir") == "/tmp/test-config/conduit"
    assert config_data.get("paths.log_dir") == "/tmp/test-state/conduit"


def test_env_vars_override_config(config_file, env_vars):
    """Test environment variables override config file."""
    config_service = ConfigService(
        config_file=config_file, validation_service=SchemaValidationService()
    )
    config_data = config_service.list()

    assert config_data.get("registry.default") == "env.registry.io"  # env wins
    assert config_data.get("sbom.enabled") is False  # env wins
    assert config_data.get("sbom.format") == "spdx"  # from file


def test_env_vars_work_without_config(env_vars):
    """Test environment variables work without config file."""
    config_service = ConfigService(validation_service=SchemaValidationService())
    config_data = config_service.list()

    assert config_data.get("registry.default") == "env.registry.io"
    assert config_data.get("sbom.enabled") is False


@pytest.mark.parametrize(
    ("env_val", "expected"),
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
    ],
)
def test_env_var_boolean_conversion(monkeypatch, env_val, expected):
    """Test boolean environment variable conversion."""
    monkeypatch.setenv("CONDUIT_SBOM_ENABLED", env_val)
    config_service = ConfigService(validation_service=SchemaValidationService())
    config_data = config_service.list()
    assert config_data.get("sbom.enabled") == expected


def test_partial_config_merges_with_defaults(tmp_path):
    """Test partial config merges with defaults."""
    config_path = tmp_path / "partial.yaml"
    config_path.write_text(
        yaml.dump({
            "apiVersion": API_VERSION,
            "kind": "Config",
            "registry": {"default": "partial.io"},
        })
    )

    config_service = ConfigService(
        config_file=config_path, validation_service=SchemaValidationService()
    )
    config_data = config_service.list()

    assert config_data.get("registry.default") == "partial.io"  # from file
    assert config_data.get("build.workers") == 4  # default
    assert config_data.get("security.verify_signatures") is True  # default


def test_invalid_config_raises_error(tmp_path):
    """Test invalid config raises validation error."""
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        yaml.dump({
            "apiVersion": API_VERSION,
            "kind": "Config",
            "registry": {"default": 123},  # int not str
        })
    )

    with pytest.raises(Exception):  # Should raise validation error
        ConfigService(
            config_file=config_path, validation_service=SchemaValidationService()
        )

