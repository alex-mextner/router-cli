"""LAN discovery, the Xiaomi mesh driver, device classification in the inventory, presence
history and stats. Everything synthetic: no sockets are opened, no network is needed."""

from __future__ import annotations

import hashlib
import json
import socket
import struct
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from router_cli import fingerprint, ha_registry, icons
from router_cli import scan as scanmod
from router_cli._errors import NotLoggedInError
from router_cli.commands import discover
from router_cli.commands.discover import _near, _wifi_via
from router_cli.drivers.miwifi import (
    KEY,
    MiClient,
    MiWiFi,
    merge_clients,
    parse_clients,
    parse_mesh_nodes,
    password_hash,
    signal_to_dbm,
)
from router_cli.http import HttpRequest, check_path
from router_cli.inventory import GRACE_S, Inventory, Sighting, from_epoch
from router_cli.lan import mdns, netbios, ssdp
from router_cli.lan.netinfo import LocalIface
from router_cli.models import Device, RouterInfo

INFO = RouterInfo(driver="ubee_evw32c", host="10.9.8.1", model="EVW32C-0N")
T0 = 1_780_000_000 - (1_780_000_000 % 3600)
A = "02:00:00:00:00:01"
B = "02:00:00:00:00:02"
C = "02:00:00:00:00:03"


@pytest.fixture
def inv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Inventory:
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setattr(Inventory, "local_ifaces", lambda self: [])
    icons.load_rules.cache_clear()
    return Inventory(tmp_path / "inv.sqlite3")


def at(offset: int) -> str:
    return from_epoch(T0 + offset)


# ── mDNS ─────────────────────────────────────────────────────────────────────
def _name(n: str) -> bytes:
    return b"".join(bytes([len(p)]) + p.encode() for p in n.split(".")) + b"\0"


def _rr(name: str, rtype: int, rdata: bytes) -> bytes:
    return _name(name) + struct.pack("!HHIH", rtype, 1, 120, len(rdata)) + rdata


def _txt(items: dict[str, str]) -> bytes:
    return b"".join(bytes([len(f"{k}={v}")]) + f"{k}={v}".encode() for k, v in items.items())


def test_mdns_answer_is_parsed_and_attributed() -> None:
    instance = "Kitchen light._esphomelib._tcp.local"
    records = [
        _rr("_esphomelib._tcp.local", mdns.T_PTR, _name(instance)),
        _rr(instance, mdns.T_SRV, struct.pack("!HHH", 0, 0, 6053) + _name("kitchen-light.local")),
        _rr(instance, mdns.T_TXT, _txt({"friendly_name": "Kitchen light", "board": "esp32dev"})),
        _rr("kitchen-light.local", mdns.T_A, socket.inet_aton("10.9.8.50")),
        _rr("50.8.9.10.in-addr.arpa.local", mdns.T_PTR, _name("kitchen-light.local")),
    ]
    packet = struct.pack("!HHHHHH", 0, 0x8400, 0, len(records), 0, 0) + b"".join(records)
    parsed = mdns.parse_message(packet)
    assert {r.rtype for r in parsed} == {mdns.T_PTR, mdns.T_SRV, mdns.T_TXT, mdns.T_A}
    collector = mdns._Collector()
    collector.add("10.9.8.50", parsed)
    hosts = mdns._assemble(collector)
    host = hosts["10.9.8.50"]
    assert "kitchen-light" in host.hostnames
    (svc,) = host.services.values()
    assert (svc.type, svc.name, svc.port) == ("_esphomelib._tcp", "Kitchen light", 6053)
    assert svc.txt["friendly_name"] == "Kitchen light"
    query = mdns.build_query([(mdns.META, mdns.T_PTR)])
    assert query[:12] == struct.pack("!HHHHHH", 0, 0, 1, 0, 0, 0)
    assert mdns.reverse_name("10.9.8.50") == "50.8.9.10.in-addr.arpa.local"


def test_mdns_garbage_does_not_raise() -> None:
    assert mdns.parse_message(b"\x00" * 5) == []
    assert mdns.parse_message(b"\x00" * 12 + b"\xc0\xff") == []


