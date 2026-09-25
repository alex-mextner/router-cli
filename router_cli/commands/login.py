"""login — verify the admin password against the router and remember it.

The password is read with getpass (or one line from stdin with --password-stdin), checked by
actually logging in, and written to ``credentials.json`` (0600, in a 0700 directory) keyed
by host, together with the driver and user; that router becomes the default. With
``--store keyring`` the password goes to the OS keyring instead and the file keeps only the
driver and user. It never appears in argv, the environment or any output.
"""

from __future__ import annotations

import getpass
import sys

from .. import credentials, drivers
from .._errors import UsageError
from ..http import HttpTransport
from . import _common as C

NAME = "login"
SUMMARY = "check the admin password against the router and store it"

FORMAT = """\
credentials.json format (you may also write it by hand; keep it chmod 600):
  {"routers": {"192.168.0.1": {"driver": "ubee_evw32c", "username": "admin",
                               "password": "..."}},
   "default": "192.168.0.1"}"""


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY, epilog=FORMAT)
    p.add_argument("--host", help="router address (default: saved default, then gateway)")
    p.add_argument("--driver", help="driver (default: auto-detect)")
    p.add_argument("--user", help="admin user (default: admin for Ubee, root for OpenWrt)")
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument(
        "--store", choices=("file", "keyring"), default="file", help="where the password goes"
    )
    p.add_argument("--password-stdin", action="store_true", help="read the password from stdin")
    p.add_argument("--no-default", action="store_true", help="do not make this the default router")
    C.add_session_arg(p)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    base = C.resolve_host(args)
    transport = HttpTransport(base, timeout=args.timeout)
    name = C.resolve_driver_name(args, base, transport)
    cls = drivers.get(name)
    user = C.resolve_user(args, base, name)

    if args.password_stdin:
        password = sys.stdin.readline().rstrip("\r\n")
    else:
        password = getpass.getpass(f"password for {user}@{credentials.host_key(base)} ({name}): ")
    if not password:
        raise UsageError(what="empty password", why="nothing was typed", how="try again")

    # Tracked like any driver: the session this check opens is closed again afterwards
    # (the admin session of some routers is open to the whole LAN) unless --keep-session.
    driver = C.track(cls(transport, None), args)
    driver.login(user, password)
    where, path = credentials.store(
        base,
        name,
        user,
        password,
        prefer=args.store,
        # An access point / mesh node is never the router the other commands should talk to.
        make_default=not args.no_default and not cls.access_point,
    )
    result = {
        "host": credentials.host_key(base),
        "driver": name,
        "user": user,
        "verified": True,
        "stored_in": where,
        "file": str(path),
    }
    if args.json:
        C.emit_json(result)
    else:
        print(f"logged in to {result['host']} as {user} ({cls.title})")
        print(f"password stored in {where}" + (f" ({path}, mode 0600)" if where == "file" else ""))
    return 0
