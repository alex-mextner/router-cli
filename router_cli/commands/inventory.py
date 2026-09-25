"""inventory — poll the router into the local device database, and list what it knows.

    router inventory update [--resolve] [--wait 120]
    router inventory list --json [--filter recent|active|all|reserved|new] [--since 24h]

``update`` reads devices and static leases from the router (GET-only), merges them into
the SQLite inventory, and (with ``--resolve``) looks up reverse-DNS/mDNS names for
devices the router gives no name for. Concurrent updates are serialized by a lock file next
to the database; one that finds a poll already running waits for it and reuses its result
instead of polling the router again. ``list --json`` is the stable contract documented
in :mod:`router_cli.inventory`.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from .._errors import RouterCliError
from ..config import db_path
from ..drivers.base import BaseDriver, Capability
from ..inventory import FILTERS, Inventory, now_iso, parse_since
from ..models import Device
from . import _common as C

NAME = "inventory"
SUMMARY = "poll devices into the local inventory DB; list it (HA/agent JSON contract)"


def resolve_names(devices: list[Device], timeout: float = 2.0) -> dict[str, str]:
    """Reverse-resolve IPs of devices without a router-reported name (best effort).

    ``gethostbyaddr`` has no timeout of its own, so each lookup runs on a DAEMON thread and
    whatever has not answered by the deadline is abandoned (a pool's worker threads would be
    joined at exit and hold the process for the resolver's full timeout).
    """
    targets = {d.mac: d.ip for d in devices if d.ip and not d.hostname}
    names: dict[str, str] = {}
    lock = threading.Lock()

    def lookup(mac: str, ip: str) -> None:
        try:
            name = socket.gethostbyaddr(ip)[0].rstrip(".")
        except OSError:
            return
        if name and name != ip:
            with lock:
                names[mac] = name

    threads = [
        threading.Thread(target=lookup, args=(mac, ip), daemon=True) for mac, ip in targets.items()
    ]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    for thread in threads:
        thread.join(max(0.0, deadline - time.monotonic()))
    with lock:
        return dict(names)


def update(driver: BaseDriver, resolve: bool = False) -> dict[str, Any]:
    driver.require(Capability.DEVICES)
    info = driver.info()
    devices = driver.devices()
    try:
        reservations = driver.reservations() if driver.supports(Capability.RESERVE) else None
    except RouterCliError:
        reservations = None
    extra = resolve_names(devices) if resolve else {}
    with Inventory() as inv:
        result = inv.record_poll(info, devices, reservations, extra_names=extra, at=now_iso())
        return {
            "at": result.at,
            "router": inv.router(),
            "seen": result.seen,
            "new": result.new,
            "went_offline": result.went_offline,
            "reservations": None if reservations is None else len(reservations),
            "resolved_names": len(extra),
            "db": str(inv.path),
        }


@contextmanager
def poll_lock(wait: float = 120.0) -> Iterator[bool]:
    """Serialize `inventory update` across processes (a timer and a UI button can collide).

    Yields True when this process holds the lock and should poll. If another poll is
    running, waits (up to ``wait`` seconds) for it to finish and yields False: its result
    is fresh, so polling the router a second time would only cost the router requests.
    """
    try:
        import fcntl
    except ImportError:  # pragma: no cover - Windows: no cross-process lock, just poll
        yield True
        return
    path = db_path().parent / "inventory-update.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        first = True
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            first = False
            deadline = time.monotonic() + max(0.0, wait)
            while True:
                time.sleep(0.2)
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() > deadline:
                        raise RouterCliError(
                            what="another `router inventory update` is still running",
                            why=f"it did not finish within {wait:g} s",
                            how="try again later (or raise --wait)",
                        ) from None
        try:
            yield first
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in ("update", "list", "-h", "--help"):
        argv = ["list", *argv]
    top = C.parser(NAME, SUMMARY)
    sub = top.add_subparsers(dest="verb")
    p = sub.add_parser("update", help="poll the router and merge into the DB")
    p.add_argument(
        "--resolve",
        action="store_true",
        help="also look up reverse-DNS/mDNS names (adds up to 2 s)",
    )
    p.add_argument(
        "--wait",
        type=float,
        default=120.0,
        help="if another poll is running, wait up to this many seconds for it and use its "
        "result instead of polling again (default 120)",
    )
    C.add_router_args(p)
    p = sub.add_parser("list", help="print the inventory")
    p.add_argument("--filter", choices=FILTERS, default="all")
    p.add_argument("--since", default="24h", help="window for recent/new (e.g. 30m, 24h, 7d)")
    p.add_argument("--json", action="store_true")
    args = top.parse_args(argv)

    if args.verb == "update":
        with poll_lock(args.wait) as first:
            if first:
                summary = update(C.open_driver(args), resolve=args.resolve)
            else:
                with Inventory() as inv:
                    summary = {"skipped": True, "at": inv.meta("last_poll"), "db": str(inv.path)}
        if args.json:
            C.emit_json(summary)
        elif summary.get("skipped"):
            print(f"another poll was running; used its result (last poll {summary['at']})")
        else:
            print(
                f"polled {summary['seen']} device(s); new: {len(summary['new'])}; "
                f"went offline: {len(summary['went_offline'])}"
            )
            print(f"database: {summary['db']}")
        return 0

    with Inventory() as inv:
        devices = inv.devices(args.filter, parse_since(args.since))
        router = inv.router()
        last_poll = inv.meta("last_poll")
    if args.json:
        C.emit_json(
            {
                "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                "last_poll": last_poll,
                "router": router,
                "devices": devices,
            }
        )
        return 0
    rows = [
        [
            d["mac"],
            d["ip"],
            d["hostname"],
            d["vendor"] or ("(random)" if d["random_mac"] else ""),
            "yes" if d["online"] else "no",
            d["reserved_ip"],
            d["icon"].replace("mdi:", ""),
            ",".join(str(s["port"]) for s in d["services"]),
        ]
        for d in devices
    ]
    print(C.table(["mac", "ip", "hostname", "vendor", "online", "reserved", "icon", "web"], rows))
    print(f"\n{len(devices)} device(s) [{args.filter}]")
    return 0
