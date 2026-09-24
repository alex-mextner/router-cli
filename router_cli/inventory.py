"""inventory — remember every device the router has ever reported, across polls.

A router only knows who is connected NOW. The inventory is a small SQLite database
(``$ROUTER_CLI_DB``, default ``<data dir>/inventory.sqlite3``) that each
``router inventory update`` merges a poll into, so questions like "what is new since
yesterday", "what used to be at .42" or "which devices run a web UI" have answers.

Per MAC it tracks first/last seen, whether it was in the latest poll (``online``), every IP
and name it has had, its interface, its static lease, the OUI vendor, whether the MAC is
randomised, local aliases (name/icon), and the HTTP(S) services ``router scan`` found.

THE JSON CONTRACT (consumed by a Home Assistant dashboard — keep it stable)
    ``router inventory list --json`` prints::

        {"generated_at": ISO-8601 with offset,
         "router": {"driver", "model", "host"},
         "devices": [{"mac", "ip", "hostname", "names": [str], "vendor", "random_mac",
                      "interface", "online", "first_seen", "last_seen", "reserved_ip",
                      "ip_history": [{"ip", "first_seen", "last_seen"}], "icon",
                      "services": [{"port", "scheme", "url", "title", "server",
                                    "favicon_data_url", "checked_at"}]}]}

    ``hostname`` is the local alias if one is set, else the router-reported name, else the
    most recent reverse-DNS name. ``names`` lists all of them, alias first, newest first.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from . import icons, oui
from .config import db_path
from .models import Device, Reservation, RouterInfo, is_random_mac, normalize_mac

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS devices (
    mac TEXT PRIMARY KEY,
    first_seen TEXT,
    last_seen TEXT,
    online INTEGER NOT NULL DEFAULT 0,
    ip TEXT,
    hostname TEXT,
    interface TEXT,
    band TEXT,
    reserved_ip TEXT,
    vendor TEXT,
    random_mac INTEGER NOT NULL DEFAULT 0,
    alias_name TEXT,
    alias_icon TEXT
);
CREATE TABLE IF NOT EXISTS ip_history (
    mac TEXT NOT NULL, ip TEXT NOT NULL, first_seen TEXT, last_seen TEXT,
    PRIMARY KEY (mac, ip)
);
CREATE TABLE IF NOT EXISTS names (
    mac TEXT NOT NULL, name TEXT NOT NULL, source TEXT, first_seen TEXT, last_seen TEXT,
    PRIMARY KEY (mac, name)
);
CREATE TABLE IF NOT EXISTS services (
    mac TEXT NOT NULL, ip TEXT, port INTEGER NOT NULL, scheme TEXT, url TEXT, title TEXT,
    server TEXT, favicon_data_url TEXT, checked_at TEXT,
    PRIMARY KEY (mac, port)
);
CREATE TABLE IF NOT EXISTS scans (
    mac TEXT PRIMARY KEY, ip TEXT, open_ports TEXT, checked_at TEXT
);
CREATE TABLE IF NOT EXISTS polls (
    id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, driver TEXT, model TEXT, host TEXT,
    devices INTEGER
);
"""

FILTERS = ("recent", "active", "all", "reserved", "new")


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def parse_since(text: str) -> timedelta:
    """'24h', '7d', '30m', '90s', '2w' -> timedelta."""
    from ._errors import UsageError

    units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    text = text.strip().lower()
    try:
        if text[-1] in units:
            return timedelta(seconds=float(text[:-1]) * units[text[-1]])
        return timedelta(seconds=float(text))
    except (ValueError, IndexError) as exc:
        raise UsageError(
            what=f"--since {text!r}", why="expected e.g. 30m, 24h, 7d", how=""
        ) from exc


def _ip_key(ip: str | None) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in (ip or "").split("."))
    except ValueError:
        return (999,)


@dataclass
class PollResult:
    at: str
    seen: int
    new: list[str]
    went_offline: list[str]


