"""inventory — remember every device the network has ever shown, across polls and sweeps.

A router only knows who is connected NOW. The inventory is a small SQLite database
(``$ROUTER_CLI_DB``, default ``<data dir>/inventory.sqlite3``) that each
``router inventory update`` (a router poll) and each ``router discover`` (a sweep of the LAN
from this machine: ARP/ping, mDNS, SSDP, NetBIOS, Xiaomi mesh) merges into, so questions like
"what is new since yesterday", "what used to be at .42", "which devices run a web UI", "was
the TV on last night" have answers.

Per MAC it tracks first/last seen, whether it is online, every IP and name it has had, its
interface, its static lease, the OUI vendor, whether the MAC is randomised, local aliases
(name/icon), the HTTP(S) services ``router scan`` found (with their health), what discovery
learned (``discovery``), how it is connected (``links``), presence samples (``presence``,
one row per device per sweep) and traffic counters (``traffic``).

ONLINE
    A sweep of the LAN is ground truth: once ``router discover`` runs (every 5 minutes from a
    timer), a device is online if a sweep saw it in the last ``GRACE_S`` seconds, and a router
    poll no longer changes anyone's online flag (a gateway's client table goes stale). The
    machine router-cli runs on is always online.

THE JSON CONTRACT (consumed by a Home Assistant dashboard — keep it stable; only add)
    ``router inventory list --json`` prints::

        {"generated_at": ISO-8601 with offset (when this list was printed),
         "last_poll": ISO-8601 of the last `inventory update`, or null,
         "last_discover": ISO-8601 of the last `discover`, or null,
         "router": {"driver", "model", "host"},
         "devices": [{"mac", "ip", "hostname", "names": [str], "vendor", "random_mac",
                      "interface", "online", "first_seen", "last_seen", "reserved_ip",
                      "ip_history": [{"ip", "first_seen", "last_seen"}], "icon",
                      "services": [{"port", "scheme", "url", "title", "server",
                                    "favicon_data_url", "checked_at",
                                    "reachable": bool|null, "http_status": int|null,
                                    "error": str|null}],
                      "category", "confidence": 0..1, "label": str|null,
                      "evidence": [{"source", "detail", "weight"}],
                      "alternatives": [{"category", "confidence"}],
                      "display_name", "pinnable": bool, "is_network_gear": bool,
                      "is_self": bool,
                      "connection": {"type": "wired|wifi|unknown", "via": mac|null,
                                     "via_name": str|null, "band": "2.4"|"5"|"6"|null,
                                     "rssi": int|null, "source": "miwifi|local|heuristic"},
                      "traffic": {"rx_bytes", "tx_bytes", "rx_rate", "tx_rate",
                                  "updated_at", "source"} | null,
                      "interfaces": [{"mac", "ip", "online", "name", "type"}],
                      "same_device_as": mac|null}]}

    ``hostname`` is the local alias if one is set, else the router-reported name, else the
    most recent other name. ``names`` lists all of them, alias first, newest first.
    ``display_name`` is the best human name (alias, a meaningful hostname, a name the device
    or Home Assistant gives it, the recognised model, "<vendor> <category>").
    One physical device with several MACs (this machine's Ethernet + Wi-Fi, a TV's two
    NICs, the gateway's second interface) is listed ONCE, under its primary MAC, with every
    MAC in ``interfaces``; ``--all-interfaces`` lists the others too (``same_device_as`` set).

    ``router inventory history <device> --json`` and ``router inventory stats --json`` are
    documented at :meth:`Inventory.history` and :meth:`Inventory.stats`.
"""

from __future__ import annotations

