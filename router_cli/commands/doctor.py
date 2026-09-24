"""doctor — say what works, what does not, and exactly how to fix each gap.

Checks, in order: Python, the credentials file (and its permissions), the OS keyring, the
inventory database, the OUI table and icon rules, then the router itself — reachable,
recognised, credentials stored, admin session usable. Every router check is a GET; doctor
never logs in unless credentials are stored and the session is gone (then it logs in once,
which is what every other command would do too).
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from .. import credentials, drivers, icons, oui
from .._errors import EXIT_NETWORK, EXIT_OK, EXIT_PERMISSION, RouterCliError
from ..http import HttpTransport
from ..inventory import Inventory
from . import _common as C

NAME = "doctor"
SUMMARY = "check setup: credentials, keyring, database, OUI table, router reachability"


def _mark(ok: bool | None) -> str:
    return "✓" if ok else ("·" if ok is None else "✗")


def run(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="router doctor", description=SUMMARY)
    p.add_argument("--host")
    p.add_argument("--driver")
    p.add_argument("--user")
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--no-router", action="store_true", help="skip the router checks")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    checks: list[dict[str, Any]] = []

    def check(section: str, name: str, ok: bool | None, detail: str, fix: str = "") -> None:
        checks.append({"section": section, "check": name, "ok": ok, "detail": detail, "fix": fix})

    py_ok = sys.version_info >= (3, 11)
    check("local", "python", py_ok, sys.version.split()[0], "" if py_ok else "install Python 3.11+")
    try:
        data = credentials.load_file()
        routers = sorted(data["routers"])
        check(
            "local",
            "credentials",
            bool(routers) or None,
            f"{credentials.path()}: {len(routers)} router(s), default {data.get('default') or '-'}",
            "" if routers else "run `router login` (needed when no admin session is open)",
        )
    except RouterCliError as exc:
        check("local", "credentials", False, exc.what, exc.how)
    keyring = credentials.available_keyring()
    check("local", "os keyring", None, keyring.name if keyring else "none (the file store is used)")
    try:
        with Inventory() as inv:
            check("local", "inventory db", True, f"{inv.path} ({inv.poll_count()} poll(s))")
    except Exception as exc:  # sqlite3 / OS errors: report, don't crash the doctor
        check("local", "inventory db", False, str(exc), "set ROUTER_CLI_DB to a writable path")
    entries = len(oui.table())
    check(
        "local",
        "oui table",
        entries > 1000,
        f"{entries} prefixes ({oui.source()})",
        "" if entries > 1000 else "run `router oui update`",
    )
    try:
        rules, _default = icons.load_rules()
        check("local", "icon rules", True, f"{len(rules)} rule(s)")
    except RouterCliError as exc:
        check("local", "icon rules", False, exc.what, exc.how)

    code = EXIT_OK
    if not args.no_router:
        code = _router_checks(args, check)

    if args.json:
        C.emit_json(
            {"ok": code == EXIT_OK and all(c["ok"] is not False for c in checks), "checks": checks}
        )
        return code
    section = ""
    for c in checks:
        if c["section"] != section:
            section = c["section"]
            print(("\n" if checks.index(c) else "") + section)
        print(f"  {_mark(c['ok'])} {c['check']:<14} {c['detail']}")
        if c["fix"] and c["ok"] is not True:
            print(f"      fix: {c['fix']}")
    return code


def _router_checks(args: argparse.Namespace, check: Any) -> int:
    try:
        base = C.resolve_host(args)
    except RouterCliError as exc:
        check("router", "address", False, exc.what, exc.how)
        return EXIT_NETWORK
    check("router", "address", True, base)
    transport = HttpTransport(base, timeout=args.timeout)
    try:
        found = drivers.detect(transport)
    except RouterCliError as exc:
        check("router", "reachable", False, exc.why or exc.what, exc.how)
        return EXIT_NETWORK
    check("router", "reachable", True, "answers HTTP")
    try:
        name = C.resolve_driver_name(args, base, transport)
    except RouterCliError as exc:
        check("router", "driver", False, exc.what, exc.how)
        return EXIT_NETWORK
    detected = f"detected {found[1]}" if found else "not auto-detected"
    check("router", "driver", True, f"{name} ({detected})")
    user = C.resolve_user(args, base, name)
    has_creds = bool(credentials.password_for(base, name, user))
    check(
        "router",
        "credentials",
        has_creds or None,
        f"{user}: {'stored' if has_creds else 'none stored'}",
        "" if has_creds else "run `router login`",
    )
    try:
        driver = C.open_driver(args)
        active = driver.session_active()
        if not active and has_creds:
            creds = driver.credentials() if driver.credentials else None
            if creds:
                driver.login(*creds)
                active = driver.session_active()
        check(
            "router",
            "session",
            active,
            "admin pages readable" if active else "no admin session",
            "" if active else "run `router login`",
        )
        if not active:
            return EXIT_PERMISSION
        info = driver.info()
        check("router", "model", True, f"{info.vendor} {info.model} {info.firmware}".strip())
    except RouterCliError as exc:
        check("router", "session", False, exc.what, exc.how)
        return EXIT_PERMISSION
    return EXIT_OK
