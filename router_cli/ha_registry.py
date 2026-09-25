"""ha_registry — what Home Assistant already knows about LAN devices (read-only).

Home Assistant's device registry names devices, knows their manufacturer, model, firmware
and room (area), and for many integrations (ESPHome, Cast, Samsung TV, DLNA, Android TV...)
records their MAC addresses or their own device ids (a Cast UUID, a Yandex Station id, a
UPnP UDN); integrations configured by address (Moonraker, Creality, Android TV Remote, ...)
keep the host in their config entry. That is the user's own curated knowledge — the best
evidence there is — so ``router discover --ha-config <HA config dir>`` reads it straight from
``.storage/core.device_registry``, ``core.config_entries`` and ``core.area_registry`` (never
writes) and stores, per MAC:

    {"name", "manufacturer", "model", "model_id", "sw_version", "area", "domains": [...],
     "title", "macs": [...], "matched": "mac" | "id" | "host" | "name"}

Secrets in config entries are never read into the result: only ``host``/``url``/
``ip_address``/``mac`` and the entry's title and domain are used.
"""

from __future__ import annotations

import ipaddress
import json
import re
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import is_mac, is_random_mac, normalize_mac

HOST_KEYS = ("host", "url", "ip_address", "ip", "address")
# Integrations whose devices carry neither a MAC nor a host, but whose device name is the
# device's own network name (the iOS/Android companion app: the phone's name = its hostname).
NAME_MATCH_DOMAINS = frozenset({"mobile_app"})
SKIP_DOMAINS = frozenset({"homekit", "bluetooth", "ibeacon", "backup", "sun", "met", "zha"})
# Registry "manufacturer"/"model" values that describe software, not the device.
JUNK_VALUES = frozenset({"integration", "service", "unknown", "none", "", "-"})
MIN_ID_LEN = 8


def normalize_id(value: Any) -> str | None:
    """A device id compared across sources: 'uuid:68733FD4-5EA8-...' == '68733fd45ea8...'."""
    text = str(value or "").strip().lower()
    text = text.removeprefix("uuid:")
    text = re.sub(r"[^0-9a-z]", "", text)
    return text if len(text) >= MIN_ID_LEN else None


@dataclass
class HaDevice:
    name: str | None
    manufacturer: str | None
    model: str | None
    domains: list[str] = field(default_factory=list)
    title: str | None = None
    macs: list[str] = field(default_factory=list)
    hosts: list[str] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)  # normalized identifiers / UPnP UDNs
    model_id: str | None = None
    sw_version: str | None = None
    area: str | None = None

    def facts(self, matched: str) -> dict[str, Any]:
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "model_id": self.model_id,
            "sw_version": self.sw_version,
            "area": self.area,
            "domains": self.domains,
            "title": self.title,
            "macs": self.macs,
            "matched": matched,
        }


def _lan_ip(value: Any) -> str | None:
    text = str(value or "").strip()
    if "://" in text:
        text = urllib.parse.urlsplit(text).hostname or ""
    text = text.split(":")[0] if text.count(":") == 1 else text
    try:
        ip = ipaddress.IPv4Address(text)
    except ValueError:
        return None
    return str(ip) if ip.is_private and not ip.is_loopback else None


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, ValueError):
        return None


def _clean(value: Any, domains: Iterable[str]) -> str | None:
    """None for empty values and for software names ("moonraker" by the moonraker domain)."""
    text = " ".join(str(value or "").split())
    if text.lower() in JUNK_VALUES or text.lower() in {d.lower() for d in domains}:
        return None
    return text


