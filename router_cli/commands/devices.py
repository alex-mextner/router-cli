"""devices — the clients the router knows right now (Wi-Fi stations and LAN/DHCP clients)."""

from __future__ import annotations

from typing import Any

from .. import oui
from ..drivers.base import Capability
from ..models import is_random_mac, to_json
from . import _common as C

NAME = "devices"
SUMMARY = "connected clients: mac, ip, hostname, wifi/lan, band, rssi"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    C.add_router_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.DEVICES)
    devices = driver.devices()
    rows: list[dict[str, Any]] = []
    for d in sorted(devices, key=lambda d: _ip_key(d.ip)):
        item = to_json(d)
        item["vendor"] = oui.vendor(d.mac)
        item["random_mac"] = is_random_mac(d.mac)
        rows.append(item)
    if args.json:
        C.emit_json(rows)
        return 0
    print(
        C.table(
            ["mac", "ip", "hostname", "if", "band", "rssi", "vendor"],
            [
                [
                    r["mac"],
                    r["ip"],
                    r["hostname"],
                    r["interface"],
                    r["band"],
                    r["rssi_dbm"],
                    r["vendor"] or ("(random)" if r["random_mac"] else ""),
                ]
                for r in rows
            ],
        )
    )
    print(f"\n{len(rows)} device(s)")
    return 0


def _ip_key(ip: str | None) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in (ip or "").split("."))
    except ValueError:
        return (999,)
