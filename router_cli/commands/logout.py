"""logout — forget a router's stored credentials.

It only removes what `router login` stored on this machine; it sends nothing to the router.
(Admin sessions need no separate logout: every command already closes a session it had to
open when it ends, unless it was run with ``--keep-session``.)
"""

from __future__ import annotations

from .. import credentials
from . import _common as C

NAME = "logout"
SUMMARY = "forget stored credentials for a router (nothing is sent to the router)"


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