def load(config_dir: Path) -> list[HaDevice]:
    """Every registry device that carries a MAC, a device id, or whose config entry names a
    LAN host."""
    storage = config_dir / ".storage"
    registry = _read(storage / "core.device_registry")
    entries_doc = _read(storage / "core.config_entries")
    if not isinstance(registry, dict) or not isinstance(entries_doc, dict):
        return []
    entries = {
        e.get("entry_id"): e
        for e in (entries_doc.get("data") or {}).get("entries") or []
        if isinstance(e, dict)
    }
    areas_doc = _read(storage / "core.area_registry")
    areas = {
        str(a.get("id")): str(a.get("name"))
        for a in ((areas_doc or {}).get("data") or {}).get("areas") or []
        if isinstance(a, dict) and a.get("id") and a.get("name")
    }
    raw_devices = [
        d
        for d in (registry.get("data") or {}).get("devices") or []
        if isinstance(d, dict) and not d.get("disabled_by")
    ]

    def entry_ids_of(dev: dict[str, Any]) -> list[str]:
        ids = list(dev.get("config_entries") or [])
        for key in ("config_entry_id", "primary_config_entry"):
            if dev.get(key) and dev[key] not in ids:
                ids.append(dev[key])
        return ids

    # An entry's title names its device only when the entry HAS one device (Android TV
    # Remote "Living room", Moonraker "Printer"); a hub entry's title ("Music Assistant", a
    # cloud account's login) names nothing on the LAN.
    per_entry: dict[str, int] = {}
    for dev in raw_devices:
        for eid in entry_ids_of(dev):
            per_entry[eid] = per_entry.get(eid, 0) + 1
    out: list[HaDevice] = []
    for dev in raw_devices:
        entry_ids = entry_ids_of(dev)
        dev_entries = [entries[i] for i in entry_ids if i in entries]
        domains = sorted({str(e.get("domain")) for e in dev_entries if e.get("domain")})
        if domains and set(domains) <= SKIP_DOMAINS:
            continue
        macs: list[str] = []
        ids: list[str] = []
        for conn in dev.get("connections") or []:
            if not (isinstance(conn, list | tuple) and len(conn) == 2):
                continue
            if conn[0] in ("mac", "network_mac") and is_mac(str(conn[1])):
                mac = normalize_mac(str(conn[1]))
                if mac not in macs:
                    macs.append(mac)
            elif conn[0] in ("upnp", "ssdp", "uuid"):
                nid = normalize_id(conn[1])
                if nid and nid not in ids:
                    ids.append(nid)
        for ident in dev.get("identifiers") or []:
            if isinstance(ident, list | tuple) and len(ident) == 2 and ident[0] != "hacs":
                nid = normalize_id(ident[1])
                if nid and nid not in ids and not is_mac(str(ident[1])):
                    ids.append(nid)
        hosts: list[str] = []
        for entry in dev_entries:
            data = entry.get("data") or {}
            for key in HOST_KEYS:
                ip = _lan_ip(data.get(key))
                if ip and ip not in hosts:
                    hosts.append(ip)
            entry_mac = data.get("mac")
            if (
                isinstance(entry_mac, str)
                and is_mac(entry_mac)
                and normalize_mac(entry_mac) not in macs
            ):
                macs.append(normalize_mac(entry_mac))
        if not macs and not hosts and not ids and not set(domains) & NAME_MATCH_DOMAINS:
            continue
        title = next(
            (
                str(e.get("title"))
                for e in dev_entries
                if e.get("title") and per_entry.get(str(e.get("entry_id"))) == 1
            ),
            None,
        )
        out.append(
            HaDevice(
                name=dev.get("name_by_user") or dev.get("name"),
                manufacturer=_clean(dev.get("manufacturer"), domains),
                model=_clean(dev.get("model"), domains),
                domains=domains,
                title=title,
                macs=macs,
                hosts=hosts,
                ids=ids,
                model_id=_clean(dev.get("model_id"), domains),
                sw_version=_clean(dev.get("sw_version"), domains),
                area=areas.get(str(dev.get("area_id") or "")),
            )
        )
    return out


def _name_key(name: str) -> str:
    """'Kitchen-Phone-2.local' -> 'kitchen-phone' (iOS adds -2, -3 on name clashes)."""
    text = name.strip().lower().removesuffix(".local").removesuffix(".lan")
    return re.sub(r"-\d{1,2}$", "", text)


