"""
Implementation of the `conduit pack` command.

This module implements the CLI command for creating OCI bundles from lock files,
using the Command Handler pattern with ORAS integration for registry operations.
"""

from typing import Optional

import click
from conduit.cli.context import ConduitContext
from ..handlers.pack import PackCommand, PackCommandHandler


class PackError(Exception):
    """Exception raised during pack operations."""

    pass


@click.command(hidden=True)
@click.argument("lockfile", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output bundle directory (default: auto-generated)",
)
@click.option(
    "--push", help="Push to registry after creating bundle (registry:tag format)"
)
@click.option(
    "--tag", default="latest", help="Tag for the bundle version (default: latest)"
)
@click.option(
    "--registry-username",
    help="Registry username (can also use CONDUIT_REGISTRY_USERNAME env var)",
)
@click.option(
    "--registry-password",
    help="Registry password (can also use CONDUIT_REGISTRY_PASSWORD env var)",
)
@click.option(
    "--insecure", is_flag=True, help="Allow insecure HTTP registry connections"
)
@click.pass_context
def pack(
    ctx,
    lockfile: str,
    output: Optional[str] = None,
    push: Optional[str] = None,
    tag: str = "latest",
    registry_username: Optional[str] = None,
    registry_password: Optional[str] = None,
    insecure: bool = False,
):
    """
    Create OCI bundle from a lock file.

    LOCKFILE is the path to the Conduit lock file (.lock.yaml).

    This command creates an OCI-compliant bundle containing all artifacts
    defined in the lock file. The bundle can be used for distribution,
    storage, or deployment to OCI-compatible registries.

    Examples:

        conduit pack myapp.lock.yaml

        conduit pack myapp.lock.yaml --output ./dist/myapp-bundle

        conduit pack myapp.lock.yaml --tag v1.2.3

        conduit pack myapp.lock.yaml --push ghcr.io/org/myapp:v1.0

        conduit pack myapp.lock.yaml --push localhost:8080/conduit/bundle:v1.0.0 --registry-username admin --insecure

        conduit pack myapp.lock.yaml --push localhost:8443/conduit/bundle:v1.0.0 --registry-username admin
    """
    try:
        click.echo(f"Loading lockfile from: {lockfile}")

        # Get config service from context
        cc: ConduitContext = ctx.obj if ctx.obj else ConduitContext()
        config_service = cc.config_service

        # Use config to provide defaults
        if config_service:
            config = config_service.config

            # If pushing and no explicit registry URL, use default from config
            # TODO: This is a hack and should not be present in production code
            if push and not any(
                push.startswith(prefix)
                for prefix in [
                    "http://",
                    "https://",
                    "localhost:",
                    "ghcr.io/",
                    "docker.io/",
                ]
            ):
                # push might be just ":tag" or "repo:tag"
                if config.registry.default:
                    # Prepend default registry if push doesn't look like a full URL
                    if push.startswith(":"):
                        # Just a tag like ":v1.0"
                        push = f"{config.registry.default}/conduit/bundle{push}"
                    elif "/" not in push:
                        # Just repo:tag like "myapp:v1.0"
                        push = f"{config.registry.default}/{push}"

            # Use auth from config if not provided via CLI
            if push and not registry_username and not registry_password:
                # Extract registry hostname from push URL
                registry_host = push.split("/")[0].split(":")[0]
                click.echo(f"Registry host: {registry_host}")

                # Check if we have auth for this registry
                if registry_host in config.registry.auth:
                    auth = config.registry.auth[registry_host]
                    registry_username = registry_username or auth.username
                    registry_password = registry_password or auth.password or auth.token

        # Handle registry authentication if pushing
        if push:
            # Prompt for password if username provided but password missing
            if registry_username and not registry_password:
                registry_password = click.prompt("Registry password", hide_input=True)

            # Validate registry URL format
            if not (":" in push and "/" in push):
                msg = "Registry URL must be in format 'host:port/repo:tag'"
                raise click.BadParameter(msg)

        # Progress callback for user feedback
        def progress_callback(progress_data):
            if isinstance(progress_data, dict):
                progress_type = progress_data.get("type", "")
                if progress_type == "pack_start":
                    click.echo(
                        progress_data.get("message", "Error: No message provided")
                    )
                elif progress_type == "bundle_exists":
                    click.echo(f"{progress_data['message']}")
                elif progress_type == "artifact_start":
                    click.echo(f"  Processing {progress_data['name']}... ", nl=False)
                elif (
                    progress_type == "artifact_progress"
                    and progress_data["status"] == "copying from cache"
                ):
                    click.echo("(from cache) ", nl=False)
                elif (
                    progress_type == "artifact_progress"
                    and progress_data["status"] == "downloading"
                ):
                    click.echo("(downloading) ", nl=False)
                elif progress_type == "artifact_complete":
                    click.echo("✓")
                elif progress_type == "download_complete":
                    click.echo(f"✓ {progress_data['message']}")
                elif progress_type == "push_start":
                    click.echo(f"🚀 Pushing bundle to {progress_data['registry']}")
                elif progress_type == "push_complete":
                    click.echo("✓ Bundle pushed successfully")
                    if progress_data.get("digest"):
                        click.echo(f"  Digest: {progress_data['digest']}")
                elif progress_type == "push_error":
                    click.echo(f"❌ Push failed: {progress_data['error']}", err=True)

        # Create pack command
        command = PackCommand(
            lockfile_path=lockfile,
            output_path=output or "./bundle",
            registry_ref=push,
            tag=tag,
            registry_username=registry_username,
            registry_password=registry_password,
            insecure=insecure,
        )

        # Execute pack operation using command handler
        pack_handler = PackCommandHandler()
        result = pack_handler.handle(command, progress_callback=progress_callback)

        click.echo("")
        click.echo(f"✓ OCI bundle created: {result.bundle_path}")
        click.echo(f"  - {result.layers_created} layers created")
        click.echo(f"  - {result.artifacts_bundled} artifacts bundled")
        if push:
            click.echo(f"✓ Bundle pushed to registry: {push}")
            click.echo("")

    except Exception as e:
        msg = f"Pack operation failed: {e}"
        raise PackError(msg) from e


if __name__ == "__main__":
    pack()
