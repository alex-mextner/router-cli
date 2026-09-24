"""openwrt — OpenWrt through rpcd's ubus JSON-RPC endpoint (``/ubus``), the API LuCI uses.

PROTOCOL
    Every call is ``POST /ubus`` with ``{"jsonrpc":"2.0","id":N,"method":"call",
    "params":[<session>, <object>, <method>, {args}]}``. The answer's ``result`` is
    ``[code]`` or ``[code, data]``; code 0 is success. A session comes from
    ``session login`` with the all-zero session id and lasts a few minutes; the driver logs
    in on first use with the stored credentials and again once if a call is refused.

    Reads used (all present on a stock OpenWrt with LuCI):
    ``system board``/``system info``, ``network.interface dump``, ``luci-rpc getHostHints``,
    ``luci-rpc getDHCPLeases``, ``iwinfo devices``/``info``/``assoclist``, ``uci get``.

    Writes are ``uci add``/``set``/``delete`` followed by ``uci commit`` (procd then reloads
    the affected service), ``luci setPassword`` and ``system reboot``. Like every other
    driver, writes are returned as a plan and only sent when the user confirmed them.

    Inspired by openwrt-luci-rpc (MIT); no code or dependency taken from it.

    Because a ubus read is itself a POST, this driver's reads are ``kind="read"`` requests;
    the transport's write gate only concerns ``kind="write"``.
"""

from __future__ import annotations

import json
import re
from typing import Any, ClassVar

from .._errors import (
    MissingTargetError,
    NotLoggedInError,
    RouterError,
    UsageError,
    unknown_item,
)
from ..http import HttpRequest, Transport
from ..models import (
    Device,
    Lease,
    PortForward,
    Reservation,
    RouterInfo,
    Status,
    WanInfo,
    is_mac,
    normalize_mac,
    validate_ipv4,
)
from .base import BaseDriver, Capability, SettingSpec, WritePlan

NULL_SESSION = "0" * 32
SECRET_OPTIONS = frozenset({"key", "password", "auth_secret", "priv_key", "sae_password"})
ACCESS_DENIED = -32002

# Single-section areas: (uci config, section, {key: help}).
SECTION_AREAS: dict[str, tuple[str, str, dict[str, str]]] = {
    "lan": (
        "network",
        "lan",
        {"ipaddr": "LAN address", "netmask": "LAN netmask", "dns": "DNS servers"},
    ),
    "dhcp": (
        "dhcp",
        "lan",
        {
            "start": "first pool offset",
            "limit": "pool size",
            "leasetime": "lease time (e.g. 12h)",
            "ignore": "1 disables DHCP on the LAN",
        },
    ),
}
# Whole-config areas: keys are "<section>.<option>".
CONFIG_AREAS: dict[str, str] = {"wifi": "wireless", "firewall": "firewall", "system": "system"}