def facts_by_mac(
    devices: list[HaDevice],
    ip_to_mac: dict[str, str],
    names: dict[str, list[str]] | None = None,
    ids: dict[str, set[str]] | None = None,
    online: dict[str, str] | None = None,
    seen: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """{mac: facts}, matching a registry device, best evidence first:

    1. by the MACs in its connections (a device with more MACs wins a shared MAC);
    2. by a device id the device announced on the LAN (``ids``: MAC -> normalized ids from
       mDNS TXT / SSDP UDNs) equal to one of its registry identifiers: a Yandex Station's
       ``deviceId``, a Cast UUID, a UPnP UDN;
    3. by the host of its config entry, resolved through the inventory's current / reserved /
       historical addresses (``ip_to_mac``) onto a globally unique MAC; or, when none of the
       registry's own MACs was ever seen on the LAN (``seen``), onto whichever MAC is online
       at that address right now (``online``: ip -> MAC). That is how a Chromecast on a
       private Wi-Fi address meets its registry entry, which has the real MAC;
    4. companion-app devices (no MAC, no host) by name: the phone's name is its hostname.
       Several devices of the same name (two phones called alike) give the shared model
       family only.

    One physical device often has several registry devices (a Chromecast: Android TV Remote
    with its MAC and room, Cast, a Music Assistant player). Every match adds what the better
    ones left empty (room, firmware, MACs, integrations); the best match names the device.
    """
    out: dict[str, dict[str, Any]] = {}
    seen = seen or set()
    done: set[tuple[str, int]] = set()

    def add(mac: str, dev: HaDevice, matched: str) -> None:
        if (mac, id(dev)) in done:
            return
        done.add((mac, id(dev)))
        facts = dev.facts(matched)
        have = out.get(mac)
        if have is None:
            out[mac] = facts
            return
        have["macs"] = list(dict.fromkeys([*have["macs"], *facts["macs"]]))
        have["domains"] = sorted(set(have["domains"]) | set(facts["domains"]))
        for key, value in facts.items():
            if have.get(key) in (None, "") and value not in (None, ""):
                have[key] = value

    for dev in sorted(devices, key=lambda d: -len(d.macs)):
        for mac in dev.macs:
            if mac not in out:
                add(mac, dev, "mac")
    by_id: dict[str, list[HaDevice]] = {}
    for dev in devices:
        for nid in dev.ids:
            by_id.setdefault(nid, []).append(dev)
    for mac, mac_ids in (ids or {}).items():
        for nid in sorted(mac_ids):
            for dev in by_id.get(nid, []):
                add(mac, dev, "id")
    for dev in devices:
        for ip in dev.hosts:
            held_by = ip_to_mac.get(ip)
            if held_by and not is_random_mac(held_by):
                add(held_by, dev, "host")
                continue
            now_at = (online or {}).get(ip)
            if now_at and not any(m in seen for m in dev.macs):
                add(now_at, dev, "host")
    by_name: dict[str, list[HaDevice]] = {}
    for dev in devices:
        if dev.name and not dev.macs and not dev.hosts and set(dev.domains) & NAME_MATCH_DOMAINS:
            by_name.setdefault(_name_key(dev.name), []).append(dev)
    for mac, mac_names in (names or {}).items():
        if mac in out:
            continue
        for name in mac_names:
            found = by_name.get(_name_key(name))
            if not found:
                continue
            facts = found[0].facts("name")
            if len(found) > 1:
                models = {str(d.model or "") for d in found}
                family = re.sub(r"\d.*$", "", sorted(models)[0])
                if len(models) > 1:
                    facts["model"] = family if all(m.startswith(family) for m in models) else None
                    facts["model_id"] = None
                if len({d.sw_version for d in found}) > 1:
                    facts["sw_version"] = None
            out[mac] = facts
            break
    return out
