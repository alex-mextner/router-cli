"""password — change the router's admin password (prompted, never on the command line).

After a successful change the password stored by `router login` is updated too, so the
driver's automatic re-login keeps working.
"""

from __future__ import annotations

import getpass
import sys

from .. import credentials
from .._errors import UsageError
from ..drivers.base import Capability
from . import _common as C

NAME = "password"
SUMMARY = "change the admin password (prompts; needs --yes)"


def _read(prompt: str, from_stdin: bool) -> str:
    if from_stdin:
        return sys.stdin.readline().rstrip("\r\n")
    return getpass.getpass(prompt)


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument(
        "--password-stdin",
        action="store_true",
        help="read old and new password as two lines from stdin",
    )
    C.add_router_args(p)
    C.add_write_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.PASSWORD, "changing the admin password")
    user = C.resolve_user(args, driver.host, driver.name)
    old = _read(f"current password for {user}: ", args.password_stdin)
    new = _read("new password: ", args.password_stdin)
    if not args.password_stdin and getpass.getpass("new password again: ") != new:
        raise UsageError(what="the two new passwords differ", why="", how="try again")
    if not new:
        raise UsageError(what="empty new password", why="", how="")
    plan = driver.plan_password(user, old, new)

    def after() -> object:
        saved = credentials.entry(driver.host)
        if saved and saved.password:
            credentials.store(
                driver.host, driver.name, user, new, prefer="file", make_default=False
            )
            return {"stored_password_updated": True}
        return {"stored_password_updated": False}

    return C.run_plan(driver, plan, args, after=after)
