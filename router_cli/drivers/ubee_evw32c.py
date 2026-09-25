"""ubee_evw32c — Ubee EVW32C-0N / -0S cable gateways (proprietary Broadcom-based firmware).

HOW THIS FIRMWARE WORKS (and why the driver is shaped like this)
    - Login is ``POST /goform/login`` with ``loginUsername``/``loginPassword``. There is no
      cookie: the admin session is GLOBAL to the box. While anyone is logged in, every page
      answers every LAN client; when nobody is, every page answers with the login page
      (title "Residential Gateway Login"). ``/`` is ALWAYS the login page, so session checks
      GET a protected page instead. An open session is therefore an open door: anyone on
      the LAN can use the admin pages until somebody logs out or it times out.
    - When a page comes back as the login page and credentials are stored, the driver logs
      in once and retries; without credentials it tells the user to run ``router login``.
    - SESSION HYGIENE: when the driver had to log in, ``end_session`` GETs ``logout.asp``
      afterwards (the CLI calls it after every command unless ``--keep-session``). When a
      session was already open (someone else logged in), the driver reads through it and
      leaves it alone — it only closes what it opened. ``logout.asp`` is sent only as a
      ``kind="logout"`` request; every other read of it is still refused by the path guard.
    - Settings pages are plain HTML forms posting to ``/goform/<Page>``; see
      :mod:`.ubee_areas` for the page-by-page map. Writes are computed from the live form
      (see :mod:`router_cli.htmlform`), never from a remembered field list.
    - ``RootDevice.xml`` (UPnP description) answers without a session and names the model.

WHAT IT CANNOT KNOW
    The LAN client table carries no host names (only Wi-Fi stations do), and a static lease
    has no name field; ``reserve --name`` is stored as a local alias instead.
"""

from __future__ import annotations

import re
import time
from typing import Any, ClassVar

