"""netinfo — the local interface router-cli discovers from: address, subnet, gateway, MAC."""

from __future__ import annotations

import ipaddress
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .._errors import UsageError
from ..config import default_gateway

MAX_HOSTS = 1024  # a /22; bigger subnets need an explicit --subnet


@dataclass
class LocalNet:
    iface: str
    ip: str
    network: ipaddress.IPv4Network
    gateway: str | None
    mac: str | None
    wireless: bool

    def hosts(self) -> list[str]:
        return [str(h) for h in self.network.hosts() if str(h) != self.ip]


def _default_iface() -> str | None:
    try:
        lines = Path("/proc/net/route").read_text(encoding="ascii").splitlines()[1:]
    except OSError:
        return None
    best: tuple[int, str] | None = None
    for line in lines:
        parts = line.split()
        if len(parts) < 8 or parts[1] != "00000000":
            continue
        try:
            metric = int(parts[6])
        except ValueError:
            continue
        if best is None or metric < best[0]:
            best = (metric, parts[0])
    return best[1] if best else None


def _iface_addr(iface: str) -> tuple[str, int] | None:
    ip_bin = shutil.which("ip")
    if not ip_bin:
        return None
    try:
        out = subprocess.run(
            [ip_bin, "-j", "-4", "addr", "show", "dev", iface],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout
        data = json.loads(out or "[]")
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    for link in data:
        for addr in link.get("addr_info", []):
            if addr.get("family") == "inet" and addr.get("scope") == "global":
                return str(addr["local"]), int(addr["prefixlen"])
    return None


@dataclass
class LocalIface:
    name: str
    mac: str
    wireless: bool
    default: bool  # holds the default route


def local_interfaces() -> list[LocalIface]:
    """This machine's PHYSICAL network interfaces (the ones with a device behind them; no
    loopback, bridges, veth, docker or VPN tunnels), default-route interface first."""
    base = Path("/sys/class/net")
    if not base.is_dir():
        return []
    default = _default_iface()
    out: list[LocalIface] = []
    for entry in sorted(base.iterdir()):
        if not (entry / "device").exists():
            continue
        try:
            mac = (entry / "address").read_text("ascii").strip().lower()
        except OSError:
            continue
        if not mac or mac == "00:00:00:00:00:00":
            continue
        out.append(
            LocalIface(
                name=entry.name,
                mac=mac,
                wireless=(entry / "wireless").exists() or (entry / "phy80211").exists(),
                default=entry.name == default,
            )
        )
    out.sort(key=lambda i: (not i.default, i.name))
    return out


def wifi_link(iface: str) -> dict[str, object] | None:
    """{"bssid", "band", "rssi"} of this machine's Wi-Fi association (``iw dev X link``)."""
    iw = shutil.which("iw") or ("/usr/sbin/iw" if Path("/usr/sbin/iw").exists() else None)
    if not iw:
        return None
    try:
        out = subprocess.run(
            [iw, "dev", iface, "link"], capture_output=True, text=True, timeout=5, check=False
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    bssid = re.search(r"Connected to ([0-9a-fA-F:]{17})", out)
    if not bssid:
        return None
    freq = re.search(r"freq:\s*([\d.]+)", out)
    signal = re.search(r"signal:\s*(-?\d+)", out)
    mhz = float(freq.group(1)) if freq else 0.0
    band = "2.4" if 2300 < mhz < 2600 else "5" if 4900 < mhz < 5900 else "6" if mhz > 5900 else None
    return {
        "bssid": bssid.group(1).lower(),
        "band": band,
        "rssi": int(signal.group(1)) if signal else None,
    }


def local_net(subnet: str | None = None, iface: str | None = None) -> LocalNet:
    """Describe the interface that holds the default route (or ``iface``)."""
    if not sys.platform.startswith("linux"):
        raise UsageError(
            what="LAN discovery needs Linux",
            why="it reads the kernel ARP table and interface details from /proc and iproute2",
            how="run `router discover` on the Linux box that sits on the LAN",
        )
    iface = iface or _default_iface()
    if not iface:
        raise UsageError(what="no default route", why="cannot tell which LAN to scan", how="")
    found = _iface_addr(iface)
    if not found:
        raise UsageError(
            what=f"no IPv4 address on {iface}", why="`ip -j addr` gave nothing", how=""
        )
    ip, prefix = found
    network = ipaddress.IPv4Network(subnet or f"{ip}/{prefix}", strict=False)
    if network.num_addresses > MAX_HOSTS and not subnet:
        network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
    try:
        mac = Path(f"/sys/class/net/{iface}/address").read_text("ascii").strip().lower() or None
    except OSError:
        mac = None
    wireless = Path(f"/sys/class/net/{iface}/wireless").exists()
    return LocalNet(
        iface=iface,
        ip=ip,
        network=network,
        gateway=default_gateway() or None,
        mac=mac,
        wireless=wireless,
    )
