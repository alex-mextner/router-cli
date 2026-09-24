"""palette — the colours argparse paints help with, borrowed for the help we write ourselves.

Every ``router <command> --help`` is built by argparse, which colours its own output on
Python 3.14 and later. The top-level ``router --help`` is hand-written, so instead of
inventing a palette this asks argparse for the one it is about to use. On a Python whose
argparse does not colour at all, and on a pipe, a dumb terminal or under ``NO_COLOR``, every
field here is the empty string.

Measure the plain text: an escape sequence occupies no columns but plenty of characters.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

_UNCOLOURED = ""


@dataclass(frozen=True)
class Palette:
    """The few argparse colours the top-level help needs. Empty means "write it plain"."""

    heading: str = _UNCOLOURED
    prog: str = _UNCOLOURED
    action: str = _UNCOLOURED
    reset: str = _UNCOLOURED


def for_help() -> Palette:
    """The colours a subcommand's ``--help`` will use right now, or none at all."""
    theme = _argparse_theme()
    if theme is None:
        return Palette()
    return Palette(heading=theme.heading, prog=theme.prog, action=theme.action, reset=theme.reset)


def _argparse_theme() -> Any | None:
    if not _argparse_colours_at_all():
        return None
    try:
        from _colorize import can_colorize, get_theme
    except ImportError:  # pragma: no cover - only on a Python without the private module
        return None
    if not can_colorize():
        return None
    return get_theme(force_color=True).argparse


def _argparse_colours_at_all() -> bool:
    """Whether this Python's argparse knows about colour, asked by trying to use it."""
    try:
        # Typed against 3.11, where the keyword does not exist yet — that is the point.
        argparse.ArgumentParser(add_help=False, color=True)  # type: ignore[call-arg,unused-ignore]
    except TypeError:
        return False
    return True
