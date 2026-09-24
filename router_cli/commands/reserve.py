"""reserve — pin a MAC to an IP (a static DHCP lease).

On routers whose static leases cannot carry a name (the Ubee), ``--name`` is stored as a
local alias in the inventory instead, so `router inventory list` still shows it.
"""

from __future__ import annotations

from ..drivers.base import Capability
from ..inventory import Inventory
from ..models import normalize_mac
from . import _common as C

NAME = "reserve"
SUMMARY = "pin an IP to a MAC (static DHCP lease)"


def run(argv: list[str]) -> int:
    p = C.parser(
        NAME,
        SUMMARY,
        epilog="example:\n  router reserve 02:00:00:00:00:01 192.168.0.250 --name test --dry-run",
    )
    p.add_argument("mac")
    p.add_argument("ip")
    p.add_argument("--name", help="a name for the device")
    C.add_router_args(p)
    C.add_write_args(p)
    args = p.parse_args(argv)
    mac = normalize_mac(args.mac)
    driver = C.open_driver(args)
    driver.require(Capability.RESERVE, "static leases")
    plan = driver.plan_reserve(mac, args.ip, args.name)

    def after() -> object:
        if args.name and not driver.reservation_names:
            with Inventory() as inv:
                inv.set_alias(mac, name=args.name)
        return [r for r in driver.reservations() if r.mac == mac]

    return C.run_plan(driver, plan, args, after=after)
