"""install-skill — register the ``router`` skill so coding agents know this tool exists.

Run by ``install.sh`` at the end of an install, and safe to run by hand at any time. See
:mod:`router_cli.install` for what it writes and why each layer exists.
"""

from __future__ import annotations

import argparse

from ..install import install_skill

NAME = "install-skill"
SUMMARY = "register the router skill so coding agents know this tool exists"


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="router install-skill", description=SUMMARY)
    parser.parse_args(argv)
    return install_skill()
