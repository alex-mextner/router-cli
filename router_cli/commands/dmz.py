"""dmz — expose one LAN host to the internet (or nobody)."""

from __future__ import annotations

from . import _area

NAME = "dmz"
SUMMARY = "show/set the DMZ host (set host=192.168.0.50 or host=off)"
run = _area.make(NAME, SUMMARY, _area.fixed("dmz"))
