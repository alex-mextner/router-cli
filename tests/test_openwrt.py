"""OpenWrt over rpcd's /ubus JSON-RPC, against a fake rpcd (shapes from rpcd/luci-rpc)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from helpers import FIXTURES, UbusFake, creds

from router_cli._errors import NotLoggedInError
from router_cli.drivers import detect
from router_cli.drivers.openwrt import OpenWrt
from router_cli.models import PortForward

DATA: dict[str, Any] = json.loads((FIXTURES / "openwrt" / "ubus.json").read_text())


def handlers() -> dict[tuple[str, str], Any]:
    def uci_get(args: dict[str, Any]) -> Any:
        config = args["config"]
        if "section" in args:
            return {"values": DATA["uci"][config][args["section"]]}
        values = DATA["uci"][config]
        if "type" in args:
            values = {k: v for k, v in values.items() if v.get(".type") == args["type"]}
        return {"values": values}

    return {
        ("system", "board"): lambda a: DATA["board"],
        ("system", "info"): lambda a: DATA["info"],
        ("network.interface", "dump"): lambda a: DATA["interfaces"],
        ("luci-rpc", "getHostHints"): lambda a: DATA["hints"],
        ("luci-rpc", "getDHCPLeases"): lambda a: DATA["leases"],
        ("iwinfo", "devices"): lambda a: {"devices": ["phy0-ap0"]},
        ("iwinfo", "info"): lambda a: {"frequency": 5180, "ssid": "TESTNET"},
        ("iwinfo", "assoclist"): lambda a: DATA["assoclist"],
        ("uci", "get"): uci_get,
    }


def driver() -> tuple[OpenWrt, UbusFake]:
    fake = UbusFake(handlers())
    return OpenWrt(fake, creds("root")), fake


def test_detect() -> None:
    assert detect(UbusFake({})) == ("openwrt", "OpenWrt")


def test_status() -> None:
    d, fake = driver()
    status = d.status()
    assert status.router.model == "Test Router AX1800"
    assert status.router.firmware.startswith("OpenWrt 23.05")
    assert status.wan is not None
    assert (status.wan.ipv4, status.wan.netmask, status.wan.gateway) == (
        "192.0.2.20",
        "255.255.255.0",
        "192.0.2.1",
    )
    assert status.lan_ip == "10.0.0.1"
    assert fake.calls[0][:2] == ("session", "login")


def test_devices_merge_leases_hints_and_stations() -> None:
    d, _ = driver()
    devices = {x.mac: x for x in d.devices()}
    wired = devices["02:00:00:00:00:21"]
    assert (wired.ip, wired.hostname, wired.interface) == ("10.0.0.21", "nas", "lan")
    wifi = devices["02:00:00:00:00:22"]
    assert (wifi.interface, wifi.band, wifi.rssi_dbm, wifi.hostname) == (
        "wifi",
        "5GHz",
        -48,
        "phone",
    )
    only_wifi = devices["02:00:00:00:00:23"]
    assert only_wifi.ip == "10.0.0.23" and only_wifi.hostname == "tablet"  # from host hints


def test_leases_and_reservations() -> None:
    d, _ = driver()
    reservations = d.reservations()
    assert [(r.mac, r.ip, r.name) for r in reservations] == [
        ("02:00:00:00:00:21", "10.0.0.21", "nas")
    ]
    leases = {x.mac: x for x in d.leases()}
    assert leases["02:00:00:00:00:21"].kind == "reservation"
    assert leases["02:00:00:00:00:22"].kind == "dynamic"


def test_reserve_plan_uses_uci_and_redacts_the_session() -> None:
    d, fake = driver()
    plan = d.plan_reserve("02:00:00:00:00:22", "10.0.0.50", "My Phone")
    add, commit = plan.requests
    assert add.kind == commit.kind == "write"
    _sid, obj, method, args = add.json_body["params"]
    assert (obj, method) == ("uci", "add")
    assert args == {
        "config": "dhcp",
        "type": "host",
        "values": {"mac": "02:00:00:00:00:22", "ip": "10.0.0.50", "name": "My-Phone"},
    }
    assert commit.json_body["params"][1:3] == ["uci", "commit"]
    shown = json.dumps(add.to_dict(fake.base_url))
    assert "<session>" in shown and fake.session not in shown
    assert not [r for r in fake.sent if r.kind == "write"]  # planning never writes
    update = d.plan_reserve("02:00:00:00:00:21", "10.0.0.60", None)
    assert update.requests[0].json_body["params"][2] == "set"
    remove = d.plan_unreserve("02:00:00:00:00:21")
    assert remove.requests[0].json_body["params"][2:] == [
        "delete",
        {"config": "dhcp", "section": "cfg01"},
    ]


def test_port_forwards() -> None:
    d, _ = driver()
    rules = d.port_forwards()
    assert len(rules) == 1 and rules[0].external_start == 8443 and rules[0].local_start == 443
    assert rules[0].protocol == "tcp"
    plan = d.plan_port_forward_add(
        PortForward(-1, "10.0.0.21", 80, 80, None, 8080, 8080, "both", "web")
    )
    values = plan.requests[0].json_body["params"][3]["values"]
    assert (
        values["proto"] == "tcp udp"
        and values["dest_ip"] == "10.0.0.21"
        and values["target"] == "DNAT"
    )


def test_settings_areas_hide_keys() -> None:
    d, _ = driver()
    wifi = d.read_area("wifi")
    assert wifi["default_radio0.key"] == "<hidden>" and wifi["default_radio0.ssid"] == "TESTNET"
    assert d.read_area("wifi", show_secrets=True)["default_radio0.key"] == "fixture-wifi-key"
    assert d.read_area("dhcp")["leasetime"] == "12h"
    plan = d.plan_area("wifi", {"default_radio0.ssid": "NEWNET"})
    assert plan.requests[0].json_body["params"][3] == {
        "config": "wireless",
        "section": "default_radio0",
        "values": {"ssid": "NEWNET"},
    }


def test_login_failures() -> None:
    fake = UbusFake(handlers())
    with pytest.raises(NotLoggedInError):
        OpenWrt(fake, creds("root", "wrong")).devices()
    with pytest.raises(NotLoggedInError):
        OpenWrt(fake, None).devices()


def test_fixture_file_exists() -> None:
    assert Path(FIXTURES / "openwrt" / "ubus.json").is_file()
