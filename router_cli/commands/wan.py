"""wan — the internet side: address, gateway, DNS, lease (read-only)."""

from __future__ import annotations

from . import _area

NAME = "wan"
SUMMARY = "show the WAN address, gateway and DNS"
run = _area.make(NAME, SUMMARY, _area.fixed("wan"), writable=False)