from .. import htmlform
from .._errors import (
    MissingTargetError,
    NotLoggedInError,
    RouterCliError,
    RouterError,
    UsageError,
    unknown_item,
)
from ..htmlform import Form, Page
from ..http import HttpRequest, Transport
from ..models import (
    Device,
    DocsisChannel,
    DocsisSummary,
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
from . import ubee_areas as A
from .base import BaseDriver, Capability, Deferred, SettingSpec, WritePlan

LOGIN_TITLE = "Residential Gateway Login"
LOGIN_PATH = "/goform/login"
LOGOUT_PATH = "/logout.asp"
SESSION_PAGE = "UbeeSysInfo.asp"
STATIC_SLOTS = 8
_EMPTY_MACS = {"00:00:00:00:00:00", ""}
_EMPTY_IPS = {"0", "0.0.0.0", ""}
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_IPV4 = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def _num(text: str) -> float | None:
    match = _NUM.search(text or "")
    return float(match.group()) if match else None


def _int(text: str) -> int | None:
    value = _num(text)
    return int(value) if value is not None else None


def _is_ip(text: str) -> bool:
    return bool(_IPV4.match((text or "").strip()))


def parse_uptime(text: str) -> int | None:
    match = re.search(r"(\d+)\s*days?\s*(\d+)h:(\d+)m:(\d+)s", text or "")
    if not match:
        return None
    d, h, m, s = (int(g) for g in match.groups())
    return ((d * 24 + h) * 60 + m) * 60 + s


def parse_expiry(text: str) -> str | None:
    try:
        parsed = time.strptime(" ".join(text.split()), "%a %b %d %H:%M:%S %Y")
    except ValueError:
        return None
    return time.strftime("%Y-%m-%dT%H:%M:%S", parsed)


class UbeeEVW32C(BaseDriver):
    name: ClassVar[str] = "ubee_evw32c"
    title: ClassVar[str] = "Ubee EVW32C-0N / EVW32C-0S cable gateway"
    vendor: ClassVar[str] = "Ubee Interactive"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(
        {
            Capability.STATUS,
            Capability.DEVICES,
            Capability.LEASES,
            Capability.RESERVE,
            Capability.PORT_FORWARD,
            Capability.PORT_FORWARD_ADD,
            Capability.SETTINGS,
            Capability.LISTS,
            Capability.PASSWORD,
            Capability.REBOOT,
            Capability.DOCSIS,
            Capability.TELEPHONY,
            Capability.LOGIN,
            Capability.RAW,
        }
    )
    areas: ClassVar[dict[str, str]] = {
        **{name: a.help for name, a in A.AREAS.items()},
        **{name: g[2] + " (raw fields)" for name, g in A.GENERIC_AREAS.items()},
        "wan": "WAN address, gateway, DNS (read-only)",
        "wps": "WPS switch, mode and PIN per band (use `router wps`)",
        "telephony": "MTA provisioning and line status (read-only)",
        "provisioning": "cable modem provisioning steps (read-only)",
    }
    lists: ClassVar[dict[str, str]] = {
        **{name: d.help for name, d in A.LISTS.items()},
        "wifi-acl-2g": "2.4 GHz MAC access list (16 slots)",
        "wifi-acl-5g": "5 GHz MAC access list (16 slots)",
        "port-trigger": "port triggering rules (remove/clear only)",
    }
    notes: ClassVar[list[str]] = [
        "the admin session is global to the router (anyone on the LAN can use it); the "
        "driver logs out after a command that had to log in (--keep-session to stay)",
        "LAN clients carry no host names; only associated Wi-Fi stations do",
        "static leases have no name field: --name is stored as a local alias",
        "port-forward add is a two-step flow whose edit form was not captured: best effort",
    ]

    def __init__(self, transport: Transport, credentials: Any = None) -> None:
        super().__init__(transport, credentials)
        self._relogged = False
        self._opened_session = False

    # ── detection / session ──────────────────────────────────────────────────
    @classmethod
    def probe(cls, transport: Transport) -> str | None:
        try:
            xml = transport.get("/RootDevice.xml")
        except RouterError:
            return None
        models = re.findall(r"<modelName>\s*([^<]+?)\s*</modelName>", xml)
        for model in models:
            if str(model).upper().startswith("EVW32C"):
                return str(model)
        return None

    def login(self, user: str, password: str) -> None:
        # The answer is what tells a wrong password apart: a good login redirects to the
        # system page, a bad one lands on the login form again. Checking the session alone
        # would not do, because the session is global — with Home Assistant logged in, the
        # admin pages are readable whatever password was just tried.
        response = self.transport.send(
            HttpRequest(
                "POST",
                LOGIN_PATH,
                kind="login",
                fields=(("loginUsername", user), ("loginPassword", password)),
                secret_fields=frozenset({"loginPassword"}),
            )
        )
        if not self._is_login(response):
            # A session is (now) open because of this POST — ours to close afterwards.
            self._opened_session = True
        if self._is_login(response) or not self.session_active():
            raise NotLoggedInError(
                what="the router rejected the login",
                why="after POST /goform/login the admin pages still show the login form",
                how="check the user name and password (the default user is 'admin')",
            )

    def session_active(self) -> bool:
        return not self._is_login(self.transport.get("/" + SESSION_PAGE))

    def end_session(self) -> bool:
        if not self._opened_session:
            return False
        self._opened_session = False
        try:
            self.transport.send(HttpRequest("GET", LOGOUT_PATH, kind="logout"))
        except RouterCliError:
            return False  # best effort: the router times the session out by itself
        return True

    def list_is_mac(self, name: str) -> bool:
        return name in A.ACL_LISTS or (name in A.LISTS and A.LISTS[name].kind == "mac")

    @staticmethod
    def _is_login(text: str) -> bool:
        return LOGIN_TITLE in text and "loginPassword" in text

    def _fetch(self, page: str) -> Page:
        text = self.transport.get("/" + page)
        if self._is_login(text):
            creds = self.credentials() if self.credentials else None
            if creds is None or self._relogged:
                raise NotLoggedInError(
                    what="the router has no active admin session",
                    why="the page came back as the login form and no credentials are stored",
                    how="run `router login` once; the driver then logs in by itself",
                )
            self._relogged = True
            self.login(*creds)
            text = self.transport.get("/" + page)
            if self._is_login(text):
                raise NotLoggedInError(
                    what="logged in, but the router still shows the login page",
                    why="another client may have logged out in between",
                    how="try again",
                )
        return htmlform.parse(text)

    def raw_get(self, path: str) -> str:
        path = path if path.startswith("/") else "/" + path
        text = self.transport.get(path)
        if self._is_login(text) and path.lower().endswith(".asp"):
            return self._fetch(path.lstrip("/")).text
        return text

    def raw_pages(self) -> dict[str, str]:
        return dict(A.PAGES)

    # ── reads ────────────────────────────────────────────────────────────────
    def info(self) -> RouterInfo:
        kv = self._fetch("UbeeSysInfo.asp").kv()
        return RouterInfo(
            driver=self.name,
            host=self.bare_host,
            model=kv.get("ID_LABEL_TABLE_MODEL", ""),
            vendor=kv.get("ID_LABEL_TABLE_VENDOR", ""),
            firmware=kv.get("ID_LABEL_TABLE_FIRMWARE_VERSION", ""),
            hardware=kv.get("ID_LABEL_TABLE_HARDWARE_VERSION", ""),
            serial=kv.get("ID_LABEL_TABLE_CABLE_MODEM_SERIAL_NUMBER", ""),
        )

    def status(self) -> Status:
        sys_kv = self._fetch("UbeeSysInfo.asp").kv()
        info = RouterInfo(
            driver=self.name,
            host=self.bare_host,
            model=sys_kv.get("ID_LABEL_TABLE_MODEL", ""),
            vendor=sys_kv.get("ID_LABEL_TABLE_VENDOR", ""),
            firmware=sys_kv.get("ID_LABEL_TABLE_FIRMWARE_VERSION", ""),
            hardware=sys_kv.get("ID_LABEL_TABLE_HARDWARE_VERSION", ""),
            serial=sys_kv.get("ID_LABEL_TABLE_CABLE_MODEM_SERIAL_NUMBER", ""),
        )
        uptime_text = sys_kv.get("ID_LABEL_TABLE_SYSTEM_UP_TIME")
        docsis = self._docsis_summary()
        docsis.mode = sys_kv.get("ID_LABEL_TABLE_DOCSIS_MODE")
        docsis.network_access = sys_kv.get("ID_LABEL_TABLE_NETWORK_ACCESS")
        lan = self.read_area("lan")
        return Status(
            router=info,
            uptime_s=parse_uptime(uptime_text or ""),
            uptime_text=uptime_text,
            wan=self._wan(),
            docsis=docsis,
            lan_ip=str(lan.get("ip")) if lan.get("ip") else None,
            extra={
                "boot_version": sys_kv.get("ID_LABEL_TABLE_BOOT_VERSION"),
                "cm_mac": (sys_kv.get("ID_LABEL_TABLE_CABLE_MODEM_MAC_ADDRESS") or "").lower()
                or None,
            },
        )

    def _wan(self) -> WanInfo:
        page = self._fetch("UbeeWanStatus.asp")
        wan = WanInfo()
        in_dns = False
        for row in page.rows:
            cells = row.cells
            if len(cells) < 2:
                continue
            label = cells[-2].rstrip(": ").strip().lower()
            value = cells[-1].strip()
            ids = set(row.ids)
            if "ID_LABEL_V4_WAN_IP_ADDRESS" in ids:
                wan.ipv4 = value if _is_ip(value) else None
            elif "ID_LABEL_V4_WAN_SUBNETMASK" in ids:
                wan.netmask = value if _is_ip(value) else None
            elif "ID_LABEL_V4_WAN_GATEWAY" in ids:
                wan.gateway = value if _is_ip(value) else None
            elif "ID_LABEL_V4_LEASE_TIME" in ids:
                wan.lease_time_s = _int(value)
            elif "ID_LABEL_V4_WAN_MAC" in ids:
                wan.mac = value.lower() if is_mac(value) else None
            elif "ID_LABEL_WAN_HOST_NAME" in ids:
                wan.hostname = None if value.upper() in ("N/A", "") else value
            if "dns" in label:
                in_dns = True
            elif label and not _is_ip(label):
                in_dns = False
            if in_dns and _is_ip(value):
                wan.dns.append(value)
        return wan

    def _channels(self) -> list[DocsisChannel]:
        page = self._fetch("UbeeConnection.asp")
        out: list[DocsisChannel] = []
        for direction, header in (
            ("downstream", "ID_LABEL_TABLE_DOWNSTREAM_CHANNEL"),
            ("upstream", "ID_LABEL_TABLE_UPSTREAM_CHANNEL"),
        ):
            for row in page.table_with(header):
                c = row.cells
                if not c or not c[0].isdigit():
                    continue
                if direction == "downstream" and len(c) >= 9:
                    out.append(
                        DocsisChannel(
                            direction=direction,
                            channel=int(c[0]),
                            locked=c[1].strip().lower() == "locked",
                            modulation=c[2],
                            frequency_hz=_int(c[3]),
                            power_dbmv=_num(c[4]),
                            snr_db=_num(c[5]),
                            symbol_rate_ksym=_int(c[6]),
                            correctable=_int(c[7]),
                            uncorrectable=_int(c[8]),
                        )
                    )
                elif direction == "upstream" and len(c) >= 6:
                    out.append(
                        DocsisChannel(
                            direction=direction,
                            channel=int(c[0]),
                            locked=c[1].strip().lower() == "locked",
                            modulation=c[2],
                            symbol_rate_ksym=_int(c[3]),
                            frequency_hz=_int(c[4]),
                            power_dbmv=_num(c[5]),
                        )
                    )
        return out

    def docsis_channels(self) -> list[DocsisChannel]:
        return self._channels()

    def _docsis_summary(self) -> DocsisSummary:
        channels = self._channels()
        down = [c for c in channels if c.direction == "downstream"]
        up = [c for c in channels if c.direction == "upstream"]
        down_locked = [c for c in down if c.locked]
        up_locked = [c for c in up if c.locked]

        def span(values: list[float | None]) -> list[float]:
            present = [v for v in values if v is not None]
            return [min(present), max(present)] if present else []

        return DocsisSummary(
            downstream_locked=len(down_locked),
            downstream_total=len(down),
            upstream_locked=len(up_locked),
            upstream_total=len(up),
            downstream_power_dbmv=span([c.power_dbmv for c in down_locked]),
            downstream_snr_db=span([c.snr_db for c in down_locked]),
            upstream_power_dbmv=span([c.power_dbmv for c in up_locked]),
            uncorrectable_total=sum(c.uncorrectable or 0 for c in down),
            provisioning=self._kv_named("UbeeCmProvisioning.asp", "ID_LABEL_TABLE_PROV_"),
        )

    def _kv_named(self, page: str, prefix: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for key, value in self._fetch(page).kv().items():
            if key.startswith(prefix):
                out[key[len(prefix) :].lower().replace("phoen", "phone")] = value
            elif not key.startswith("ID_"):
                out[key.lower().replace(" ", "_")] = value
        return out

    def devices(self) -> list[Device]:
        page = self._fetch("UbeeAdvConnectedDevicesList.asp")
        by_mac: dict[str, Device] = {}
        for band, header in (
            ("2.4GHz", "ID_LABEl_STA_MAC_ADDR_2G"),
            ("5GHz", "ID_LABEl_STA_MAC_ADDR_5G"),
        ):
            for row in page.table_with(header):
                c = row.cells
                if len(c) < 7 or not is_mac(c[0]):
                    continue
                mac = normalize_mac(c[0])
                by_mac[mac] = Device(
                    mac=mac,
                    ip=c[3] if _is_ip(c[3]) else None,
                    hostname=c[4] or None,
                    interface="wifi",
                    band=band,
                    rssi_dbm=_int(c[2]),
                    mode=c[5] or None,
                    speed_kbps=_int(c[6]),
                    connected_s=_int(c[1]),
                )
        for row in self._lan_rows(page):
            c = row.cells
            mac = normalize_mac(c[0])
            static = "STATIC" in c[3].upper()
            existing = by_mac.get(mac)
            if existing is not None:
                existing.ip = existing.ip or c[1]
                existing.lease_expires = None if static else parse_expiry(c[3])
                existing.static_ip = static
                continue
            by_mac[mac] = Device(
                mac=mac,
                ip=c[1],
                interface="lan",
                lease_expires=None if static else parse_expiry(c[3]),
                static_ip=static,
            )
        return list(by_mac.values())

    @staticmethod
    def _lan_rows(page: Page) -> list[htmlform.Row]:
        return [
            row
            for row in page.table_with("ID_LABEL_EXPIRES")
            if len(row.cells) >= 4 and is_mac(row.cells[0]) and _is_ip(row.cells[1])
        ]

    def leases(self) -> list[Lease]:
        page = self._fetch("UbeeAdvConnectedDevicesList.asp")
        reservations = {r.mac: r for r in self.reservations()}
        out: list[Lease] = []
        seen: set[str] = set()
        for row in self._lan_rows(page):
            c = row.cells
            mac = normalize_mac(c[0])
            static = "STATIC" in c[3].upper()
            kind = "reservation" if mac in reservations else ("static" if static else "dynamic")
            out.append(
                Lease(mac=mac, ip=c[1], kind=kind, expires=None if static else parse_expiry(c[3]))
            )
            seen.add(mac)
        for mac, res in reservations.items():
            if mac not in seen:
                out.append(Lease(mac=mac, ip=res.ip, kind="reservation", active=False))
        return out

    # ── static leases ────────────────────────────────────────────────────────
    def _static_form(self) -> Form:
        return self._fetch("UbeeLanStaticLease.asp").form("UbeeLanStaticLease")

    @staticmethod
    def _slot_fields(slot: int) -> tuple[list[str], str]:
        macs = [f"MacAddStaticLease{slot:02d}MA{i}" for i in range(6)]
        return macs, f"IpAddStaticLease{slot}IPX"

    def _slots(self, form: Form) -> list[tuple[int, str, str]]:
        slots: list[tuple[int, str, str]] = []
        for slot in range(1, STATIC_SLOTS + 1):
            macs, ip_field = self._slot_fields(slot)
            if not form.has(ip_field):
                continue
            octets = [form.raw_value(f).strip().lower().zfill(2) for f in macs]
            slots.append((slot, ":".join(octets), form.raw_value(ip_field).strip()))
        return slots

    def reservations(self) -> list[Reservation]:
        form = self._static_form()
        return [
            Reservation(mac=mac, ip=ip, slot=str(slot))
            for slot, mac, ip in self._slots(form)
            if mac not in _EMPTY_MACS and ip not in _EMPTY_IPS
        ]

    def plan_reserve(self, mac: str, ip: str, name: str | None) -> WritePlan:
        mac = normalize_mac(mac)
        ip = validate_ipv4(ip)
        form = self._static_form()
        pool_start = form.value("MY_POOL_START_IP")
        pool_end = form.value("MY_POOL_END_IP")
        self._check_pool(ip, pool_start, pool_end)
        slots = self._slots(form)
        target: int | None = None
        for slot, smac, sip in slots:
            if smac == mac:
                if sip == ip:
                    return WritePlan(
                        summary=f"{mac} is already reserved at {ip} (slot {slot}); nothing to do",
                        notes=self._name_note(name),
                    )
                target = slot
            elif sip == ip and smac not in _EMPTY_MACS:
                raise UsageError(
                    what=f"{ip} is already reserved for {smac} (slot {slot})",
                    why="two static leases cannot share an address",
                    how=f"run `router unreserve {smac}` first, or pick another address",
                )
        if target is None:
            free = [slot for slot, smac, sip in slots if smac in _EMPTY_MACS or sip in _EMPTY_IPS]
            if not free:
                raise UsageError(
                    what=f"all {len(slots)} static lease slots are in use",
                    why="this firmware keeps at most eight static leases",
                    how="free one with `router unreserve <mac>`",
                )
            target = free[0]
        macs, ip_field = self._slot_fields(target)
        for field, octet in zip(macs, mac.split(":"), strict=True):
            form.set(field, octet)
        form.set(ip_field, ip)
        return WritePlan(
            summary=f"reserve {ip} for {mac} in static lease slot {target}",
            steps=[self._post(form, "UbeeLanStaticLease")],
            notes=[
                "the page submits all eight slots at once; untouched slots are resent as-is",
                *self._name_note(name),
            ],
        )

    @staticmethod
    def _name_note(name: str | None) -> list[str]:
        if not name:
            return []
        return [f"the Ubee has no name field for static leases; {name!r} is kept as a local alias"]

    @staticmethod
    def _check_pool(ip: str, start: str, end: str) -> None:
        """The page's own CheckIPRange: same /24 as the pool, above its first address."""
        if not (_is_ip(start) and _is_ip(end)):
            return
        s, e, i = start.split("."), end.split("."), ip.split(".")
        if i[:3] != s[:3]:
            raise UsageError(
                what=f"{ip} is not on the LAN subnet {'.'.join(s[:3])}.0/24",
                why="the router only reserves addresses inside its DHCP pool",
                how=f"pick an address between {start} and {end}",
            )
        if i[3] == s[3] or not int(s[3]) < int(i[3]) <= int(e[3]):
            raise UsageError(
                what=f"{ip} is outside the reservable range",
                why=f"the page accepts addresses above {start} up to {end}",
                how=f"pick an address in {'.'.join(s[:3])}.{int(s[3]) + 1}-{e[3]}",
            )

    def plan_unreserve(self, mac: str) -> WritePlan:
        mac = normalize_mac(mac)
        form = self._static_form()
        for slot, smac, _sip in self._slots(form):
            if smac == mac:
                macs, ip_field = self._slot_fields(slot)
                # Exactly what the page's "Clear" checkbox makes its JavaScript do.
                for field in macs:
                    form.set(field, "00")
                form.set(ip_field, "0")
                return WritePlan(
                    summary=f"remove the static lease for {mac} (slot {slot})",
                    steps=[self._post(form, "UbeeLanStaticLease")],
                )
        raise MissingTargetError(
            what=f"{mac} has no static lease",
            why="it is not in any of the eight slots",
            how="`router leases` lists the current reservations",
        )

    # ── settings areas ───────────────────────────────────────────────────────
    def _area(self, area: str) -> A.Area:
        if area in A.AREAS:
            return A.AREAS[area]
        raise unknown_item("settings area", area, sorted(self.areas))

    def area_keys(self, area: str) -> list[SettingSpec]:
        if area in A.GENERIC_AREAS:
            page, form_name, _ = A.GENERIC_AREAS[area]
            form = self._fetch(page).form(form_name)
            specs = []
            for c in form.controls:
                if not c.name or c.is_button:
                    continue
                choices = [o.value for o in c.options] if c.tag == "select" else None
                specs.append(
                    SettingSpec(
                        c.name, f"{c.type} field", choices=choices, secret=c.type == "password"
                    )
                )
            return specs
        if area.startswith("wifi-") and area in ("wifi-2g", "wifi-5g"):
            base = self._specs(self._area(area))
            return [
                *base,
                SettingSpec(
                    "security", "none, wpa-personal, wpa-enterprise", list(A.SECURITY_MODES)
                ),
                SettingSpec("wpa_version", "wpa2 or mixed (v1/v2)", ["wpa2", "mixed"]),
                SettingSpec("encryption", "aes or auto (tkip+aes)", ["aes", "auto"]),
                SettingSpec("psk", "WPA pre-shared key, 8-63 characters", secret=True),
                SettingSpec("radius_ip", "RADIUS server (wpa-enterprise)"),
                SettingSpec("radius_port", "RADIUS port (wpa-enterprise)"),
                SettingSpec("radius_secret", "RADIUS shared secret", secret=True),
            ]
        if area in ("wan", "wps", "telephony", "provisioning"):
            return [SettingSpec(k, "read-only", writable=False) for k in self.read_area(area)]
        return self._specs(self._area(area))

    @staticmethod
    def _specs(area: A.Area) -> list[SettingSpec]:
        return [
            SettingSpec(
                f.key,
                f.help,
                choices=[label for label, _ in f.choices] or None,
                secret=f.secret,
                writable=f.writable,
            )
            for f in area.fields
        ]

    def read_area(self, area: str, show_secrets: bool = False) -> dict[str, Any]:
        if area == "wan":
            return _asdict(self._wan())
        if area == "telephony":
            return self._kv_named("UbeeTelStatus.asp", "ID_TABLE_")
        if area == "provisioning":
            return self._kv_named("UbeeCmProvisioning.asp", "ID_LABEL_TABLE_PROV_")
        if area == "wps":
            page = self._fetch("UbeeWlanWPS.asp")
            return A.wps_read(
                page.json_vars.get("web_item_data_wireless_setup_jsonData", {}),
                page.json_vars.get("web_item_data_wireless_setup_5g_jsonData", {}),
                show_secrets,
            )
        if area in A.GENERIC_AREAS:
            page_name, form_name, _ = A.GENERIC_AREAS[area]
            return A.read_generic(self._fetch(page_name).form(form_name), show_secrets)
        spec = self._area(area)
        page = self._fetch(spec.page)
        form = page.form(spec.form)
        values = A.read_area(form, spec, show_secrets)
        values.update(self._area_extras(area, page, form, show_secrets))
        return values

    def _area_extras(self, area: str, page: Page, form: Form, show_secrets: bool) -> dict[str, Any]:
        if area == "lan":
            kv = page.kv()
            mac = kv.get("ID_LABEL_MAC_ADDRESS", "")
            return {
                "ip": f"192.168.{form.raw_value('LocalIpAddressIP2')}.1",
                "netmask": "255.255.255.0",
                "mac": mac.lower() if is_mac(mac) else None,
            }
        if area == "dhcp":
            start = ".".join(form.raw_value(f"DhcpIpStart{i}") for i in range(4))
            end = ".".join(form.raw_value(f"DhcpIpEnd{i}") for i in range(4))
            return {"pool_start": start, "pool_end": end}
        if area in ("wifi-2g", "wifi-5g"):
            band = area[-2:]
            sec = self._fetch("UbeeWlanSecurity.asp")
            var = (
                "web_item_data_wireless_setup_jsonData"
                if band == "2g"
                else "web_item_data_wireless_5g_setup_jsonData"
            )
            return A.wifi_security_read(sec.json_vars.get(var, {}), band, show_secrets)
        if area in ("wifi-acl-2g", "wifi-acl-5g"):
            return {"macs": self.list_items(area)}
        if area == "dmz":
            octet = form.raw_value("AdvDmzHostIP3").strip()
            return {"host": None if octet in ("", "0") else f"{self._lan_prefix()}.{octet}"}
        if area == "firewall":
            services = [r.cells[0] for r in page.rows if len(r.cells) == 1 and "Port" in r.cells[0]]
            return {"allowed_services": services}
        if area == "vpn":
            tunnels = [
                r.cells
                for r in page.table_with("ID_LABEL_VPN_BASIC_NAME")
                if r.cells and r.cells[0].isdigit()
            ]
            return {"tunnels": tunnels}
        if area == "nas":
            usb = next(
                (
                    r.cells[1]
                    for r in page.rows
                    if "ID_LABEL_NAS_USB_SLOT" in r.ids and len(r.cells) > 1
                ),
                None,
            )
            return {"usb": usb}
        return {}

    def _lan_prefix(self) -> str:
        form = self._fetch("UbeeLanSetup.asp").form("UbeeLanSetup")
        return f"192.168.{form.raw_value('LocalIpAddressIP2').strip()}"

    def plan_area(self, area: str, changes: dict[str, str]) -> WritePlan:
        if not changes:
            raise UsageError(what="nothing to change", why="no key=value given", how="")
        if area == "wps":
            raise UsageError(what="use `router wps` to change WPS", why="", how="")
        if area in A.GENERIC_AREAS:
            page_name, form_name, _ = A.GENERIC_AREAS[area]
            form = self._fetch(page_name).form(form_name)
            A.apply_generic(form, changes)
            return WritePlan(
                summary=f"set {', '.join(changes)} on {page_name}",
                steps=[self._post(form, form.action, secrets=A.generic_secrets(form))],
                destructive=True,
                notes=["raw field edit: the page's JavaScript validation is not replicated"],
            )
        if area == "dmz" and "host" in changes:
            changes = dict(changes)
            host = changes.pop("host").strip().lower()
            if host in ("", "0", "off", "none", "no", "disabled"):
                changes["host_octet"] = "0"
            else:
                ip = validate_ipv4(host)
                prefix = self._lan_prefix()
                if ip.rsplit(".", 1)[0] != prefix:
                    raise UsageError(
                        what=f"{ip} is not on the LAN ({prefix}.0/24)",
                        why="the DMZ host must be a LAN address",
                        how=f"use an address like {prefix}.50",
                    )
                changes["host_octet"] = ip.rsplit(".", 1)[1]
        spec = self._area(area)
        requested = sorted(changes)
        steps: list[HttpRequest | Deferred] = []
        destructive = spec.destructive
        if area in ("wifi-2g", "wifi-5g"):
            band = area[-2:]
            sec_changes = {k: v for k, v in changes.items() if k in A.SECURITY_KEYS}
            changes = {k: v for k, v in changes.items() if k not in A.SECURITY_KEYS}
            if sec_changes:
                sec = self._fetch("UbeeWlanSecurity.asp")
                var = (
                    "web_item_data_wireless_setup_jsonData"
                    if band == "2g"
                    else "web_item_data_wireless_5g_setup_jsonData"
                )
                body = A.wifi_security_json(sec.json_vars.get(var, {}), band, sec_changes)
                steps.append(
                    HttpRequest(
                        "POST",
                        "/goform/ubee_post",
                        kind="write",
                        json_body=body,
                        secret_fields=frozenset(
                            {
                                f"wireless_{band}_sec_wpap_preshare_key",
                                f"wireless_{band}_sec_wpae_radius_share_sec",
                            }
                        ),
                    )
                )
        if changes:
            page = self._fetch(spec.page)
            form = page.form(spec.form)
            fields, destructive_change = A.apply_area(form, spec, changes)
            destructive = destructive or destructive_change
            steps.insert(
                0,
                HttpRequest(
                    "POST",
                    "/goform/" + _action_name(form),
                    kind="write",
                    fields=tuple(fields),
                    secret_fields=A.secret_names(spec),
                ),
            )
        return WritePlan(
            summary=f"set {area}: " + ", ".join(requested),
            steps=steps,
            destructive=destructive,
        )

    def plan_wps(
        self, action: str, band: str, mode: str | None, pin: str | None, enabled: bool | None
    ) -> WritePlan:
        body = A.wps_json(action, band, mode=mode, pin=pin, enabled=enabled)
        return WritePlan(
            summary=f"WPS {action}" + ("" if action == "enable" else f" ({band})"),
            steps=[
                HttpRequest(
                    "POST",
                    "/goform/ubee_post",
                    kind="write",
                    json_body=body,
                    secret_fields=frozenset({f"wireless_{band}_wps_pin"}),
                )
            ],
            destructive=action == "connect",
        )

    # ── lists ────────────────────────────────────────────────────────────────
    def list_items(self, name: str) -> list[str]:
        if name in A.ACL_LISTS:
            form_name, prefix, _ = A.ACL_LISTS[name]
            form = self._fetch("UbeeWlanAccessControl.asp").form(form_name)
            values = [form.raw_value(f"{prefix}{i:02d}").strip() for i in range(1, 17)]
            return [normalize_mac(v) for v in values if v and is_mac(v)]
        if name == "port-trigger":
            page = self._fetch("UbeeAdvancedPortTriggering.asp")
            return [
                " | ".join(r.cells) for r in page.rows if len(r.cells) >= 7 and r.cells[0].isdigit()
            ]
        spec = self._list(name)
        form = self._fetch(spec.page).form(spec.form)
        control = form.control(spec.select)
        items = []
        for option in control.options:
            text = option.text.strip()
            if not option.value.strip() or not text or text.lower().startswith("no "):
                continue
            items.append(normalize_mac(text) if spec.kind == "mac" and is_mac(text) else text)
        return items

    def _list(self, name: str) -> A.ListDef:
        if name in A.LISTS:
            return A.LISTS[name]
        raise unknown_item("list", name, sorted(self.lists))

    def plan_list_edit(self, name: str, action: str, value: str | None) -> WritePlan:
        if action not in ("add", "remove", "clear"):
            raise UsageError(
                what=f"unknown list action {action!r}", why="", how="use add, remove or clear"
            )
        if action != "clear" and not value:
            raise UsageError(what=f"{action} needs a value", why="", how="")
        if name in A.ACL_LISTS:
            return self._plan_acl(name, action, value)
        if name == "port-trigger":
            return self._plan_trigger(action, value)
        spec = self._list(name)
        form = self._fetch(spec.page).form(spec.form)
        shown = value or ""
        if spec.kind == "mac" and value:
            shown = normalize_mac(value).upper()
        if action == "add":
            if spec.mac_octets:
                for i, octet in enumerate(normalize_mac(shown).split(":")):
                    form.set(f"{spec.new_field}{i}", octet)
            else:
                form.set(spec.new_field, shown)
            form.add_hidden(spec.action_field, spec.add)
        elif action == "remove":
            control = form.control(spec.select)
            wanted = shown.lower()
            match = [
                o
                for o in control.options
                if o.value.strip()
                and (
                    o.text.strip().lower() == wanted
                    or (
                        spec.kind == "mac"
                        and is_mac(o.text)
                        and normalize_mac(o.text) == normalize_mac(shown)
                    )
                )
            ]
            if not match:
                raise MissingTargetError(
                    what=f"{value!r} is not in the {name} list",
                    why="nothing to remove",
                    how=f"`router lists show {name}` shows the current entries",
                )
            form.set(spec.select, match[0].value)
            form.add_hidden(spec.remove_action_field or spec.action_field, spec.remove)
        else:
            if spec.clear is None:
                raise UsageError(
                    what=f"the {name} list has no clear-all",
                    why="",
                    how="remove entries one by one",
                )
            form.add_hidden(spec.action_field, spec.clear)
        return WritePlan(
            summary=f"{action} {shown or 'all'} {'to' if action == 'add' else 'from'} {name}",
            steps=[self._post(form, form.action)],
            destructive=action == "clear",
        )

    def _plan_acl(self, name: str, action: str, value: str | None) -> WritePlan:
        form_name, prefix, commit = A.ACL_LISTS[name]
        form = self._fetch("UbeeWlanAccessControl.asp").form(form_name)
        fields = [f"{prefix}{i:02d}" for i in range(1, 17)]
        current = {f: form.raw_value(f).strip() for f in fields}
        mac = normalize_mac(value).upper() if value else ""
        if action == "add":
            if any(is_mac(v) and normalize_mac(v) == normalize_mac(mac) for v in current.values()):
                return WritePlan(summary=f"{mac} is already in {name}; nothing to do")
            free = [f for f, v in current.items() if not v]
            if not free:
                raise UsageError(
                    what=f"all 16 {name} slots are used", why="", how="remove one first"
                )
            form.set(free[0], mac)
        elif action == "remove":
            hits = [
                f
                for f, v in current.items()
                if is_mac(v) and normalize_mac(v) == normalize_mac(mac)
            ]
            if not hits:
                raise MissingTargetError(what=f"{mac} is not in {name}", why="", how="")
            for f in hits:
                form.set(f, "")
        else:
            for f in fields:
                form.set(f, "")
        form.add_hidden(commit, "1")
        return WritePlan(
            summary=f"{action} {mac or 'all'} in {name}",
            steps=[self._post(form, form.action)],
            destructive=True,
        )

    def _plan_trigger(self, action: str, value: str | None) -> WritePlan:
        form = self._fetch("UbeeAdvancedPortTriggering.asp").form("UbeeAdvancedPortTriggering")
        if action == "add":
            raise UsageError(
                what="adding port triggers is not supported yet",
                why="the create/edit form of this page was never captured",
                how="use the web UI once, or `router raw form UbeeAdvancedPortTriggering.asp`",
            )
        if action == "remove":
            index = A.parse_int("index", value or "", 0, 63)
            form.set("PortTriggeringCreateRemove", "2")
            form.set("PortTriggeringTable", str(index))
        else:
            form.set("PortTriggeringCreateRemove", "3")
        return WritePlan(
            summary=f"port trigger {action} {value or 'all'}",
            steps=[self._post(form, form.action)],
            destructive=True,
        )

    # ── port forwarding ──────────────────────────────────────────────────────
    def port_forwards(self) -> list[PortForward]:
        page = self._fetch("UbeeAdvancedPortForwarding.asp")
        out: list[PortForward] = []
        for row in page.rows:
            c = row.cells
            if len(c) < 9 or not _is_ip(c[0]):
                continue
            out.append(
                PortForward(
                    index=len(out),
                    local_ip=c[0],
                    local_start=_int(c[1]) or 0,
                    local_end=_int(c[2]) or 0,
                    external_ip=None if c[3] in ("0.0.0.0", "") else c[3],
                    external_start=_int(c[4]) or 0,
                    external_end=_int(c[5]) or 0,
                    protocol=c[6].lower(),
                    description=c[7],
                    enabled=c[8].strip().lower() in ("yes", "enabled", "on", "1"),
                )
            )
        return out

    def plan_port_forward_remove(self, index: int | None) -> WritePlan:
        form = self._fetch("UbeeAdvancedPortForwarding.asp").form("UbeeAdvancedPortForwarding")
        if index is None:
            form.set("PortForwardingCreateRemove", "4")
            return WritePlan(
                summary="remove ALL port forwarding rules",
                steps=[self._post(form, form.action)],
                destructive=True,
            )
        rules = self.port_forwards()
        if not 0 <= index < len(rules):
            raise MissingTargetError(
                what=f"there is no port forwarding rule #{index}",
                why=f"there are {len(rules)} rule(s), numbered from 0",
                how="`router port-forward list` shows them",
            )
        form.set("PortForwardingCreateRemove", "3")
        form.set("PortForwardingTable", str(index))
        rule = rules[index]
        return WritePlan(
            summary=(
                f"remove port forward #{index}: {rule.external_start}->"
                f"{rule.local_ip}:{rule.local_start} {rule.protocol}"
            ),
            steps=[self._post(form, form.action)],
            destructive=True,
        )

    def plan_port_forward_add(self, rule: PortForward) -> WritePlan:
        form = self._fetch("UbeeAdvancedPortForwarding.asp").form("UbeeAdvancedPortForwarding")
        for port in (rule.local_start, rule.local_end, rule.external_start, rule.external_end):
            if port in (22, 23) or not 1 <= port <= 65535:
                raise UsageError(
                    what=f"port {port} cannot be forwarded on this router",
                    why="the page refuses 22 and 23 and anything outside 1-65535",
                    how="pick another port",
                )
        form.set("PortForwardingCreateRemove", "1")
        step1 = self._post(form, form.action, note="opens the create form (step 1 of 2)")

        def fill(_transport: Transport, response: str) -> list[HttpRequest]:
            return [self._fill_forward_form(response, rule)]

        return WritePlan(
            summary=(
                f"forward {rule.protocol} {rule.external_start}-{rule.external_end} -> "
                f"{rule.local_ip}:{rule.local_start}-{rule.local_end}"
            ),
            steps=[
                step1,
                Deferred("fill and apply the create form the router returns (step 2 of 2)", fill),
            ],
            destructive=True,
            verified=False,
            notes=[
                "the create form was not in the capture; step 2 locates its fields at run time",
                "check the result with `router port-forward list` afterwards",
            ],
        )

    def _fill_forward_form(self, response: str, rule: PortForward) -> HttpRequest:
        page = htmlform.parse(response)
        if not any(f.has("PortForwardingLocalIp") for f in page.forms):
            page = self._fetch("UbeeAdvancedPortForwarding.asp")
        form = next((f for f in page.forms if f.has("PortForwardingLocalIp")), None)
        if form is None:
            raise RouterError(
                what="the router did not return the port forwarding create form",
                why="no PortForwardingLocalIp field after 'Create IPv4'",
                how="add the rule in the web UI; please report the firmware version",
            )
        form.set("PortForwardingLocalIp", rule.local_ip)
        form.set("PortForwardingLocalStartPort", str(rule.local_start))
        form.set("PortForwardingLocalEndPort", str(rule.local_end))
        form.set("PortForwardingExtIp", rule.external_ip or "0.0.0.0")
        form.set("PortForwardingExtStartPort", str(rule.external_start))
        form.set("PortForwardingExtEndPort", str(rule.external_end))
        for c in form.controls:
            lname = c.name.lower()
            if c.tag == "select" and any(o.text.upper() in ("TCP", "UDP") for o in c.options):
                wanted = {"tcp": "TCP", "udp": "UDP", "both": "BOTH"}.get(
                    rule.protocol, rule.protocol.upper()
                )
                opts = [o for o in c.options if o.text.upper().startswith(wanted[:3])]
                if wanted == "BOTH":
                    opts = [
                        o for o in c.options if "/" in o.text or "BOTH" in o.text.upper()
                    ] or opts
                if opts:
                    form.set(c.name, opts[0].value)
            elif "desc" in lname and c.tag == "input":
                c.value = rule.description
            elif "enable" in lname and c.type == "checkbox":
                c.checked = rule.enabled
            elif "enable" in lname and c.tag == "select":
                form.set(c.name, "1" if rule.enabled else "0")
        apply_value = "2"
        for c in form.controls:
            onclick = c.attrs.get("onclick", "")
            match = re.search(r"applyCommitForwarding\((\d+)\)", onclick)
            if match and match.group(1) != "1":
                apply_value = match.group(1)
        form.add_hidden("PortForwardingApply", apply_value)
        return self._post(form, form.action)

    # ── password, reboot, raw ────────────────────────────────────────────────
    def plan_password(self, user: str, old: str, new: str) -> WritePlan:
        if not 1 <= len(new) <= 24:
            raise UsageError(what="the new password must be 1-24 characters", why="", how="")
        form = self._fetch("UbeeManagementPassword.asp").form("Security")
        form.set("OldPassword", old)
        form.set("Password", new)
        form.set("PasswordReEnter", new)
        return WritePlan(
            summary="change the admin password",
            steps=[
                self._post(
                    form,
                    form.action,
                    secrets=frozenset({"OldPassword", "Password", "PasswordReEnter"}),
                )
            ],
            destructive=True,
            notes=["run `router login` again afterwards so the stored password matches"],
        )

    def plan_reboot(self) -> WritePlan:
        form = self._fetch("UbeeConfiguration.asp").form("Configuration")
        form.check("ResetYes", True)
        form.check("ResetNo", False)
        form.check("ResetFactoryYes", False)
        form.check("ResetFactoryNo", True)
        fields = form.successful()
        if ("ResetFactoryYes", "0x01") in fields:  # belt and braces: never a factory reset
            raise RouterError(what="refusing: the reboot form would factory-reset", why="", how="")
        return WritePlan(
            summary="reboot the gateway (internet and phone lines drop for a few minutes)",
            steps=[self._post(form, form.action)],
            destructive=True,
        )

    def plan_raw_form(
        self, page: str, form_name: str | None, changes: dict[str, str], clicked: str | None
    ) -> WritePlan:
        parsed = self._fetch(page.lstrip("/"))
        if form_name:
            form = parsed.form(form_name)
        elif len(parsed.forms) == 1:
            form = parsed.forms[0]
        else:
            raise UsageError(
                what=f"{page} has {len(parsed.forms)} forms",
                why="say which one with --form",
                how=f"forms: {', '.join(f.name or f.action for f in parsed.forms)}",
            )
        if any(k.lower().startswith("resetfactory") for k in changes):
            raise UsageError(
                what="router-cli does not send factory resets", why="", how="use the web UI"
            )
        A.apply_generic(form, changes)
        return WritePlan(
            summary=f"post {form.name or form.action} on {page}",
            steps=[self._post(form, form.action, clicked=clicked, secrets=A.generic_secrets(form))],
            destructive=True,
            notes=["raw form post: none of the page's JavaScript checks were run"],
        )

    # ── helpers ──────────────────────────────────────────────────────────────
    def _post(
        self,
        form: Form,
        action: str,
        clicked: str | None = None,
        secrets: frozenset[str] = frozenset(),
        note: str = "",
    ) -> HttpRequest:
        return HttpRequest(
            "POST",
            "/goform/" + _action_name(form, action),
            kind="write",
            fields=tuple(form.successful(clicked)),
            secret_fields=secrets,
            note=note,
        )


def _action_name(form: Form, fallback: str = "") -> str:
    action = form.action or fallback
    return action.rstrip("/").split("/")[-1]


def _asdict(value: Any) -> dict[str, Any]:
    from dataclasses import asdict

    result: dict[str, Any] = asdict(value)
    return result
