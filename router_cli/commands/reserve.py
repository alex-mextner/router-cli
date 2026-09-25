"""reserve — pin a device to an IP (a static DHCP lease).

The device is a MAC in any format, a current IP, or a name/alias from the inventory (see
:mod:`router_cli.device_selector`). Without an IP, the device's current address (from the
local inventory) is pinned.

On routers whose static leases cannot carry a name (the Ubee), ``--name`` is stored as a
local alias in the inventory instead, so `router inventory list` still shows it.
"""

from __future__ import annotations

from .. import device_selector
from .._errors import MissingTargetError
from ..drivers.base import Capability
from ..inventory import Inventory
from ..models import is_ipv4, validate_ipv4
from . import _common as C

NAME = "reserve"
SUMMARY = "pin an IP to a device (static DHCP lease); no IP = its current one"

EPILOG = f"""\
DEVICE: {device_selector.HELP}

examples:
  router reserve 02:00:00:00:00:01 192.168.0.250 --name test --dry-run
  router reserve printer               pin the printer's current address
  router reserve 192.168.0.25          pin whatever is at .25 to .25"""


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY, epilog=EPILOG)
    p.add_argument("device", metavar="DEVICE", help=device_selector.HELP)
    p.add_argument("ip", nargs="?", help="the address to pin (default: the current one)")
    p.add_argument("--name", help="a name for the device")
    C.add_router_args(p)
    C.add_write_args(p)
    args = p.parse_args(argv)
    with Inventory() as inv:
        mac = device_selector.resolve_mac(args.device, inv)
        ip = args.ip
        if ip is None:
            ip = validate_ipv4(args.device) if is_ipv4(args.device) else inv.ip_for_mac(mac)
        if not ip:
            raise MissingTargetError(
                what=f"no current IP known for {args.device!r} ({mac})",
                why="no IP was given and the inventory has no address for this device",
                how=f"give one: router reserve {args.device} 192.168.0.50",
            )
    driver = C.open_driver(args)
    driver.require(Capability.RESERVE, "static leases")
    plan = driver.plan_reserve(mac, ip, args.name)

    def after() -> object:
        if args.name and not driver.reservation_names:
            with Inventory() as inv:
                inv.set_alias(mac, name=args.name)
        return [r for r in driver.reservations() if r.mac == mac]

    return C.run_plan(driver, plan, args, after=after)
