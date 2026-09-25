"""models — the router-independent shapes every driver returns.

Home Assistant, an agent and a human all get the same JSON from an Ubee cable gateway and
an OpenWrt box. A driver's job is to fill these in; a field a router does not report stays
``None`` rather than being invented. MAC addresses are always lowercase, colon-separated.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from ._errors import UsageError

_MAC_HEX = re.compile(r"[0-9a-fA-F]")


def normalize_mac(text: str) -> str:
    """Accept aa:bb:cc:dd:ee:ff, AA-BB-..., aa_bb_..., aabb.ccdd.eeff or aabbccddeeff (any
    case); return aa:bb:cc:dd:ee:ff."""
    digits = "".join(_MAC_HEX.findall(text))
    stripped = re.sub(r"[\s:.\-_]", "", text)
    if len(digits) != 12 or len(stripped) != 12:
        raise UsageError(
            what=f"{text!r} is not a MAC address",
            why="a MAC address is six hex octets",
            how="write it like 02:00:00:00:00:01",
        )
    digits = digits.lower()
    return ":".join(digits[i : i + 2] for i in range(0, 12, 2))


def is_mac(text: str) -> bool:
    try:
        normalize_mac(text)
    except UsageError:
        return False
    return True


def is_random_mac(mac: str) -> bool:
    """Locally administered (bit 1 of the first octet): phones' private addresses, VMs."""
    try:
        first = int(normalize_mac(mac)[:2], 16)
    except (UsageError, ValueError):
        return False
    return bool(first & 0x02)


def is_ipv4(text: str) -> bool:
    try:
        ipaddress.IPv4Address(text.strip())
    except ValueError:
        return False
    return True


def validate_ipv4(text: str) -> str:
    try:
        return str(ipaddress.IPv4Address(text.strip()))
    except ValueError as exc:
        raise UsageError(
            what=f"{text!r} is not an IPv4 address",
            why=str(exc),
            how="write it like 192.168.0.50",
        ) from exc


@dataclass
class RouterInfo:
    driver: str
    host: str
    model: str = ""
    vendor: str = ""
    firmware: str = ""
    hardware: str = ""
    serial: str = ""


@dataclass
class WanInfo:
    ipv4: str | None = None
    netmask: str | None = None
    gateway: str | None = None
    dns: list[str] = field(default_factory=list)
    mac: str | None = None
    lease_time_s: int | None = None
    hostname: str | None = None


@dataclass
class DocsisChannel:
    direction: str  # downstream | upstream
    channel: int
    locked: bool
    modulation: str
    frequency_hz: int | None
    power_dbmv: float | None
    snr_db: float | None = None
    symbol_rate_ksym: int | None = None
    correctable: int | None = None
    uncorrectable: int | None = None


@dataclass
class DocsisSummary:
    mode: str | None = None
    network_access: str | None = None
    downstream_locked: int = 0
    downstream_total: int = 0
    upstream_locked: int = 0
    upstream_total: int = 0
    downstream_power_dbmv: list[float] = field(default_factory=list)  # [min, max]
    downstream_snr_db: list[float] = field(default_factory=list)  # [min, max]
    upstream_power_dbmv: list[float] = field(default_factory=list)  # [min, max]
    uncorrectable_total: int = 0
    provisioning: dict[str, str] = field(default_factory=dict)


@dataclass
class Status:
    router: RouterInfo
    uptime_s: int | None = None
    uptime_text: str | None = None
    wan: WanInfo | None = None
    docsis: DocsisSummary | None = None
    lan_ip: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Device:
    """A client the router currently knows about."""

    mac: str
    ip: str | None = None
    hostname: str | None = None
    interface: str = "lan"  # lan | wifi
    band: str | None = None  # "2.4GHz" | "5GHz" | None
    rssi_dbm: int | None = None
    online: bool = True
    speed_kbps: int | None = None
    mode: str | None = None
    connected_s: int | None = None
    lease_expires: str | None = None
    static_ip: bool = False  # the device reported a self-assigned static address


@dataclass
class Lease:
    mac: str
    ip: str
    hostname: str | None = None
    kind: str = "dynamic"  # dynamic | reservation | static
    expires: str | None = None
    active: bool = True


@dataclass
class Reservation:
    """A static DHCP lease ("pin this MAC to this IP")."""

    mac: str
    ip: str
    name: str | None = None
    slot: str | None = None


@dataclass
class PortForward:
    index: int
    local_ip: str
    local_start: int
    local_end: int
    external_ip: str | None
    external_start: int
    external_end: int
    protocol: str
    description: str = ""
    enabled: bool = True


def to_json(value: Any) -> Any:
    """Dataclasses (and lists of them) to plain JSON-able structures."""
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [to_json(v) for v in value]
    if isinstance(value, dict):
        return {k: to_json(v) for k, v in value.items()}
    return value
