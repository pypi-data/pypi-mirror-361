"""
Main CLI entry point for Conduit (MVP version).

This module defines the main CLI group and registers available commands.
"""

import importlib.metadata as _ilmd

import click

from conduit.cli.context import CONTEXT_SETTINGS
from conduit.cli.global_group import ConduitGroup
from conduit.commands.bundle import bundle
from conduit.commands.config import config

from ..commands.keys import keys

_VERSION = _ilmd.version("conduit-cli") if _ilmd.packages_distributions() else "dev"


@click.group(cls=ConduitGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(_VERSION, "-V", "--version", prog_name="Conduit")
def main():
    """Conduit CLI - Manage and deploy software artifacts."""


# Register commands
main.add_command(bundle)
main.add_command(keys)
main.add_command(config)
