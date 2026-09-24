"""wifi-acl — per-band MAC access control: the mode (set) and the MAC list (add/rm/clear)."""

from __future__ import annotations

import argparse

from .._errors import UsageError, unsupported
from ..drivers.base import BaseDriver
from . import _area, _lists
from . import _common as C
from .wifi import band_arg, banded

NAME = "wifi-acl"
SUMMARY = "show/set Wi-Fi MAC access control (mode and MAC list)"


def _list_for(driver: BaseDriver, args: argparse.Namespace) -> str:
    if args.band == "all":
        raise UsageError(what="say which radio", why="", how="add --band 2g or --band 5g")
    name = f"wifi-acl-{args.band}"
    if name not in driver.lists:
        raise unsupported(driver.name, "Wi-Fi MAC access lists")
    return name


_area_run = _area.make(
    NAME,
    SUMMARY,
    banded("wifi-acl"),
    extra_args=band_arg,
    epilog="list edits: router wifi-acl add|rm <mac> --band 2g ; router wifi-acl clear --band 5g",
)


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in ("add", "rm", "clear"):
        return _area_run(argv)
    top = C.parser(NAME, SUMMARY)
    sub = top.add_subparsers(dest="verb")
    for verb in ("add", "rm", "clear"):
        p = sub.add_parser(verb)
        if verb != "clear":
            p.add_argument("value", help="MAC address")
        band_arg(p)
        C.add_router_args(p)
        C.add_write_args(p)
    return _lists.run_list(top.parse_args(argv), _list_for)
