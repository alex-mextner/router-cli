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
    ``GET  /cgi-bin/luci/;stok=T/api/misystem/devicelist``   clients: mac, ip, name, type
                                                   (0 wired, 1 2.4 GHz, 2 5 GHz, 3 guest,
                                                   6 5 GHz game), parent (mesh node), isap
    ``GET  /cgi-bin/luci/;stok=T/api/misystem/status``       ``dev``: per-client upload/
                                                   download totals and current speeds (B/s)
    ``GET  /cgi-bin/luci/;stok=T/api/xqnetwork/wifi_connect_devices``   signal per client
    ``GET  /cgi-bin/luci/;stok=T/api/misystem/topo_graph``   mesh nodes
    ``GET  /cgi-bin/luci/;stok=T/web/logout``      ends the session (kind="logout")

    Field names follow the firmware's JSON as documented by the open-source integrations
    (e.g. hass-miwifi); parsing is defensive and missing keys become None. This driver was
    written without a logged-in capture from a real device: treat per-client signal and
    traffic as best effort until verified.
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
LOGIN = "/cgi-bin/luci/api/xqsystem/login"
BANDS = {0: None, 1: "2.4", 2: "5", 3: "2.4", 6: "5", 7: "6"}
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
    via: str | None = None  # MAC of the mesh node / AP the client hangs off
    rssi: int | None = None
    online: bool = True
    is_ap: bool = False
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


def parse_clients(
    devicelist: dict[str, Any] | None,
    status: dict[str, Any] | None = None,
    wifi: dict[str, Any] | None = None,
    self_mac: str | None = None,
) -> list[MiClient]:
    """Merge devicelist + status (traffic) + wifi_connect_devices (signal) by MAC."""
    clients: dict[str, MiClient] = {}
    for item in (devicelist or {}).get("list") or []:
        if not isinstance(item, dict):
            continue
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        ctype = _int(item.get("type"))
        raw_ips = item.get("ip")
        ips: list[Any] = raw_ips if isinstance(raw_ips, list) else []
        ip = None
        rx_rate = tx_rate = None
        for entry in ips:
            if isinstance(entry, dict) and entry.get("ip"):
                ip = str(entry["ip"])
                rx_rate = _int(entry.get("downspeed"))
                tx_rate = _int(entry.get("upspeed"))
                break
        stats = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}
        parent = _mac(item.get("parent"))
        clients[mac] = MiClient(
            mac=mac,
            ip=ip,
            name=(str(item.get("name") or item.get("oname") or "").strip() or None),
            connection="wired" if ctype == 0 else "wifi" if ctype in BANDS else "unknown",
            band=BANDS.get(ctype) if ctype is not None else None,
            guest=ctype == 3,
            via=parent or self_mac,
            online=str(item.get("online", "1")) not in ("0", "false", "False"),
            is_ap=str(item.get("isap", "0")) not in ("0", "", "None", "False"),
            rx_rate=_int(stats.get("downspeed")) if stats else rx_rate,
            tx_rate=_int(stats.get("upspeed")) if stats else tx_rate,
        )
    for item in (status or {}).get("dev") or []:
        if not isinstance(item, dict):
            continue
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        c = clients.setdefault(mac, MiClient(mac=mac, via=self_mac))
        c.name = c.name or (str(item.get("devname") or "").strip() or None)
        c.rx_bytes = _int(item.get("download"))
        c.tx_bytes = _int(item.get("upload"))
        c.rx_rate = _int(item.get("downspeed")) if item.get("downspeed") is not None else c.rx_rate
        c.tx_rate = _int(item.get("upspeed")) if item.get("upspeed") is not None else c.tx_rate
    for item in (wifi or {}).get("list") or []:
        if not isinstance(item, dict):
            continue
        mac = _mac(item.get("mac"))
        if not mac:
            continue
        c = clients.setdefault(mac, MiClient(mac=mac, connection="wifi", via=self_mac))
        for key in ("signal", "rssi", "wifi_signal"):
            value = _int(item.get(key))
            if value is not None and value < 0:  # dBm; other scales are not guessed
                c.rssi = value
                break
        c.connection = "wifi"
    return sorted(clients.values(), key=lambda c: c.mac)


def parse_mesh_nodes(topo: dict[str, Any] | None) -> list[dict[str, Any]]:
    """[{mac, ip, name}] of every node in ``topo_graph`` (root first)."""
    out: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        mac = _mac(node.get("mac") or node.get("macaddr"))
        if mac:
            out.append(
                {
                    "mac": mac,
                    "ip": node.get("ip"),
                    "name": node.get("name") or node.get("locale") or node.get("hardware"),
                }
            )
        for child in node.get("leafs") or node.get("nodes") or []:
            walk(child)

    graph = (topo or {}).get("graph")
    walk(graph)
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
        "unverified against a logged-in capture: signal/traffic parsing is best effort",
    ]

    def __init__(self, transport: Transport, credentials: Any = None) -> None:
        super().__init__(transport, credentials)
        self._token: str | None = None
        self._init: dict[str, Any] | None = None

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
        devicelist = self.api("misystem/devicelist")
        status = self._optional("misystem/status")
        wifi = self._optional("xqnetwork/wifi_connect_devices")
        return parse_clients(devicelist, status, wifi)

    def mesh_nodes(self) -> list[dict[str, Any]]:
        return parse_mesh_nodes(self._optional("misystem/topo_graph"))

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
                )
            )
        return out
