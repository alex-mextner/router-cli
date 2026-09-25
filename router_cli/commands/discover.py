"""discover — sweep the LAN from this machine into the inventory. Never touches the router.

    router discover [--json] [--ha-config ~/homeassistant]

One run (about 10 seconds, meant for a 5-minute timer):

- ICMP echo to every address of the subnet (reply TTLs kept) and the kernel ARP table after
  it: who is here right now, with their MACs. Each run is a presence sample, so
  ``router inventory history`` has 5-minute resolution without polling the gateway.
- mDNS / DNS-SD (multicast + direct unicast questions, reverse lookups), SSDP + UPnP
  descriptions, NetBIOS names: what each device calls itself and what it is.
- Xiaomi mesh nodes: the public ``init_info`` (model, AP mode) of Xiaomi devices, and with
  stored credentials (``router login --driver miwifi --host <node> --no-default``) the
  Wi-Fi client list: node, band, signal and per-device traffic counters.
- Moonraker (Klipper 3D printers): ``/printer/info`` and ``/server/info``, once a day.
- Home Assistant's device registry (``--ha-config`` or ``ROUTER_CLI_HA_CONFIG``, read-only).
- A quick health check (one GET of ``/``) of every known web service of online devices.

The default gateway and its other interfaces get ARP/ping only: nothing here ever sends an
HTTP, SSDP-description, mDNS-unicast or NetBIOS request to them (a cable gateway's web
server can hang when polled).
"""

from __future__ import annotations

import concurrent.futures
import contextlib
import http.client
import ipaddress
import json
import os
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .. import credentials, ha_registry
from .._errors import RouterCliError
from ..config import db_path
from ..drivers.miwifi import MiClient, MiWiFi
from ..http import HttpTransport, normalize_base
from ..inventory import Inventory, Sighting, now_iso, to_epoch
from ..lan import mdns, netbios, netinfo, ssdp, sweep
from ..scan import check_service
from . import _common as C

NAME = "discover"
SUMMARY = "sweep the LAN from this host (ARP/ping, mDNS, SSDP, NetBIOS, Xiaomi mesh) — no router"

SETTLE_S = 8.5  # ARP needs DELAY (5 s) + PROBE retries to turn a stale entry into an answer
DAY = 86400


@contextmanager
def _lock() -> Iterator[bool]:
    try:
        import fcntl
    except ImportError:  # pragma: no cover - Windows
        yield True
        return
    path = db_path().parent / "discover.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _json_get(ip: str, port: int, path: str, timeout: float = 2.5) -> Any:
    conn = http.client.HTTPConnection(ip, port, timeout=timeout)
    try:
        # codeql[py/partial-ssrf]
        # Justified: a fixed, read-only public API path on a LAN device the sweep just found.
        conn.request("GET", path, headers={"User-Agent": "router-cli discover"})
        response = conn.getresponse()
        if response.status != 200:
            return None
        return json.loads(response.read(256 * 1024).decode("utf-8", errors="replace"))
    except (OSError, http.client.HTTPException, ValueError):
        return None
    finally:
        conn.close()


def _stale(inv: Inventory, mac: str, source: str, max_age: int, now: int) -> bool:
    updated = inv.fact_updated(mac, source)
    try:
        return updated is None or now - to_epoch(updated) > max_age
    except ValueError:
        return True


def _miwifi_info(ip: str) -> dict[str, Any] | None:
    data = _json_get(ip, 80, "/cgi-bin/luci/api/xqsystem/init_info")
    if not isinstance(data, dict) or not str(data.get("model", "")).startswith("xiaomi.router"):
        return None
    return {
        "model": data.get("model"),
        "hardware": data.get("hardware"),
        "display_name": data.get("displayName"),
        "wifi_ap": str(data.get("wifi_ap", "")),
        "mesh_root": 1 if "mesh_nodes" in data else 0,
        "romversion": data.get("romversion"),
        "routername": data.get("routername"),
    }


def _moonraker_info(ip: str) -> dict[str, Any] | None:
    printer = _json_get(ip, 7125, "/printer/info")
    if not isinstance(printer, dict) or not isinstance(printer.get("result"), dict):
        return None
    result = printer["result"]
    server = _json_get(ip, 7125, "/server/info")
    sres = server.get("result") if isinstance(server, dict) else None
    return {
        "hostname": result.get("hostname"),
        "software_version": result.get("software_version"),
        "state": result.get("state"),
        "moonraker_version": sres.get("moonraker_version") if isinstance(sres, dict) else None,
    }


