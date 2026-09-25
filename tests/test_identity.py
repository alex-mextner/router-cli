"""Device identity in the inventory: brand / product / model / friendly name / location, the
Home Assistant registry matched by device id and by host onto a private MAC, IP-conflict
attribution, Xiaomi mesh placement, expected and offline services, HTTPS on the LAN. All
synthetic: no sockets are opened, no network is needed."""

from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from router_cli import fingerprint, ha_registry, icons
from router_cli import scan as scanmod
from router_cli._vendor.netprint import MdnsService, Signals
from router_cli.commands import discover
from router_cli.drivers.miwifi import MiWiFi, parse_mesh_nodes
from router_cli.http import (
    HttpRequest,
    _RedirectHandler,
    _UpgradeToHttps,
    check_path,
    is_lan_host,
    lan_tls_context,
)
from router_cli.inventory import Inventory, Sighting, _with_expected, from_epoch
from router_cli.lan.netinfo import host_facts

T0 = 1_780_000_000 - (1_780_000_000 % 3600)
CAST_REAL = "3c:00:00:00:00:10"  # the MAC Home Assistant registered
CAST_WIFI = "da:00:00:00:00:24"  # the private MAC it uses on this Wi-Fi
MINI = "b8:87:6e:00:00:17"
NODE = "50:88:11:00:00:20"


@pytest.fixture
def inv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Inventory:
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setattr(Inventory, "local_ifaces", lambda self: [])
    icons.load_rules.cache_clear()
    return Inventory(tmp_path / "inv.sqlite3")


def at(offset: int) -> str:
    return from_epoch(T0 + offset)


def _write_ha(tmp_path: Path) -> Path:
    storage = tmp_path / "ha" / ".storage"
    storage.mkdir(parents=True)
    entries = [
        {"entry_id": "e1", "domain": "androidtv_remote", "title": "Kitchen",
         "data": {"host": "10.9.8.24", "mac": CAST_REAL, "name": "Kitchen"}},
        {"entry_id": "e2", "domain": "yandex_station", "title": "acc", "data": {"token": "S"}},
        {"entry_id": "e3", "domain": "moonraker", "title": "3D", "data": {"url": "10.9.8.26"}},
    ]  # fmt: skip
    devices = [
        {"id": "d1", "config_entries": ["e1"], "name": "Kitchen", "name_by_user": "Хромкаст",
         "manufacturer": "Google", "model": "Chromecast HD", "area_id": "kitchen",
         "connections": [["mac", CAST_REAL]], "identifiers": [["androidtv_remote", CAST_REAL]]},
        {"id": "d2", "config_entries": ["e2"], "name": "Мини детская", "manufacturer": "Яндекс",
         "model": "Станция Мини 2 (2021)", "sw_version": "1.2.3", "area_id": "kids",
         "connections": [], "identifiers": [["yandex_station", "SYNTH0000000X"]]},
        {"id": "d3", "config_entries": ["e3"], "name": "Printer", "manufacturer": "moonraker",
         "model": "moonraker", "connections": [], "identifiers": [["moonraker", "01ABC"]]},
    ]  # fmt: skip
    areas = [{"id": "kitchen", "name": "Кухня"}, {"id": "kids", "name": "Детская"}]
    (storage / "core.config_entries").write_text(json.dumps({"data": {"entries": entries}}))
    (storage / "core.device_registry").write_text(json.dumps({"data": {"devices": devices}}))
    (storage / "core.area_registry").write_text(json.dumps({"data": {"areas": areas}}))
    return tmp_path / "ha"


def test_ha_registry_ids_areas_and_private_mac_host(tmp_path: Path) -> None:
    devices = {d.name: d for d in ha_registry.load(_write_ha(tmp_path))}
    assert devices["Хромкаст"].area == "Кухня"
    printer = devices["Printer"]
    assert printer.manufacturer is None and printer.model is None  # software, not the device
    assert "S" not in json.dumps([d.facts("x") for d in devices.values()])  # no secrets
    ids = {MINI: {"synth0000000x"}}
    online = {"10.9.8.24": CAST_WIFI}
    facts = ha_registry.facts_by_mac(list(devices.values()), {}, {}, ids, online, set())
    assert facts[CAST_REAL]["matched"] == "mac"
    assert facts[CAST_WIFI]["matched"] == "host" and facts[CAST_WIFI]["macs"] == [CAST_REAL]
    assert facts[MINI]["matched"] == "id" and facts[MINI]["sw_version"] == "1.2.3"
    # once the registered MAC itself was seen on the LAN, a private MAC at the host is not it
    facts = ha_registry.facts_by_mac(list(devices.values()), {}, {}, ids, online, {CAST_REAL})
    assert CAST_WIFI not in facts
    assert ha_registry.normalize_id("uuid:68AB-CD01-23EF") == "68abcd0123ef"
    assert ha_registry.normalize_id("short") is None


