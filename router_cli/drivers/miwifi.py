"""miwifi — Xiaomi / Redmi routers and mesh systems through their local LuCI JSON API.

A Xiaomi mesh in access-point (bridge) mode still knows every Wi-Fi client: which node and
band it is on, its signal, and per-device traffic counters. None of that reaches the main
router (to the gateway, bridged Wi-Fi clients look like LAN clients), so this driver is the
only source of per-client Wi-Fi topology and traffic on such a network.

PROTOCOL (read-only here)
    ``GET  /cgi-bin/luci/api/xqsystem/init_info``  public: model, hardware, ``wifi_ap`` (1 =
                                                   AP/bridge mode), ``newEncryptMode``
    ``POST /cgi-bin/luci/api/xqsystem/login``      ``username=admin&logtype=2&nonce=N&
                                                   password=H(N + H(pw + KEY))`` -> ``token``
                                                   (H = SHA-256 when newEncryptMode=1, else SHA-1)
    ``GET  /cgi-bin/luci/;stok=T/api/xqsystem/device_list``   the richest client list: mac,
                                                   ip, name / origin_name, ``parent`` (MAC of
                                                   the satellite the client is on; "" = this
                                                   node), ``port`` (0 wired, 1 2.4 GHz, 2 5
                                                   GHz), ``type`` ("line" | "wifi" | "ap" = on
                                                   a satellite), ``statistics``: upload /
                                                   download totals (bytes), upspeed / downspeed
                                                   (B/s), ``online`` (seconds connected)
    ``GET  /cgi-bin/luci/;stok=T/api/misystem/devicelist``   the same clients, older shape:
                                                   ``type`` 0/1/2 (wired / 2.4 / 5), rates
                                                   but no totals (fallback)
    ``GET  /cgi-bin/luci/;stok=T/api/misystem/status``       ``hardware.mac``: this node's
                                                   LAN MAC; ``dev``: totals for some clients
    ``GET  /cgi-bin/luci/;stok=T/api/xqnetwork/wifi_connect_devices``   the stations
                                                   associated to THIS node's radios: mac,
                                                   ``wifiIndex`` (1 2.4 GHz, 2 5 GHz) and
                                                   ``signal`` (see SIGNAL)
    ``GET  /cgi-bin/luci/api/misystem/topo_graph``  public on current firmware: every node
                                                   (``ip``, ``name``, ``locale`` = the
                                                   placement set in the app, ``hardware``,
                                                   ``mode``; satellites under ``leafs`` with
                                                   ``link_type`` wired/wireless, ``onlines``)
    ``GET  /cgi-bin/luci/;stok=T/web/logout``      ends the session (kind="logout"; answers
                                                   with a redirect to the login page)

MESH
    Only the root node (``mode`` 2 in topo_graph, netmode 2) keeps the client list with IPs,
    names and traffic; a satellite (mode 1, netmode 3) answers ``device_list`` with bare MACs
    and ``status.dev`` empty. Every node answers ``wifi_connect_devices`` for its own radios,
    and that list is longer than the root's client list (clients it has no IP for), so a
    complete picture asks every node and merges by MAC (``merge_clients``). The admin password
    is shared across the mesh.

SIGNAL
    ``signal`` is not dBm: it is a positive number (about 40..150), which the web UI only
    buckets (> 30 "Good"). It reads as twice the SNR over a -95 dBm noise floor: a station
    that measured the node at -54 dBm (average) was reported as 84 -> 84 / 2 - 95 = -53.
    ``rssi`` is that estimate; the raw value is kept as ``signal``.

    Verified against firmware 1.0.148 (RD28 "Mesh System AX3000 NE", root + one wired
    satellite); fixtures under tests/fixtures/miwifi are those answers, anonymised. No
    endpoint reports the link rate (PHY speed) of a client.

    Current firmware answers everything but ``init_info`` on plain HTTP with a redirect to
    HTTPS (self-signed certificate); ``HttpTransport`` follows it. Over IPv6 link-local the
    node's nginx wants ``Host: localhost`` (``HttpTransport(host_header=...)``).
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import time
from dataclasses import dataclass
from typing import Any, ClassVar

from .._errors import NotLoggedInError, RouterCliError, RouterError
from ..http import HttpRequest, Transport
from ..models import Device, RouterInfo, is_mac, normalize_mac
from .base import BaseDriver, Capability

# Not a secret: the fixed salt every Xiaomi router's web UI uses to hash the password before
# sending it (it ships in the firmware's public JavaScript and in open-source integrations).
KEY = "a2ffa5c9be07488bbb04a3a47d3c5f6a"  # gitleaks:allow
INIT_INFO = "/cgi-bin/luci/api/xqsystem/init_info"
TOPO_GRAPH = "/cgi-bin/luci/api/misystem/topo_graph"
LOGIN = "/cgi-bin/luci/api/xqsystem/login"
# devicelist ``type`` / device_list ``port`` / wifi_connect_devices ``wifiIndex`` -> band
BANDS = {0: None, 1: "2.4", 2: "5", 3: "2.4", 6: "5", 7: "6"}
WIFI_INDEX_BANDS = {1: "2.4", 2: "5", 3: "2.4"}
NOISE_FLOOR_DBM = -95
TOKEN_RE = re.compile(r";stok=[0-9a-fA-F]+")


@dataclass
class MiClient:
    """One client as the Xiaomi router sees it (all optional except mac)."""

    mac: str
    ip: str | None = None
    name: str | None = None
    connection: str = "unknown"  # wired | wifi | unknown
    band: str | None = None  # "2.4" | "5" | "6"
    guest: bool = False
    via: str | None = None  # LAN MAC of the mesh node the client hangs off
    rssi: int | None = None  # dBm, estimated from ``signal``
    signal: int | None = None  # the firmware's raw station signal (not dBm, see SIGNAL)
    online: bool = True
    is_ap: bool = False
    connected_s: int | None = None  # seconds since the client (re)connected
    rx_bytes: int | None = None  # received BY the client (router "download")
    tx_bytes: int | None = None
    rx_rate: float | None = None  # bytes/s
    tx_rate: float | None = None

    def to_json(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _mac(value: Any) -> str | None:
    text = str(value or "")
    return normalize_mac(text) if text and is_mac(text) else None


def _name(*values: Any) -> str | None:
    """The first real name: the firmware fills ``name`` with the MAC when it knows none."""
    for value in values:
        text = str(value or "").strip()
        if text and not is_mac(text):
            return text
    return None


def signal_to_dbm(signal: Any) -> int | None:
    """The firmware's station ``signal`` (twice the SNR) as an estimated RSSI in dBm."""
    value = _int(signal)
    if value is None or value <= 0:
        return None
    return max(-100, min(-10, round(value / 2) + NOISE_FLOOR_DBM))


