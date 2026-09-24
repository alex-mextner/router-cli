"""leases — DHCP leases, with static reservations marked (and listed even when offline)."""

from __future__ import annotations

from ..drivers.base import Capability
from . import _common as C
from .devices import _ip_key

NAME = "leases"
SUMMARY = "DHCP leases and static reservations"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    C.add_router_args(p)
    p.add_argument("--reserved", action="store_true", help="only static reservations")
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.LEASES)
    leases = sorted(driver.leases(), key=lambda lease: _ip_key(lease.ip))
    if args.reserved:
        leases = [lease for lease in leases if lease.kind == "reservation"]
    if args.json:
        C.emit_json(leases)
        return 0
    print(
        C.table(
            ["mac", "ip", "kind", "active", "expires", "hostname"],
            [
                [x.mac, x.ip, x.kind, "yes" if x.active else "no", x.expires, x.hostname]
                for x in leases
            ],
        )
    )
    return 0
