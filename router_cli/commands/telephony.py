"""telephony — the built-in MTA: provisioning steps and line status (read-only)."""

from __future__ import annotations

from . import _area

NAME = "telephony"
SUMMARY = "show telephony (MTA) provisioning and line status"
run = _area.make(NAME, SUMMARY, _area.fixed("telephony"), writable=False)
