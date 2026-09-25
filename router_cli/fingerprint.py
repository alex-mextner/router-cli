"""fingerprint — what each inventory device is (category, icon, confidence, evidence, name)
and how it is connected (wired / Wi-Fi, which mesh node, band, signal).

The classification itself is netprint (vendored in ``router_cli/_vendor/netprint``): this
module only turns what the inventory knows about a device — OUI vendor, every name it had,
web services, open ports, and the discovery facts ``router discover`` stored (mDNS, SSDP,
NetBIOS, ICMP TTL, gateway/self flags, Xiaomi mesh data) — into netprint ``Signals``.

Connection: a Xiaomi mesh (``router login --driver miwifi``) says exactly who is on Wi-Fi,
on which node and band, with what signal. Without it the answer is a heuristic, and says so
(``source: "heuristic"``): a randomized MAC or a phone/watch/IoT category means Wi-Fi; a
motherboard NIC vendor or NAS means wired; everything else is ``unknown``.
"""

from __future__ import annotations

import re
from typing import Any

from ._vendor.netprint import (
    HttpService,
    MdnsService,
    Result,
    Signals,
    SsdpDevice,
    classify,
)

WIFI_CATEGORIES = frozenset(
    {"phone", "tablet", "watch", "iot-plug", "iot-light", "iot-sensor", "ir-remote", "esp-diy"}
)
WIRED_CATEGORIES = frozenset({"nas"})
WIFI_VENDORS = re.compile(
    r"^(Espressif|Tuya|AMPAK|Bilian|Fn-link|FN-LINK|Intertech Services|Bouffalo|Beken|"
    r"Hui Zhou Gaoshengda|Sichuan AI-Link|AzureWave|Liteon|Murata|Universal Global|"
    r"Chongqing Fugui|Hon Hai|Intel Corporate|Realtek Semi)",
    re.I,
)
WIRED_VENDORS = re.compile(
    r"^(ASRock|Gigabyte|GIGA-BYTE|Micro-Star|Micro-star|Elitegroup|Biostar|Supermicro|"
    r"Synology|QNAP)",
    re.I,
)
SSDP_KEYS = (
    "server",
    "st",
    "usn",
    "location",
    "friendly_name",
    "manufacturer",
    "model_name",
    "model_number",
    "model_description",
    "device_type",
)


def build_signals(
    mac: str,
    vendor: str | None,
    names: list[str],
    services: list[dict[str, Any]],
    open_ports: list[int],
    facts: dict[str, Any],
) -> Signals:
    """netprint Signals from inventory data (``facts``: discovery source -> stored value)."""
    mdns_facts = facts.get("mdns") or {}
    mdns = [
        MdnsService(
            type=str(s.get("type") or ""),
            name=s.get("name"),
            port=s.get("port"),
            txt={str(k): str(v) for k, v in (s.get("txt") or {}).items()},
        )
        for s in mdns_facts.get("services") or []
        if s.get("type")
    ]
    ssdp = [
        SsdpDevice(**{k: (str(d[k]) if d.get(k) else None) for k in SSDP_KEYS})
        for d in (facts.get("ssdp") or {}).get("devices") or []
    ]
    http = [
        HttpService(
            port=int(s["port"]),
            title=s.get("title"),
            server=s.get("server"),
            favicon_hash=s.get("favicon_hash"),
            markers=list(s.get("markers") or []),
            status=s.get("http_status"),
        )
        for s in services
        if s.get("reachable") is not False or s.get("title")
    ]
    extra: dict[str, str] = {}
    for key, value in (facts.get("net") or {}).items():
        extra[str(key)] = str(value)
    for key, value in (facts.get("miwifi_info") or {}).items():
        if value is not None and value != "":
            extra[f"miwifi.{key}"] = str(value)
    client = facts.get("miwifi") or {}
    if client.get("is_ap"):
        extra["miwifi.is_ap"] = "1"
    if client.get("name"):
        extra["miwifi.name"] = str(client["name"])
    if client.get("connection") == "wifi":
        extra["wifi"] = "1"
    all_names = list(names)
    for extra_name in mdns_facts.get("hostnames") or []:
        if extra_name not in all_names:
            all_names.append(str(extra_name))
    ttl = (facts.get("icmp") or {}).get("ttl")
    return Signals(
        mac=mac,
        vendor=vendor,
        hostnames=all_names,
        netbios=[str(n) for n in (facts.get("netbios") or {}).get("names") or []],
        mdns=mdns,
        ssdp=ssdp,
        http=http,
        open_ports=sorted({int(p) for p in open_ports}),
        ttl=int(ttl) if isinstance(ttl, int) else None,
        extra=extra,
    )


def classify_device(signals: Signals, alias: str | None = None) -> Result:
    return classify(signals, alias=alias)


def connection(
    result: Result,
    vendor: str | None,
    random_mac: bool,
    link: dict[str, Any] | None,
    facts: dict[str, Any],
) -> dict[str, Any]:
    """The ``connection`` object of the inventory contract."""
    if link and link.get("type") in ("wired", "wifi"):
        return {
            "type": link["type"],
            "via": link.get("via"),
            "via_name": link.get("via_name"),
            "band": link.get("band"),
            "rssi": link.get("rssi"),
            "source": link.get("source") or "miwifi",
        }
    net = facts.get("net") or {}
    out: dict[str, Any] = {
        "type": "unknown",
        "via": None,
        "via_name": None,
        "band": None,
        "rssi": None,
        "source": "heuristic",
    }
    if net.get("self"):
        out.update(type="wifi" if net.get("wireless") else "wired", source="local")
        for key in ("via", "via_name", "band", "rssi"):
            if net.get(key) is not None:
                out[key] = net[key]
        return out
    if net.get("gateway") or net.get("gateway_iface"):
        out.update(type="wired")
        return out
    if random_mac or result.category in WIFI_CATEGORIES or WIFI_VENDORS.search(vendor or ""):
        out["type"] = "wifi"
    elif result.category in WIRED_CATEGORIES or WIRED_VENDORS.search(vendor or ""):
        out["type"] = "wired"
    return out