def _miwifi_hosts() -> list[str]:
    try:
        routers = credentials.load_file().get("routers") or {}
    except RouterCliError:
        return []
    return [h for h, e in routers.items() if isinstance(e, dict) and e.get("driver") == "miwifi"]


def _collect_miwifi(timeout: float = 8.0) -> tuple[str, list[MiClient], list[dict[str, Any]]]:
    hosts = _miwifi_hosts()
    if not hosts:
        return "no-credentials", [], []
    clients: dict[str, MiClient] = {}
    nodes: list[dict[str, Any]] = []
    errors: list[str] = []
    for host in hosts:
        base = normalize_base(host)
        entry = credentials.entry(base)
        user = (entry.username if entry else "") or "admin"

        def creds(base: str = base, user: str = user) -> tuple[str, str] | None:
            secret = credentials.password_for(base, "miwifi", user)
            return (user, secret) if secret else None

        driver = MiWiFi(HttpTransport(base, timeout=timeout), creds)
        try:
            for client in driver.clients():
                clients.setdefault(client.mac, client)
            nodes.extend(driver.mesh_nodes())
        except RouterCliError as exc:
            errors.append(f"{host}: {exc.what}")
        finally:
            with contextlib.suppress(RouterCliError):
                driver.end_session()
    status = "ok" if not errors else ("partial: " if clients else "error: ") + "; ".join(errors)
    return status, list(clients.values()), nodes


def _near(mac_a: str, mac_b: str, span: int = 16) -> bool:
    """Same first five octets and last octets within ``span`` (one box's interfaces/radios)."""
    if not mac_a or not mac_b or mac_a[:14] != mac_b[:14]:
        return False
    return abs(int(mac_a[15:], 16) - int(mac_b[15:], 16)) <= span


def _wifi_via(bssid: str, nodes: dict[str, str]) -> tuple[str | None, str | None]:
    """The mesh node (mac, name) a BSSID belongs to: radios sit next to the LAN MAC."""
    for mac, name in nodes.items():
        if bssid == mac or _near(bssid, mac, 8):
            return mac, name
    return None, None