def password_hash(password: str, nonce: str, sha256: bool) -> str:
    h = hashlib.sha256 if sha256 else hashlib.sha1
    # codeql[py/weak-sensitive-data-hashing]
    # Justified: this is not storing a password, it is the Xiaomi login protocol itself: the
    # router accepts only H(nonce + H(password + KEY)) with H = SHA-256 (or SHA-1 on old
    # firmware). The result goes over the LAN once and is never stored.
    return h((nonce + h((password + KEY).encode()).hexdigest()).encode()).hexdigest()


def make_nonce(device_mac: str | None = None) -> str:
    tail = ":".join(f"{random.randrange(256):02x}" for _ in range(3))
    mac = device_mac or f"02:00:00:{tail}"
    return f"0_{mac}_{int(time.time())}_{random.randint(0, 9999)}"


def _items(payload: dict[str, Any] | None, key: str) -> list[dict[str, Any]]:
    raw = (payload or {}).get(key)
    return [x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _set_traffic(c: MiClient, stats: dict[str, Any]) -> None:
    """``upload``/``download`` are from the client's side of the router: the client's
    upload is what it sent (tx)."""
    for attr, key in (
        ("rx_bytes", "download"),
        ("tx_bytes", "upload"),
        ("rx_rate", "downspeed"),
        ("tx_rate", "upspeed"),
    ):
        value = _int(stats.get(key))
        if value is not None:
            setattr(c, attr, value)


def self_mac_of(status: dict[str, Any] | None) -> str | None:
    """This node's LAN MAC, from ``misystem/status`` (``hardware.mac``)."""
    hardware = (status or {}).get("hardware")
    return _mac(hardware.get("mac")) if isinstance(hardware, dict) else None


def parse_clients(
    devicelist: dict[str, Any] | None,
    status: dict[str, Any] | None = None,
    wifi: dict[str, Any] | None = None,
    self_mac: str | None = None,
    device_list: dict[str, Any] | None = None,
) -> list[MiClient]:
    """One node's view, merged by MAC: ``xqsystem/device_list`` (preferred) or
    ``misystem/devicelist`` (names, IPs, node, band, connected time, traffic), ``status.dev``
    (traffic, where the list had none) and ``wifi_connect_devices`` (who is on this node's
    radios, band, signal)."""
    self_mac = self_mac or self_mac_of(status)
    clients: dict[str, MiClient] = {}
    rich = [x for x in _items(device_list, "list") if "ip" in x or "statistics" in x]
    for item in rich:
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        port = _int(item.get("port"))
        kind = str(item.get("type") or "")
        stats = _dict(item.get("statistics"))
        wired = kind == "line" or (port == 0 and kind not in ("wifi", "ap"))
        wifi_client = not wired and (kind in ("wifi", "ap") or bool(port))
        c = clients[mac] = MiClient(
            mac=mac,
            ip=str(item.get("ip") or "") or None,
            name=_name(item.get("name"), item.get("origin_name"), item.get("hostname")),
            connection="wired" if wired else "wifi" if wifi_client else "unknown",
            band=BANDS.get(port) if wifi_client and port is not None else None,
            guest=port == 3,
            via=_mac(item.get("parent")) or self_mac,
            online=str(item.get("online", "1")) not in ("0", "false", "False"),
            is_ap=str(item.get("isap", "0")) not in ("0", "", "None", "False"),
            connected_s=_int(stats.get("online")),
        )
        _set_traffic(c, stats)
    for item in [] if rich else _items(devicelist, "list"):
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        ctype = _int(item.get("type"))
        ip = None
        for entry in _items(item, "ip"):
            if entry.get("ip"):
                ip = str(entry["ip"])
                break
        stats = _dict(item.get("statistics"))
        c = clients[mac] = MiClient(
            mac=mac,
            ip=ip,
            name=_name(item.get("name"), item.get("oname")),
            connection="wired" if ctype == 0 else "wifi" if ctype in BANDS else "unknown",
            band=BANDS.get(ctype) if ctype is not None else None,
            guest=ctype == 3,
            via=_mac(item.get("parent")) or self_mac,
            online=str(item.get("online", "1")) not in ("0", "false", "False"),
            is_ap=str(item.get("isap", "0")) not in ("0", "", "None", "False"),
            connected_s=_int(stats.get("online")),
        )
        _set_traffic(c, stats)
    for item in _items(status, "dev"):
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        c = clients.setdefault(mac, MiClient(mac=mac, via=self_mac))
        c.name = c.name or _name(item.get("devname"))
        if c.rx_bytes is None:
            _set_traffic(c, item)
        if c.connected_s is None:
            c.connected_s = _int(item.get("online"))
    for item in _items(wifi, "list"):
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        c = clients.setdefault(mac, MiClient(mac=mac))
        c.connection = "wifi"
        c.via = self_mac or c.via  # associated to this node's radio, whatever the list said
        index = _int(item.get("wifiIndex"))
        c.band = WIFI_INDEX_BANDS.get(index or 0) or c.band
        c.guest = c.guest or index == 3
        raw = _int(item.get("signal"))
        if raw is not None and raw < 0:  # some firmware reports dBm directly
            c.rssi = raw
        elif raw:
            c.signal = raw
            c.rssi = signal_to_dbm(raw)
    return sorted(clients.values(), key=lambda c: c.mac)


def merge_clients(views: list[list[MiClient]]) -> list[MiClient]:
    """Every node's view in one list. A node that has the client on its own radio (it
    reported a signal) decides node, band and signal; other fields fill in from any view."""
    merged: dict[str, MiClient] = {}
    for view in views:
        for c in view:
            have = merged.get(c.mac)
            if have is None:
                merged[c.mac] = MiClient(**c.to_json())
                continue
            radio = c.rssi is not None and have.rssi is None
            for key, value in c.to_json().items():
                if key in ("via", "band", "rssi", "signal", "connection") and radio:
                    if value is not None:
                        setattr(have, key, value)
                elif getattr(have, key) is None and value is not None:
                    setattr(have, key, value)
            if have.connection == "unknown":
                have.connection = c.connection
            have.guest = have.guest or c.guest
            have.is_ap = have.is_ap or c.is_ap
    return sorted(merged.values(), key=lambda c: c.mac)


def parse_mesh_nodes(topo: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Every node of ``topo_graph``, root first: ``{mac, ip, name, locale, hardware, root,
    mode, link_type, clients}``. ``locale`` is the placement the user picked in the Mi Home /
    Xiaomi WiFi app ("Bedroom", "Living room"); ``name`` the router name; ``mac`` is often
    absent (the graph identifies nodes by address), ``link_type`` is the satellite's
    backhaul ("wired" / "wireless")."""
    out: list[dict[str, Any]] = []

    def walk(node: Any, root: bool) -> None:
        if not isinstance(node, dict):
            return
        mac = _mac(node.get("mac") or node.get("macaddr"))
        ip = str(node.get("ip") or "") or None
        if mac or ip:
            out.append(
                {
                    "mac": mac,
                    "ip": ip,
                    "name": (str(node.get("name") or "").strip() or None),
                    "locale": (str(node.get("locale") or "").strip() or None),
                    "hardware": node.get("hardware"),
                    "root": root,
                    "mode": _int(node.get("mode")),
                    "link_type": node.get("link_type"),
                    "clients": _int(node.get("onlines")),
                }
            )
        for child in node.get("leafs") or node.get("nodes") or []:
            walk(child, False)

    walk((topo or {}).get("graph"), True)
    return out


class MiWiFi(BaseDriver):
    name: ClassVar[str] = "miwifi"
    title: ClassVar[str] = "Xiaomi MiWiFi router / mesh (local LuCI JSON API)"
    vendor: ClassVar[str] = "Xiaomi"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(
        {Capability.DEVICES, Capability.LOGIN}
    )
    access_point: ClassVar[bool] = True
    notes: ClassVar[list[str]] = [
        "read-only: Wi-Fi clients, mesh node, band, signal, per-client traffic",
        "login: `router login --driver miwifi --host <node> --no-default` (user admin)",
        "on a mesh the root node has IPs/names/traffic; each node has its own radios' "
        "stations: `router discover` asks every node (same admin password)",
        "rssi is estimated from the firmware's signal figure (not reported in dBm)",
    ]

    def __init__(self, transport: Transport, credentials: Any = None) -> None:
        super().__init__(transport, credentials)
        self._token: str | None = None
        self._init: dict[str, Any] | None = None
        self.lan_mac: str | None = None  # this node's LAN MAC, once ``clients`` ran

    # ── session ──────────────────────────────────────────────────────────────
    @classmethod
    def probe(cls, transport: Transport) -> str | None:
        try:
            data = json.loads(transport.get(INIT_INFO))
        except (RouterCliError, ValueError):
            return None
        if isinstance(data, dict) and str(data.get("model", "")).startswith("xiaomi.router"):
            return str(data.get("displayName") or data.get("hardware") or data["model"])
        return None

    def init_info(self) -> dict[str, Any]:
        if self._init is None:
            try:
                data = json.loads(self.transport.get(INIT_INFO))
            except ValueError as exc:
                raise RouterError(what="init_info is not JSON", why=str(exc), how="") from exc
            self._init = data if isinstance(data, dict) else {}
        return self._init

    def login(self, user: str, password: str) -> None:
        info = self.init_info()
        nonce = make_nonce()
        hashed = password_hash(password, nonce, sha256=str(info.get("newEncryptMode")) == "1")
        request = HttpRequest(
            "POST",
            LOGIN,
            kind="login",
            fields=(
                ("username", user or "admin"),
                ("password", hashed),
                ("logtype", "2"),
                ("nonce", nonce),
            ),
            secret_fields=frozenset({"password"}),
        )
        try:
            reply = json.loads(self.transport.send(request))
        except (ValueError, RouterError) as exc:
            raise NotLoggedInError(
                what="the Xiaomi router rejected the login",
                why=str(getattr(exc, "what", exc)),
                how="check the admin password (the one for the router's web page)",
            ) from exc
        token = reply.get("token") if isinstance(reply, dict) else None
        if not token or reply.get("code") not in (0, "0"):
            raise NotLoggedInError(
                what="the Xiaomi router rejected the login",
                why=f"code {reply.get('code') if isinstance(reply, dict) else '?'}",
                how="check the admin password (the one for the router's web page)",
            )
        self._token = str(token)

    def session_active(self) -> bool:
        return self._token is not None

    def end_session(self) -> bool:
        if not self._token:
            return False
        try:
            self.transport.send(
                HttpRequest("GET", f"/cgi-bin/luci/;stok={self._token}/web/logout", kind="logout")
            )
        except RouterCliError:
            return False
        finally:
            self._token = None
        return True

    def _ensure_login(self) -> str:
        if self._token:
            return self._token
        creds = self.credentials() if self.credentials else None
        if creds is None:
            raise NotLoggedInError(
                what="no Xiaomi router credentials stored",
                why="the client list needs an admin session",
                how=f"run `router login --driver miwifi --host {self.bare_host} --no-default`",
            )
        self.login(*creds)
        assert self._token is not None
        return self._token

    def api(self, path: str) -> dict[str, Any]:
        """GET ``/api/<path>`` with the session token (re-login once if it expired)."""
        for attempt in (0, 1):
            token = self._ensure_login()
            try:
                text = self.transport.get(f"/cgi-bin/luci/;stok={token}/api/{path}")
            except RouterError as exc:
                raise RouterError(
                    what=TOKEN_RE.sub(";stok=<token>", exc.what), why=exc.why, how=exc.how
                ) from None
            try:
                data = json.loads(text)
            except ValueError as exc:
                raise RouterError(what=f"api/{path} is not JSON", why=text[:80], how="") from exc
            if isinstance(data, dict) and data.get("code") in (401, "401") and attempt == 0:
                self._token = None
                continue
            if not isinstance(data, dict):
                raise RouterError(what=f"unexpected api/{path} answer", why=text[:80], how="")
            return data
        raise NotLoggedInError(what="the Xiaomi router keeps refusing the session", why="", how="")

    def _optional(self, path: str) -> dict[str, Any] | None:
        try:
            return self.api(path)
        except NotLoggedInError:
            raise
        except RouterCliError:
            return None

    # ── reads ────────────────────────────────────────────────────────────────
    def info(self) -> RouterInfo:
        data = self.init_info()
        return RouterInfo(
            driver=self.name,
            host=self.bare_host,
            model=str(data.get("displayName") or data.get("hardware") or ""),
            vendor="Xiaomi",
            firmware=str(data.get("romversion") or ""),
            hardware=str(data.get("hardware") or ""),
        )

    def clients(self) -> list[MiClient]:
        """This node's view (on a mesh, ``merge_clients`` joins every node's). Three reads;
        ``misystem/devicelist`` too when ``xqsystem/device_list`` has no client details."""
        status = self.api("misystem/status")
        self.lan_mac = self_mac_of(status)
        device_list = self._optional("xqsystem/device_list")
        wifi = self._optional("xqnetwork/wifi_connect_devices")
        rich = any(
            isinstance(x, dict) and ("ip" in x or "statistics" in x)
            for x in (device_list or {}).get("list") or []
        )
        devicelist = None if rich else self._optional("misystem/devicelist")
        return parse_clients(devicelist, status, wifi, device_list=device_list)

    def topo_graph(self) -> dict[str, Any] | None:
        """``misystem/topo_graph`` — public on current firmware (no token), else with one."""
        try:
            data = json.loads(self.transport.get(TOPO_GRAPH))
        except (RouterCliError, ValueError):
            data = None
        if isinstance(data, dict) and isinstance(data.get("graph"), dict):
            return data
        if self.credentials is None:
            return None
        return self._optional("misystem/topo_graph")

    def mesh_nodes(self) -> list[dict[str, Any]]:
        return parse_mesh_nodes(self.topo_graph())

    def devices(self) -> list[Device]:
        out = []
        for c in self.clients():
            if not c.online:
                continue
            out.append(
                Device(
                    mac=c.mac,
                    ip=c.ip,
                    hostname=c.name,
                    interface="wifi" if c.connection == "wifi" else "lan",
                    band=f"{c.band}GHz" if c.band else None,
                    rssi_dbm=c.rssi,
                    connected_s=c.connected_s,
                )
            )
        return out
