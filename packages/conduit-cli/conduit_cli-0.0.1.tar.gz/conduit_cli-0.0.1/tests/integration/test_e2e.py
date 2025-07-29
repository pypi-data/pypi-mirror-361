"""
Test the bundle command from start to finish.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from conduit.commands.legacy import create
from conduit.commands.unpack import unpack as fetch

from ..conftest import API_VERSION

BUNDLE_NAME = "proxy-manager"
BUNDLE_DIR_NAME = f"{BUNDLE_NAME}-bundle"
BUNDLE_VERSION = "1.0.0"
BUNDLE_FILE_NAME = f"{BUNDLE_NAME}.yaml"
LATEST_NGINX_VERSION = "2.12.3"
OLDEST_NGINX_VERSION = "2.1.0"
LATEST_VERSION = "2.0.0"

BUNDLE_REGISTRY_URL = (
    f"localhost:8080/integration-test-registry/{BUNDLE_NAME}:{LATEST_VERSION}"
)
BUNDLE_OCI_REGISTRY_URL = f"oci://{BUNDLE_REGISTRY_URL}"


LATEST_MARIADB_VERSION = "10.11.5"
OLDEST_MARIADB_VERSION = "10.4.15"


@pytest.fixture
def bundle_file(tmp_path, entrypoint_file):
    bundle_content = (
        "apiVersion: "
        + API_VERSION
        + f"""
kind: Manifest
metadata:
    name: {BUNDLE_NAME}
    version: {BUNDLE_VERSION}
    description: "A bundle for using a reverse proxy with a UI on the system"
"""
        + f"""
variables:
    nginx_version: {OLDEST_NGINX_VERSION}
    mariadb_version: {OLDEST_MARIADB_VERSION}
"""
        + f"""
entrypoint: {entrypoint_file!s}
"""
        + """
artifacts:
    - name: nginx-proxy-manager-{{metadata.version}}-{{variables.nginx_version}}
      origin: oci://docker.io/jc21/nginx-proxy-manager:{{variables.nginx_version}}
      target: nginx-proxy-manager-{{metadata.version}}-{{variables.nginx_version}}.tar
    - name: mariadb-aria-{{metadata.version}}-{{variables.mariadb_version}}
      origin: oci://docker.io/jc21/mariadb-aria:{{variables.mariadb_version}}
      target: mariadb-aria-{{metadata.version}}-{{variables.mariadb_version}}.tar
"""
    )
    bundle_file = tmp_path / BUNDLE_FILE_NAME
    bundle_file.write_text(bundle_content)
    return bundle_file


@pytest.fixture
def entrypoint_file(tmp_path):
    entrypoint_content = """
    #!/bin/bash
    echo "Hello, world!" >> hello_world.txt
    """
    entrypoint_file = tmp_path / "some_kind_of_entrypoint.sh"
    entrypoint_file.write_text(entrypoint_content)
    entrypoint_file.chmod(0o755)
    return entrypoint_file


@pytest.fixture
def env(tmp_path):
    # Mapping of the environment variables to use for the integration tests
    return {
        "CONDUIT_REGISTRY_USER": "admin",
        "CONDUIT_REGISTRY_PASSWORD": "qazesxXSEZAQ1234",
        "CONDUIT_DATA_DIR": str(tmp_path / "data" / "conduit"),
        "CONDUIT_CACHE_DIR": str(tmp_path / "data" / "conduit" / "cache"),
        "CONDUIT_LOG_DIR": str(tmp_path / "var" / "logs" / "conduit"),
    }


@pytest.fixture
def runner(env):
    return CliRunner(env=env, echo_stdin=True)


@pytest.fixture
def create_args(bundle_file: Path):
    # conduit bundle create <bundle_file> --var
    return [
        str(bundle_file),
        "--var",
        f"metadata.version={LATEST_VERSION}",
        "--var",
        f"nginx_version={LATEST_NGINX_VERSION}",
        "--var",
        f"mariadb_version={LATEST_MARIADB_VERSION}",
        "--push",
        BUNDLE_REGISTRY_URL,
        "--tag",
        f"{LATEST_VERSION}",
        "--insecure",
    ]


@pytest.mark.slow
def test_run_e2w(bundle_file, env, runner, capsys, create_args, tmp_path):
    with capsys.disabled(), runner.isolated_filesystem(temp_dir=tmp_path):
        current_dir = Path.cwd()

        # Create the bundle
        create_results = runner.invoke(create, create_args)
        # Verify the bundle was created
        assert create_results.exit_code == 0
        assert "Bundle pushed successfully" in create_results.output
        assert Path(current_dir / BUNDLE_DIR_NAME).exists()

        # Fetch the bundle
        fetch_args = [
            BUNDLE_OCI_REGISTRY_URL,
            "--output",
            str(current_dir / "extracted"),
            "--insecure",
        ]
        fetch_results = runner.invoke(fetch, fetch_args)
        # Verify the bundle was unpacked
        assert fetch_results.exit_code == 0
            # assert "Bundle unpacked successfully" in create_results.output
