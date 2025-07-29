"""
Implementation of the `conduit generate` command with Jinja2 templating support.

This module implements the CLI command for generating lock files from manifest files,
focusing on simple local file-to-file copy operations with templating capability.
"""

import asyncio
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import click

from ..cli.progress import ProgressDisplay, create_progress_callback
from ..core.models import Manifest
from ..services.lock import LockService
from ..services.manifest import ManifestError, ManifestService
from ..services.templating import TemplatingError, TemplatingService


def deprecated(reason: Optional[str] = None, version: Optional[str] = None):
    def decorator(func):
        message = f"{func.__name__} is deprecated"
        message += (
            f" since version {version} and may be removed in the future"
            if version
            else " and may be removed in the future"
        )
        message += f" | {reason}" if reason else "."

        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class LockError(Exception):
    """Exception raised during the generate process."""

    pass


@deprecated("Use TemplatingService.parse_variables directly instead")
def parse_variables(var_options: Tuple[str, ...]) -> Dict[str, str]:
    """
    Parse --var key=value options into a dictionary.

    Args:
        var_options: Tuple of "key=value" strings from CLI options

    Returns:
        Dictionary of parsed variables

    Raises:
        LockError: If any variable is malformed
    """
    # Delegate to TemplatingService for the actual implementation
    try:
        templating_service = TemplatingService()
        return templating_service.parse_variables(var_options)
    except TemplatingError as e:
        # Convert TemplatingError to LockError for backward compatibility
        raise LockError(str(e)) from e


@deprecated("Use TemplatingService.merge_variables instead")
def merge_variables(
    manifest_variables: Optional[Dict[str, Any]],
    cli_variables: Optional[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Merge manifest variables with CLI variables, with CLI variables taking precedence.

    Args:
        manifest_variables: Variables defined in the manifest
        cli_variables: Variables provided via CLI options

    Returns:
        Merged dictionary of variables
    """
    # Delegate to TemplatingService for the actual implementation
    templating_service = TemplatingService()
    return templating_service.merge_variables(
        manifest_variables=manifest_variables, parsed_cli_options=cli_variables
    )


@deprecated(
    "Use TemplatingService.resolve_self_referencing_variables direcltly instead"
)
def resolve_self_referencing_variables(
    variables: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Resolve self-referencing variables using {{.variable_key}} syntax.

    Variables can reference other variables within the same variables section using
    the {{.variable_key}} syntax. This function iteratively resolves these references
    while detecting circular dependencies.

    Args:
        variables: Dictionary of variables that may contain self-references, or None

    Returns:
        Dictionary with all self-references resolved, or None if input was None

    Raises:
        LockError: If circular dependencies are detected or undefined variables are referenced
    """
    # Delegate to TemplatingService for the actual implementation
    try:
        templating_service = TemplatingService()
        return templating_service.resolve_self_referencing_variables(variables)
    except TemplatingError as e:
        # Convert TemplatingError to LockError for backward compatibility
        raise LockError(str(e)) from e


@deprecated("Use ManifestService.load_manifest_from_file directly instead")
def load_manifest_from_file(
    manifest_path: str, cli_variables: Optional[Dict[str, str]] = None
) -> Manifest:
    """
    Load and validate a manifest from a YAML file, with optional Jinja2 templating.

    Args:
        manifest_path: Path to the manifest YAML file
        cli_variables: Optional dictionary of CLI variables for template rendering

    Returns:
        Parsed and validated Manifest model

    Raises:
        LockError: If the manifest cannot be loaded or validated
    """
    # Delegate to ManifestService for the actual implementation
    try:
        templating_service = TemplatingService()
        manifest_service = ManifestService()
        return manifest_service.load_manifest_from_file(
            manifest_path, templating_service, cli_variables
        )
    except ManifestError as e:
        # Convert ManifestError to LockError for backward compatibility
        raise LockError(str(e)) from e


@click.command(hidden=True)
@click.argument(
    "manifest_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output lockfile path (default: auto-generated)",
)
@click.option(
    "--var",
    "-v",
    multiple=True,
    help="Template variable in key=value format (can be used multiple times)",
)
@click.option(
    "--no-progress", is_flag=True, help="Disable progress display for HTTP downloads"
)
@click.pass_context
def lock(
    ctx,
    manifest_file: str,
    output: Optional[str] = None,
    var: Tuple[str, ...] = (),
    no_progress: bool = False,
):
    """
    Generate a lock file from a manifest file with optional Jinja2 templating.

    MANIFEST_FILE is the path to the Conduit manifest YAML file.

    Variables can be defined in the manifest under a 'variables' section and/or
    provided via CLI options. CLI variables override manifest variables.

    Examples:

        conduit bundle lock manifest.yaml
        conduit bundle lock manifest.yaml --var env=prod --var version=1.2.3
        conduit bundle lock manifest.yaml --no-progress  # Disable download progress
    """
    # Get config service from context
    # Output path is determined by CLI argument or auto-generated by LockService
    if not output:
        output_path_object = Path.cwd() / "output"
        output_path_object.mkdir(parents=True, exist_ok=True)
        output = str(output_path_object)

    async def async_lock():
        service = LockService()

        # Setup progress display unless disabled
        progress_callback = None
        display = None  # Initialize display to None
        if not no_progress:
            display = ProgressDisplay()
            progress_callback = create_progress_callback(display)
            display.start()

        try:

            # Use async generation for concurrent downloads and progress
            lockfile_path, lockfile = await service.generate_lockfile_async(
                manifest_file,
                cli_variables=var,
                output_path=output,
                progress_callback=progress_callback,
            )

            # Stop progress display before printing results
            if (
                display and display.progress
            ):  # Check if display was initialized and started
                display.stop()

            if service.parsed_cli_variables:
                click.echo(
                    f"Using template variables: {', '.join(f'{k}={v}' for k, v in service.parsed_cli_variables.items())}"
                )

            click.echo(f"✓ Loaded manifest from: {manifest_file}")
            click.echo(f"✓ Lock file generated: {lockfile_path}")
            click.echo(f"  - {len(lockfile.artifacts)} artifact(s) processed")

        finally:
            # Ensure display is stopped even on error
            if (
                display and display.progress
            ):  # Check if display was initialized and started
                display.stop()

    try:
        asyncio.run(async_lock())

    except LockError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort() from e


if __name__ == "__main__":
    lock()
