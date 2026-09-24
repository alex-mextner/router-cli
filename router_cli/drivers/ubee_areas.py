"""ubee_areas — the Ubee EVW32C web UI as data: every page, every form, every setting.

This module is both the driver's configuration and the reverse-engineering notes. Each
:class:`Area` says which page renders a group of settings, which ``<form>`` on it posts to
which ``/goform/<Name>``, how a friendly key maps onto the form's field(s), and which hidden
"apply" flags the page's own JavaScript sets before submitting. The engine at the bottom
reads current values out of a parsed form and applies changes to it; everything that is not
a changed field is submitted exactly as the page rendered it.

Findings that shaped this (all from a GET-only capture of firmware 2.4.1015-SIP):

- Pages are ``/<Name>.asp``; each form posts urlencoded to ``/goform/<Name>``. The Wi-Fi
  security, WPS and language pages instead ``POST /goform/ubee_post`` with a JSON body of
  ``wireless_{2g,5g}_*`` keys (see ``wifi_security_json`` and ``wps_json``).
- The admin session is global to the box, not per client: while anyone is logged in, GETs
  from any LAN address succeed without a cookie. There are no CSRF tokens.
- Fixed IP octets are rendered as ``disabled`` inputs and so are never submitted; only the
  editable last (or third) octet is.
- Several on/off choices are two radios with DIFFERENT names (``DhcpServerEnable`` /
  ``DhcpServerDisable``); only the checked one is sent, and its presence is the value.
- List pages (MAC filter, keywords, domains) are "type a value, press Add" forms driven by
  an ``...Action`` hidden field: 1 add, 2 remove the selected entry, 3 clear all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._errors import UsageError, unknown_item
from ..htmlform import Form
from ..models import normalize_mac, validate_ipv4

HIDDEN = "<hidden>"

_TRUE = {"1", "yes", "y", "on", "true", "enable", "enabled"}
_FALSE = {"0", "no", "n", "off", "false", "disable", "disabled"}


def parse_bool(key: str, value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise UsageError(
        what=f"{key}={value!r} is not a yes/no value",
        why="this setting is a switch",
        how=f"use {key}=yes or {key}=no",
    )


def parse_int(key: str, value: str, lo: int, hi: int) -> int:
    try:
        number = int(value.strip())
    except ValueError:
        number = lo - 1
    if not lo <= number <= hi:
        raise UsageError(
            what=f"{key}={value!r} is out of range",
            why=f"it must be a whole number from {lo} to {hi}",
            how=f"pick a value between {lo} and {hi}",
        )
    return number


@dataclass(frozen=True)
class F:
    """How one friendly key maps onto the form.

    kinds: ``text`` ``number`` ``select`` ``selbool`` (a 1/0 select) ``check`` (checkbox)
    ``radio2`` (two differently-named radios; ``alt`` is the "off" one) ``ipv4`` (four
    fields ``<field>0``..``<field>3``) ``password2`` (a password and its ``alt`` re-entry).
    """

    key: str
    kind: str
    field: str
    help: str
    alt: str = ""
    choices: tuple[tuple[str, str], ...] = ()
    secret: bool = False
    writable: bool = True
    destructive: bool = False
    lo: int = 0
    hi: int = 65535


@dataclass(frozen=True)
class Area:
    name: str
    page: str
    form: str
    help: str
    fields: tuple[F, ...]
    apply: tuple[tuple[str, str], ...] = ()
    clicked: str | None = None
    destructive: bool = False

    def field(self, key: str) -> F:
        for f in self.fields:
            if f.key == key:
                return f
        raise unknown_item("setting", key, [f.key for f in self.fields])


# ── choice tables ────────────────────────────────────────────────────────────
MODE_2G = (("b/g/n", "0"), ("g/n", "1"), ("b/g", "2"), ("n", "3"))
MODE_5G = (("a/n/ac", "4"), ("n/ac", "7"), ("ac", "6"), ("a", "5"))
SIDEBAND = (("lower", "-1"), ("none", "0"), ("upper", "1"))
FIREWALL_LEVEL = (("off", "0"), ("low", "1"), ("medium", "2"), ("high", "3"))
ACL_MODE = (("disabled", "0"), ("allow", "1"), ("deny", "2"))
PROTOCOL = (("tcp", "4"), ("udp", "3"), ("both", "254"))
CHANNEL_AUTO = (("auto", "0"),)


def _wifi_fields(sfx: str, mode: tuple[tuple[str, str], ...]) -> tuple[F, ...]:
    return (
        F("enabled", "selbool", f"WirelessEnable{sfx}", "radio on/off"),
        F("ssid", "text", f"ServiceSetIdentifier{sfx}", "network name (1-32 characters)"),
        F("hidden", "selbool", f"ClosedNetwork{sfx}", "hide the SSID"),
        F("mode", "select", f"NMode{sfx}", "802.11 mode", choices=mode),
        F("power", "select", f"OutputPower{sfx}", "output power percent: 25, 50, 75, 100"),
        F(
            "channel",
            "select",
            f"ChannelNumber{sfx}",
            "control channel, or auto",
            choices=CHANNEL_AUTO,
        ),
        F("bandwidth", "select", f"NBandwidth{sfx}", "channel width in MHz"),
        F(
            "sideband",
            "select",
            f"NSideband{sfx}",
            "control sideband (40 MHz only)",
            choices=SIDEBAND,
        ),
    )


def _ip_filter_fields() -> tuple[F, ...]:
    out: list[F] = []
    for n in range(1, 11):
        out += [
            F(
                f"rule{n}_start",
                "number",
                f"IpFilterAddressStart{n}IP3",
                f"rule {n}: first host octet",
                hi=254,
            ),
            F(
                f"rule{n}_end",
                "number",
                f"IpFilterAddressEnd{n}IP3",
                f"rule {n}: last host octet",
                hi=254,
            ),
            F(f"rule{n}_enabled", "check", f"IpFilteringEnable{n}", f"rule {n}: active"),
        ]
    return tuple(out)


def _port_filter_fields() -> tuple[F, ...]:
    out: list[F] = []
    for n in range(1, 11):
        out += [
            F(f"rule{n}_start", "number", f"IpFilterPortStart{n}", f"rule {n}: first port", lo=1),
            F(f"rule{n}_end", "number", f"IpFilterPortEnd{n}", f"rule {n}: last port", lo=1),
            F(
                f"rule{n}_protocol",
                "select",
                f"PortFilteringProtocol{n}",
                f"rule {n}: tcp/udp/both",
                choices=PROTOCOL,
            ),
            F(f"rule{n}_enabled", "check", f"PortFilteringEnable{n}", f"rule {n}: active"),
        ]
    return tuple(out)


AREAS: dict[str, Area] = {
    a.name: a
    for a in (
        Area(
            "lan",
            "UbeeLanSetup.asp",
            "UbeeLanSetup",
            "LAN address, DNS servers handed to clients, domain name",
            (
                F(
                    "ip_octet",
                    "number",
                    "LocalIpAddressIP2",
                    "third octet of the LAN address 192.168.X.1",
                    hi=254,
                    destructive=True,
                ),
                F("dns1", "ipv4", "PrimaryDnsIpAddressIP", "primary DNS server"),
                F("dns2", "ipv4", "SecondaryDnsIpAddressIP", "secondary DNS server"),
                F("dns3", "ipv4", "ThirdDnsIpAddressIP", "third DNS server"),
                F("domain", "text", "DomainName", "LAN domain name"),
            ),
            apply=(("ApplyRgLanSetupAction", "1"),),
        ),
        Area(
            "dhcp",
            "UbeeLanDhcp.asp",
            "UbeeLanDhcp",
            "the LAN DHCP server: on/off, pool range, lease time",
            (
                F(
                    "enabled",
                    "radio2",
                    "DhcpServerEnable",
                    "DHCP server on/off",
                    alt="DhcpServerDisable",
                    destructive=True,
                ),
                F(
                    "start",
                    "number",
                    "DhcpIpStart3",
                    "last octet of the first pool address",
                    lo=2,
                    hi=254,
                ),
                F(
                    "end",
                    "number",
                    "DhcpIpEnd3",
                    "last octet of the last pool address",
                    lo=2,
                    hi=254,
                ),
                F(
                    "lease_time",
                    "number",
                    "LeaseTime",
                    "lease time in seconds",
                    lo=1,
                    hi=9999999999,
                ),
            ),
            apply=(("ApplyAction", "1"),),
        ),
        Area(
            "wifi-2g",
            "UbeeWlanBasic.asp",
            "wlanRadio",
            "2.4 GHz radio: on/off, SSID, mode, channel, power",
            _wifi_fields("", MODE_2G),
            apply=(("commitwlanRadio", "1"), ("restoreWirelessDefaults", "0")),
            destructive=True,
        ),
        Area(
            "wifi-5g",
            "UbeeWlanBasic.asp",
            "wlanRadio5G",
            "5 GHz radio: on/off, SSID, mode, channel, power",
            _wifi_fields("5G", MODE_5G),
            apply=(("commitwlanRadio5G", "1"), ("restoreWirelessDefaults5G", "0")),
            # The 5 GHz Apply button is NAMED, so a browser sends ID_BUTTON_APPLY=Apply.
            clicked="ID_BUTTON_APPLY",
            destructive=True,
        ),
        Area(
            "wifi-acl-2g",
            "UbeeWlanAccessControl.asp",
            "UbeeWlanAccessControl",
            "2.4 GHz MAC access control mode (edit the list with `wifi acl add/rm`)",
            (
                F(
                    "mode",
                    "select",
                    "MacRestrictMode",
                    "disabled, allow (only listed), deny (listed)",
                    choices=ACL_MODE,
                ),
            ),
            apply=(("commitwlanAccess", "1"),),
            destructive=True,
        ),
        Area(
            "wifi-acl-5g",
            "UbeeWlanAccessControl.asp",
            "UbeeWlanAccessControl5G",
            "5 GHz MAC access control mode (edit the list with `wifi acl add/rm`)",
            (
                F(
                    "mode",
                    "select",
                    "MacRestrictMode5G",
                    "disabled, allow (only listed), deny (listed)",
                    choices=ACL_MODE,
                ),
            ),
            apply=(("commitwlanAccess5G", "1"),),
            destructive=True,
        ),
        Area(
            "dmz",
            "UbeeAdvancedDmz.asp",
            "UbeeAdvancedDmz",
            "DMZ host (last octet; 0 = off)",
            (
                F(
                    "host_octet",
                    "number",
                    "AdvDmzHostIP3",
                    "last octet of the DMZ host, 0 disables",
                    hi=254,
                ),
            ),
            apply=(("ApplyAdvDMZAction", "1"),),
        ),
        Area(
            "firewall",
            "UbeeAdvancedFirewall.asp",
            "UbeeAdvancedFirewall",
            "IPv4 firewall level and attack detection",
            (
                F(
                    "level",
                    "select",
                    "AdvFirewall",
                    "off, low, medium, high",
                    choices=FIREWALL_LEVEL,
                ),
                F("block_fragments", "check", "AdvBlockIpFragments", "drop fragmented IP packets"),
                F("port_scan_detection", "check", "AdvPortScanDetection", "detect port scans"),
                F("ip_flood_detection", "check", "AdvSynFloodDetection", "detect SYN/IP floods"),
            ),
        ),
        Area(
            "options",
            "UbeeAdvancedOption.asp",
            "UbeeAdvancedOption",
            "WAN ping blocking, VPN passthrough, multicast, UPnP",
            (
                F("wan_blocking", "check", "cbWanBlocking", "ignore pings/probes from the WAN"),
                F("ipsec_passthrough", "check", "cbIpsecPassThrough", "IPSec passthrough"),
                F("pptp_passthrough", "check", "cbPptpPassThrough", "PPTP passthrough"),
                F("multicast", "check", "cbOptMulticast", "multicast"),
                F("upnp", "check", "cbOptUPnP", "UPnP port mapping"),
            ),
            apply=(("ApplyRgOpAction", "1"),),
        ),
        Area(
            "ip-filter",
            "UbeeAdvancedIpFiltering.asp",
            "UbeeAdvancedIpFiltering",
            "block internet access for LAN address ranges (10 rules)",
            _ip_filter_fields(),
        ),
        Area(
            "port-filter",
            "UbeeAdvancedPortFiltering.asp",
            "UbeeAdvancedPortFiltering",
            "block outbound port ranges for the whole LAN (10 rules)",
            _port_filter_fields(),
        ),
        Area(
            "parental",
            "UbeeParentalBasic.asp",
            "UbeeParentalBasic",
            "parental control switch and override password (lists: keywords/domains)",
            (
                F("enabled", "check", "ParentalControlEnabled", "parental control on/off"),
                F(
                    "override_password",
                    "password2",
                    "ParentalPassword",
                    "password to bypass a block",
                    alt="ParentalPasswordReEnter",
                    secret=True,
                ),
                F(
                    "access_duration",
                    "number",
                    "AccessDuration",
                    "minutes an override lasts",
                    lo=1,
                    hi=99999999,
                ),
            ),
        ),
        Area(
            "vpn",
            "UbeeVpnBasic.asp",
            "UbeeVpnBasic",
            "IPSec endpoint on/off (tunnels: `router raw form UbeeVpnIPSec.asp`)",
            (F("ipsec_endpoint", "selbool", "UbeeIpsecEnable", "IPSec endpoint on/off"),),
        ),
        Area(
            "nas",
            "UbeeNasControl.asp",
            "UbeeNasControl",
            "USB storage sharing: Samba, FTP, DLNA, credentials",
            (
                F("device_name", "text", "NasStorageAdvancedNetworkName", "network/device name"),
                F("samba", "radio2", "NasSambaEnable", "Samba file sharing", alt="NasSambaDisable"),
                F("ftp", "radio2", "NasFtpEnable", "FTP file sharing", alt="NasFtpDisable"),
                F(
                    "dlna",
                    "radio2",
                    "NasBasicEnableMsc",
                    "DLNA media server",
                    alt="NasBasicDisableMsc",
                ),
                F(
                    "anonymous",
                    "radio2",
                    "NasPermissionAnonymous",
                    "allow anonymous access",
                    alt="NasPermissionAdmin",
                ),
                F("username", "text", "NasUsername", "file sharing user name"),
                F("password", "text", "NasPassword", "file sharing password", secret=True),
            ),
            apply=(("NasBasicApplyAction", "1"), ("NasEjectAction", "0")),
        ),
    )
}

# Pages whose forms are exposed field-by-field (keys are the raw form field names).
GENERIC_AREAS: dict[str, tuple[str, str, str]] = {
    "parental-users": (
        "UbeeParentalUserSetup.asp",
        "UbeeParentalUserSetup",
        "parental control users",
    ),
    "parental-time": (
        "UbeeParentalTimeFilter.asp",
        "UbeeParentalTimeFilter",
        "time-of-day access policies",
    ),
    "vpn-ipsec": ("UbeeVpnIPSec.asp", "UbeeVpnIPSec", "IPSec tunnel settings"),
    "nas-samba": (
        "UbeeNasStorageAdvSamba.asp",
        "UbeeNasStorageAdvSamba",
        "Samba workgroup and shares",
    ),
    "nas-ftp": ("UbeeNasStorageAdvFtp.asp", "UbeeNasStorageAdvFtp", "FTP sharing"),
    "media-server": ("UbeeNasMediaServer.asp", "UbeeNasMediaServer", "DLNA media server"),
    "cm-scan": ("UbeeConnection.asp", "Connection", "cable modem favourite downstream frequency"),
}


@dataclass(frozen=True)
class ListDef:
    """A "type a value, press Add / select one, press Remove" list on a page."""

    name: str
    page: str
    form: str
    help: str
    select: str  # the list box holding current entries
    new_field: str  # the text box (or MAC octet prefix when mac_octets)
    action_field: str
    add: str = "1"
    remove: str = "2"
    clear: str | None = "3"
    kind: str = "text"  # text | mac
    mac_octets: bool = False
    remove_action_field: str = ""  # a separate "remove" flag (parental trusted computers)


LISTS: dict[str, ListDef] = {
    d.name: d
    for d in (
        ListDef(
            "mac-filter",
            "UbeeAdvancedMacFiltering.asp",
            "UbeeAdvancedMacFiltering",
            "MACs blocked from the internet (max 20)",
            "MacFilterList",
            "NewMacFilter",
            "MacFilterAction",
            kind="mac",
        ),
        ListDef(
            "keywords",
            "UbeeParentalBasic.asp",
            "UbeeParentalBasic",
            "parental control: blocked keywords",
            "KeywordList",
            "NewKeyword",
            "KeywordAction",
            clear=None,
        ),
        ListDef(
            "blocked-domains",
            "UbeeParentalBasic.asp",
            "UbeeParentalBasic",
            "parental control: blocked domains",
            "DomainList",
            "NewDomain",
            "DomainAction",
            clear=None,
        ),
        ListDef(
            "allowed-domains",
            "UbeeParentalBasic.asp",
            "UbeeParentalBasic",
            "parental control: allowed domains (white list)",
            "AllowedDomainList",
            "NewAllowedDomain",
            "AllowedDomainAction",
            clear=None,
        ),
        ListDef(
            "trusted-computers",
            "UbeeParentalUserSetup.asp",
            "UbeeParentalUserSetup",
            "parental control: computers that bypass the login",
            "TrustedComputers",
            "NewTrustedComputerMA",
            "addTrustedClient",
            add="1",
            remove="1",
            clear=None,
            kind="mac",
            mac_octets=True,
            remove_action_field="removeTrustedClient",
        ),
    )
}

# Wireless MAC access lists are 16 plain text boxes rather than a list box.
ACL_LISTS = {
    "wifi-acl-2g": ("UbeeWlanAccessControl", "WirelessMac", "commitwlanAccess"),
    "wifi-acl-5g": ("UbeeWlanAccessControl5G", "WirelessMac5G", "commitwlanAccess5G"),
}

# Every page of the web UI that is safe to GET, with what it shows.
PAGES: dict[str, str] = {
    "UbeeSysInfo.asp": "cable modem: vendor, model, versions, serial, uptime",
    "UbeeCmProvisioning.asp": "cable modem: provisioning steps",
    "UbeeConnection.asp": "cable modem: DOCSIS downstream/upstream channels",
    "UbeeConfiguration.asp": "cable modem: reboot / factory reset (POST only; never GET-harmful)",
    "UbeeTelStatus.asp": "telephony: MTA provisioning and line status",
    "UbeeLanSetup.asp": "gateway: LAN address and DNS",
    "UbeeLanDhcp.asp": "gateway: DHCP server",
    "UbeeLanStaticLease.asp": "gateway: static DHCP leases (8 slots)",
    "UbeeWanStatus.asp": "gateway: WAN address, gateway, DNS",
    "UbeeWlanBasic.asp": "wireless: radios, SSIDs, channels",
    "UbeeWlanSecurity.asp": "wireless: security mode and keys (JSON)",
    "UbeeWlanWPS.asp": "wireless: WPS (JSON)",
    "UbeeWlanAccessControl.asp": "wireless: MAC access control and stations",
    "UbeeAdvConnectedDevicesList.asp": "advanced: connected Wi-Fi stations and LAN DHCP clients",
    "UbeeAdvancedOption.asp": "advanced: WAN blocking, passthrough, multicast, UPnP",
    "UbeeAdvancedIpFiltering.asp": "advanced: IP range filters",
    "UbeeAdvancedMacFiltering.asp": "advanced: MAC filters",
    "UbeeAdvancedPortFiltering.asp": "advanced: port filters",
    "UbeeAdvancedPortForwarding.asp": "advanced: port forwarding",
    "UbeeAdvancedPortTriggering.asp": "advanced: port triggering",
    "UbeeAdvancedDmz.asp": "advanced: DMZ host",
    "UbeeAdvancedFirewall.asp": "advanced: firewall",
    "UbeeManagementPassword.asp": "management: admin password",
    "UbeeVpnBasic.asp": "VPN: IPSec endpoint and tunnel list",
    "UbeeVpnIPSec.asp": "VPN: IPSec tunnel editor",
    "UbeeNasControl.asp": "file sharing: USB, Samba/FTP/DLNA switches",
    "UbeeNasStorageAdvSamba.asp": "file sharing: Samba",
    "UbeeNasStorageAdvFtp.asp": "file sharing: FTP",
    "UbeeNasMediaServer.asp": "file sharing: DLNA media server",
    "UbeeParentalBasic.asp": "parental control: rules, keywords, domains",
    "UbeeParentalUserSetup.asp": "parental control: users, trusted computers",
    "UbeeParentalTimeFilter.asp": "parental control: time-of-day policies",
}


# ── the engine ───────────────────────────────────────────────────────────────
NUMERIC_SELECTS = frozenset({"power", "channel", "bandwidth"})


def _label(value: str, choices: tuple[tuple[str, str], ...]) -> str | None:
    for label, v in choices:
        if v == value:
            return label
    return None


def read_field(form: Form, f: F, show_secrets: bool) -> Any:
    value: Any
    if f.kind in ("text", "password2"):
        value = form.raw_value(f.field)
    elif f.kind == "number":
        raw = form.raw_value(f.field).strip()
        value = int(raw) if raw.lstrip("-").isdigit() else raw
    elif f.kind == "selbool":
        value = form.raw_value(f.field) == "1"
    elif f.kind == "select":
        control = form.control(f.field)
        raw = form.raw_value(f.field)
        if not raw and control.options:
            raw = control.options[0].value
        label = _label(raw, f.choices)
        if label is None and f.key in NUMERIC_SELECTS:
            label = raw  # power "100", channel "6", bandwidth "20": the value IS the answer
        if label is None:
            texts = [o.text for o in control.options if o.value == raw]
            label = texts[0] if texts else raw
        value = label
    elif f.kind == "check" or f.kind == "radio2":
        value = form.is_checked(f.field)
    elif f.kind == "ipv4":
        value = ".".join(form.raw_value(f"{f.field}{i}").strip() for i in range(4))
    else:  # pragma: no cover - table typo
        raise UsageError(what=f"unknown field kind {f.kind}", why="", how="")
    if f.secret and not show_secrets:
        return HIDDEN if value else ""
    return value


def read_area(form: Form, area: Area, show_secrets: bool) -> dict[str, Any]:
    return {f.key: read_field(form, f, show_secrets) for f in area.fields}


def apply_change(form: Form, f: F, value: str) -> None:
    if not f.writable:
        raise UsageError(what=f"{f.key} is read-only", why="the page does not accept it", how="")
    if f.kind == "text":
        form.enable(f.field)
        form.set(f.field, value)
    elif f.kind == "password2":
        form.enable(f.field)
        form.enable(f.alt)
        form.set(f.field, value)
        form.set(f.alt, value)
    elif f.kind == "number":
        form.enable(f.field)
        form.set(f.field, str(parse_int(f.key, value, f.lo, f.hi)))
    elif f.kind == "selbool":
        form.set(f.field, "1" if parse_bool(f.key, value) else "0")
    elif f.kind == "select":
        form.enable(f.field)
        lowered = value.strip().lower()
        mapped = next((v for label, v in f.choices if label == lowered), value.strip())
        form.set(f.field, mapped)
    elif f.kind == "check":
        form.check(f.field, parse_bool(f.key, value))
    elif f.kind == "radio2":
        on = parse_bool(f.key, value)
        form.check(f.field, on)
        form.check(f.alt, not on)
    elif f.kind == "ipv4":
        octets = validate_ipv4(value).split(".")
        for i, octet in enumerate(octets):
            form.set(f"{f.field}{i}", octet)
    else:  # pragma: no cover - table typo
        raise UsageError(what=f"unknown field kind {f.kind}", why="", how="")


def apply_area(
    form: Form, area: Area, changes: dict[str, str]
) -> tuple[list[tuple[str, str]], bool]:
    """Apply changes; return (the POST fields, whether the change is destructive)."""
    destructive = area.destructive
    for key, value in changes.items():
        f = area.field(key)
        apply_change(form, f, value)
        destructive = destructive or f.destructive
    for name, value in area.apply:
        form.add_hidden(name, value)
    return form.successful(area.clicked), destructive


def secret_names(area: Area) -> frozenset[str]:
    names: set[str] = set()
    for f in area.fields:
        if f.secret:
            names.add(f.field)
            if f.alt:
                names.add(f.alt)
    return frozenset(names)


# ── generic (field-by-field) forms ───────────────────────────────────────────
def read_generic(form: Form, show_secrets: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for control in form.controls:
        if not control.name or control.is_button:
            continue
        if control.type == "checkbox":
            out[control.name] = control.checked
            continue
        if control.type == "radio":
            if control.checked:
                out[control.name] = control.value
            else:
                out.setdefault(control.name, None)
            continue
        if control.tag == "select":
            values = control.selected_values()
            out[control.name] = values if control.multiple else (values[0] if values else "")
            continue
        value = control.value
        if control.type == "password" and not show_secrets:
            value = HIDDEN if value else ""
        out[control.name] = value
    return out


def apply_generic(form: Form, changes: dict[str, str]) -> None:
    for name, value in changes.items():
        controls = form.all(name)
        if not controls:
            form.control(name)  # raises the diagnosed error
        control = controls[0]
        if control.type == "checkbox":
            form.check(name, parse_bool(name, value))
        elif control.type == "radio" and len(controls) > 1:
            form.check(name, True, value=value)
        elif control.type == "radio":
            form.check(name, parse_bool(name, value))
        else:
            form.enable(name)
            form.set(name, value)


def generic_secrets(form: Form) -> frozenset[str]:
    return frozenset(c.name for c in form.controls if c.type == "password" and c.name)


# ── Wi-Fi security and WPS (JSON to /goform/ubee_post) ───────────────────────
SECURITY_MODES = ("none", "wpa-personal", "wpa-enterprise")
WPA_VERSIONS = {"wpa": 0, "wpa2": 1, "mixed": 2}
ENCRYPTIONS = {"tkip": 2, "aes": 3, "auto": 4}


def wifi_security_read(state: dict[str, Any], band: str, show_secrets: bool) -> dict[str, Any]:
    p = f"wireless_{band}_"
    auth = int(state.get(p + "auth_mode", 0) or 0)
    enc = int(state.get(p + "sec_encrypt_type", 0) or 0)
    if auth == 0:
        mode = "none"
    elif auth == 1:
        mode = "wep-64" if enc == 5 else "wep-128"
    elif auth in (2, 3, 4):
        mode = "wpa-personal"
    elif auth in (5, 6, 7):
        mode = "wpa-enterprise"
    else:
        mode = f"unknown({auth})"
    version = {2: "wpa", 3: "wpa2", 4: "mixed", 5: "wpa", 6: "wpa2", 7: "mixed"}.get(auth)
    encryption = {2: "tkip", 3: "aes", 4: "auto", 1: "wep-128", 5: "wep-64"}.get(enc)
    psk = str(state.get(p + "sec_wpap_preshare_key", "") or "")
    secret = str(state.get(p + "sec_wpae_radius_share_sec", "") or "")
    return {
        "security": mode,
        "wpa_version": version,
        "encryption": encryption,
        "psk": psk if show_secrets else (HIDDEN if psk else ""),
        "radius_ip": state.get(p + "sec_wpae_radius_ip1"),
        "radius_port": state.get(p + "sec_wpae_radius_port"),
        "radius_secret": secret if show_secrets else (HIDDEN if secret else ""),
    }


SECURITY_KEYS = (
    "security",
    "wpa_version",
    "encryption",
    "psk",
    "radius_ip",
    "radius_port",
    "radius_secret",
)


def wifi_security_json(state: dict[str, Any], band: str, changes: dict[str, str]) -> dict[str, Any]:
    """Build the exact JSON object the page's Apply handler would POST."""
    current = wifi_security_read(state, band, show_secrets=True)
    p = f"wireless_{band}_"
    mode = changes.get("security", current["security"]).strip().lower()
    if mode not in SECURITY_MODES:
        raise UsageError(
            what=f"security={mode!r} is not offered by this page",
            why="the Ubee web UI offers none, wpa-personal and wpa-enterprise",
            how="use security=wpa-personal (WEP is not offered and should not be used)",
        )
    body: dict[str, Any] = {}
    if mode == "none":
        body[p + "auth_mode"] = 0
        body[p + "sec_encrypt_type"] = 0
        return body
    version = changes.get("wpa_version", current["wpa_version"] or "wpa2").strip().lower()
    if version not in ("wpa2", "mixed"):
        raise UsageError(
            what=f"wpa_version={version!r}", why="the page offers wpa2 or mixed", how=""
        )
    encryption = changes.get("encryption", current["encryption"] or "aes").strip().lower()
    if encryption not in ("aes", "auto"):
        raise UsageError(
            what=f"encryption={encryption!r}", why="the page offers aes or auto", how=""
        )
    base = 2 if mode == "wpa-personal" else 5
    body[p + "auth_mode"] = base + WPA_VERSIONS[version]
    body[p + "sec_encrypt_type"] = ENCRYPTIONS[encryption]
    if mode == "wpa-personal":
        psk = changes.get("psk", current["psk"] or "")
        if not 8 <= len(psk) <= 63:
            raise UsageError(
                what="the pre-shared key must be 8 to 63 characters",
                why=f"got {len(psk)} characters",
                how="choose a longer passphrase",
            )
        body[p + "sec_wpap_preshare_key"] = psk
    else:
        radius_ip = validate_ipv4(changes.get("radius_ip", str(current["radius_ip"] or "")))
        port = parse_int(
            "radius_port",
            changes.get("radius_port", str(current["radius_port"] or "1812")),
            1,
            65535,
        )
        body[p + "sec_wpae_radius_ip1"] = radius_ip
        body[p + "sec_wpae_radius_port"] = port
        body[p + "sec_wpae_radius_share_sec"] = changes.get(
            "radius_secret", current["radius_secret"] or ""
        )
    return body


