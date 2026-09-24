"""vpn — the IPSec endpoint switch and tunnel list (tunnel editor: `settings vpn-ipsec`)."""

from __future__ import annotations

from . import _area

NAME = "vpn"
SUMMARY = "show/set the VPN (IPSec endpoint, tunnels)"
run = _area.make(
    NAME, SUMMARY, _area.fixed("vpn"), epilog="tunnel editor: router settings show vpn-ipsec"
)
