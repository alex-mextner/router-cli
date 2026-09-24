"""unreserve — remove a MAC's static DHCP lease."""

from __future__ import annotations

from ..drivers.base import Capability
from ..models import normalize_mac
from . import _common as C

NAME = "unreserve"
SUMMARY = "remove a static DHCP lease"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument("mac")
    C.add_router_args(p)
    C.add_write_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.RESERVE, "static leases")
    plan = driver.plan_unreserve(normalize_mac(args.mac))
    return C.run_plan(driver, plan, args, after=driver.reservations)
