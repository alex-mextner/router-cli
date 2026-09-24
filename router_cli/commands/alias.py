"""alias — give a device a local name and/or icon (beats router names and icon rules)."""

from __future__ import annotations

import re

from .._errors import UsageError
from ..inventory import Inventory
from ..models import normalize_mac
from . import _common as C

NAME = "alias"
SUMMARY = "set a device's local name/icon: alias <mac> --name N --icon mdi:x"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument("mac")
    p.add_argument("--name", help="display name ('' to remove)")
    p.add_argument("--icon", help="MDI icon, e.g. mdi:printer-3d ('' to remove)")
    p.add_argument("--clear", action="store_true", help="remove name and icon")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    mac = normalize_mac(args.mac)
    if args.icon and not re.fullmatch(r"mdi:[a-z0-9-]+", args.icon):
        raise UsageError(
            what=f"{args.icon!r} is not an MDI icon name", why="", how="e.g. mdi:laptop"
        )
    with Inventory() as inv:
        if args.clear or args.name is not None or args.icon is not None:
            inv.set_alias(mac, name=args.name, icon=args.icon, clear=args.clear)
        device = next((d for d in inv.devices("all") if d["mac"] == mac), None)
    if args.json:
        C.emit_json(device)
    elif device:
        print(f"{mac}: name {device['hostname'] or '-'}, icon {device['icon']}")
    return 0
