from __future__ import annotations

import re
from typing import List

import click

from conduit.cli.context import ConduitContext
from conduit.core.logging import configure_logging

_V_RE = re.compile(r"^\-([v]+)$")


class ConduitGroup(click.Group):
    """Strip ‑v/‑vv/‑vvv/‑‑verbosity N anywhere, then launch normal parsing."""  # noqa: RUF002

    def parse_args(self, ctx: click.Context, args: List[str]):
        verbosity = 0
        remaining: List[str] = []
        itr = iter(args)
        for token in itr:
            m = _V_RE.match(token)
            if m:
                verbosity += len(m.group(1))
                continue
            if token == "--verbose":  # treat as single -v
                verbosity += 1
                continue
            if token == "--verbosity":
                try:
                    verbosity = int(next(itr))
                except (StopIteration, ValueError):
                    raise click.BadParameter(msg="--verbosity requires an integer")
                continue
            remaining.append(token)

        configure_logging(verbosity)
        ctx.obj = ctx.obj or ConduitContext(verbosity=verbosity)
        super().parse_args(ctx, remaining)