def wps_read(state2: dict[str, Any], state5: dict[str, Any], show_secrets: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for band, st in (("2g", state2), ("5g", state5)):
        p = f"wireless_{band}_"
        pin = str(st.get(p + "wps_pin", "") or "")
        out[band] = {
            "radio_enabled": bool(st.get(p + "enable", 0)),
            "ssid_broadcast": bool(st.get(p + "ssid_broadcast", 0)),
            "wps_enabled": bool(st.get(p + "wps_enable", 0)),
            "mode": "pin" if str(st.get(p + "wps_mode", 0)) == "1" else "pbc",
            "pin": pin if show_secrets else (HIDDEN if pin else ""),
            "last_status": st.get(p + "wps_last_status"),
        }
    return out


def wps_json(
    action: str,
    band: str,
    mode: str | None = None,
    pin: str | None = None,
    enabled: bool | None = None,
) -> dict[str, Any]:
    """The JSON each WPS button on the page posts (quirks included, see comments)."""
    if action == "enable":
        flag = "1" if enabled else "0"
        # One radio switch drives both bands; the page sends the radio's string value.
        return {"wireless_2g_wps_enable": flag, "wireless_5g_wps_enable": flag}
    p = f"wireless_{band}_"
    if action == "mode":
        body: dict[str, Any] = {p + "wps_mode": "1" if mode == "pin" else "0"}
        if mode == "pin":
            if not pin or not pin.isdigit() or len(pin) not in (4, 8):
                raise UsageError(what="a WPS PIN is 4 or 8 digits", why=f"got {pin!r}", how="")
            body[p + "wps_pin"] = pin
        return body
    if action == "connect":
        if band == "2g":
            # The 2.4 GHz Connect handler reads a select id that does not exist on the page,
            # so jQuery yields undefined and JSON.stringify drops the mode key. Mirror it.
            return {p + "wps_trigger": 1}
        return {p + "wps_trigger": 1, p + "wps_mode": "1" if mode == "pin" else "0"}
    raise UsageError(what=f"unknown WPS action {action!r}", why="", how="")


def mac_octets(mac: str) -> list[str]:
    return normalize_mac(mac).split(":")