def test_chromecast_on_a_private_mac_is_google_and_grouped(inv: Inventory) -> None:
    cast_mdns = {
        "hostnames": ["00000000-0000-0000-0000-000000000024"],
        "services": [
            {"type": "_googlecast._tcp", "name": "Chromecast-HD-0", "port": 8009,
             "txt": {"md": "Chromecast HD", "fn": "Kitchen TV", "id": "0000000000000024"}}
        ],
    }  # fmt: skip
    ha = ha_registry.HaDevice(
        name="Хромкаст",
        manufacturer="Google",
        model="Chromecast HD",
        domains=["androidtv_remote"],
        title="Kitchen",
        macs=[CAST_REAL],
        area="Кухня",
    )
    inv.record_discovery(
        [
            Sighting(CAST_WIFI, "10.9.8.24", facts={"mdns": cast_mdns, "ha": ha.facts("host")}),
            Sighting(CAST_REAL, present=False, facts={"ha": ha.facts("mac")}),
        ],
        at=at(0),
    )
    devices = inv.devices("all", now=datetime.fromtimestamp(T0, UTC))
    (cast,) = devices  # the registered MAC is folded into the device it uses on Wi-Fi
    assert cast["mac"] == CAST_WIFI and [i["mac"] for i in cast["interfaces"]] == [
        CAST_WIFI,
        CAST_REAL,
    ]
    assert cast["display_name"] == "Google Chromecast «Kitchen TV»"
    assert (cast["brand"], cast["vendor"], cast["oui_vendor"]) == ("Google", "Google", None)
    assert cast["product"] == "Chromecast HD" and cast["friendly_name"] == "Kitchen TV"
    assert cast["location"] == "Кухня" and cast["category"] == "media-player"


def test_expected_and_offline_services(inv: Inventory) -> None:
    printer = "fc:ee:28:00:00:27"
    ha = {"domains": ["ha_creality_ws"], "manufacturer": "Creality", "model": "K1 SE",
          "name": "K1SE-0A1B", "title": "K1", "macs": [], "matched": "host"}  # fmt: skip
    inv.record_discovery([Sighting(printer, present=False, facts={"ha": ha})], at=at(0))
    with inv.db:
        inv.db.execute("UPDATE devices SET reserved_ip = '10.9.8.27' WHERE mac = ?", (printer,))
    (dev,) = inv.devices("all")
    assert dev["display_name"] == "Creality K1 SE" and dev["ip"] == "10.9.8.27"
    (svc,) = dev["services"]
    assert svc["url"] == "http://10.9.8.27/" and svc["expected"] is True
    assert (svc["reachable"], svc["error"]) == (False, "offline")
    known = [{"port": 4408, "scheme": "http", "url": "u", "title": "Fluidd", "reachable": True,
              "http_status": 200, "error": None}]  # fmt: skip
    out = _with_expected(known, [{"port": 80, "title": "UI"}], "10.9.8.27", False, None)
    assert [(s["port"], s["reachable"], s["error"], s["expected"]) for s in out] == [
        (80, False, "offline", True),
        (4408, False, "offline", False),
    ]
    # online and scanned with port 80 closed: the expected UI is not invented
    out = _with_expected([], [{"port": 80}], "10.9.8.27", True, {7125})
    assert out == []


def test_mesh_topology_locale_and_link_local() -> None:
    topo = {
        "graph": {
            "ip": "192.168.31.1", "name": "home-mesh", "locale": "Hallway", "hardware": "RD28",
            "mode": 2,
            "leafs": [{"ip": "192.168.31.2", "name": "rd28_minet_0000", "locale": "Study",
                       "link_type": "wired", "onlines": 3, "mode": 1}],
        }
    }  # fmt: skip
    root, leaf = parse_mesh_nodes(topo)
    assert (root["locale"], root["root"], root["mac"]) == ("Hallway", True, None)
    assert (leaf["locale"], leaf["link_type"], leaf["clients"], leaf["root"]) == (
        "Study",
        "wired",
        3,
        False,
    )
    assert discover.link_local("50:88:11:00:00:20", "wlan0") == "fe80::5288:11ff:fe00:20%wlan0"


class TopoFake:
    base_url = "https://192.168.31.2"

    def get(self, path: str) -> str:
        check_path(path)
        if path.endswith("topo_graph") and ";stok=" not in path:
            return json.dumps({"graph": {"ip": "192.168.31.2", "locale": "Study"}, "code": 0})
        return json.dumps({"code": 401})

    def send(self, request: HttpRequest) -> str:
        raise AssertionError("no login needed for the public topology")


def test_miwifi_topology_is_public() -> None:
    driver = MiWiFi(TopoFake(), None)
    (node,) = driver.mesh_nodes()
    assert node["locale"] == "Study"