def discover(args: Any) -> dict[str, Any]:
    started = time.monotonic()
    at = now_iso()
    now_t = to_epoch(at)
    net = netinfo.local_net(args.subnet, args.iface)
    own = netinfo.local_interfaces()
    with Inventory() as inv:
        protected = inv.protected_ips() | ({net.gateway} if net.gateway else set())
        prior_online = [ip for _mac, ip in inv.online_targets()]
        conflicts = inv.ip_conflicts(now_t - 6 * 3600, now_t + 60)
        ssdp_cache: dict[str, dict[str, str]] = {}
        for mac_row in inv.db.execute("SELECT mac FROM discovery WHERE source = 'ssdp'"):
            mac = str(mac_row["mac"])
            if _stale(inv, mac, "ssdp", DAY, now_t):
                continue
            for dev in (inv.fact(mac, "ssdp") or {}).get("devices") or []:
                if dev.get("location") and dev.get("model_name"):
                    ssdp_cache[dev["location"]] = {
                        k: v for k, v in dev.items() if k in ssdp.FIELDS and v
                    }

    targets = [] if args.no_sweep else net.hosts()
    box: dict[str, Any] = {}

    def run_ssdp() -> None:
        box["ssdp"] = ssdp.search(net.ip, 3.0)

    def run_miwifi() -> None:
        box["miwifi"] = _collect_miwifi()

    threads = []
    if not args.no_ssdp:
        threads.append(threading.Thread(target=run_ssdp, daemon=True))
    if not args.no_miwifi:
        threads.append(threading.Thread(target=run_miwifi, daemon=True))
    for th in threads:
        th.start()

    pings = sweep.ping_sweep(targets, timeout=args.timeout) if targets else {}
    if targets and not pings:
        sweep.poke(targets)  # no ping sockets: at least make the kernel ARP everyone
    neigh = sweep.neighbors(net.iface)
    first_macs = {ip: n.mac for ip, n in neigh.items() if n.mac}
    gw_mac = neigh[net.gateway].mac if net.gateway in neigh else None
    gateway_ifaces = {
        ip: n.mac
        for ip, n in neigh.items()
        if n.mac and gw_mac and n.mac != gw_mac and _near(n.mac, gw_mac)
    }
    protected |= set(gateway_ifaces)
    candidates = sorted(
        (
            set(pings)
            | {ip for ip, n in neigh.items() if n.state not in sweep.DEAD_STATES}
            | set(prior_online)
        )
        - {net.ip},
        key=lambda ip: tuple(int(x) for x in ip.split(".")),
    )
    candidates = [ip for ip in candidates if ipaddress.IPv4Address(ip) in net.network]

    mdns_hosts: dict[str, mdns.MdnsHost] = {}
    nb: dict[str, list[str]] = {}

    def run_mdns() -> None:
        mdns_hosts.update(mdns.browse(candidates, net.ip, exclude=frozenset(protected)))

    def run_netbios() -> None:
        nb.update(netbios.query([ip for ip in candidates if ip not in protected]))

    later = []
    if not args.no_mdns:
        later.append(threading.Thread(target=run_mdns, daemon=True))
    if not args.no_netbios:
        later.append(threading.Thread(target=run_netbios, daemon=True))
    for th in later:
        th.start()
    for th in [*threads, *later]:
        th.join(30)
    ssdp_hosts: dict[str, ssdp.SsdpHost] = box.get("ssdp") or {}
    ssdp.describe(ssdp_hosts, exclude=frozenset(protected), cached=ssdp_cache)
    mi_status, mi_clients, mi_nodes = box.get("miwifi") or ("skipped", [], [])

    wait = SETTLE_S - (time.monotonic() - started)
    if targets and wait > 0:
        time.sleep(wait)
    neigh = sweep.neighbors(net.iface)
    # Two devices on one address: whatever answered from it cannot be told apart, so none of
    # it is attributed (and what was attributed before is dropped). Reported by `stats`.
    conflicted = {c["ip"] for c in conflicts}
    conflicted |= {
        ip for ip, n in neigh.items() if n.mac and first_macs.get(ip) not in (None, n.mac)
    }
    conflict_macs = {m for c in conflicts for m in c["macs"]}
    conflict_macs |= {n.mac for ip, n in neigh.items() if ip in conflicted and n.mac}
    conflict_macs |= {first_macs[ip] for ip in conflicted if ip in first_macs}

    responders = set(pings) | set(nb) | set(ssdp_hosts)
    responders |= {ip for ip, h in mdns_hosts.items() if h.answered}
    present: dict[str, str | None] = {}
    for ip, n in neigh.items():
        if not n.mac or ipaddress.IPv4Address(ip) not in net.network:
            continue
        if n.state in sweep.ALIVE_STATES or ip in responders:
            present[n.mac] = ip
    mi_by_mac = {c.mac: c for c in mi_clients}
    for c in mi_clients:
        if c.online and c.mac not in present:
            present[c.mac] = c.ip
    ip_mac: dict[str, str] = {}
    for ip, n in neigh.items():
        if n.mac:
            ip_mac[ip] = n.mac
    for iface in own:
        present[iface.mac] = net.ip if iface.default else None

    # names of mesh nodes (for connection.via_name)
    node_names: dict[str, str] = {}
    with Inventory() as inv:
        for node in mi_nodes:
            node_names[node["mac"]] = str(node.get("name") or node["mac"])
        for row in inv.db.execute("SELECT mac FROM discovery WHERE source = 'miwifi_info'"):
            info = inv.fact(str(row["mac"]), "miwifi_info") or {}
            node_names.setdefault(
                str(row["mac"]),
                str(info.get("routername") or info.get("display_name") or row["mac"]),
            )

    sightings: dict[str, Sighting] = {}

    def sight(mac: str, present_now: bool = True) -> Sighting:
        s = sightings.get(mac)
        if s is None:
            s = sightings[mac] = Sighting(mac=mac, ip=present.get(mac), present=present_now)
        return s

    for mac in present:
        sight(mac)

    def mac_at(ip: str) -> str | None:
        return None if ip in conflicted else ip_mac.get(ip)

    for ip, ttl in pings.items():
        at_ip = mac_at(ip)
        if at_ip and ttl:
            sight(at_ip).facts["icmp"] = {"ttl": ttl}
    for ip, mhost in mdns_hosts.items():
        at_ip = mac_at(ip)
        if not at_ip or not (mhost.services or mhost.hostnames):
            continue
        s = sight(at_ip, at_ip in present)
        s.facts["mdns"] = {
            "hostnames": mhost.hostnames[:6],
            "services": [svc.to_json() for svc in mhost.services.values()][:30],
        }
        for hostname in mhost.hostnames[:3]:
            s.names.append((hostname, "mdns"))
    for ip, shost in ssdp_hosts.items():
        at_ip = mac_at(ip)
        if at_ip:
            sight(at_ip, at_ip in present).facts["ssdp"] = {"devices": shost.devices()}
    for ip, nb_names in nb.items():
        at_ip = mac_at(ip)
        if at_ip:
            s = sight(at_ip, at_ip in present)
            s.facts["netbios"] = {"names": nb_names}
            s.names.extend((n, "netbios") for n in nb_names[:2])
    # flags: this machine, the gateway, the gateway's other interfaces
    link = netinfo.wifi_link(net.iface) if net.wireless else None
    for iface in own:
        flags: dict[str, Any] = {"self": 1, "iface": iface.name, "wireless": int(iface.wireless)}
        if iface.default and link:
            via, via_name = _wifi_via(str(link["bssid"]), node_names)
            flags.update(via=via, via_name=via_name, band=link["band"], rssi=link["rssi"])
        if not iface.default and own:
            flags["same_device_as"] = own[0].mac
        sight(iface.mac).facts["net"] = flags
    if gw_mac:
        sight(gw_mac, gw_mac in present).facts["net"] = {"gateway": 1}
    for _ip, mac in gateway_ifaces.items():
        if mac:
            sight(mac, mac in present).facts["net"] = {"gateway_iface": 1, "same_device_as": gw_mac}
    # Xiaomi mesh client data
    for c in mi_clients:
        s = sight(c.mac, c.mac in present)
        s.facts["miwifi"] = {
            "name": c.name,
            "connection": c.connection,
            "band": c.band,
            "via": c.via,
            "rssi": c.rssi,
            "is_ap": int(c.is_ap),
            "guest": int(c.guest),
        }
        if c.name:
            s.names.append((c.name, "miwifi"))
        if c.connection in ("wired", "wifi"):
            s.link = {
                "type": c.connection,
                "via": c.via,
                "via_name": node_names.get(c.via or ""),
                "band": c.band,
                "rssi": c.rssi,
                "source": "miwifi",
            }
        if c.rx_bytes is not None or c.rx_rate is not None:
            s.traffic = {
                "rx_bytes": c.rx_bytes,
                "tx_bytes": c.tx_bytes,
                "rx_rate": c.rx_rate,
                "tx_rate": c.tx_rate,
                "source": "miwifi",
            }

    # once-a-day HTTP facts: Xiaomi init_info, Moonraker printer info
    with Inventory() as inv:
        vendors = {
            str(r["mac"]): r["vendor"] for r in inv.db.execute("SELECT mac, vendor FROM devices")
        }
        open_ports = {
            str(r["mac"]): set(json.loads(r["open_ports"] or "[]"))
            for r in inv.db.execute("SELECT mac, open_ports FROM scans")
        }
        jobs: list[tuple[str, str, str]] = []
        for pmac, pip in present.items():
            if not pip or pip in protected or pip in conflicted or pip == net.ip:
                continue
            vendor = str(vendors.get(pmac) or "")
            if vendor.startswith("Xiaomi") and _stale(inv, pmac, "miwifi_info", DAY, now_t):
                jobs.append((pmac, pip, "miwifi_info"))
            services = {
                str(svc.get("type"))
                for svc in ((sightings.get(pmac) or Sighting(pmac)).facts.get("mdns") or {}).get(
                    "services"
                )
                or []
            }
            if (
                7125 in open_ports.get(pmac, set())
                or services & {"_moonraker._tcp", "_snapmaker._tcp"}
            ) and _stale(inv, pmac, "moonraker", DAY, now_t):
                jobs.append((pmac, pip, "moonraker"))
        health = [t for t in inv.service_targets() if t["ip"] in set(present.values())]
        if args.no_services:
            health = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        fetch = {
            pool.submit(_miwifi_info if kind == "miwifi_info" else _moonraker_info, ip): (mac, kind)
            for mac, ip, kind in jobs
        }
        checks = {
            pool.submit(check_service, t["scheme"], t["ip"], t["port"], 2.5): t for t in health
        }
        for future in concurrent.futures.as_completed(fetch):
            mac, kind = fetch[future]
            value = future.result()
            if value:
                sight(mac, mac in present).facts[kind] = value
        health_results = [(checks[f], *f.result()) for f in concurrent.futures.as_completed(checks)]

    ha_count = 0
    ha_config = args.ha_config or os.environ.get("ROUTER_CLI_HA_CONFIG")
    with Inventory() as inv:
        if ha_config:
            ha_devices = ha_registry.load(Path(ha_config).expanduser())
            known_names = {str(r["mac"]): list(r["names"]) for r in inv.selector_rows()}
            for smac, sighting in sightings.items():
                known_names.setdefault(smac, []).extend(n for n, _src in sighting.names)
            ha_facts = ha_registry.facts_by_mac(ha_devices, inv.ip_to_mac(), known_names)
            for hmac, value in ha_facts.items():
                ha_sighting = sight(hmac, hmac in present)
                ha_sighting.facts["ha"] = value
                for ha_name in (value.get("name"), value.get("title")):
                    if ha_name:  # so `router scan --ip "Snapmaker U1"` works too
                        ha_sighting.names.append((str(ha_name), "ha"))
            ha_count = len(ha_facts)
            inv.drop_facts("ha", ha_facts)
        if conflict_macs:
            inv.forget_identity(conflict_macs)
        took = time.monotonic() - started
        result = inv.record_discovery(
            list(sightings.values()), at=at, took=took, full_sweep=bool(targets)
        )
        stamp = datetime.now(UTC).replace(microsecond=0).isoformat()
        for target, status, error in health_results:
            inv.update_service_health(target["mac"], target["port"], status, error, stamp)

    return {
        "at": result.at,
        "took_s": round(time.monotonic() - started, 1),
        "interface": net.iface,
        "subnet": str(net.network),
        "online": result.online,
        "new": result.new,
        "went_offline": result.went_offline,
        "ping_replies": len(pings),
        "mdns_hosts": sum(1 for h in mdns_hosts.values() if h.services or h.hostnames),
        "ssdp_hosts": len(ssdp_hosts),
        "netbios_hosts": len(nb),
        "miwifi": {"status": mi_status, "clients": len(mi_clients), "nodes": len(mi_nodes)},
        "ha_registry": ha_count if ha_config else None,
        "services_checked": len(health_results),
        "services_down": sum(1 for _t, status, _e in health_results if status is None),
        "protected": sorted(protected),
        "ip_conflicts": sorted(conflicted),
        "mi_clients_online": sum(1 for c in mi_by_mac.values() if c.online),
    }


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument("--json", action="store_true")
    p.add_argument("--subnet", help="CIDR to sweep (default: the default-route interface's)")
    p.add_argument("--iface", help="interface (default: the one with the default route)")
    p.add_argument("--timeout", type=float, default=2.5, help="ping reply window, seconds")
    p.add_argument(
        "--ha-config",
        help="Home Assistant config dir to read the device registry from (read-only); "
        "env ROUTER_CLI_HA_CONFIG",
    )
    for flag, what in (
        ("--no-sweep", "the ping/ARP sweep (then no presence sample is recorded)"),
        ("--no-mdns", "mDNS"),
        ("--no-ssdp", "SSDP"),
        ("--no-netbios", "NetBIOS"),
        ("--no-miwifi", "the Xiaomi mesh API"),
        ("--no-services", "the web-service health check"),
    ):
        p.add_argument(flag, action="store_true", help=f"skip {what}")
    args = p.parse_args(argv)
    with _lock() as mine:
        if not mine:
            if args.json:
                C.emit_json({"skipped": True, "reason": "another discover is running"})
            else:
                print("another `router discover` is running; skipped")
            return 0
        summary = discover(args)
    if args.json:
        C.emit_json(summary)
        return 0
    print(
        f"{summary['online']} online on {summary['subnet']} ({summary['interface']}), "
        f"{summary['took_s']} s; new: {len(summary['new'])}; "
        f"went offline: {len(summary['went_offline'])}"
    )
    print(
        f"ping {summary['ping_replies']}, mDNS {summary['mdns_hosts']}, "
        f"SSDP {summary['ssdp_hosts']}, NetBIOS {summary['netbios_hosts']}, "
        f"Xiaomi mesh: {summary['miwifi']['status']} ({summary['miwifi']['clients']} clients), "
        f"services checked {summary['services_checked']} ({summary['services_down']} down)"
    )
    return 0
