"""nas — USB storage sharing (Samba, FTP, DLNA) and its credentials."""

from __future__ import annotations

from . import _area

NAME = "nas"
SUMMARY = "show/set USB file sharing: Samba, FTP, DLNA, credentials"
run = _area.make(NAME, SUMMARY, _area.fixed("nas"))
