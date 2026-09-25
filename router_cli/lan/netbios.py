"""netbios — NetBIOS node-status ("nbtstat -A") names of Windows PCs, Samba servers, NASes."""

from __future__ import annotations

import random
import select
import socket
import struct
import time

# "*" padded with NULs, first-level encoded (RFC 1002 section 4.1).
_WILDCARD = b"\x20" + b"CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + b"\x00"


def build_request(tid: int) -> bytes:
    return struct.pack("!HHHHHH", tid, 0, 1, 0, 0, 0) + _WILDCARD + struct.pack("!HH", 0x21, 1)


def parse_response(data: bytes) -> tuple[list[str], str | None]:
    """(unique workstation names, workgroup) from a node-status answer."""
    try:
        offset = 12
        # answer name (same encoded wildcard, maybe compressed)
        if data[offset] & 0xC0 == 0xC0:
            offset += 2
        else:
            while data[offset] != 0:
                offset += data[offset] + 1
            offset += 1
        rtype, _rclass, _ttl, _rdlen = struct.unpack("!HHIH", data[offset : offset + 10])
        if rtype != 0x21:
            return [], None
        offset += 10
        count = data[offset]
        offset += 1
        names: list[str] = []
        group = None
        for _ in range(count):
            raw = data[offset : offset + 15].decode("ascii", errors="replace").strip()
            suffix = data[offset + 15]
            flags = struct.unpack("!H", data[offset + 16 : offset + 18])[0]
            offset += 18
            is_group = bool(flags & 0x8000)
            if suffix == 0x00 and not is_group and raw and raw not in names:
                names.append(raw)
            elif suffix == 0x00 and is_group and group is None:
                group = raw
        return names, group
    except (IndexError, struct.error):
        return [], None


def query(targets: list[str], timeout: float = 1.5) -> dict[str, list[str]]:
    """{ip: [names]} for every target that answered."""
    out: dict[str, list[str]] = {}
    if not targets:
        return out
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("", 0))
        sock.setblocking(False)
        tid = random.randint(1, 0xFFFF)
        for ip in targets:
            try:
                sock.sendto(build_request(tid), (ip, 137))
            except OSError:
                continue
        deadline = time.monotonic() + timeout
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                break
            ready, _, _ = select.select([sock], [], [], left)
            if not ready:
                continue
            while True:
                try:
                    data, addr = sock.recvfrom(2048)
                except (BlockingIOError, InterruptedError):
                    break
                except OSError:
                    break
                names, _group = parse_response(data)
                if names:
                    out[addr[0]] = names
    finally:
        sock.close()
    return out