def test_conflicted_address_answers_are_attributed_by_brand() -> None:
    answer = Signals(
        mdns=[MdnsService("_yandexio._tcp", "YandexIOReceiver-0", txt={"platform": "yandexmini"})]
    )
    vendors = {MINI: "Intertech Services", NODE: "Xiaomi Mobile Software"}
    assert discover.attribute(answer, [NODE, MINI], vendors) == MINI
    assert discover.attribute(Signals(), [NODE, MINI], vendors) is None  # names no brand
    both = {MINI: "Intertech Services", "3c:0b:4f:00:00:01": "Intertech Services"}
    assert discover.attribute(answer, sorted(both), both) is None  # two could have sent it


def test_device_ids_from_announcements() -> None:
    facts = {
        "mdns": {"services": [{"type": "_yandexio._tcp", "txt": {"deviceId": "SYNTH0000000X"}}]},
        "ssdp": {"devices": [{"usn": "uuid:00000000-1111-2222-3333-444444444444::upnp:root"}]},
    }  # fmt: skip
    assert fingerprint.device_ids(facts) == {"synth0000000x", "00000000111122223333444444444444"}


def test_rescan_targets(inv: Inventory) -> None:
    inv.save_scan("02:00:00:00:00:31", "10.9.8.31", [80], [], from_epoch(T0))
    present: dict[str, str | None] = {
        "02:00:00:00:00:30": "10.9.8.30",  # never scanned
        "02:00:00:00:00:31": "10.9.8.31",  # scanned long ago
        "02:00:00:00:00:32": "10.9.8.1",  # the gateway: never
        "02:00:00:00:00:33": None,
    }
    targets = discover._rescan_targets(inv, present, {"10.9.8.1"})
    assert targets == [("10.9.8.30", "02:00:00:00:00:30"), ("10.9.8.31", "02:00:00:00:00:31")]


def test_ssh_banner_is_read_and_classified(inv: Inventory, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scanmod, "port_state", lambda ip, port, timeout: None)
    monkeypatch.setattr(scanmod, "probe_http", lambda *a, **k: None)
    monkeypatch.setattr(
        scanmod, "read_banner", lambda ip, port, timeout: "SSH-2.0-OpenSSH_9.6p1 Ubuntu-3"
    )
    (result,) = scanmod.scan_hosts([("10.9.8.36", "02:00:00:00:00:36")], ports=(22,))
    assert result.banners == {"22": "SSH-2.0-OpenSSH_9.6p1 Ubuntu-3"}
    inv.record_discovery([Sighting("02:00:00:00:00:36", "10.9.8.36")], at=at(0))
    inv.save_scan(result.mac or "", result.ip, result.open_ports, [], at(0), result.banners)
    (dev,) = inv.devices("all", now=datetime.fromtimestamp(T0, UTC))
    assert dev["os"] == "Ubuntu"


def test_host_facts(tmp_path: Path) -> None:
    dmi = tmp_path / "sys" / "class" / "dmi" / "id"
    dmi.mkdir(parents=True)
    (dmi / "sys_vendor").write_text("Synthetic Computers Inc.\n")
    (dmi / "product_name").write_text("To Be Filled By O.E.M.\n")
    (tmp_path / "etc").mkdir()
    (tmp_path / "etc" / "os-release").write_text('NAME="X"\nPRETTY_NAME="Synthetic OS 1.0"\n')
    facts = host_facts(tmp_path)
    assert facts == {"dmi.vendor": "Synthetic Computers Inc.", "os.name": "Synthetic OS 1.0"}
    assert host_facts(tmp_path / "missing") == {}


def test_https_upgrade_on_the_lan() -> None:
    handler = _RedirectHandler()
    req = urllib.request.Request("http://192.168.31.1/cgi-bin/luci/api/x", data=b"a=1")
    with pytest.raises(_UpgradeToHttps) as info:
        handler.redirect_request(req, None, 301, "Moved", {}, "https://192.168.31.1/cgi-bin/x")
    assert info.value.url == "https://192.168.31.1/cgi-bin/x"
    same_scheme: Any = handler.redirect_request(
        urllib.request.Request("http://192.168.31.1/a"), None, 302, "Found", {}, "http://192.168.31.1/b"
    )  # fmt: skip
    assert same_scheme is not None and same_scheme.full_url == "http://192.168.31.1/b"
    assert is_lan_host("192.168.31.1") and is_lan_host("fe80::1%wlan0") and is_lan_host("x.local")
    assert not is_lan_host("example.com") and not is_lan_host("8.8.8.8")
    assert lan_tls_context("https://192.168.31.1/") is not None
    assert lan_tls_context("https://example.com/") is None
    assert lan_tls_context("http://192.168.31.1/") is None
