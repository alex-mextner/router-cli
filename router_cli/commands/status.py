"""status — model, firmware, uptime, WAN, and (on cable gateways) a DOCSIS summary."""

from __future__ import annotations

from ..drivers.base import Capability
from . import _common as C

NAME = "status"
SUMMARY = "model, firmware, uptime, WAN and DOCSIS summary"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    C.add_router_args(p)
    args = p.parse_args(argv)
    driver = C.open_driver(args)
    driver.require(Capability.STATUS)
    status = driver.status()
    if args.json:
        C.emit_json(status)
        return 0
    r = status.router
    print(f"router     {r.vendor} {r.model}".rstrip() + f"  ({driver.name} @ {r.host})")
    if r.firmware:
        print(f"firmware   {r.firmware}" + (f"  (hardware {r.hardware})" if r.hardware else ""))
    if status.uptime_text:
        print(f"uptime     {status.uptime_text}")
    if status.lan_ip:
        print(f"lan        {status.lan_ip}")
    if status.wan:
        w = status.wan
        print(f"wan        {w.ipv4 or '-'}/{w.netmask or '-'} via {w.gateway or '-'}")
        if w.dns:
            print(f"dns        {', '.join(w.dns)}")
    if status.docsis:
        d = status.docsis
        print(f"docsis     {d.mode or '-'}, network access {d.network_access or '-'}")
        print(
            f"channels   down {d.downstream_locked}/{d.downstream_total} locked, "
            f"up {d.upstream_locked}/{d.upstream_total} locked"
        )
        if d.downstream_power_dbmv:
            lo, hi = d.downstream_power_dbmv
            print(f"ds power   {lo:.1f} .. {hi:.1f} dBmV", end="")
            if d.downstream_snr_db:
                print(
                    f", SNR {d.downstream_snr_db[0]:.1f} .. {d.downstream_snr_db[1]:.1f} dB", end=""
                )
            print()
        if d.upstream_power_dbmv:
            print(
                f"us power   {d.upstream_power_dbmv[0]:.1f} .. {d.upstream_power_dbmv[1]:.1f} dBmV"
            )
        pending = [
            k
            for k, v in d.provisioning.items()
            if v and v.lower() not in ("completed", "enabled", "enabled / bpi+")
        ]
        print(
            f"provision  {'all steps completed' if not pending else 'check: ' + ', '.join(pending)}"
        )
    return 0
