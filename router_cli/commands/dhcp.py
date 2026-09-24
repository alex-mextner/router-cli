"""dhcp — the LAN DHCP server: on/off, pool, lease time (static leases: `reserve`)."""

from __future__ import annotations

from . import _area

NAME = "dhcp"
SUMMARY = "show/set the DHCP server (pool, lease time, on/off)"
run = _area.make(
    NAME,
    SUMMARY,
    _area.fixed("dhcp"),
    epilog="examples:\n  router dhcp\n  router dhcp set lease_time=7200 --dry-run",
)