import itertools
import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from . import fingerprint, icons, oui
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
CREATE TABLE IF NOT EXISTS discovery (
    mac TEXT NOT NULL, source TEXT NOT NULL, value TEXT, updated_at TEXT,
    PRIMARY KEY (mac, source)
);
CREATE TABLE IF NOT EXISTS links (
    mac TEXT PRIMARY KEY, type TEXT, via TEXT, via_name TEXT, band TEXT, rssi INTEGER,
    source TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS sweeps (
    t INTEGER PRIMARY KEY, online INTEGER, source TEXT, took REAL
);
CREATE TABLE IF NOT EXISTS presence (
    mac TEXT NOT NULL, t INTEGER NOT NULL, ip TEXT, PRIMARY KEY (mac, t)
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS presence_by_t ON presence (t);
CREATE TABLE IF NOT EXISTS traffic (
    mac TEXT NOT NULL, t INTEGER NOT NULL, rx_bytes INTEGER, tx_bytes INTEGER,
    rx_rate REAL, tx_rate REAL, source TEXT, PRIMARY KEY (mac, t)
) WITHOUT ROWID;
"""
# Columns added after the first release (created by _migrate on older databases).
SERVICE_COLUMNS = {
    "reachable": "INTEGER",
    "http_status": "INTEGER",
    "error": "TEXT",
    "markers": "TEXT",
    "favicon_hash": "TEXT",
}

FILTERS = ("recent", "active", "all", "reserved", "new")
GRACE_S = 660  # a device missing from a single 5-minute sweep is still online
DISCOVER_FRESH_S = 1200  # a sweep this recent makes sweeps (not router polls) the truth
KEEP_PRESENCE_S = 120 * 86400
KEEP_TRAFFIC_S = 60 * 86400
MAX_EVIDENCE = 8


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def to_epoch(text: str) -> int:
    return int(datetime.fromisoformat(text).timestamp())


def from_epoch(t: float) -> str:
    return datetime.fromtimestamp(t, UTC).replace(microsecond=0).isoformat()


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


@dataclass
class Sighting:
    """What one discovery run learned about one MAC."""

    mac: str
    ip: str | None = None
    present: bool = True  # False: facts about a device that was not seen (e.g. from HA)
    names: list[tuple[str, str]] = field(default_factory=list)  # (name, source)
    facts: dict[str, Any] = field(default_factory=dict)  # discovery source -> JSON value
    link: dict[str, Any] | None = None
    traffic: dict[str, Any] | None = None


@dataclass
class DiscoveryResult:
    at: str
    online: int
    new: list[str]
    went_offline: list[str]


def _merge_mdns(old: Any, new: dict[str, Any]) -> dict[str, Any]:
    """mDNS answers are partial and devices sleep: keep what was heard before, update it."""
    if not isinstance(old, dict):
        return new
    services: dict[tuple[str, str], dict[str, Any]] = {}
    for svc in [*(old.get("services") or []), *(new.get("services") or [])]:
        key = (str(svc.get("type")), str(svc.get("name")))
        merged = dict(services.get(key, {}))
        for k, v in svc.items():
            if v not in (None, {}, []):
                merged[k] = v
        services[key] = merged
    hostnames = list(dict.fromkeys([*(new.get("hostnames") or []), *(old.get("hostnames") or [])]))
    return {"hostnames": hostnames[:8], "services": list(services.values())[:40]}


class Inventory:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self._migrate()
        self._local: list[Any] | None = None

    def _migrate(self) -> None:
        have = {r["name"] for r in self.db.execute("PRAGMA table_info(services)")}
        with self.db:
            for column, kind in SERVICE_COLUMNS.items():
                if column not in have:
                    self.db.execute(f"ALTER TABLE services ADD COLUMN {column} {kind}")

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

    def _discover_is_fresh(self, at: str) -> bool:
        last = self.meta("last_discover")
        if not last:
            return False
        try:
            return abs(to_epoch(at) - to_epoch(last)) <= DISCOVER_FRESH_S
        except ValueError:
            return False

    def local_ifaces(self) -> list[Any]:
        """This machine's physical interfaces (cached per Inventory; [] off Linux)."""
        if self._local is None:
            from .lan.netinfo import local_interfaces

            try:
                self._local = list(local_interfaces())
            except OSError:
                self._local = []
        return self._local

    # ── merging a router poll ────────────────────────────────────────────────
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
        sweeps_rule = self._discover_is_fresh(at)
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
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(mac) DO UPDATE SET
                        first_seen = COALESCE(devices.first_seen, excluded.first_seen),
                        last_seen = excluded.last_seen,
                        online = CASE WHEN ? THEN devices.online ELSE 1 END,
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
                        0 if sweeps_rule else 1,
                        dev.ip,
                        dev.hostname,
                        dev.interface,
                        dev.band,
                        oui.vendor(mac),
                        int(is_random_mac(mac)),
                        int(sweeps_rule),
                    ),
                )
                if dev.ip:
                    self._touch("ip_history", mac, "ip", dev.ip, at)
                if dev.hostname:
                    self._touch_name(mac, dev.hostname, "router", at)
                if mac in extra_names:
                    self._touch_name(mac, extra_names[mac], "rdns", at)
            offline: list[str] = []
            if not sweeps_rule:
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
            "source = CASE WHEN names.source IN ('reservation', 'router') "
            "THEN names.source ELSE excluded.source END",
            (mac, name, source, at, at),
        )

    # ── merging a LAN discovery run ──────────────────────────────────────────
    def record_discovery(
        self,
        sightings: list[Sighting],
        at: str | None = None,
        took: float = 0.0,
        full_sweep: bool = True,
        source: str = "discover",
    ) -> DiscoveryResult:
        """Merge one ``router discover`` run. With ``full_sweep`` the run is a presence
        sample: every present sighting gets a presence row, and online devices that no
        sweep saw for ``GRACE_S`` seconds go offline."""
        at = at or now_iso()
        t = to_epoch(at)
        known = {
            r["mac"]
            for r in self.db.execute("SELECT mac FROM devices WHERE first_seen IS NOT NULL")
        }
        new: list[str] = []
        present: set[str] = set()
        with self.db:
            for s in sightings:
                mac = normalize_mac(s.mac)
                if s.present:
                    present.add(mac)
                    if mac not in known:
                        new.append(mac)
                    self.db.execute(
                        """
                        INSERT INTO devices (mac, first_seen, last_seen, online, ip, vendor,
                                             random_mac)
                        VALUES (?, ?, ?, 1, ?, ?, ?)
                        ON CONFLICT(mac) DO UPDATE SET
                            first_seen = COALESCE(devices.first_seen, excluded.first_seen),
                            last_seen = excluded.last_seen,
                            online = 1,
                            ip = COALESCE(excluded.ip, devices.ip),
                            vendor = COALESCE(devices.vendor, excluded.vendor)
                        """,
                        (mac, at, at, s.ip, oui.vendor(mac), int(is_random_mac(mac))),
                    )
                    if s.ip:
                        self._touch("ip_history", mac, "ip", s.ip, at)
                    if full_sweep:
                        self.db.execute(
                            "INSERT OR REPLACE INTO presence (mac, t, ip) VALUES (?, ?, ?)",
                            (mac, t, s.ip),
                        )
                else:
                    self.db.execute(
                        "INSERT INTO devices (mac, vendor, random_mac) VALUES (?, ?, ?) "
                        "ON CONFLICT(mac) DO NOTHING",
                        (mac, oui.vendor(mac), int(is_random_mac(mac))),
                    )
                for name, name_source in s.names:
                    if name:
                        self._touch_name(mac, name, name_source, at)
                for fact_source, value in s.facts.items():
                    self._save_fact(mac, fact_source, value, at)
                if s.link:
                    self.db.execute(
                        """INSERT OR REPLACE INTO links
                           (mac, type, via, via_name, band, rssi, source, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            mac,
                            s.link.get("type"),
                            s.link.get("via"),
                            s.link.get("via_name"),
                            s.link.get("band"),
                            s.link.get("rssi"),
                            s.link.get("source"),
                            at,
                        ),
                    )
                if s.traffic:
                    self.db.execute(
                        """INSERT OR REPLACE INTO traffic
                           (mac, t, rx_bytes, tx_bytes, rx_rate, tx_rate, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            mac,
                            t,
                            s.traffic.get("rx_bytes"),
                            s.traffic.get("tx_bytes"),
                            s.traffic.get("rx_rate"),
                            s.traffic.get("tx_rate"),
                            s.traffic.get("source"),
                        ),
                    )
            went_offline: list[str] = []
            if full_sweep:
                self.db.execute(
                    "INSERT OR REPLACE INTO sweeps (t, online, source, took) VALUES (?, ?, ?, ?)",
                    (t, len(present), source, round(took, 2)),
                )
                went_offline = [
                    str(r["mac"])
                    for r in self.db.execute(
                        "SELECT mac FROM devices WHERE online = 1 AND mac NOT IN "
                        "(SELECT mac FROM presence WHERE t >= ?)",
                        (t - GRACE_S,),
                    )
                ]
                self.db.executemany(
                    "UPDATE devices SET online = 0 WHERE mac = ?", [(m,) for m in went_offline]
                )
                self._set_meta("last_discover", at)
                self.db.execute("DELETE FROM presence WHERE t < ?", (t - KEEP_PRESENCE_S,))
                self.db.execute("DELETE FROM sweeps WHERE t < ?", (t - KEEP_PRESENCE_S,))
                self.db.execute("DELETE FROM traffic WHERE t < ?", (t - KEEP_TRAFFIC_S,))
        return DiscoveryResult(at=at, online=len(present), new=new, went_offline=went_offline)

    def _save_fact(self, mac: str, source: str, value: Any, at: str) -> None:
        if source == "mdns":
            value = _merge_mdns(self.fact(mac, "mdns"), value)
        self.db.execute(
            "INSERT OR REPLACE INTO discovery (mac, source, value, updated_at) VALUES (?, ?, ?, ?)",
            (mac, source, json.dumps(value, ensure_ascii=False, sort_keys=True), at),
        )

    def save_fact(self, mac: str, source: str, value: Any, at: str | None = None) -> None:
        with self.db:
            self._save_fact(normalize_mac(mac), source, value, at or now_iso())

    def drop_facts(self, source: str, keep: Iterable[str]) -> None:
        """Forget ``source`` facts of every MAC not in ``keep`` (e.g. HA devices removed)."""
        keep_set = set(keep)
        with self.db:
            for r in self.db.execute(
                "SELECT mac FROM discovery WHERE source = ?", (source,)
            ).fetchall():
                if r["mac"] not in keep_set:
                    self.db.execute(
                        "DELETE FROM discovery WHERE mac = ? AND source = ?", (r["mac"], source)
                    )

    def forget_identity(self, macs: Iterable[str]) -> None:
        """Drop what discovery and scans attributed to these MACs (their address was shared
        with another device, so the answers may have come from either)."""
        with self.db:
            for mac in macs:
                self.db.execute(
                    "DELETE FROM discovery WHERE mac = ? AND source IN "
                    "('mdns', 'ssdp', 'netbios', 'icmp', 'moonraker')",
                    (mac,),
                )
                self.db.execute("DELETE FROM services WHERE mac = ?", (mac,))
                self.db.execute("DELETE FROM scans WHERE mac = ?", (mac,))

    def fact(self, mac: str, source: str) -> Any:
        row = self.db.execute(
            "SELECT value FROM discovery WHERE mac = ? AND source = ?", (mac, source)
        ).fetchone()
        return json.loads(row["value"]) if row and row["value"] else None

    def facts(self, mac: str) -> dict[str, Any]:
        return {
            str(r["source"]): json.loads(r["value"])
            for r in self.db.execute("SELECT source, value FROM discovery WHERE mac = ?", (mac,))
            if r["value"]
        }

    def fact_updated(self, mac: str, source: str) -> str | None:
        row = self.db.execute(
            "SELECT updated_at FROM discovery WHERE mac = ? AND source = ?", (mac, source)
        ).fetchone()
        return str(row["updated_at"]) if row and row["updated_at"] else None

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

    def ip_for_mac(self, mac: str) -> str | None:
        row = self.db.execute(
            "SELECT ip FROM devices WHERE mac = ?", (normalize_mac(mac),)
        ).fetchone()
        return str(row["ip"]) if row and row["ip"] else None

    def ip_to_mac(self) -> dict[str, str]:
        """Every address a device has had -> its MAC (current IP beats reserved beats history)."""
        out: dict[str, str] = {}
        for r in self.db.execute("SELECT mac, ip FROM ip_history ORDER BY last_seen"):
            out[str(r["ip"])] = str(r["mac"])
        for r in self.db.execute(
            "SELECT mac, reserved_ip FROM devices WHERE reserved_ip IS NOT NULL"
        ):
            out[str(r["reserved_ip"])] = str(r["mac"])
        for r in self.db.execute(
            "SELECT mac, ip FROM devices WHERE ip IS NOT NULL ORDER BY online, last_seen"
        ):
            out[str(r["ip"])] = str(r["mac"])
        return out

    def selector_rows(self) -> list[dict[str, Any]]:
        """Every device with every name it answers to — what device selectors match against.

        ``names`` holds the local alias, the current router name and every name ever seen
        (router, reservation, reverse DNS, mDNS, NetBIOS), de-duplicated, alias first.
        """
        out: list[dict[str, Any]] = []
        rows = self.db.execute(
            "SELECT mac, ip, hostname, alias_name, online, last_seen FROM devices "
            "ORDER BY online DESC, last_seen DESC, mac"
        ).fetchall()
        for row in rows:
            names: list[str] = []
            for name in (row["alias_name"], row["hostname"]):
                if name and name not in names:
                    names.append(str(name))
            for r in self.db.execute(
                "SELECT name FROM names WHERE mac = ? ORDER BY last_seen DESC, name",
                (row["mac"],),
            ):
                if r["name"] not in names:
                    names.append(str(r["name"]))
            out.append(
                {
                    "mac": str(row["mac"]),
                    "ip": row["ip"],
                    "names": names,
                    "online": bool(row["online"]),
                }
            )
        return out

    def protected_ips(self) -> set[str]:
        """Addresses no scan / probe may touch: the gateway and its other interfaces."""
        from .config import default_gateway

        out = {ip for ip in (default_gateway(), self.meta("router.host")) if ip}
        for r in self.db.execute(
            "SELECT d.ip, x.value FROM discovery x JOIN devices d ON d.mac = x.mac "
            "WHERE x.source = 'net'"
        ):
            try:
                value = json.loads(r["value"] or "{}")
            except ValueError:
                continue
            if r["ip"] and (value.get("gateway") or value.get("gateway_iface")):
                out.add(str(r["ip"]))
        return out

    def online_targets(self) -> list[tuple[str, str]]:
        """(mac, ip) of online devices, one MAC per address (this machine's default-route NIC,
        else the most recently seen), never a protected address."""
        protected = self.protected_ips()
        own_default = {i.mac for i in self.local_ifaces() if i.default}
        by_ip: dict[str, str] = {}
        for r in self.db.execute(
            "SELECT mac, ip FROM devices WHERE online = 1 AND ip IS NOT NULL "
            "ORDER BY last_seen DESC"
        ):
            ip, mac = str(r["ip"]), str(r["mac"])
            if ip in protected:
                continue
            if ip not in by_ip or mac in own_default:
                by_ip[ip] = mac
        return [(mac, ip) for ip, mac in sorted(by_ip.items(), key=lambda kv: _ip_key(kv[0]))]

    def known_services(self, mac: str) -> list[dict[str, Any]]:
        return [
            {
                "port": int(r["port"]),
                "scheme": r["scheme"],
                "url": r["url"],
                "title": r["title"],
                "server": r["server"],
                "favicon_data_url": r["favicon_data_url"],
                "markers": json.loads(r["markers"]) if r["markers"] else [],
                "favicon_hash": r["favicon_hash"],
            }
            for r in self.db.execute("SELECT * FROM services WHERE mac = ? ORDER BY port", (mac,))
        ]

    def save_scan(
        self, mac: str, ip: str, open_ports: list[int], services: list[dict[str, Any]], at: str
    ) -> None:
        with self.db:
            self.db.execute("DELETE FROM services WHERE mac = ?", (mac,))
            for svc in services:
                reachable = svc.get("reachable", True)
                self.db.execute(
                    """INSERT INTO services
                       (mac, ip, port, scheme, url, title, server, favicon_data_url, checked_at,
                        reachable, http_status, error, markers, favicon_hash)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                        None if reachable is None else int(bool(reachable)),
                        svc.get("http_status"),
                        svc.get("error"),
                        json.dumps(svc.get("markers") or []),
                        svc.get("favicon_hash"),
                    ),
                )
            self.db.execute(
                "INSERT INTO scans (mac, ip, open_ports, checked_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(mac) DO UPDATE SET ip = excluded.ip, "
                "open_ports = excluded.open_ports, "
                "checked_at = excluded.checked_at",
                (mac, ip, json.dumps(sorted(open_ports)), at),
            )

    def service_targets(self) -> list[dict[str, Any]]:
        """Known web services of online devices (for a quick health re-check)."""
        protected = self.protected_ips()
        rows = self.db.execute(
            "SELECT s.mac, s.port, s.scheme, d.ip FROM services s JOIN devices d ON d.mac = s.mac "
            "WHERE d.online = 1 AND d.ip IS NOT NULL"
        )
        return [
            {
                "mac": r["mac"],
                "port": int(r["port"]),
                "scheme": r["scheme"] or "http",
                "ip": r["ip"],
            }
            for r in rows
            if r["ip"] not in protected
        ]

    def update_service_health(
        self, mac: str, port: int, status: int | None, error: str | None, at: str
    ) -> None:
        with self.db:
            self.db.execute(
                "UPDATE services SET reachable = ?, http_status = ?, error = ?, checked_at = ? "
                "WHERE mac = ? AND port = ?",
                (int(status is not None), status, error, at, mac, port),
            )

    # ── listing ──────────────────────────────────────────────────────────────
    def devices(
        self,
        filter_: str = "all",
        since: timedelta | None = None,
        now: datetime | None = None,
        favicons: bool = True,
        group: bool = True,
    ) -> list[dict[str, Any]]:
        now = now or datetime.now(UTC)
        cutoff = (now - (since or timedelta(hours=24))).replace(microsecond=0).isoformat()
        rows = self.db.execute("SELECT * FROM devices").fetchall()
        own = {i.mac: i for i in self.local_ifaces()}
        facts = self._all_facts()
        groups = self._groups([str(r["mac"]) for r in rows], facts, own)
        by_mac = {str(r["mac"]): r for r in rows}
        # this machine is always online
        items = [self._device_json(r, facts.get(str(r["mac"]), {}), own, favicons) for r in rows]
        by_json = {d["mac"]: d for d in items}
        for d in items:
            primary = groups.get(d["mac"])
            d["same_device_as"] = primary if primary and primary != d["mac"] else None
        for d in items:
            members = [m for m, p in groups.items() if p == d["mac"]]
            if len(members) > 1 or d["mac"] in own:
                d["interfaces"] = [
                    self._iface_json(by_json[m], by_mac[m], own)
                    for m in sorted(members or [d["mac"]], key=lambda m: (m != d["mac"], m))
                ]
                if any(i["online"] for i in d["interfaces"]):
                    d["online"] = True
                if not d["ip"]:
                    d["ip"] = next((i["ip"] for i in d["interfaces"] if i["ip"]), None)
            else:
                d["interfaces"] = [self._iface_json(d, by_mac[d["mac"]], own)]
        if group:
            items = [d for d in items if not d["same_device_as"]]

        def keep(d: dict[str, Any]) -> bool:
            if filter_ == "active":
                return bool(d["online"])
            if filter_ == "recent":
                return bool(d["online"]) or (d["last_seen"] or "") >= cutoff
            if filter_ == "new":
                return (d["first_seen"] or "") >= cutoff
            if filter_ == "reserved":
                return d["reserved_ip"] is not None
            return True

        items = [d for d in items if keep(d)]
        items.sort(key=lambda d: (not d["online"], d["ip"] is None, _ip_key(d["ip"]), d["mac"]))
        return items

    def _iface_json(
        self, d: dict[str, Any], row: sqlite3.Row, own: dict[str, Any]
    ) -> dict[str, Any]:
        local = own.get(d["mac"])
        return {
            "mac": d["mac"],
            "ip": d["ip"],
            "online": bool(d["online"]),
            "name": local.name if local else None,
            "type": ("wifi" if local.wireless else "wired") if local else d["connection"]["type"],
        }

    def _all_facts(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for r in self.db.execute("SELECT mac, source, value FROM discovery"):
            try:
                out.setdefault(str(r["mac"]), {})[str(r["source"])] = json.loads(r["value"])
            except (TypeError, ValueError):
                continue
        return out

    def _groups(
        self, macs: list[str], facts: dict[str, dict[str, Any]], own: dict[str, Any]
    ) -> dict[str, str]:
        """{mac: primary mac} for every MAC that belongs to a multi-MAC physical device."""
        present = set(macs)
        out: dict[str, str] = {}
        own_present = [m for m in own if m in present]
        if own_present:
            primary = own_present[0]  # local_interfaces() lists the default-route NIC first
            for m in own_present:
                out[m] = primary
        for mac, f in facts.items():
            net = f.get("net") or {}
            other = net.get("same_device_as")
            if isinstance(other, str) and other in present and mac in present:
                out.setdefault(mac, other)
                out.setdefault(other, other)
            ha = f.get("ha") or {}
            ha_macs = [m for m in ha.get("macs") or [] if m in present]
            if len(ha_macs) > 1 and mac in ha_macs:
                for member in ha_macs:
                    out.setdefault(member, ha_macs[0])
        return out

    def _names(self, row: sqlite3.Row) -> list[str]:
        mac = str(row["mac"])
        name_rows = self.db.execute(
            "SELECT name, source FROM names WHERE mac = ? ORDER BY "
            "CASE source WHEN 'reservation' THEN 0 WHEN 'router' THEN 1 WHEN 'miwifi' THEN 2 "
            "WHEN 'mdns' THEN 3 WHEN 'netbios' THEN 4 ELSE 5 END, last_seen DESC, name",
            (mac,),
        ).fetchall()
        names: list[str] = []
        if row["alias_name"]:
            names.append(str(row["alias_name"]))
        for r in name_rows:
            if r["name"] not in names:
                names.append(str(r["name"]))
        return names

    def _device_json(
        self,
        row: sqlite3.Row,
        facts: dict[str, Any],
        own: dict[str, Any],
        favicons: bool = True,
    ) -> dict[str, Any]:
        mac = str(row["mac"])
        names = self._names(row)
        hostname = row["alias_name"] or row["hostname"] or (names[0] if names else None)
        history = [
            {"ip": r["ip"], "first_seen": r["first_seen"], "last_seen": r["last_seen"]}
            for r in self.db.execute(
                "SELECT ip, first_seen, last_seen FROM ip_history "
                "WHERE mac = ? ORDER BY last_seen DESC",
                (mac,),
            )
        ]
        service_rows = self.db.execute(
            "SELECT * FROM services WHERE mac = ? ORDER BY port", (mac,)
        ).fetchall()
        services = [
            {
                "port": int(r["port"]),
                "scheme": r["scheme"],
                "url": r["url"],
                "title": r["title"],
                "server": r["server"],
                "favicon_data_url": r["favicon_data_url"] if favicons else None,
                "checked_at": r["checked_at"],
                "reachable": None if r["reachable"] is None else bool(r["reachable"]),
                "http_status": r["http_status"],
                "error": r["error"],
            }
            for r in service_rows
        ]
        scan = self.db.execute("SELECT open_ports FROM scans WHERE mac = ?", (mac,)).fetchone()
        open_ports = json.loads(scan["open_ports"]) if scan and scan["open_ports"] else []
        local = own.get(mac)
        if local is not None:
            net = dict(facts.get("net") or {})
            net["self"] = 1
            if local.wireless:
                net["wireless"] = 1
            facts = {**facts, "net": net}
        ha = facts.get("ha") or {}
        rich_services = [
            {
                **s,
                "markers": json.loads(r["markers"]) if r["markers"] else [],
                "favicon_hash": r["favicon_hash"],
            }
            for s, r in zip(services, service_rows, strict=True)
        ]
        signals = fingerprint.build_signals(
            mac,
            row["vendor"],
            [n for n in names if n != row["alias_name"]],
            rich_services,
            open_ports,
            facts,
        )
        if ha.get("name"):
            signals.extra["name"] = str(ha["name"])
        for key in ("model", "manufacturer", "title"):
            if ha.get(key):
                signals.extra[f"ha.{key}"] = str(ha[key])
        if ha.get("domains"):
            signals.extra["ha.domain"] = " ".join(ha["domains"])
        result = fingerprint.classify_device(signals, alias=row["alias_name"])
        display = result.display_name or hostname or mac
        if local is not None and not row["alias_name"]:
            import socket

            host = socket.gethostname().split(".")[0]
            display = f"{host} ({result.label})" if result.label else host
        link_row = self.db.execute("SELECT * FROM links WHERE mac = ?", (mac,)).fetchone()
        link = dict(link_row) if link_row else None
        conn = fingerprint.connection(result, row["vendor"], bool(row["random_mac"]), link, facts)
        traffic_row = self.db.execute(
            "SELECT * FROM traffic WHERE mac = ? ORDER BY t DESC LIMIT 1", (mac,)
        ).fetchone()
        traffic = (
            {
                "rx_bytes": traffic_row["rx_bytes"],
                "tx_bytes": traffic_row["tx_bytes"],
                "rx_rate": traffic_row["rx_rate"],
                "tx_rate": traffic_row["tx_rate"],
                "updated_at": from_epoch(traffic_row["t"]),
                "source": traffic_row["source"],
            }
            if traffic_row
            else None
        )
        legacy = icons.Facts(
            vendor=row["vendor"],
            hostnames=names,
            titles=[s["title"] for s in services if s["title"]],
            servers=[s["server"] for s in services if s["server"]],
            ports=[s["port"] for s in services],
            random_mac=bool(row["random_mac"]),
        )
        icon = (
            row["alias_icon"]
            or icons.choose_user(legacy)
            or (result.icon if result.category != "unknown" else None)
            or icons.choose(legacy)
        )
        return {
            "mac": mac,
            "ip": row["ip"],
            "hostname": hostname,
            "names": names,
            "vendor": row["vendor"],
            "random_mac": bool(row["random_mac"]),
            "interface": row["interface"],
            "online": bool(row["online"]) or local is not None,
            "first_seen": row["first_seen"],
            "last_seen": row["last_seen"],
            "reserved_ip": row["reserved_ip"],
            "ip_history": history,
            "icon": icon,
            "services": services,
            "category": result.category,
            "confidence": result.confidence,
            "label": result.label,
            "evidence": [e.to_dict() for e in result.evidence[:MAX_EVIDENCE]],
            "alternatives": result.alternatives(),
            "display_name": display,
            "pinnable": not bool(row["random_mac"]),
            "is_network_gear": result.network_gear,
            "is_self": local is not None,
            "connection": conn,
            "traffic": traffic,
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

    # ── history & stats ──────────────────────────────────────────────────────
    def history(
        self, mac: str, days: float = 7, bucket_s: int = 3600, now: datetime | None = None
    ) -> dict[str, Any]:
        """``{"mac", "days", "bucket_s", "buckets": [{"t": ISO start of bucket,
        "online_ratio": share of sweeps in the bucket that saw the device (null: no sweep ran),
        "samples": sweeps in the bucket, "rx_bytes", "tx_bytes": bytes counted in the bucket
        (null: no traffic data)}]}``. Traffic counters that reset (reboot, reconnect) count
        from zero again."""
        mac = normalize_mac(mac)
        end = int((now or datetime.now(UTC)).timestamp())
        end = (end // bucket_s + 1) * bucket_s
        start = end - int(days * 86400)
        start -= start % bucket_s
        n = (end - start) // bucket_s
        sweeps = [0] * n
        seen = [0] * n
        for r in self.db.execute("SELECT t FROM sweeps WHERE t >= ? AND t < ?", (start, end)):
            sweeps[(int(r["t"]) - start) // bucket_s] += 1
        for r in self.db.execute(
            "SELECT t FROM presence WHERE mac = ? AND t >= ? AND t < ?", (mac, start, end)
        ):
            seen[(int(r["t"]) - start) // bucket_s] += 1
        rx: list[int | None] = [None] * n
        tx: list[int | None] = [None] * n
        self._traffic_into(mac, start, end, bucket_s, rx, tx)
        buckets = [
            {
                "t": from_epoch(start + i * bucket_s),
                "online_ratio": round(min(1.0, seen[i] / sweeps[i]), 3) if sweeps[i] else None,
                "samples": sweeps[i],
                "rx_bytes": rx[i],
                "tx_bytes": tx[i],
            }
            for i in range(n)
        ]
        return {"mac": mac, "days": days, "bucket_s": bucket_s, "buckets": buckets}

    def _traffic_into(
        self,
        mac: str,
        start: int,
        end: int,
        bucket_s: int,
        rx: list[int | None],
        tx: list[int | None],
    ) -> tuple[int, int]:
        rows = self.db.execute(
            "SELECT t, rx_bytes, tx_bytes FROM traffic WHERE mac = ? AND t >= ? AND t < ? "
            "ORDER BY t",
            (mac, start - 86400, end),
        ).fetchall()
        total_rx = total_tx = 0
        prev: sqlite3.Row | None = None
        for r in rows:
            if prev is not None and int(r["t"]) >= start:
                i = (int(r["t"]) - start) // bucket_s
                for col, series in (("rx_bytes", rx), ("tx_bytes", tx)):
                    cur, old = r[col], prev[col]
                    if cur is None:
                        continue
                    delta = cur - old if old is not None and cur >= old else cur
                    series[i] = (series[i] or 0) + int(delta)
                    if col == "rx_bytes":
                        total_rx += int(delta)
                    else:
                        total_tx += int(delta)
            prev = r
        return total_rx, total_tx

    def stats(self, days: float = 7, now: datetime | None = None) -> dict[str, Any]:
        """``{"online_now", "online_avg", "per_hour": [{"t", "online": average count, null
        when no sweep ran, "samples"}], "top_traffic": [{"mac", "display_name", "rx_bytes",
        "tx_bytes"}], "network_gear": [{"mac", "ip", "display_name", "category", "role":
        "gateway"|"mesh-node"|"other", "online"}], "unexpected_network_gear": int,
        "ip_conflicts": [{"ip", "macs"}], "sweeps", "since"}``."""
        end_dt = now or datetime.now(UTC)
        end = int(end_dt.timestamp())
        end = (end // 3600 + 1) * 3600
        start = end - int(days * 86400)
        devices = self.devices("all", now=end_dt, favicons=False)
        by_mac = {d["mac"]: d for d in devices}
        online_now = sum(1 for d in devices if d["online"])
        n = (end - start) // 3600
        totals = [0] * n
        counts = [0] * n
        all_counts: list[int] = []
        for r in self.db.execute(
            "SELECT t, online FROM sweeps WHERE t >= ? AND t < ?", (start, end)
        ):
            i = (int(r["t"]) - start) // 3600
            totals[i] += int(r["online"] or 0)
            counts[i] += 1
            all_counts.append(int(r["online"] or 0))
        per_hour = [
            {
                "t": from_epoch(start + i * 3600),
                "online": round(totals[i] / counts[i], 1) if counts[i] else None,
                "samples": counts[i],
            }
            for i in range(n)
        ]
        traffic: list[dict[str, Any]] = []
        for r in self.db.execute(
            "SELECT DISTINCT mac FROM traffic WHERE t >= ? AND t < ?", (start, end)
        ).fetchall():
            mac = str(r["mac"])
            rx_total, tx_total = self._traffic_into(mac, start, end, end - start, [None], [None])
            dev = by_mac.get(mac)
            traffic.append(
                {
                    "mac": mac,
                    "display_name": dev["display_name"] if dev else mac,
                    "rx_bytes": rx_total,
                    "tx_bytes": tx_total,
                }
            )
        traffic.sort(key=lambda x: -(x["rx_bytes"] + x["tx_bytes"]))
        gear = []
        for d in devices:
            if not d["is_network_gear"]:
                continue
            facts = self.facts(d["mac"])
            net = facts.get("net") or {}
            role = (
                "gateway"
                if net.get("gateway")
                else "mesh-node"
                if (facts.get("miwifi_info") or (facts.get("miwifi") or {}).get("is_ap"))
                else "other"
            )
            gear.append(
                {
                    "mac": d["mac"],
                    "ip": d["ip"],
                    "display_name": d["display_name"],
                    "category": d["category"],
                    "role": role,
                    "online": d["online"],
                }
            )
        first = self.db.execute("SELECT MIN(t) AS t FROM sweeps").fetchone()
        return {
            "online_now": online_now,
            "online_avg": round(sum(all_counts) / len(all_counts), 1) if all_counts else None,
            "per_hour": per_hour,
            "top_traffic": traffic[:10],
            "network_gear": gear,
            "unexpected_network_gear": sum(1 for g in gear if g["role"] == "other"),
            "ip_conflicts": self.ip_conflicts(end - 6 * 3600, end),
            "sweeps": len(all_counts),
            "since": from_epoch(first["t"]) if first and first["t"] else None,
        }

    def ip_conflicts(self, start: int, end: int) -> list[dict[str, Any]]:
        """Addresses two devices answer for at once, between ``start`` and ``end``: the ARP
        answer flipped back and forth between MACs (A, B, A ...) in the presence samples, or
        the address history has two MACs on it seen less than an hour apart, both recently."""
        by_ip: dict[str, list[tuple[int, str]]] = {}
        for r in self.db.execute(
            "SELECT t, ip, mac FROM presence WHERE t >= ? AND t < ? AND ip IS NOT NULL ORDER BY t",
            (start, end),
        ):
            by_ip.setdefault(str(r["ip"]), []).append((int(r["t"]), str(r["mac"])))
        found: dict[str, dict[str, Any]] = {}
        for ip, rows in by_ip.items():
            macs = list(dict.fromkeys(m for _, m in rows))
            if len(macs) < 2:
                continue
            flips = sum(1 for a, b in itertools.pairwise(rows) if a[1] != b[1])
            if flips >= 2:
                found[ip] = {"ip": ip, "macs": macs, "flips": flips, "source": "sweeps"}
        recent: dict[str, list[tuple[int, str]]] = {}
        for r in self.db.execute("SELECT ip, mac, last_seen FROM ip_history"):
            try:
                t = to_epoch(str(r["last_seen"]))
            except (TypeError, ValueError):
                continue
            if start <= t <= end:
                recent.setdefault(str(r["ip"]), []).append((t, str(r["mac"])))
        for ip, rows in recent.items():
            if ip in found or len(rows) < 2:
                continue
            rows.sort()
            if rows[-1][0] - rows[-2][0] <= 3600:
                found[ip] = {
                    "ip": ip,
                    "macs": [m for _, m in rows[-2:]],
                    "flips": 1,
                    "source": "ip_history",
                }
        return sorted(found.values(), key=lambda x: _ip_key(x["ip"]))