# ── SSDP / NetBIOS ───────────────────────────────────────────────────────────
def test_ssdp_answer_and_description() -> None:
    answer = ssdp.parse_answer(
        b"HTTP/1.1 200 OK\r\nST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n"
        b"USN: uuid:00000000-0000-0000-0000-000000000001\r\nSERVER: Synthetic/1.0 UPnP/1.0\r\n"
        b"LOCATION: http://10.9.8.60:7676/desc.xml\r\n\r\n"
    )
    assert answer is not None and answer.location == "http://10.9.8.60:7676/desc.xml"
    assert ssdp.parse_answer(b"garbage") is None
    xml = (
        "<root><device><deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>"
        "<friendlyName>[TV] Living &amp; room</friendlyName><manufacturer>Samsung Electronics"
        "</manufacturer><modelName><![CDATA[UE55TU7100]]></modelName></device></root>"
    )
    desc = ssdp.parse_description(xml)
    assert desc["friendly_name"] == "[TV] Living & room" and desc["model_name"] == "UE55TU7100"
    host = ssdp.SsdpHost(ip="10.9.8.60", answers=[answer])
    host.descriptions[answer.location or ""] = desc
    (dev,) = host.devices()
    assert dev["model_name"] == "UE55TU7100" and dev["st"].endswith("MediaRenderer:1")
    # descriptions are only ever fetched from the answering address, over plain HTTP
    assert ssdp.fetch_description("10.9.8.61", "http://10.9.8.60/desc.xml") is None
    assert ssdp.fetch_description("10.9.8.60", "https://10.9.8.60/desc.xml") is None


def test_netbios_node_status() -> None:
    names = [("WORKSTATION1", 0x00, 0x0400), ("WORKGROUP", 0x00, 0x8400), ("WORKSTATION1", 0x20, 0)]
    body = bytes([len(names)]) + b"".join(
        n.ljust(15).encode() + bytes([suffix]) + struct.pack("!H", flags)
        for n, suffix, flags in names
    )
    packet = (
        struct.pack("!HHHHHH", 1, 0x8400, 0, 1, 0, 0)
        + netbios._WILDCARD
        + struct.pack("!HHIH", 0x21, 1, 0, len(body))
        + body
    )
    assert netbios.parse_response(packet) == (["WORKSTATION1"], "WORKGROUP")
    assert netbios.parse_response(b"\x00" * 10) == ([], None)


# ── Xiaomi ───────────────────────────────────────────────────────────────────
DEVICELIST = {
    "code": 0,
    "list": [
        {"mac": "02:00:00:00:00:11", "name": "phone", "type": 2, "online": 1,
         "parent": "02:00:00:00:00:21", "ip": [{"ip": "192.168.31.11", "downspeed": "10"}]},
        {"mac": "02:00:00:00:00:12", "name": "desk", "type": 0, "online": 1,
         "ip": [{"ip": "192.168.31.12"}]},
        {"mac": "02:00:00:00:00:21", "name": "node", "type": 0, "isap": 1, "online": 1},
        {"mac": "not-a-mac"},
    ],
}  # fmt: skip
STATUS = {"dev": [{"mac": "02:00:00:00:00:11", "upload": "1000", "download": "5000",
                   "upspeed": "3", "downspeed": "7", "devname": "phone"}]}  # fmt: skip
WIFI = {"list": [{"mac": "02:00:00:00:00:11", "signal": -61}]}


def test_miwifi_parse_clients_older_shape() -> None:
    """``misystem/devicelist`` + ``status.dev`` + a firmware that reports dBm directly."""
    clients = {c.mac: c for c in parse_clients(DEVICELIST, STATUS, WIFI)}
    phone = clients["02:00:00:00:00:11"]
    assert (phone.connection, phone.band, phone.via, phone.rssi) == (
        "wifi",
        "5",
        "02:00:00:00:00:21",
        -61,
    )
    assert (phone.rx_bytes, phone.tx_bytes, phone.rx_rate, phone.tx_rate) == (5000, 1000, 7, 3)
    assert clients["02:00:00:00:00:12"].connection == "wired"
    assert clients["02:00:00:00:00:12"].via is None
    assert clients["02:00:00:00:00:21"].is_ap
    # a station on this node's radio is on this node, whatever the list's parent says
    on_node = parse_clients(DEVICELIST, STATUS, WIFI, self_mac="02:00:00:00:00:20")
    assert {c.mac: c for c in on_node}["02:00:00:00:00:11"].via == "02:00:00:00:00:20"
    nodes = parse_mesh_nodes(
        {
            "graph": {
                "mac": "02:00:00:00:00:20",
                "ip": "192.168.31.1",
                "name": "main",
                "leafs": [{"mac": "02:00:00:00:00:21", "name": "satellite"}],
            }
        }
    )
    assert [n["name"] for n in nodes] == ["main", "satellite"]


