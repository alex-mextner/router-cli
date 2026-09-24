"""settings — every settings area of the router by name (the generic form of `dhcp`, `lan`...).

Besides the areas that have their own command, this reaches the raw-field areas: on the
Ubee ``parental-users``, ``parental-time``, ``vpn-ipsec``, ``nas-samba``, ``nas-ftp``,
``media-server`` and ``cm-scan``; on OpenWrt whole uci configs (``wifi``, ``firewall``,
``system``) with ``<section>.<option>`` keys.
"""

from __future__ import annotations

import argparse

from .._errors import unknown_item
from ..drivers.base import BaseDriver
from . import _area
from . import _common as C

NAME = "settings"
SUMMARY = "show/keys/set any settings area by name"


def _named(driver: BaseDriver, args: argparse.Namespace, for_write: bool) -> list[str]:
    if args.area not in driver.areas:
        raise unknown_item("settings area", args.area, sorted(driver.areas))
    return [str(args.area)]


def _area_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("area")


_run = _area.make(NAME, SUMMARY, _named, extra_args=_area_arg)


def run(argv: list[str]) -> int:
    if argv and argv[0] in ("show", "keys", "set", "-h", "--help"):
        return _run(argv)
    p = C.parser(NAME, SUMMARY, epilog="usage: router settings show|keys <area> ; set <area> k=v")
    C.add_router_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    if args.json:
        C.emit_json(driver.areas)
    else:
        print(C.table(["area", "what"], sorted(driver.areas.items())))
    return 0
