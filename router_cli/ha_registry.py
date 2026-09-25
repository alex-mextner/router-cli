"""ha_registry — what Home Assistant already knows about LAN devices (read-only).

Home Assistant's device registry names devices, knows their manufacturer and model, and for
many integrations (ESPHome, Cast, Samsung TV, DLNA, Android TV...) records their MAC
addresses; integrations configured by address (Moonraker, Creality, ESPHome, ...) keep the
host in their config entry. That is the user's own curated knowledge — the best evidence
there is — so ``router discover --ha-config <HA config dir>`` reads it straight from
``.storage/core.device_registry`` and ``.storage/core.config_entries`` (never writes) and
stores, per MAC:

    {"name", "manufacturer", "model", "domains": [...], "title", "macs": [...],
     "matched": "mac" | "host" | "name"}

Secrets in config entries are never read into the result: only ``host``/``url``/
``ip_address`` and the entry's title and domain are used.
"""

from __future__ import annotations

import ipaddress
import json
import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import is_mac, is_random_mac, normalize_mac

HOST_KEYS = ("host", "url", "ip_address", "ip", "address")
# Integrations whose devices carry neither a MAC nor a host, but whose device name is the
# device's own network name (the iOS/Android companion app: the phone's name = its hostname).
NAME_MATCH_DOMAINS = frozenset({"mobile_app"})
SKIP_DOMAINS = frozenset({"homekit", "bluetooth", "ibeacon", "backup", "sun", "met", "zha"})


@dataclass
class HaDevice:
    name: str | None
    manufacturer: str | None
    model: str | None
    domains: list[str] = field(default_factory=list)
    title: str | None = None
    macs: list[str] = field(default_factory=list)
    hosts: list[str] = field(default_factory=list)

    def facts(self, matched: str) -> dict[str, Any]:
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
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


def load(config_dir: Path) -> list[HaDevice]:
    """Every registry device that carries a MAC or whose config entry names a LAN host."""
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
    out: list[HaDevice] = []
    for dev in (registry.get("data") or {}).get("devices") or []:
        if not isinstance(dev, dict) or dev.get("disabled_by"):
            continue
        entry_ids = list(dev.get("config_entries") or [])
        for key in ("config_entry_id", "primary_config_entry"):
            if dev.get(key) and dev[key] not in entry_ids:
                entry_ids.append(dev[key])
        dev_entries = [entries[i] for i in entry_ids if i in entries]
        domains = sorted({str(e.get("domain")) for e in dev_entries if e.get("domain")})
        if domains and set(domains) <= SKIP_DOMAINS:
            continue
        macs: list[str] = []
        for conn in dev.get("connections") or []:
            if (
                isinstance(conn, list | tuple)
                and len(conn) == 2
                and conn[0] in ("mac", "network_mac")
                and is_mac(str(conn[1]))
            ):
                mac = normalize_mac(str(conn[1]))
                if mac not in macs:
                    macs.append(mac)
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
        if not macs and not hosts and not set(domains) & NAME_MATCH_DOMAINS:
            continue
        title = next((str(e.get("title")) for e in dev_entries if e.get("title")), None)
        out.append(
            HaDevice(
                name=dev.get("name_by_user") or dev.get("name"),
                manufacturer=dev.get("manufacturer"),
                model=dev.get("model"),
                domains=domains,
                title=title,
                macs=macs,
                hosts=hosts,
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
) -> dict[str, dict[str, Any]]:
    """{mac: facts}, matching a registry device, best evidence first:

    1. by the MACs in its connections (a device with more MACs wins a shared MAC);
    2. by the host of its config entry, resolved through the inventory's current / reserved /
       historical addresses — only onto a globally unique (not randomized) MAC, since a
       randomized device's address is soon reused by someone else;
    3. companion-app devices (no MAC, no host) by name: the phone's name is its hostname.
       Several devices of the same name (two phones called alike) give the shared model
       family only.
    """
    out: dict[str, dict[str, Any]] = {}
    for dev in sorted(devices, key=lambda d: -len(d.macs)):
        for mac in dev.macs:
            out.setdefault(mac, dev.facts("mac"))
    for dev in devices:
        for ip in dev.hosts:
            held_by = ip_to_mac.get(ip)
            if held_by and held_by not in out and not is_random_mac(held_by):
                out[held_by] = dev.facts("host")
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
            out[mac] = facts
            break
    return out