MIWIFI = Path(__file__).parent / "fixtures" / "miwifi"
ROOT_NODE, SAT_NODE = "02:00:00:00:00:a0", "02:00:00:00:00:a1"


def mi_fixture(node: str) -> dict[str, Any]:
    """Real answers of firmware 1.0.148 (root / wired satellite), anonymised."""
    return {p.stem: json.loads(p.read_text()) for p in (MIWIFI / node).glob("*.json")}


def mi_view(node: str) -> list[MiClient]:
    d = mi_fixture(node)
    return parse_clients(
        d["misystem_devicelist"],
        d["misystem_status"],
        d["xqnetwork_wifi_connect_devices"],
        device_list=d["xqsystem_device_list"],
    )


def test_miwifi_real_root_and_satellite_answers() -> None:
    root = {c.mac: c for c in mi_view("root")}
    sat = {c.mac: c for c in mi_view("satellite")}
    # the root has IPs, names, traffic and the node of every client it knows
    speaker = root["02:00:00:00:01:04"]
    assert (speaker.ip, speaker.name, speaker.via, speaker.band) == (
        "10.9.8.103",
        "device-1",
        SAT_NODE,
        "5",
    )
    assert (speaker.rx_bytes, speaker.tx_bytes, speaker.tx_rate) == (519436248, 83174777, 21)
    assert speaker.connected_s == 6799 and speaker.rssi is None  # not on the root's radio
    wired = root["02:00:00:00:01:07"]
    assert (wired.connection, wired.band, wired.via) == ("wired", None, ROOT_NODE)
    busy = root["02:00:00:00:01:10"]
    assert (busy.via, busy.band, busy.signal, busy.rssi) == (ROOT_NODE, "5", 82, -54)
    assert (busy.rx_rate, busy.tx_rate) == (28837, 125497)
    # a satellite knows only its own stations: MAC, band, signal
    assert all(c.ip is None and c.via == SAT_NODE for c in sat.values())
    assert (sat["02:00:00:00:01:04"].band, sat["02:00:00:00:01:04"].rssi) == ("5", -39)
    assert sat["02:00:00:00:01:03"].band == "2.4"


def test_miwifi_views_merge() -> None:
    merged = {c.mac: c for c in merge_clients([mi_view("root"), mi_view("satellite")])}
    assert len(merged) == 28
    speaker = merged["02:00:00:00:01:04"]
    assert (speaker.ip, speaker.via, speaker.band, speaker.rssi, speaker.signal) == (
        "10.9.8.103",
        SAT_NODE,
        "5",
        -39,
        112,
    )
    assert speaker.rx_bytes == 519436248
    assert sum(1 for c in merged.values() if c.rssi is not None) == 27  # all but the wired one
    assert sum(1 for c in merged.values() if c.rx_bytes is not None) == 14
    # the order of the views does not matter, nor a view seen twice
    again = merge_clients([mi_view("satellite"), mi_view("root"), mi_view("root")])
    assert [c.to_json() for c in again] == [c.to_json() for c in merged.values()]


def test_miwifi_signal_estimate() -> None:
    assert signal_to_dbm(84) == -53  # a station that measured the node at -54 dBm
    assert signal_to_dbm(0) is None and signal_to_dbm("x") is None
    assert signal_to_dbm(400) == -10


class MeshFake:
    """One mesh node serving the fixtures (a logged-in session is needed for all but the
    public init_info and topo_graph)."""

    def __init__(self, node: str, base_url: str) -> None:
        self.node = node
        self.base_url = base_url
        self.data = mi_fixture(node)
        self.gets: list[str] = []
        self.sent: list[HttpRequest] = []

    def get(self, path: str) -> str:
        check_path(path)
        self.gets.append(path)
        if path.endswith("init_info"):
            return json.dumps({"model": "xiaomi.router.synth", "newEncryptMode": 1})
        name = path.rsplit("/api/", 1)[-1].replace("/", "_")
        if ";stok=" not in path and name != "misystem_topo_graph":
            return json.dumps({"code": 401})
        return json.dumps(self.data.get(name, {"code": 404}))

    def send(self, request: HttpRequest) -> str:
        self.sent.append(request)
        if request.kind == "logout":
            return ""
        assert request.kind == "login"
        return json.dumps({"code": 0, "token": "0123abcd"})


