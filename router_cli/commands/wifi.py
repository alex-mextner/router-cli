"""wifi — radios, SSIDs, channels, security (keys hidden unless --show-secrets)."""

from __future__ import annotations

import argparse

from .._errors import UsageError, unsupported
from ..drivers.base import BaseDriver
from . import _area

NAME = "wifi"
SUMMARY = "show/set Wi-Fi radios, SSIDs, channels and security"


def band_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--band", choices=("2g", "5g", "all"), default="all", help="which radio (default all)"
    )


def banded(prefix: str) -> _area.Resolver:
    """Per-band areas (<prefix>-2g / -5g) when the driver has them, else one <prefix> area."""

    def resolve(driver: BaseDriver, args: argparse.Namespace, for_write: bool) -> list[str]:
        pair = [f"{prefix}-2g", f"{prefix}-5g"]
        if all(b in driver.areas for b in pair):
            if args.band == "all":
                if for_write:
                    raise UsageError(
                        what="say which radio to change", why="", how="add --band 2g or --band 5g"
                    )
                return pair
            return [f"{prefix}-{args.band}"]
        if prefix in driver.areas:
            return [prefix]
        raise unsupported(driver.name, f"{prefix} settings")

    return resolve


run = _area.make(
    NAME,
    SUMMARY,
    banded("wifi"),
    extra_args=band_arg,
    epilog=(
        "examples:\n"
        "  router wifi\n"
        "  router wifi keys --band 2g\n"
        "  router wifi set --band 5g channel=44 --dry-run\n"
        "  router wifi set --band 2g security=wpa-personal psk=... --dry-run\n"
        "MAC access control: router wifi-acl"
    ),
)