class OpenWrt(BaseDriver):
    name: ClassVar[str] = "openwrt"
    title: ClassVar[str] = "OpenWrt (LuCI / rpcd ubus JSON-RPC)"
    vendor: ClassVar[str] = "OpenWrt"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(
        {
            Capability.STATUS,
            Capability.DEVICES,
            Capability.LEASES,
            Capability.RESERVE,
            Capability.PORT_FORWARD,
            Capability.PORT_FORWARD_ADD,
            Capability.SETTINGS,
            Capability.PASSWORD,
            Capability.REBOOT,
            Capability.LOGIN,
            Capability.RAW,
        }
    )
    areas: ClassVar[dict[str, str]] = {
        "lan": "network.lan: address, netmask, DNS",
        "dhcp": "dhcp.lan: pool start/limit, lease time, on/off",
        "wifi": "the whole `wireless` config (keys: <section>.<option>)",
        "firewall": "the whole `firewall` config (keys: <section>.<option>)",
        "system": "the whole `system` config (keys: <section>.<option>)",
    }
    reservation_names: ClassVar[bool] = True
    notes: ClassVar[list[str]] = [
        "needs stored credentials (`router login --driver openwrt`): ubus has no global session",
        "reads are JSON-RPC POSTs to /ubus; writes: uci add/set/delete/commit, setPassword, reboot",
        "verified against fixtures only; no OpenWrt device was available while writing it",
    ]

    def __init__(self, transport: Transport, credentials: Any = None) -> None:
        super().__init__(transport, credentials)
        self._sid: str | None = None
        self._id = 0

    # ── JSON-RPC ─────────────────────────────────────────────────────────────
    def _envelope(self, sid: str, obj: str, method: str, args: dict[str, Any]) -> dict[str, Any]:
        self._id += 1
        return {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": "call",
            "params": [sid, obj, method, args],
        }

    def _rpc(self, request: HttpRequest) -> Any:
        text = self.transport.send(request)
        if request.kind == "write" and not text:
            return None  # dry run: nothing was sent
        try:
            reply = json.loads(text)
        except ValueError as exc:
            raise RouterError(
                what="the router's /ubus answer is not JSON",
                why=text[:120],
                how="is this really OpenWrt with rpcd? try `router detect`",
            ) from exc
        if not isinstance(reply, dict):
            raise RouterError(what="unexpected /ubus answer", why=text[:120], how="")
        if "error" in reply:
            err = reply["error"] if isinstance(reply["error"], dict) else {}
            if err.get("code") == ACCESS_DENIED:
                raise NotLoggedInError(
                    what="ubus refused the session", why=str(err.get("message")), how=""
                )
            raise RouterError(what="ubus call failed", why=str(err.get("message", err)), how="")
        result = reply.get("result")
        if not isinstance(result, list) or not result:
            raise RouterError(what="malformed ubus result", why=str(result)[:120], how="")
        code = result[0]
        if code != 0:
            if code == 6:
                raise NotLoggedInError(
                    what="ubus: permission denied",
                    why="the user's rpcd ACL does not allow this call",
                    how="log in as root, or extend the ACL in /usr/share/rpcd/acl.d",
                )
            raise RouterError(
                what=f"ubus call returned status {code}", why=str(request.json_body)[:160], how=""
            )
        return result[1] if len(result) > 1 else {}

    def _session(self) -> str:
        if self._sid:
            return self._sid
        creds = self.credentials() if self.credentials else None
        if creds is None:
            raise NotLoggedInError(
                what="no OpenWrt credentials stored",
                why="every ubus call needs a session, and a session needs a login",
                how="run `router login --driver openwrt --host <router>`",
            )
        self.login(*creds)
        assert self._sid is not None
        return self._sid

    def login(self, user: str, password: str) -> None:
        body = self._envelope(
            NULL_SESSION, "session", "login", {"username": user, "password": password}
        )
        try:
            data = self._rpc(HttpRequest("POST", "/ubus", kind="login", json_body=body))
        except RouterError as exc:
            raise NotLoggedInError(
                what="OpenWrt rejected the login",
                why=exc.what,
                how="check the user (usually root) and password",
            ) from exc
        sid = data.get("ubus_rpc_session") if isinstance(data, dict) else None
        if not sid:
            raise NotLoggedInError(
                what="OpenWrt rejected the login", why="no session returned", how=""
            )
        self._sid = str(sid)

    def session_active(self) -> bool:
        return self._sid is not None

    def call(self, obj: str, method: str, args: dict[str, Any] | None = None) -> Any:
        """A read-only ubus call (re-logging in once if the session expired)."""
        for attempt in range(2):
            request = HttpRequest(
                "POST",
                "/ubus",
                kind="read",
                json_body=self._envelope(self._session(), obj, method, args or {}),
            )
            try:
                return self._rpc(request)
            except NotLoggedInError:
                if attempt or not self.credentials:
                    raise
                self._sid = None
        return None  # pragma: no cover

    def _write(self, obj: str, method: str, args: dict[str, Any], note: str = "") -> HttpRequest:
        secrets = frozenset(k for k in args if k in SECRET_OPTIONS)
        body = self._envelope(self._session(), obj, method, args)
        return HttpRequest(
            "POST", "/ubus", kind="write", json_body=body, secret_fields=secrets, note=note
        )

    # ── detection ────────────────────────────────────────────────────────────
    @classmethod
    def probe(cls, transport: Transport) -> str | None:
        try:
            text = transport.get("/")
        except RouterError:
            return None
        if re.search(r"cgi-bin/luci|luci-static|LuCI", text):
            return "OpenWrt"
        return None

    # ── reads ────────────────────────────────────────────────────────────────
    def info(self) -> RouterInfo:
        board = self.call("system", "board")
        release = board.get("release", {}) if isinstance(board, dict) else {}
        return RouterInfo(
            driver=self.name,
            host=self.bare_host,
            model=str(board.get("model", "")),
            vendor="OpenWrt",
            firmware=str(release.get("description") or release.get("version") or ""),
            hardware=str(board.get("board_name", "")),
        )

    def status(self) -> Status:
        info = self.info()
        sysinfo = self.call("system", "info")
        uptime = int(sysinfo.get("uptime", 0)) if isinstance(sysinfo, dict) else None
        wan, lan_ip = self._interfaces()
        return Status(
            router=info,
            uptime_s=uptime,
            uptime_text=_human_uptime(uptime) if uptime is not None else None,
            wan=wan,
            lan_ip=lan_ip,
            extra={"load": sysinfo.get("load"), "memory": sysinfo.get("memory")},
        )

    def _interfaces(self) -> tuple[WanInfo, str | None]:
        dump = self.call("network.interface", "dump")
        wan = WanInfo()
        lan_ip: str | None = None
        for iface in dump.get("interface", []) if isinstance(dump, dict) else []:
            if not isinstance(iface, dict):
                continue
            addrs = [a for a in iface.get("ipv4-address", []) if isinstance(a, dict)]
            if iface.get("interface") == "wan":
                if addrs:
                    wan.ipv4 = addrs[0].get("address")
                    wan.netmask = _mask(int(addrs[0].get("mask", 0)))
                for route in iface.get("route", []):
                    if isinstance(route, dict) and route.get("target") == "0.0.0.0":
                        wan.gateway = route.get("nexthop")
                wan.dns = [str(d) for d in iface.get("dns-server", [])]
                data = iface.get("data", {})
                if isinstance(data, dict) and "leasetime" in data:
                    wan.lease_time_s = int(data["leasetime"])
            elif iface.get("interface") == "lan" and addrs:
                lan_ip = addrs[0].get("address")
        return wan, lan_ip

    def _hints(self) -> dict[str, dict[str, Any]]:
        hints = self.call("luci-rpc", "getHostHints")
        out: dict[str, dict[str, Any]] = {}
        if isinstance(hints, dict):
            for mac, hint in hints.items():
                if is_mac(mac) and isinstance(hint, dict):
                    out[normalize_mac(mac)] = hint
        return out

    def _raw_leases(self) -> list[dict[str, Any]]:
        data = self.call("luci-rpc", "getDHCPLeases")
        leases = data.get("dhcp_leases", []) if isinstance(data, dict) else []
        return [
            lease
            for lease in leases
            if isinstance(lease, dict) and is_mac(str(lease.get("macaddr", "")))
        ]

    def _stations(self) -> list[Device]:
        out: list[Device] = []
        devices = self.call("iwinfo", "devices")
        for dev in devices.get("devices", []) if isinstance(devices, dict) else []:
            info = self.call("iwinfo", "info", {"device": dev})
            freq = int(info.get("frequency", 0) or 0) if isinstance(info, dict) else 0
            band = "5GHz" if freq >= 4900 else ("2.4GHz" if freq else None)
            assoc = self.call("iwinfo", "assoclist", {"device": dev})
            for sta in assoc.get("results", []) if isinstance(assoc, dict) else []:
                if not isinstance(sta, dict) or not is_mac(str(sta.get("mac", ""))):
                    continue
                rx = sta.get("rx", {}) if isinstance(sta.get("rx"), dict) else {}
                out.append(
                    Device(
                        mac=normalize_mac(str(sta["mac"])),
                        interface="wifi",
                        band=band,
                        rssi_dbm=int(sta["signal"]) if "signal" in sta else None,
                        speed_kbps=int(rx["rate"]) if "rate" in rx else None,
                        connected_s=int(sta["connected_time"]) if "connected_time" in sta else None,
                    )
                )
        return out

    def devices(self) -> list[Device]:
        hints = self._hints()
        by_mac: dict[str, Device] = {}
        for lease in self._raw_leases():
            mac = normalize_mac(str(lease["macaddr"]))
            by_mac[mac] = Device(
                mac=mac,
                ip=str(lease.get("ipaddr") or "") or None,
                hostname=str(lease.get("hostname") or "") or None,
                lease_expires=_expiry(lease.get("expires")),
            )
        try:
            stations = self._stations()
        except RouterError:
            stations = []  # no wireless (or no iwinfo ACL): wired-only view
        for sta in stations:
            existing = by_mac.get(sta.mac)
            if existing:
                existing.interface, existing.band, existing.rssi_dbm = (
                    "wifi",
                    sta.band,
                    sta.rssi_dbm,
                )
                existing.speed_kbps, existing.connected_s = sta.speed_kbps, sta.connected_s
            else:
                by_mac[sta.mac] = sta
        for mac, dev in by_mac.items():
            hint = hints.get(mac, {})
            if not dev.hostname and hint.get("name"):
                dev.hostname = str(hint["name"])
            if not dev.ip and hint.get("ipaddrs"):
                dev.ip = str(hint["ipaddrs"][0])
        return list(by_mac.values())

    def leases(self) -> list[Lease]:
        reservations = {r.mac: r for r in self.reservations()}
        out: list[Lease] = []
        seen: set[str] = set()
        for lease in self._raw_leases():
            mac = normalize_mac(str(lease["macaddr"]))
            seen.add(mac)
            out.append(
                Lease(
                    mac=mac,
                    ip=str(lease.get("ipaddr", "")),
                    hostname=str(lease.get("hostname") or "") or None,
                    kind="reservation" if mac in reservations else "dynamic",
                    expires=_expiry(lease.get("expires")),
                )
            )
        for mac, res in reservations.items():
            if mac not in seen:
                out.append(
                    Lease(mac=mac, ip=res.ip, hostname=res.name, kind="reservation", active=False)
                )
        return out

    def _uci_sections(
        self, config: str, section_type: str | None = None
    ) -> dict[str, dict[str, Any]]:
        args: dict[str, Any] = {"config": config}
        if section_type:
            args["type"] = section_type
        data = self.call("uci", "get", args)
        values = data.get("values", {}) if isinstance(data, dict) else {}
        return {k: v for k, v in values.items() if isinstance(v, dict)}

    def _hosts(self) -> list[tuple[str, dict[str, Any]]]:
        out = []
        for section, values in self._uci_sections("dhcp", "host").items():
            macs = values.get("mac", "")
            for mac in macs if isinstance(macs, list) else str(macs).split():
                if is_mac(mac):
                    out.append((section, {**values, "mac": normalize_mac(mac)}))
        return out

    def reservations(self) -> list[Reservation]:
        return [
            Reservation(mac=v["mac"], ip=str(v.get("ip", "")), name=v.get("name"), slot=section)
            for section, v in self._hosts()
            if v.get("ip")
        ]

    def plan_reserve(self, mac: str, ip: str, name: str | None) -> WritePlan:
        mac, ip = normalize_mac(mac), validate_ipv4(ip)
        values: dict[str, Any] = {"mac": mac, "ip": ip}
        if name:
            values["name"] = _hostname(name)
        for section, v in self._hosts():
            if v["mac"] == mac:
                if v.get("ip") == ip and (not name or v.get("name") == values.get("name")):
                    return WritePlan(summary=f"{mac} is already reserved at {ip}; nothing to do")
                return WritePlan(
                    summary=f"update reservation {section}: {mac} -> {ip}",
                    steps=[
                        self._write(
                            "uci", "set", {"config": "dhcp", "section": section, "values": values}
                        ),
                        self._write("uci", "commit", {"config": "dhcp"}),
                    ],
                )
            if v.get("ip") == ip:
                raise UsageError(
                    what=f"{ip} is already reserved for {v['mac']}",
                    why="",
                    how="unreserve it first",
                )
        return WritePlan(
            summary=f"reserve {ip} for {mac}",
            steps=[
                self._write("uci", "add", {"config": "dhcp", "type": "host", "values": values}),
                self._write("uci", "commit", {"config": "dhcp"}),
            ],
        )

    def plan_unreserve(self, mac: str) -> WritePlan:
        mac = normalize_mac(mac)
        for section, v in self._hosts():
            if v["mac"] == mac:
                return WritePlan(
                    summary=f"remove reservation {section} ({mac} -> {v.get('ip')})",
                    steps=[
                        self._write("uci", "delete", {"config": "dhcp", "section": section}),
                        self._write("uci", "commit", {"config": "dhcp"}),
                    ],
                )
        raise MissingTargetError(what=f"{mac} has no static lease", why="", how="`router leases`")

    # ── port forwards (firewall redirects) ───────────────────────────────────
    def _redirects(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self._uci_sections("firewall", "redirect").items())

    def port_forwards(self) -> list[PortForward]:
        out = []
        for i, (_section, v) in enumerate(self._redirects()):
            ext = _ports(str(v.get("src_dport", "")))
            loc = _ports(str(v.get("dest_port", v.get("src_dport", ""))))
            proto = v.get("proto", "tcp udp")
            proto_text = " ".join(proto) if isinstance(proto, list) else str(proto)
            out.append(
                PortForward(
                    index=i,
                    local_ip=str(v.get("dest_ip", "")),
                    local_start=loc[0],
                    local_end=loc[1],
                    external_ip=None,
                    external_start=ext[0],
                    external_end=ext[1],
                    protocol="both"
                    if ("tcp" in proto_text and "udp" in proto_text)
                    else proto_text,
                    description=str(v.get("name", "")),
                    enabled=str(v.get("enabled", "1")) != "0",
                )
            )
        return out

    def plan_port_forward_add(self, rule: PortForward) -> WritePlan:
        proto = {"both": "tcp udp"}.get(rule.protocol, rule.protocol)
        values = {
            "name": rule.description or f"router-cli {rule.external_start}",
            "target": "DNAT",
            "src": "wan",
            "dest": "lan",
            "proto": proto,
            "src_dport": _port_text(rule.external_start, rule.external_end),
            "dest_ip": rule.local_ip,
            "dest_port": _port_text(rule.local_start, rule.local_end),
            "enabled": "1" if rule.enabled else "0",
        }
        return WritePlan(
            summary=(
                f"forward {rule.protocol} {values['src_dport']} -> "
                f"{rule.local_ip}:{values['dest_port']}"
            ),
            steps=[
                self._write(
                    "uci", "add", {"config": "firewall", "type": "redirect", "values": values}
                ),
                self._write("uci", "commit", {"config": "firewall"}),
            ],
            destructive=True,
        )

    def plan_port_forward_remove(self, index: int | None) -> WritePlan:
        redirects = self._redirects()
        targets = (
            redirects
            if index is None
            else ([redirects[index]] if 0 <= index < len(redirects) else [])
        )
        if not targets:
            raise MissingTargetError(
                what=f"there is no port forwarding rule #{index}",
                why="",
                how="`router port-forward list`",
            )
        steps = [
            self._write("uci", "delete", {"config": "firewall", "section": s}) for s, _ in targets
        ]
        steps.append(self._write("uci", "commit", {"config": "firewall"}))
        return WritePlan(
            summary="remove ALL port forwards"
            if index is None
            else f"remove port forward #{index}",
            steps=[*steps],
            destructive=True,
        )

    # ── settings areas (uci) ─────────────────────────────────────────────────
    def area_keys(self, area: str) -> list[SettingSpec]:
        if area in SECTION_AREAS:
            return [SettingSpec(k, h) for k, h in SECTION_AREAS[area][2].items()]
        values = self.read_area(area)
        return [
            SettingSpec(k, "uci option", secret=k.split(".")[-1] in SECRET_OPTIONS) for k in values
        ]

    def read_area(self, area: str, show_secrets: bool = False) -> dict[str, Any]:
        if area in SECTION_AREAS:
            config, section, _keys = SECTION_AREAS[area]
            data = self.call("uci", "get", {"config": config, "section": section})
            values = data.get("values", {}) if isinstance(data, dict) else {}
            return {
                k: _shown(k, v, show_secrets) for k, v in values.items() if not k.startswith(".")
            }
        if area in CONFIG_AREAS:
            out: dict[str, Any] = {}
            for section, values in self._uci_sections(CONFIG_AREAS[area]).items():
                for k, v in values.items():
                    if not k.startswith("."):
                        out[f"{section}.{k}"] = _shown(k, v, show_secrets)
                out[f"{section}..type"] = values.get(".type")
            return out
        raise unknown_item("settings area", area, sorted(self.areas))

    def plan_area(self, area: str, changes: dict[str, str]) -> WritePlan:
        if area in SECTION_AREAS:
            config, section, _keys = SECTION_AREAS[area]
            steps = [
                self._write(
                    "uci", "set", {"config": config, "section": section, "values": dict(changes)}
                ),
                self._write("uci", "commit", {"config": config}),
            ]
            return WritePlan(
                summary=f"set {config}.{section}: {', '.join(changes)}",
                steps=[*steps],
                destructive=area == "lan",
            )
        if area in CONFIG_AREAS:
            config = CONFIG_AREAS[area]
            by_section: dict[str, dict[str, str]] = {}
            for key, value in changes.items():
                section, _, option = key.partition(".")
                if not section or not option:
                    raise UsageError(
                        what=f"{key!r} is not <section>.<option>",
                        why="",
                        how="see `router settings show " + area + "`",
                    )
                by_section.setdefault(section, {})[option] = value
            steps = [
                self._write("uci", "set", {"config": config, "section": s, "values": v})
                for s, v in by_section.items()
            ]
            steps.append(self._write("uci", "commit", {"config": config}))
            return WritePlan(
                summary=f"set {config}: {', '.join(changes)}", steps=[*steps], destructive=True
            )
        raise unknown_item("settings area", area, sorted(self.areas))

    def plan_password(self, user: str, old: str, new: str) -> WritePlan:
        return WritePlan(
            summary=f"change the password of {user}",
            steps=[self._write("luci", "setPassword", {"username": user, "password": new})],
            destructive=True,
            notes=["run `router login` again afterwards so the stored password matches"],
        )

    def plan_reboot(self) -> WritePlan:
        return WritePlan(
            summary="reboot the router",
            steps=[self._write("system", "reboot", {})],
            destructive=True,
        )

    def raw_get(self, path: str) -> str:
        return self.transport.get(path if path.startswith("/") else "/" + path)

    def raw_call(self, obj: str, method: str, args: dict[str, Any]) -> Any:
        return self.call(obj, method, args)


def _shown(key: str, value: Any, show_secrets: bool) -> Any:
    if key in SECRET_OPTIONS and not show_secrets:
        return "<hidden>" if value else ""
    return value


def _mask(bits: int) -> str:
    raw = (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF if bits else 0
    return ".".join(str((raw >> s) & 0xFF) for s in (24, 16, 8, 0))


def _ports(text: str) -> tuple[int, int]:
    parts = re.split(r"[-:]", text.strip()) if text.strip() else ["0"]
    try:
        start = int(parts[0])
        end = int(parts[-1])
    except ValueError:
        return (0, 0)
    return (start, end)


def _port_text(start: int, end: int) -> str:
    return str(start) if start == end else f"{start}-{end}"


def _hostname(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9-]+", "-", name).strip("-")
    return cleaned or "host"


def _expiry(value: Any) -> str | None:
    if isinstance(value, (int, float)) and value > 0:
        import time

        return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + float(value)))
    return None


def _human_uptime(seconds: int) -> str:
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return f"{d} days {h:02d}h:{m:02d}m:{s:02d}s"
