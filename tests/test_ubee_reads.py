"""Ubee EVW32C: every read, against the (synthetic) page fixtures."""

from __future__ import annotations

import pytest
from helpers import UbeeFake, creds, ubee_page

from router_cli._errors import NotLoggedInError
from router_cli.drivers import detect
from router_cli.drivers.ubee_evw32c import UbeeEVW32C, parse_expiry, parse_uptime

STATION_ROWS = (
    "<tr bgcolor=#9999CC><td>02:00:00:00:0F:01</td><td>12</td><td>-55</td><td>192.168.0.150</td>"
    "<td>test-phone</td><td>11n</td><td>72000</td></tr>"
)


def driver(fake: UbeeFake | None = None) -> UbeeEVW32C:
    return UbeeEVW32C(fake or UbeeFake(), creds())


def test_detect_from_rootdevice_xml() -> None:
    assert detect(UbeeFake()) == ("ubee_evw32c", "EVW32C-0N")


def test_status() -> None:
    status = driver().status()
    assert status.router.model == "EVW32C-0N"
    assert status.router.firmware == "2.4.1015-SIP"
    assert status.router.host == "192.168.0.1"  # bare, as users type it
    assert status.uptime_s == parse_uptime("94 days 01h:25m:22s")
    assert status.wan is not None
    assert status.wan.ipv4 == "192.0.2.10" and status.wan.gateway == "192.0.2.1"
    assert status.wan.dns == ["198.51.100.30", "198.51.100.40", "198.51.100.50"]
    assert status.docsis is not None
    assert (status.docsis.downstream_locked, status.docsis.downstream_total) == (24, 24)
    assert (status.docsis.upstream_locked, status.docsis.upstream_total) == (6, 8)
    assert status.docsis.provisioning["registration"] == "Completed"
    assert status.lan_ip == "192.168.0.1"


def test_uptime_and_expiry_parsing() -> None:
    assert parse_uptime("1 days 01h:00m:05s") == 90005
    assert parse_uptime("garbage") is None
    assert parse_expiry("Thu Sep 24 20:20:57 2026\n") == "2026-09-24T20:20:57"
    assert parse_expiry("*** STATIC IP ADDRESS **") is None


def test_devices_lan_table() -> None:
    devices = driver().devices()
    assert len(devices) == 20
    by_ip = {d.ip: d for d in devices}
    static = by_ip["192.168.0.13"]
    assert static.static_ip and static.lease_expires is None
    assert static.mac == "02:00:00:00:01:08"  # the table's uppercase MACs are normalised
    dynamic = by_ip["192.168.0.14"]
    assert dynamic.lease_expires and dynamic.lease_expires.startswith("2026-09-24T")
    assert all(d.interface == "lan" and d.hostname is None for d in devices)


def test_devices_wifi_stations_merge() -> None:
    fake = UbeeFake()
    page = ubee_page("UbeeAdvConnectedDevicesList.asp")
    marker = '<tr><td colspan=5><label id="ID_LABEL_NO_STA_DESC_2G">'
    fake.overrides["UbeeAdvConnectedDevicesList.asp"] = page.replace(marker, STATION_ROWS + marker)
    devices = {d.mac: d for d in driver(fake).devices()}
    sta = devices["02:00:00:00:0f:01"]
    assert (sta.interface, sta.band, sta.rssi_dbm, sta.hostname) == (
        "wifi",
        "2.4GHz",
        -55,
        "test-phone",
    )
    assert sta.speed_kbps == 72000 and sta.ip == "192.168.0.150"


def test_reservations_and_leases() -> None:
    d = driver()
    reservations = d.reservations()
    assert len(reservations) == 7  # slot 8 is all zeros
    assert reservations[0].mac == "02:00:00:00:01:01" and reservations[0].ip == "192.168.0.39"
    leases = {lease.mac: lease for lease in d.leases()}
    assert leases["02:00:00:00:01:01"].kind == "reservation" and leases["02:00:00:00:01:01"].active
    offline = [x for x in leases.values() if x.kind == "reservation" and not x.active]
    assert {x.ip for x in offline} == {
        "192.168.0.11",
        "192.168.0.12",
        "192.168.0.27",
        "192.168.0.52",
    }
    assert leases["02:00:00:00:01:08"].kind == "static"


