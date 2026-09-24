"""logout — forget a router's stored credentials.

This does NOT end the router's admin session: on the Ubee that session is global, and
logging it out would log out every other client (Home Assistant included). It only removes
what `router login` stored on this machine.
"""

from __future__ import annotations

from .. import credentials
from . import _common as C

NAME = "logout"
SUMMARY = "forget stored credentials for a router (the router session is left alone)"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument("--host", help="router address (default: the saved default)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    host = credentials.host_key(args.host or credentials.default_host())
    removed = credentials.remove(host) if host else []
    if args.json:
        C.emit_json({"host": host, "removed_from": removed})
    elif removed:
        print(f"forgot {host} (removed from: {', '.join(removed)})")
    else:
        print(f"nothing stored for {host or 'any router'}")
    return 0