def test_miwifi_driver_reads_a_node() -> None:
    fake = MeshFake("root", "http://10.9.8.2")
    driver = MiWiFi(fake, lambda: ("admin", "secret"))
    clients = driver.clients()
    assert driver.lan_mac == ROOT_NODE and len(clients) == 22
    assert not any("misystem/devicelist" in g for g in fake.gets)  # device_list sufficed
    sat = MeshFake("satellite", "http://10.9.8.3")
    MiWiFi(sat, lambda: ("admin", "secret")).clients()
    assert any("misystem/devicelist" in g for g in sat.gets)  # bare device_list: fallback
    (device,) = [d for d in driver.devices() if d.mac == "02:00:00:00:01:10"]
    assert (device.band, device.rssi_dbm, device.connected_s) == ("5GHz", -54, 334006)


def test_discover_asks_every_mesh_node(monkeypatch: pytest.MonkeyPatch) -> None:
    fakes: dict[str, MeshFake] = {}

    def transport(base: str, timeout: float = 8.0, host_header: str | None = None) -> MeshFake:
        if base.startswith("https://[fe80::"):
            assert host_header == "localhost"
        node = "root" if base.endswith("a0%eth0]") else "satellite"
        fakes[base] = MeshFake(node, base)
        return fakes[base]

    monkeypatch.setattr(discover, "_miwifi_hosts", lambda: ["10.9.8.3"])
    monkeypatch.setattr(discover.credentials, "entry", lambda base: None)
    monkeypatch.setattr(discover.credentials, "password_for", lambda *a: "secret")
    monkeypatch.setattr(discover, "HttpTransport", transport)
    status, clients, _nodes = discover._collect_miwifi("eth0", [ROOT_NODE, SAT_NODE])
    assert status == "ok" and len(clients) == 28
    # the satellite by its stored address, the root over link-local; the satellite not twice
    assert sorted(fakes) == ["http://10.9.8.3", "https://[fe80::0:ff:fe00:a0%eth0]"]
    assert all(f.sent[-1].kind == "logout" for f in fakes.values())
    assert all(sum(r.kind == "login" for r in f.sent) == 1 for f in fakes.values())
    # no credentials stored at all: no mesh node is asked
    monkeypatch.setattr(discover, "_miwifi_hosts", lambda: [])
    assert discover._collect_miwifi("eth0", [ROOT_NODE]) == ("no-credentials", [], [])


def test_miwifi_password_hash() -> None:
    nonce = "0_02:00:00:00:00:01_1700000000_42"
    inner = hashlib.sha256(("secret" + KEY).encode()).hexdigest()
    assert (
        password_hash("secret", nonce, sha256=True)
        == hashlib.sha256((nonce + inner).encode()).hexdigest()
    )
    assert len(password_hash("secret", nonce, sha256=False)) == 40


class MiFake:
    base_url = "http://192.168.31.1"

    def __init__(self, token_ok: bool = True) -> None:
        self.token_ok = token_ok
        self.sent: list[HttpRequest] = []
        self.gets: list[str] = []

    def get(self, path: str) -> str:
        check_path(path)
        self.gets.append(path)
        if path.endswith("init_info"):
            info = {
                "model": "xiaomi.router.synth",
                "hardware": "SYN1",
                "displayName": "Synthetic Mesh",
                "newEncryptMode": 1,
                "wifi_ap": 1,
            }
            return json.dumps(info)
        if "misystem/devicelist" in path:
            return json.dumps(DEVICELIST)
        if "misystem/status" in path:
            return json.dumps(STATUS)
        if "wifi_connect_devices" in path:
            return json.dumps(WIFI)
        return json.dumps({"code": 404})

    def send(self, request: HttpRequest) -> str:
        self.sent.append(request)
        if request.kind == "logout":
            check_path(request.path, allow_logout=True)
            return "{}"
        if request.kind == "login":
            ok = self.token_ok and dict(request.fields).get("username") == "admin"
            return json.dumps({"code": 0, "token": "0123abcd"} if ok else {"code": 401})
        raise AssertionError("no writes")


