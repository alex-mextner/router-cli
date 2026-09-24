"""reboot — restart the router. Always destructive: --yes, or --dry-run to see the request.

Factory reset is deliberately not offered by router-cli at all.
"""

from __future__ import annotations

from ..drivers.base import Capability
from . import _common as C

NAME = "reboot"
SUMMARY = "reboot the router (needs --yes; there is no factory reset)"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    C.add_router_args(p)
    C.add_write_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.REBOOT, "reboot")
    return C.run_plan(driver, driver.plan_reboot(), args)
