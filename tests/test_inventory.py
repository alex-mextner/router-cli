"""The inventory DB and the JSON contract the Home Assistant dashboard reads."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from router_cli import icons, oui
from router_cli.inventory import Inventory, parse_since
from router_cli.models import Device, Reservation, RouterInfo, is_random_mac, normalize_mac
from router_cli.scan import favicon, icon_href, title_of

CONTRACT_KEYS = {
    "mac",
    "ip",
    "hostname",
    "names",
    "vendor",
    "random_mac",
    "interface",
    "online",
    "first_seen",
    "last_seen",
    "reserved_ip",
    "ip_history",
    "icon",
    "services",
}
# Added later (the contract only grows): classification, topology, traffic, grouping.
ADDED_KEYS = {
    "category",
    "confidence",
    "label",
    "evidence",
    "alternatives",
    "display_name",
    "pinnable",
    "is_network_gear",
    "is_self",
    "connection",
    "traffic",
    "interfaces",
    "same_device_as",
}
SERVICE_KEYS = {
    "port",
    "scheme",
    "url",
    "title",
    "server",
    "favicon_data_url",
    "checked_at",
    "reachable",
    "http_status",
    "error",
}
INFO = RouterInfo(driver="ubee_evw32c", host="192.168.0.1", model="EVW32C-0N")


@pytest.fixture
def inv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Inventory:
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    icons.load_rules.cache_clear()
    return Inventory(tmp_path / "inv.sqlite3")


def test_polls_merge(inv: Inventory) -> None:
    a = Device(mac="02:00:00:00:00:01", ip="192.168.0.20", hostname="printer")
    b = Device(mac="02:00:00:00:00:02", ip="192.168.0.21", interface="wifi", band="5GHz")
    first = inv.record_poll(
        INFO,
        [a, b],
        [Reservation("02:00:00:00:00:03", "192.168.0.30")],
        at="2026-01-01T00:00:00+00:00",
    )
    assert sorted(first.new) == ["02:00:00:00:00:01", "02:00:00:00:00:02"]
    a2 = Device(mac="02:00:00:00:00:01", ip="192.168.0.25")
    second = inv.record_poll(INFO, [a2], None, at="2026-01-02T00:00:00+00:00")
    assert second.new == [] and second.went_offline == ["02:00:00:00:00:02"]
    devices = {d["mac"]: d for d in inv.devices("all")}
    assert set(devices) == {"02:00:00:00:00:01", "02:00:00:00:00:02", "02:00:00:00:00:03"}
    d1 = devices["02:00:00:00:00:01"]
    assert set(d1) == CONTRACT_KEYS | ADDED_KEYS
    assert d1["pinnable"] is False and d1["connection"]["type"] == "wifi"  # random MAC
    assert (
        d1["first_seen"] == "2026-01-01T00:00:00+00:00"
        and d1["last_seen"] == "2026-01-02T00:00:00+00:00"
    )
    assert d1["ip"] == "192.168.0.25" and d1["online"] is True
    assert [h["ip"] for h in d1["ip_history"]] == ["192.168.0.25", "192.168.0.20"]
    assert d1["hostname"] == "printer" and d1["names"] == ["printer"]  # kept across polls
    assert devices["02:00:00:00:00:02"]["online"] is False
    reserved = devices["02:00:00:00:00:03"]
    assert reserved["reserved_ip"] == "192.168.0.30" and reserved["first_seen"] is None
    assert reserved["random_mac"] is True  # 02:... is locally administered
    json.dumps(devices)  # the contract is plain JSON


def test_filters(inv: Inventory) -> None:
    now = datetime(2026, 1, 10, tzinfo=UTC)
    inv.record_poll(
        INFO,
        [Device(mac="02:00:00:00:00:01", ip="192.168.0.20")],
        None,
        at="2026-01-01T00:00:00+00:00",
    )
    inv.record_poll(
        INFO,
        [Device(mac="02:00:00:00:00:02", ip="192.168.0.21")],
        [Reservation("02:00:00:00:00:01", "192.168.0.20")],
        at="2026-01-09T12:00:00+00:00",
    )
    macs = lambda f, s="24h": [d["mac"] for d in inv.devices(f, parse_since(s), now=now)]  # noqa: E731
    assert macs("active") == ["02:00:00:00:00:02"]
    assert macs("recent") == ["02:00:00:00:00:02"]
    assert macs("recent", "30d") == ["02:00:00:00:00:02", "02:00:00:00:00:01"]
    assert macs("new") == ["02:00:00:00:00:02"]
    assert macs("reserved") == ["02:00:00:00:00:01"]
    assert parse_since("90m") == timedelta(minutes=90)


def test_alias_and_services_drive_hostname_and_icon(inv: Inventory) -> None:
    mac = "02:00:00:00:00:05"
    inv.record_poll(INFO, [Device(mac=mac, ip="192.168.0.50")], None)
    assert inv.devices("all")[0]["icon"] == "mdi:cellphone"  # random MAC, nothing else known
    inv.save_scan(
        mac,
        "192.168.0.50",
        [80, 8123],
        [
            {
                "port": 8123,
                "scheme": "http",
                "url": "http://192.168.0.50:8123/",
                "title": "Home Assistant",
                "server": None,
                "favicon_data_url": None,
                "checked_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        "2026-01-01T00:00:00+00:00",
    )
    device = inv.devices("all")[0]
    assert device["icon"] == "mdi:home-assistant"
    assert set(device["services"][0]) == SERVICE_KEYS
    inv.set_alias(mac, name="Kitchen HA", icon="mdi:chip")
    device = inv.devices("all")[0]
    assert device["hostname"] == "Kitchen HA" and device["names"][0] == "Kitchen HA"
    assert device["icon"] == "mdi:chip"
    inv.set_alias(mac, clear=True)
    assert inv.devices("all")[0]["icon"] == "mdi:home-assistant"


def test_icon_rules() -> None:
    icons.load_rules.cache_clear()
    choose = icons.choose
    assert choose(icons.Facts(ports=[7125])) == "mdi:printer-3d"
    assert choose(icons.Facts(titles=["fluidd"])) == "mdi:printer-3d"
    assert choose(icons.Facts(vendor="Espressif")) == "mdi:chip"
    assert choose(icons.Facts(vendor="Raspberry Pi Trading")) == "mdi:raspberry-pi"
    assert choose(icons.Facts(hostnames=["Johns-iPhone"])) == "mdi:apple"
    assert choose(icons.Facts(random_mac=True, ports=[8123])) == "mdi:home-assistant"
    assert choose(icons.Facts()) == "mdi:help-network"


def test_user_icon_rules_come_first(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / "icon_rules.json").write_text(
        json.dumps({"rules": [{"icon": "mdi:fish", "vendor": "espressif"}]})
    )
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(cfg))
    icons.load_rules.cache_clear()
    try:
        assert icons.choose(icons.Facts(vendor="Espressif")) == "mdi:fish"
    finally:
        icons.load_rules.cache_clear()


def test_oui_and_macs() -> None:
    assert normalize_mac("02-00-00-00-00-AA") == "02:00:00:00:00:aa"
    assert normalize_mac("0200.0000.00aa") == "02:00:00:00:00:aa"
    assert is_random_mac("02:00:00:00:00:01") and not is_random_mac("b8:27:eb:00:00:01")
    assert oui.shorten("Apple, Inc.") == "Apple"
    assert oui.shorten("Espressif Inc.") == "Espressif"
    assert oui.shorten("SHENZHEN BILIAN ELECTRONIC\uff0cLTD") == "Bilian"
    assert oui.shorten("Beijing Xiaomi Mobile Software Co., Ltd") == "Xiaomi Mobile Software"
    assert len(oui.table()) > 1000
    assert oui.vendor("b8:27:eb:00:00:01") == "Raspberry Pi Foundation"
    assert oui.vendor("02:00:00:00:00:01") is None  # random: never looked up


def test_scan_parsing() -> None:
    assert title_of("<html><TITLE>\n  Home &amp; Garden </TITLE>") == "Home & Garden"
    page = (
        '<link rel="apple-touch-icon" href="/big.png">'
        "<link rel='shortcut icon' href='/fav.png'>"
        '<link rel="mask-icon" href="/mask.svg">'
    )
    assert icon_href(page) == "/fav.png"
    assert icon_href("<p>no icons</p>") is None
    # an icon hosted elsewhere is never fetched
    assert (
        favicon("http", "192.0.2.9", 80, '<link rel="icon" href="http://example.com/x.ico">', 0.1)
        is None
    )
