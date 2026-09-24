"""_common — what every router-touching command shares: options, driver opening, output,
and the one path by which a write plan is shown, confirmed and sent.

(The leading underscore keeps the dispatcher from registering this as a command.)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Sequence
from typing import Any

from .. import credentials, drivers
from .._errors import ConfirmationRequired, UsageError
from ..config import default_gateway
from ..drivers.base import BaseDriver, WritePlan, execute
from ..http import HttpTransport, normalize_base, render_requests
from ..models import to_json

DEFAULT_USERS = {"ubee_evw32c": "admin", "openwrt": "root"}


def parser(prog: str, summary: str, epilog: str | None = None) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog=f"router {prog}",
        description=summary,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def add_router_args(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("router selection")
    g.add_argument("--host", help="router address (default: saved profile, then default gateway)")
    g.add_argument("--driver", help="driver name (default: saved profile, then auto-detect)")
    g.add_argument("--user", help="admin user (default: saved profile, then the driver's default)")
    g.add_argument("--timeout", type=float, default=8.0, help="HTTP timeout in seconds (default 8)")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")


def add_write_args(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("writing")
    g.add_argument(
        "--dry-run",
        action="store_true",
        help="print the exact HTTP request(s) instead of sending them",
    )
    g.add_argument("--yes", action="store_true", help="confirm a destructive change")
    g.add_argument(
        "--show-secrets",
        action="store_true",
        help="do not redact passwords/keys in the output",
    )


def resolve_host(args: argparse.Namespace) -> str:
    host = (
        getattr(args, "host", None)
        or os.environ.get("ROUTER_CLI_HOST")
        or credentials.default_host()
        or default_gateway()
    )
    if not host:
        raise UsageError(
            what="no router address",
            why="no --host, no ROUTER_CLI_HOST, no default in credentials.json, no gateway",
            how="pass --host 192.168.0.1 (and run `router login` to remember it)",
        )
    return normalize_base(host)


def resolve_driver_name(args: argparse.Namespace, base_url: str, transport: HttpTransport) -> str:
    explicit = getattr(args, "driver", None) or os.environ.get("ROUTER_CLI_DRIVER")
    if explicit:
        return drivers.get(explicit).name
    saved = credentials.entry(base_url)
    if saved and saved.driver:
        return drivers.get(saved.driver).name
    found = drivers.detect(transport)
    if found is None:
        raise UsageError(
            what=f"could not tell which router {base_url} is",
            why="no driver recognised it (GET-only probes)",
            how="pass --driver (see `router drivers`)",
        )
    return found[0]


def resolve_user(args: argparse.Namespace, base_url: str, driver: str) -> str:
    saved = credentials.entry(base_url)
    return (
        getattr(args, "user", None)
        or os.environ.get("ROUTER_CLI_USER")
        or (saved.username if saved else "")
        or DEFAULT_USERS.get(driver, "admin")
    )


def open_driver(args: argparse.Namespace) -> BaseDriver:
    base = resolve_host(args)
    transport = HttpTransport(base, timeout=float(getattr(args, "timeout", 8.0) or 8.0))
    name = resolve_driver_name(args, base, transport)
    cls = drivers.get(name)
    user = resolve_user(args, base, name)

    def creds() -> tuple[str, str] | None:
        secret = credentials.password_for(base, name, user)
        return (user, secret) if secret else None

    return cls(transport, creds)


# ── output ───────────────────────────────────────────────────────────────────
def emit_json(data: Any) -> None:
    # codeql[py/clear-text-logging-sensitive-data]
    # Justified: callers pass already-redacted data (secrets are replaced by <hidden> /
    # <redacted> unless --show-secrets was given explicitly by the user).
    print(json.dumps(to_json(data), indent=2, ensure_ascii=False, default=str))


def table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    cells = [[("" if v is None else str(v)) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in cells:
        for i, v in enumerate(row):
            widths[i] = max(widths[i], len(v))
    lines = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip()]
    lines.append("  ".join("-" * w for w in widths))
    for row in cells:
        lines.append("  ".join(v.ljust(widths[i]) for i, v in enumerate(row)).rstrip())
    return "\n".join(lines)


def kv_lines(data: dict[str, Any], indent: str = "") -> str:
    lines = []
    width = max((len(str(k)) for k in data), default=0)
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append(f"{indent}{k}:")
            lines.append(kv_lines(v, indent + "  "))
        elif isinstance(v, list):
            shown = ", ".join(" | ".join(map(str, x)) if isinstance(x, list) else str(x) for x in v)
            lines.append(f"{indent}{str(k).ljust(width)}  {shown or '-'}")
        else:
            shown = "yes" if v is True else "no" if v is False else ("-" if v in (None, "") else v)
            lines.append(f"{indent}{str(k).ljust(width)}  {shown}")
    return "\n".join(lines)


# ── writes ───────────────────────────────────────────────────────────────────
def plan_json(
    plan: WritePlan, base_url: str, show_secrets: bool, dry_run: bool, executed: bool
) -> dict[str, Any]:
    return {
        "dry_run": dry_run,
        "executed": executed,
        "summary": plan.summary,
        "destructive": plan.destructive,
        "verified": plan.verified,
        "requests": [r.to_dict(base_url, show_secrets) for r in plan.requests],
        "then": [d.description for d in plan.deferred],
        "notes": plan.notes,
    }


def print_plan(plan: WritePlan, base_url: str, show_secrets: bool) -> None:
    print(f"plan: {plan.summary}")
    if not plan.verified:
        print("  (request shape inferred, not captured from this firmware)")
    for note in plan.notes:
        print(f"  note: {note}")
    if plan.requests:
        print()
        # codeql[py/clear-text-logging-sensitive-data]
        # Justified: render_requests replaces every secret field with <redacted> unless the
        # user explicitly passed --show-secrets; this is the reviewable dry-run output.
        print(render_requests(plan.requests, base_url, show_secrets))
    for deferred in plan.deferred:
        print(f"\nthen: {deferred.description}")


def run_plan(
    driver: BaseDriver,
    plan: WritePlan,
    args: argparse.Namespace,
    after: Callable[[], Any] | None = None,
) -> int:
    """Show (--dry-run), refuse (destructive without --yes) or send a plan."""
    base = driver.host
    show = bool(getattr(args, "show_secrets", False))
    as_json = bool(getattr(args, "json", False))
    if not plan.steps:
        if as_json:
            emit_json(plan_json(plan, base, show, dry_run=bool(args.dry_run), executed=False))
        else:
            print(plan.summary)
            for note in plan.notes:
                print(f"  note: {note}")
        return 0
    if args.dry_run:
        if as_json:
            emit_json(plan_json(plan, base, show, dry_run=True, executed=False))
        else:
            print("DRY RUN - nothing was sent.")
            print_plan(plan, base, show)
        return 0
    if plan.destructive and not args.yes:
        if not as_json:
            print_plan(plan, base, show)
            print()
        raise ConfirmationRequired(
            what="this change is destructive and needs --yes",
            why=plan.summary,
            how="review the request above (or run with --dry-run), then add --yes",
        )
    transport = driver.transport
    if isinstance(transport, HttpTransport):
        transport.allow_writes = True
    try:
        execute(plan, transport)
    finally:
        if isinstance(transport, HttpTransport):
            transport.allow_writes = False
    result = after() if after else None
    if as_json:
        out = plan_json(plan, base, show, dry_run=False, executed=True)
        if result is not None:
            out["result"] = to_json(result)
        emit_json(out)
    else:
        print(f"done: {plan.summary}")
        for note in plan.notes:
            print(f"  note: {note}")
    return 0


def parse_assignments(items: Sequence[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep or not key:
            raise UsageError(what=f"{item!r} is not key=value", why="", how="e.g. lease_time=7200")
        out[key.strip()] = value
    return out


def warn(message: str) -> None:
    print(f"router: {message}", file=sys.stderr)
