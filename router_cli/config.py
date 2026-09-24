"""config — where router-cli keeps things.

Config (``credentials.json`` written by ``router login``, local ``icon_rules.json``) lives
under ``$XDG_CONFIG_HOME/router-cli`` (``~/.config/router-cli``). Data (the inventory SQLite
database and a downloaded OUI table) lives under ``$XDG_DATA_HOME/router-cli``
(``~/.local/share/router-cli``). Every path is overridable by an environment variable so
tests, CI and a Home Assistant add-on can point elsewhere:

    ``ROUTER_CLI_CONFIG_DIR``, ``ROUTER_CLI_DATA_DIR``, ``ROUTER_CLI_DB``.

Which router to talk to, highest precedence first: the ``--host``/``--driver``/``--user``
flags, ``ROUTER_CLI_HOST``/``ROUTER_CLI_DRIVER``/``ROUTER_CLI_USER``, the ``default`` router
and its entry in ``credentials.json``, and for the host the machine's default gateway.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP = "router-cli"


def config_dir() -> Path:
    override = os.environ.get("ROUTER_CLI_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        return base / APP
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / APP


def data_dir() -> Path:
    override = os.environ.get("ROUTER_CLI_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / APP
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / APP


def db_path() -> Path:
    override = os.environ.get("ROUTER_CLI_DB")
    if override:
        return Path(override).expanduser()
    return data_dir() / "inventory.sqlite3"


def default_gateway() -> str:
    """The IPv4 default gateway on Linux (from /proc/net/route), or '' elsewhere."""
    try:
        lines = Path("/proc/net/route").read_text(encoding="ascii").splitlines()[1:]
    except OSError:
        return ""
    best: tuple[int, str] | None = None
    for line in lines:
        parts = line.split()
        if len(parts) < 8 or parts[1] != "00000000":
            continue
        try:
            raw = int(parts[2], 16)
            metric = int(parts[6])
        except ValueError:
            continue
        ip = ".".join(str((raw >> shift) & 0xFF) for shift in (0, 8, 16, 24))
        if best is None or metric < best[0]:
            best = (metric, ip)
    return best[1] if best else ""