def test_miwifi_driver_session() -> None:
    fake = MiFake()
    driver = MiWiFi(fake, lambda: ("admin", "secret"))
    assert MiWiFi.probe(fake) == "Synthetic Mesh"
    clients = driver.clients()
    assert len(clients) == 3
    login = fake.sent[0]
    assert login.kind == "login" and "password" in login.secret_fields
    assert dict(login.fields)["password"] != "secret"
    assert any(";stok=0123abcd/api/misystem/devicelist" in g for g in fake.gets)
    assert driver.end_session() and fake.sent[-1].kind == "logout"
    assert driver.info().model == "Synthetic Mesh"
    with pytest.raises(NotLoggedInError):
        MiWiFi(MiFake(token_ok=False), lambda: ("admin", "wrong")).clients()
    with pytest.raises(NotLoggedInError, match="no Xiaomi"):
        MiWiFi(MiFake(), None).clients()
    assert MiWiFi.access_point


# ── helpers of discover ──────────────────────────────────────────────────────
def test_mac_neighbourhood() -> None:
    assert _near("02:00:00:00:00:10", "02:00:00:00:00:11")
    assert not _near("02:00:00:00:00:10", "02:00:00:00:01:10")
    assert _wifi_via("02:00:00:00:00:13", {"02:00:00:00:00:11": "satellite"}) == (
        "02:00:00:00:00:11",
        "satellite",
    )
    assert _wifi_via("02:00:00:00:99:13", {"02:00:00:00:00:11": "x"}) == (None, None)


# ── the inventory: presence, history, stats, grouping ───────────────────────
def test_discovery_presence_and_online(inv: Inventory) -> None:
    r = inv.record_discovery(
        [
            Sighting(A, "10.9.8.20", names=[("kitchen-light", "mdns")]),
            Sighting(B, "10.9.8.21"),
        ],
        at=at(0),
    )
    assert sorted(r.new) == [A, B] and r.online == 2
    inv.record_discovery([Sighting(A, "10.9.8.20")], at=at(300))
    devices = {d["mac"]: d for d in inv.devices("all")}
    assert devices[B]["online"] is True  # missed one sweep: still within the grace period
    r = inv.record_discovery([Sighting(A, "10.9.8.20")], at=at(GRACE_S + 60))
    assert r.went_offline == [B]
    # a router poll does not override a fresh sweep
    inv.record_poll(INFO, [Device(mac=B, ip="10.9.8.21")], None, at=at(GRACE_S + 90))
    assert {d["mac"]: d for d in inv.devices("all")}[B]["online"] is False
    assert "kitchen-light" in {d["mac"]: d for d in inv.devices("all")}[A]["names"]


def test_history_and_traffic_with_counter_reset(inv: Inventory) -> None:
    for i, (rx, tx) in enumerate([(100, 10), (300, 30), (50, 5)]):
        inv.record_discovery(
            [
                Sighting(
                    A, "10.9.8.20", traffic={"rx_bytes": rx, "tx_bytes": tx, "source": "miwifi"}
                )
            ],
            at=at(i * 300),
        )
    inv.record_discovery([Sighting(B, "10.9.8.21")], at=at(3600 + 60))
    now = datetime.fromtimestamp(T0 + 3600 + 120, UTC)
    h = inv.history(A, days=1, bucket_s=3600, now=now)
    first, second = h["buckets"][-2], h["buckets"][-1]
    assert first["t"] == from_epoch(T0) and first["samples"] == 3
    assert first["online_ratio"] == 1.0 and first["rx_bytes"] == 200 + 50
    assert second["online_ratio"] == 0.0 and second["rx_bytes"] is None
    assert h["buckets"][0]["online_ratio"] is None  # no sweep ran then
    s = inv.stats(days=1, now=now)
    assert s["top_traffic"][0]["mac"] == A and s["top_traffic"][0]["rx_bytes"] == 250
    assert s["sweeps"] == 4 and s["per_hour"][-2]["online"] == 1.0
    device = {d["mac"]: d for d in inv.devices("all")}[A]
    assert device["traffic"]["rx_bytes"] == 50 and device["traffic"]["source"] == "miwifi"


def test_ip_conflict_detection(inv: Inventory) -> None:
    for i, mac in enumerate([A, B, A, B]):
        inv.record_discovery([Sighting(mac, "10.9.8.30")], at=at(i * 300))
    (conflict,) = inv.ip_conflicts(T0 - 10, T0 + 3600)
    assert conflict["ip"] == "10.9.8.30" and set(conflict["macs"]) == {A, B}
    inv.save_fact(A, "mdns", {"hostnames": ["x"], "services": []})
    inv.forget_identity([A])
    assert inv.fact(A, "mdns") is None


