"""unreserve — remove a device's static DHCP lease (MAC, current IP or name)."""

from __future__ import annotations

from .. import device_selector
from ..drivers.base import Capability
from . import _common as C

NAME = "unreserve"
SUMMARY = "remove a static DHCP lease"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument("device", metavar="DEVICE", help=device_selector.HELP)
    C.add_router_args(p)
    C.add_write_args(p)
    args = p.parse_args(argv)
    mac = device_selector.resolve_mac(args.device)
    driver = C.open_driver(args)
    driver.require(Capability.RESERVE, "static leases")
    plan = driver.plan_unreserve(mac)
    return C.run_plan(driver, plan, args, after=driver.reservations)
