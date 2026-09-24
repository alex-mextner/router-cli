"""lan — the LAN side: router address, DNS handed to clients, domain."""

from __future__ import annotations

from . import _area

NAME = "lan"
SUMMARY = "show/set LAN address, DNS servers and domain"
run = _area.make(NAME, SUMMARY, _area.fixed("lan"))