def test_areas_read() -> None:
    d = driver()
    dhcp = d.read_area("dhcp")
    assert dhcp == {
        "enabled": True,
        "start": 10,
        "end": 254,
        "lease_time": 3600,
        "pool_start": "192.168.0.10",
        "pool_end": "192.168.0.254",
    }
    lan = d.read_area("lan")
    assert lan["ip"] == "192.168.0.1" and lan["dns1"] == "198.51.100.30"
    wifi = d.read_area("wifi-2g")
    assert wifi["ssid"] == "TESTNET" and wifi["enabled"] is False and wifi["mode"] == "g/n"
    assert wifi["channel"] == "6" and wifi["power"] == "100"
    assert (wifi["security"], wifi["wpa_version"], wifi["encryption"]) == (
        "wpa-personal",
        "mixed",
        "auto",
    )
    assert wifi["psk"] == "<hidden>"
    assert d.read_area("wifi-2g", show_secrets=True)["psk"] == "fixture-psk-12345"
    assert d.read_area("wifi-5g")["mode"] == "a/n/ac"
    assert d.read_area("firewall")["level"] == "low"
    assert d.read_area("options")["upnp"] is True
    assert d.read_area("dmz")["host"] is None
    nas = d.read_area("nas")
    assert nas["password"] == "<hidden>" and nas["samba"] is True and nas["ftp"] is False
    assert d.read_area("parental")["override_password"] == "<hidden>"
    assert d.read_area("telephony")["port_1_phone_number"] == "[N/A]"
    wps = d.read_area("wps")
    assert wps["2g"]["wps_enabled"] is True and wps["2g"]["mode"] == "pbc"
    generic = d.read_area("vpn-ipsec")
    assert generic["TunnelEnable"] == "0"


def test_lists_and_port_forwards() -> None:
    d = driver()
    assert d.list_items("keywords") == ["anonymizer"]
    assert d.list_items("blocked-domains") == ["anonymizer.com"]
    assert d.list_items("mac-filter") == []
    assert d.list_items("wifi-acl-2g") == []
    rules = d.port_forwards()
    assert len(rules) == 1
    r = rules[0]
    assert (r.local_ip, r.local_start, r.external_start, r.protocol, r.description, r.enabled) == (
        "192.168.0.200",
        8080,
        18080,
        "tcp",
        "test",
        True,
    )


def test_docsis_channels() -> None:
    channels = driver().docsis_channels()
    down = [c for c in channels if c.direction == "downstream"]
    assert down[0].frequency_hz == 266_000_000 and down[0].snr_db == 39.7
    up = [c for c in channels if c.direction == "upstream"]
    assert up[-1].locked is False


def test_relogin_when_session_is_gone() -> None:
    fake = UbeeFake(logged_in=False)
    status = driver(fake).status()
    assert status.router.model == "EVW32C-0N"
    logins = [r for r in fake.sent if r.kind == "login"]
    assert len(logins) == 1
    assert logins[0].path == "/goform/login"
    assert dict(logins[0].fields) == {"loginUsername": "admin", "loginPassword": "secret"}
    assert not [r for r in fake.sent if r.kind == "write"]


def test_no_session_no_credentials() -> None:
    with pytest.raises(NotLoggedInError):
        UbeeEVW32C(UbeeFake(logged_in=False), None).devices()


def test_wrong_password() -> None:
    fake = UbeeFake(logged_in=False, password="other")
    with pytest.raises(NotLoggedInError):
        driver(fake).devices()


def test_never_fetches_logout() -> None:
    fake = UbeeFake()
    d = driver(fake)
    d.status()
    d.devices()
    d.leases()
    assert not any("logout" in g.lower() for g in fake.gets)
