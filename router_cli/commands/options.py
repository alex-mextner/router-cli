"""options — gateway options: WAN ping blocking, VPN passthrough, multicast, UPnP."""

from __future__ import annotations

from . import _area

NAME = "options"
SUMMARY = "show/set UPnP, multicast, IPSec/PPTP passthrough, WAN blocking"
run = _area.make(NAME, SUMMARY, _area.fixed("options"))
