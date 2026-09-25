"""scan — probe LAN devices for web UIs (title, server, favicon) and remember them.

    router scan --all-online --json      every device online in the last inventory poll
    router scan --ip 192.168.0.25        one (or several: repeat --ip) address
    router scan --ip printer             ... or a MAC / device name from the inventory

Results are saved per MAC in the inventory (``services`` in `router inventory list`).
With ``--all-online`` and an empty inventory, the router is polled first.
"""

from __future__ import annotations

from datetime import UTC, datetime

from .. import device_selector
from .._errors import UsageError
from ..inventory import Inventory
from ..scan import DEFAULT_PORTS, scan_hosts
from . import _common as C

NAME = "scan"
SUMMARY = "find web UIs on LAN devices (port, title, server, favicon)"


def _ports(text: str | None) -> tuple[int, ...]:
    if not text:
        return DEFAULT_PORTS
    try:
        ports = tuple(int(p) for p in text.split(",") if p.strip())
    except ValueError as exc:
        raise UsageError(what=f"--ports {text!r}", why="expected 80,443,8123", how="") from exc
    return ports


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--ip",
        action="append",
        metavar="DEVICE",
        help="address, MAC or device name to scan (repeatable)",
    )
    target.add_argument("--all-online", action="store_true", help="every online inventory device")
    p.add_argument("--ports", help="comma-separated ports (default: the built-in web port list)")
    p.add_argument("--connect-timeout", type=float, default=0.6)
    p.add_argument("--http-timeout", type=float, default=3.0)
    p.add_argument("--no-favicon", action="store_true")
    p.add_argument("--no-save", action="store_true", help="do not store results in the inventory")
    C.add_router_args(p)
    args = p.parse_args(argv)

    with Inventory() as inv:
        if args.all_online:
            if inv.poll_count() == 0:
                from .inventory import update

                update(C.open_driver(args))
            targets: list[tuple[str, str | None]] = [(ip, mac) for mac, ip in inv.online_targets()]
        else:
            targets = [device_selector.resolve_target(sel, inv) for sel in args.ip]
        results = scan_hosts(
            targets,
            ports=_ports(args.ports),
            connect_timeout=args.connect_timeout,
            http_timeout=args.http_timeout,
            with_icons=not args.no_favicon,
        )
        at = datetime.now(UTC).replace(microsecond=0).isoformat()
        if not args.no_save:
            for r in results:
                if r.mac:
                    inv.save_scan(r.mac, r.ip, r.open_ports, [s.to_json() for s in r.services], at)

    out = [
        {
            "ip": r.ip,
            "mac": r.mac,
            "open_ports": r.open_ports,
            "services": [s.to_json() for s in r.services],
        }
        for r in results
    ]
    if args.json:
        C.emit_json({"generated_at": at, "results": out})
        return 0
    for r in results:
        if not r.open_ports:
            continue
        print(f"{r.ip}  {r.mac or '(not in inventory)'}  open: {', '.join(map(str, r.open_ports))}")
        for s in r.services:
            icon = " [favicon]" if s.favicon_data_url else ""
            print(f"    {s.url}  {s.title or '-'}  ({s.server or 'no server header'}){icon}")
    scanned = len(results)
    with_web = sum(1 for r in results if r.services)
    print(f"\nscanned {scanned} host(s); {with_web} with a web UI")
    return 0