def test_classification_topology_and_groups(inv: Inventory) -> None:
    gw = "02:00:00:00:00:a0"
    inv.record_discovery(
        [
            Sighting(gw, "10.9.8.1", facts={"net": {"gateway": 1}}),
            Sighting(
                "02:00:00:00:00:a1",
                "10.9.8.10",
                facts={"net": {"gateway_iface": 1, "same_device_as": gw}},
            ),
            Sighting(
                A,
                "10.9.8.20",
                facts={
                    "mdns": {
                        "hostnames": ["ir-remote-bedroom"],
                        "services": [
                            {
                                "type": "_esphomelib._tcp",
                                "name": "ir-remote-bedroom",
                                "port": 6053,
                                "txt": {"friendly_name": "IR Remote"},
                            }
                        ],
                    }
                },
                link={
                    "type": "wifi",
                    "via": gw,
                    "via_name": "node",
                    "band": "5",
                    "rssi": -50,
                    "source": "miwifi",
                },
            ),
            Sighting(B, "10.9.8.21", facts={"ha": {"macs": [B, C], "name": "TV"}}),
            Sighting(C, "10.9.8.22"),
        ],
        at=at(0),
    )
    devices = {d["mac"]: d for d in inv.devices("all", now=datetime.fromtimestamp(T0, UTC))}
    assert set(devices) == {gw, A, B}  # secondary interfaces are folded into their device
    assert devices[gw]["category"] == "router" and devices[gw]["is_network_gear"]
    assert [i["mac"] for i in devices[gw]["interfaces"]] == [gw, "02:00:00:00:00:a1"]
    remote = devices[A]
    assert remote["category"] == "ir-remote" and remote["confidence"] > 0.9
    assert remote["connection"] == {"type": "wifi", "via": gw, "via_name": "node", "band": "5",
                                    "rssi": -50, "source": "miwifi"}  # fmt: skip
    assert remote["evidence"][0]["source"] == "mdns" and remote["pinnable"] is False
    assert [i["mac"] for i in devices[B]["interfaces"]] == [B, C]
    everything = inv.devices("all", group=False)
    assert {d["mac"]: d["same_device_as"] for d in everything}[C] == B
    assert "10.9.8.10" in inv.protected_ips() and "10.9.8.1" in inv.protected_ips()
    stats = inv.stats(days=1, now=datetime.fromtimestamp(T0 + 60, UTC))
    assert [g["role"] for g in stats["network_gear"]] == ["gateway"]
    assert stats["unexpected_network_gear"] == 0


def test_self_is_always_online(inv: Inventory, monkeypatch: pytest.MonkeyPatch) -> None:
    ifaces = [
        LocalIface(name="wlan0", mac=A, wireless=True, default=True),
        LocalIface(name="eth0", mac=B, wireless=False, default=False),
    ]
    monkeypatch.setattr(Inventory, "local_ifaces", lambda self: ifaces)
    inv.record_poll(INFO, [Device(mac=A, ip="10.9.8.39"), Device(mac=B, ip="10.9.8.40")], None)
    inv.record_poll(INFO, [], None)  # the router forgets us: we are still here
    (me,) = inv.devices("all")
    assert me["mac"] == A and me["online"] and me["is_self"]
    assert [(i["name"], i["type"]) for i in me["interfaces"]] == [
        ("wlan0", "wifi"),
        ("eth0", "wired"),
    ]
    assert me["connection"]["source"] == "local" and me["connection"]["type"] == "wifi"


def test_services_health_and_known_service_down(
    inv: Inventory, monkeypatch: pytest.MonkeyPatch
) -> None:
    inv.record_poll(INFO, [Device(mac=A, ip="10.9.8.20")], None)
    known = {"port": 8080, "scheme": "http", "url": "http://10.9.8.20:8080/", "title": "Old UI"}
    monkeypatch.setattr(scanmod, "port_state", lambda ip, port, timeout: "refused")
    (result,) = scanmod.scan_hosts([("10.9.8.20", A)], ports=(80,), known={"10.9.8.20": [known]})
    (svc,) = result.services
    assert (svc.port, svc.reachable, svc.error, svc.title) == (8080, False, "refused", "Old UI")
    inv.save_scan(A, "10.9.8.20", [], [svc.to_json()], at(0))
    (service,) = inv.devices("all")[0]["services"]
    assert service["reachable"] is False and service["error"] == "refused"
    inv.update_service_health(A, 8080, 200, None, at(60))
    (service,) = inv.devices("all")[0]["services"]
    assert service["reachable"] is True and service["http_status"] == 200
    assert inv.devices("all", favicons=False)[0]["services"][0]["favicon_data_url"] is None


