"""oui — look up a MAC's manufacturer; `oui update` refreshes the table from the IEEE."""

from __future__ import annotations

from .. import device_selector, oui
from ..models import is_random_mac
from . import _common as C

NAME = "oui"
SUMMARY = "MAC vendor lookup; `oui update` downloads the IEEE registry"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument(
        "mac", nargs="?", metavar="DEVICE", help="MAC (or device name/IP) to look up, or 'update'"
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.mac == "update":
        path, count = oui.update()
        if args.json:
            C.emit_json({"path": str(path), "entries": count})
        else:
            print(f"downloaded {count} prefixes to {path}")
        return 0
    if not args.mac:
        info = {"source": oui.source(), "entries": len(oui.table())}
        if args.json:
            C.emit_json(info)
        else:
            print(f"{info['entries']} prefixes ({info['source']})")
        return 0
    mac = device_selector.resolve_mac(args.mac)
    result = {"mac": mac, "vendor": oui.vendor(mac), "random_mac": is_random_mac(mac)}
    if args.json:
        C.emit_json(result)
    else:
        print(
            result["vendor"]
            or ("(locally administered / random)" if result["random_mac"] else "(unknown)")
        )
    return 0