class Inventory:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> Inventory:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ── meta ─────────────────────────────────────────────────────────────────
    def _set_meta(self, key: str, value: str) -> None:
        self.db.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def meta(self, key: str) -> str | None:
        row = self.db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return str(row["value"]) if row else None

    def router(self) -> dict[str, str | None]:
        return {k: self.meta(f"router.{k}") for k in ("driver", "model", "host")}

    def poll_count(self) -> int:
        row = self.db.execute("SELECT COUNT(*) AS n FROM polls").fetchone()
        return int(row["n"])

    # ── merging a poll ───────────────────────────────────────────────────────
    def record_poll(
        self,
        info: RouterInfo,
        devices: list[Device],
        reservations: list[Reservation] | None,
        extra_names: dict[str, str] | None = None,
        at: str | None = None,
    ) -> PollResult:
        at = at or now_iso()
        extra_names = extra_names or {}
        known = {
            r["mac"]
            for r in self.db.execute("SELECT mac FROM devices WHERE first_seen IS NOT NULL")
        }
        seen: set[str] = set()
        new: list[str] = []
        with self.db:
            for dev in devices:
                mac = normalize_mac(dev.mac)
                seen.add(mac)
                if mac not in known:
                    new.append(mac)
                self.db.execute(
                    """
                    INSERT INTO devices (mac, first_seen, last_seen, online, ip, hostname,
                                         interface, band, vendor, random_mac)
                    VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(mac) DO UPDATE SET
                        first_seen = COALESCE(devices.first_seen, excluded.first_seen),
                        last_seen = excluded.last_seen,
                        online = 1,
                        ip = COALESCE(excluded.ip, devices.ip),
                        hostname = COALESCE(excluded.hostname, devices.hostname),
                        interface = excluded.interface,
                        band = excluded.band,
                        vendor = COALESCE(excluded.vendor, devices.vendor),
                        random_mac = excluded.random_mac
                    """,
                    (
                        mac,
                        at,
                        at,
                        dev.ip,
                        dev.hostname,
                        dev.interface,
                        dev.band,
                        oui.vendor(mac),
                        int(is_random_mac(mac)),
                    ),
                )
                if dev.ip:
                    self._touch("ip_history", mac, "ip", dev.ip, at)
                if dev.hostname:
                    self._touch_name(mac, dev.hostname, "router", at)
                if mac in extra_names:
                    self._touch_name(mac, extra_names[mac], "rdns", at)
            offline = [
                r["mac"]
                for r in self.db.execute("SELECT mac FROM devices WHERE online = 1")
                if r["mac"] not in seen
            ]
            self.db.executemany(
                "UPDATE devices SET online = 0 WHERE mac = ?", [(m,) for m in offline]
            )
            if reservations is not None:
                self.db.execute("UPDATE devices SET reserved_ip = NULL")
                for res in reservations:
                    mac = normalize_mac(res.mac)
                    self.db.execute(
                        """
                        INSERT INTO devices (mac, reserved_ip, vendor, random_mac, online)
                        VALUES (?, ?, ?, ?, 0)
                        ON CONFLICT(mac) DO UPDATE SET reserved_ip = excluded.reserved_ip
                        """,
                        (mac, res.ip, oui.vendor(mac), int(is_random_mac(mac))),
                    )
                    if res.name:
                        self._touch_name(mac, res.name, "reservation", at)
            self.db.execute(
                "INSERT INTO polls(at, driver, model, host, devices) VALUES (?, ?, ?, ?, ?)",
                (at, info.driver, info.model, info.host, len(devices)),
            )
            self._set_meta("router.driver", info.driver)
            self._set_meta("router.model", info.model)
            self._set_meta("router.host", info.host)
            self._set_meta("last_poll", at)
        return PollResult(at=at, seen=len(seen), new=new, went_offline=offline)

    def _touch(self, table: str, mac: str, column: str, value: str, at: str) -> None:
        self.db.execute(
            f"INSERT INTO {table} (mac, {column}, first_seen, last_seen) VALUES (?, ?, ?, ?) "
            f"ON CONFLICT(mac, {column}) DO UPDATE SET last_seen = excluded.last_seen",
            (mac, value, at, at),
        )

    def _touch_name(self, mac: str, name: str, source: str, at: str) -> None:
        self.db.execute(
            "INSERT INTO names (mac, name, source, first_seen, last_seen) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(mac, name) DO UPDATE SET last_seen = excluded.last_seen, "
            "source = excluded.source",
            (mac, name, source, at, at),
        )

    # ── aliases ──────────────────────────────────────────────────────────────
    def set_alias(
        self, mac: str, name: str | None = None, icon: str | None = None, clear: bool = False
    ) -> None:
        mac = normalize_mac(mac)
        with self.db:
            self.db.execute(
                "INSERT INTO devices (mac, vendor, random_mac) VALUES (?, ?, ?) "
                "ON CONFLICT(mac) DO NOTHING",
                (mac, oui.vendor(mac), int(is_random_mac(mac))),
            )
            if clear:
                self.db.execute(
                    "UPDATE devices SET alias_name = NULL, alias_icon = NULL WHERE mac = ?", (mac,)
                )
            if name is not None:
                self.db.execute(
                    "UPDATE devices SET alias_name = ? WHERE mac = ?", (name or None, mac)
                )
            if icon is not None:
                self.db.execute(
                    "UPDATE devices SET alias_icon = ? WHERE mac = ?", (icon or None, mac)
                )

    # ── scans ────────────────────────────────────────────────────────────────
    def mac_for_ip(self, ip: str) -> str | None:
        row = self.db.execute(
            "SELECT mac FROM devices WHERE ip = ? ORDER BY online DESC, last_seen DESC LIMIT 1",
            (ip,),
        ).fetchone()
        return str(row["mac"]) if row else None

    def online_targets(self) -> list[tuple[str, str]]:
        rows = self.db.execute(
            "SELECT mac, ip FROM devices WHERE online = 1 AND ip IS NOT NULL ORDER BY ip"
        )
        return [(str(r["mac"]), str(r["ip"])) for r in rows]

    def save_scan(
        self, mac: str, ip: str, open_ports: list[int], services: list[dict[str, Any]], at: str
    ) -> None:
        with self.db:
            self.db.execute("DELETE FROM services WHERE mac = ?", (mac,))
            for svc in services:
                self.db.execute(
                    """INSERT INTO services
                       (mac, ip, port, scheme, url, title, server, favicon_data_url, checked_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        mac,
                        ip,
                        int(svc["port"]),
                        svc.get("scheme"),
                        svc.get("url"),
                        svc.get("title"),
                        svc.get("server"),
                        svc.get("favicon_data_url"),
                        svc.get("checked_at", at),
                    ),
                )
            self.db.execute(
                "INSERT INTO scans (mac, ip, open_ports, checked_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(mac) DO UPDATE SET ip = excluded.ip, "
                "open_ports = excluded.open_ports, "
                "checked_at = excluded.checked_at",
                (mac, ip, json.dumps(sorted(open_ports)), at),
            )

    # ── listing ──────────────────────────────────────────────────────────────
    def devices(
        self, filter_: str = "all", since: timedelta | None = None, now: datetime | None = None
    ) -> list[dict[str, Any]]:
        now = now or datetime.now(UTC)
        cutoff = (now - (since or timedelta(hours=24))).replace(microsecond=0).isoformat()
        where, args = {
            "all": ("1 = 1", ()),
            "active": ("online = 1", ()),
            "recent": ("last_seen >= ?", (cutoff,)),
            "new": ("first_seen >= ?", (cutoff,)),
            "reserved": ("reserved_ip IS NOT NULL", ()),
        }[filter_]
        rows = self.db.execute(f"SELECT * FROM devices WHERE {where}", args).fetchall()
        rows.sort(key=lambda r: (not r["online"], r["ip"] is None, _ip_key(r["ip"]), r["mac"]))
        return [self._device_json(r) for r in rows]

    def _device_json(self, row: sqlite3.Row) -> dict[str, Any]:
        mac = str(row["mac"])
        name_rows = self.db.execute(
            "SELECT name, source FROM names WHERE mac = ? ORDER BY last_seen DESC, name", (mac,)
        ).fetchall()
        names: list[str] = []
        if row["alias_name"]:
            names.append(str(row["alias_name"]))
        for r in name_rows:
            if r["name"] not in names:
                names.append(str(r["name"]))
        hostname = row["alias_name"] or row["hostname"] or (names[0] if names else None)
        history = [
            {"ip": r["ip"], "first_seen": r["first_seen"], "last_seen": r["last_seen"]}
            for r in self.db.execute(
                "SELECT ip, first_seen, last_seen FROM ip_history "
                "WHERE mac = ? ORDER BY last_seen DESC",
                (mac,),
            )
        ]
        services = [
            {
                "port": int(r["port"]),
                "scheme": r["scheme"],
                "url": r["url"],
                "title": r["title"],
                "server": r["server"],
                "favicon_data_url": r["favicon_data_url"],
                "checked_at": r["checked_at"],
            }
            for r in self.db.execute("SELECT * FROM services WHERE mac = ? ORDER BY port", (mac,))
        ]
        facts = icons.Facts(
            vendor=row["vendor"],
            hostnames=names,
            titles=[s["title"] for s in services if s["title"]],
            servers=[s["server"] for s in services if s["server"]],
            ports=[s["port"] for s in services],
            random_mac=bool(row["random_mac"]),
        )
        return {
            "mac": mac,
            "ip": row["ip"],
            "hostname": hostname,
            "names": names,
            "vendor": row["vendor"],
            "random_mac": bool(row["random_mac"]),
            "interface": row["interface"],
            "online": bool(row["online"]),
            "first_seen": row["first_seen"],
            "last_seen": row["last_seen"],
            "reserved_ip": row["reserved_ip"],
            "ip_history": history,
            "icon": row["alias_icon"] or icons.choose(facts),
            "services": services,
        }

    def scan_state(self, macs: Iterable[str]) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for mac in macs:
            row = self.db.execute("SELECT * FROM scans WHERE mac = ?", (mac,)).fetchone()
            if row:
                out[mac] = {
                    "open_ports": json.loads(row["open_ports"] or "[]"),
                    "checked_at": row["checked_at"],
                }
        return out
