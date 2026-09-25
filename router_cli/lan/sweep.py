"""sweep — who is on the subnet right now: an ICMP echo sweep plus the kernel's ARP table.

ICMP uses an unprivileged "ping socket" (``SOCK_DGRAM``/``IPPROTO_ICMP``, allowed by
``net.ipv4.ping_group_range`` on current distributions), so no root and no raw sockets. The
reply TTL comes back as ancillary data (``IP_RECVTTL``): hosts on the same L2 segment answer
with their initial TTL (64 Linux/Android/iOS/macOS, 128 Windows, 255 some embedded stacks).

Sending anything to an address makes the kernel resolve it with ARP, so even hosts that
ignore ping (phones in power save, firewalled PCs) end up REACHABLE in the neighbour table
when they are there. :func:`neighbors` reads that table (``ip -j neigh``; ``/proc/net/arp``
as a fallback).
"""

from __future__ import annotations

import contextlib
import json
import os
import select
import shutil
import socket
import struct
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

IP_RECVTTL = getattr(socket, "IP_RECVTTL", 12)
IP_TTL = getattr(socket, "IP_TTL", 2)
ALIVE_STATES = frozenset({"REACHABLE", "PERMANENT", "NOARP"})
DEAD_STATES = frozenset({"FAILED", "INCOMPLETE"})


@dataclass
class Neighbor:
    ip: str
    mac: str | None
    state: str


def _checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    total = (total >> 16) + (total & 0xFFFF)
    total += total >> 16
    return int(~total & 0xFFFF)


def _echo_request(ident: int, seq: int) -> bytes:
    payload = b"router-cli discover"
    header = struct.pack("!BBHHH", 8, 0, 0, ident, seq)
    return struct.pack("!BBHHH", 8, 0, _checksum(header + payload), ident, seq) + payload


def ping_sweep(
    targets: list[str], timeout: float = 2.0, gap: float = 0.002
) -> dict[str, int | None]:
    """ICMP echo to every target; {ip: reply TTL (None if the kernel did not report it)}.

    Returns {} when ping sockets are not permitted for this user (the caller still has the
    ARP table)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
    except OSError:
        return {}
    replies: dict[str, int | None] = {}
    try:
        with contextlib.suppress(OSError):
            sock.setsockopt(socket.IPPROTO_IP, IP_RECVTTL, 1)
        sock.setblocking(False)
        ident = os.getpid() & 0xFFFF
        wanted = set(targets)
        for seq, ip in enumerate(targets):
            try:
                sock.sendto(_echo_request(ident, seq & 0xFFFF), (ip, 0))
            except OSError:
                continue
            _drain(sock, replies, wanted)
            time.sleep(gap)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            ready, _, _ = select.select([sock], [], [], max(0.0, deadline - time.monotonic()))
            if ready:
                _drain(sock, replies, wanted)
    finally:
        sock.close()
    return replies


def _drain(sock: socket.socket, replies: dict[str, int | None], wanted: set[str]) -> None:
    while True:
        try:
            data, anc, _flags, addr = sock.recvmsg(1024, socket.CMSG_SPACE(4))
        except (BlockingIOError, InterruptedError):
            return
        except OSError:
            return
        if not data or data[0] != 0 or addr[0] not in wanted:  # 0 = echo reply
            continue
        ttl = None
        for level, kind, value in anc:
            if level == socket.IPPROTO_IP and kind == IP_TTL and len(value) >= 4:
                ttl = int.from_bytes(value[:4], sys.byteorder)
        replies[addr[0]] = ttl


def poke(targets: list[str]) -> None:
    """A UDP datagram to the discard port of each target: makes the kernel ARP for it."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for ip in targets:
            try:
                sock.sendto(b"", (ip, 9))
            except OSError:
                continue


def neighbors(iface: str | None = None) -> dict[str, Neighbor]:
    """The kernel neighbour (ARP) table: {ip: Neighbor(ip, mac, state)}."""
    ip_bin = shutil.which("ip")
    if ip_bin:
        cmd = [ip_bin, "-j", "-4", "neigh", "show"]
        if iface:
            cmd += ["dev", iface]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False).stdout
            rows = json.loads(out or "[]")
        except (OSError, ValueError, subprocess.SubprocessError):
            rows = None
        if isinstance(rows, list):
            table: dict[str, Neighbor] = {}
            for row in rows:
                ip = row.get("dst")
                if not ip:
                    continue
                states = row.get("state") or []
                state = states[0] if states else "UNKNOWN"
                mac = row.get("lladdr")
                table[ip] = Neighbor(ip=ip, mac=mac.lower() if mac else None, state=state)
            return table
    return _proc_arp(iface)


def _proc_arp(iface: str | None) -> dict[str, Neighbor]:
    table: dict[str, Neighbor] = {}
    try:
        lines = Path("/proc/net/arp").read_text("ascii").splitlines()[1:]
    except OSError:
        return table
    for line in lines:
        parts = line.split()
        if len(parts) < 6 or (iface and parts[5] != iface):
            continue
        ip, flags, mac = parts[0], parts[2], parts[3].lower()
        complete = int(flags, 16) & 0x2
        table[ip] = Neighbor(
            ip=ip,
            mac=mac if complete and mac != "00:00:00:00:00:00" else None,
            state="REACHABLE" if complete else "INCOMPLETE",
        )
    return table