def test_fingerprint_heuristic_connection() -> None:
    signals = fingerprint.build_signals(A, None, ["kitchen-plug"], [], [6668], {})
    result = fingerprint.classify_device(signals)
    conn = fingerprint.connection(result, "Tuya Smart", False, None, {})
    assert (
        result.category == "iot-plug" and conn["type"] == "wifi" and conn["source"] == "heuristic"
    )
    desk = fingerprint.classify_device(fingerprint.build_signals(B, "Micro-Star", [], [], [], {}))
    assert fingerprint.connection(desk, "Micro-Star", False, None, {})["type"] == "wired"


# ── Home Assistant registry ──────────────────────────────────────────────────
def _write_ha(tmp_path: Path) -> Path:
    storage = tmp_path / "ha" / ".storage"
    storage.mkdir(parents=True)
    entries = [
        {"entry_id": "e1", "domain": "esphome", "title": "Hall light",
         "data": {"host": "10.9.8.50", "noise_psk": "SECRET-NEVER-READ"}},
        {"entry_id": "e2", "domain": "ha_creality_ws", "title": "Creality K1",
         "data": {"host": "10.9.8.51"}},
        {"entry_id": "e3", "domain": "mobile_app", "title": "phone", "data": {}},
        {"entry_id": "e4", "domain": "mobile_app", "title": "phone", "data": {}},
        {"entry_id": "e5", "domain": "cast", "title": "Cast", "data": {"host": "10.9.8.53"}},
    ]  # fmt: skip
    devices = [
        {"id": "d1", "config_entries": ["e1"], "name": "hall-light", "name_by_user": "Hall light",
         "manufacturer": "Espressif", "model": "esp32", "connections": [["mac", A.upper()]]},
        {"id": "d2", "config_entries": ["e2"], "name": "K1-0A0B", "manufacturer": "Creality",
         "model": "K1", "connections": []},
        {"id": "d3", "config_entries": ["e3"], "name": "Family-Phone", "manufacturer": "Apple",
         "model": "iPhone16,1", "connections": []},
        {"id": "d4", "config_entries": ["e4"], "name": "Family-Phone", "manufacturer": "Apple",
         "model": "iPhone17,2", "connections": []},
        {"id": "d5", "config_entries": ["e5"], "name": "Cast", "connections": []},
        {"id": "d6", "config_entries": ["e1"], "name": "disabled", "disabled_by": "user",
         "connections": [["mac", "02:00:00:00:00:99"]]},
    ]  # fmt: skip
    (storage / "core.config_entries").write_text(json.dumps({"data": {"entries": entries}}))
    (storage / "core.device_registry").write_text(json.dumps({"data": {"devices": devices}}))
    return tmp_path / "ha"


def test_ha_registry(tmp_path: Path) -> None:
    devices = ha_registry.load(_write_ha(tmp_path))
    assert {d.name for d in devices} == {"Hall light", "K1-0A0B", "Family-Phone", "Cast"}
    assert "SECRET" not in json.dumps([d.facts("x") for d in devices])
    printer_mac = "00:11:22:00:00:05"  # a real (not randomized) MAC holds the printer's address
    facts = ha_registry.facts_by_mac(
        devices,
        {"10.9.8.51": printer_mac, "10.9.8.53": "da:00:00:00:00:07"},
        {"02:00:00:00:00:44": ["Family-Phone-2.local"]},
    )
    assert facts[A]["name"] == "Hall light" and facts[A]["matched"] == "mac"
    assert (
        facts[printer_mac]["domains"] == ["ha_creality_ws"]
        and facts[printer_mac]["matched"] == "host"
    )
    assert "da:00:00:00:00:07" not in facts  # an address on a randomized MAC is not trusted
    phone = facts["02:00:00:00:00:44"]
    assert phone["matched"] == "name" and phone["model"] == "iPhone"  # two phones, same name
    assert ha_registry.load(tmp_path / "missing") == []
