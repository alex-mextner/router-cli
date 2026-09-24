"""cm — the cable modem: DOCSIS downstream/upstream channels and provisioning steps."""

from __future__ import annotations

from .._errors import unsupported
from ..drivers.base import Capability
from . import _common as C

NAME = "cm"
SUMMARY = "cable modem: DOCSIS channels, signal levels, provisioning"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    C.add_router_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.DOCSIS, "DOCSIS / cable modem information")
    channels_fn = getattr(driver, "docsis_channels", None)
    if channels_fn is None:
        raise unsupported(driver.name, "DOCSIS channels")
    channels = channels_fn()
    provisioning = driver.read_area("provisioning")
    if args.json:
        C.emit_json({"channels": channels, "provisioning": provisioning})
        return 0
    for direction in ("downstream", "upstream"):
        rows = [c for c in channels if c.direction == direction]
        print(f"{direction} ({sum(c.locked for c in rows)}/{len(rows)} locked)")
        print(
            C.table(
                ["ch", "lock", "mod", "MHz", "dBmV", "SNR", "corr", "uncorr"],
                [
                    [
                        c.channel,
                        "yes" if c.locked else "no",
                        c.modulation,
                        f"{c.frequency_hz / 1e6:.1f}" if c.frequency_hz else "-",
                        c.power_dbmv,
                        c.snr_db,
                        c.correctable,
                        c.uncorrectable,
                    ]
                    for c in rows
                ],
            )
        )
        print()
    print("provisioning")
    print(C.kv_lines(provisioning, "  "))
    return 0
