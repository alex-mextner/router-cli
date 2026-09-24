"""firewall — firewall level and attack detection switches."""

from __future__ import annotations

from . import _area

NAME = "firewall"
SUMMARY = "show/set firewall level, fragment/scan/flood protection"
run = _area.make(NAME, SUMMARY, _area.fixed("firewall"))
