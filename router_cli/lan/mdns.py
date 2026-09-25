"""mdns — a small mDNS / DNS-SD browser (RFC 6762/6763), stdlib sockets only.

Queries go out from an ephemeral port, so responders answer by unicast straight back to us
("legacy unicast", RFC 6762 section 6.7) and nothing needs to share port 5353 with Avahi or
Home Assistant. Three kinds of question are asked:

1. multicast: ``_services._dns-sd._udp.local`` (the service-type meta query) plus a fixed
   list of interesting service types, with the QU bit set;
2. unicast to each candidate host's port 5353 (RFC 6762 section 5.5): the meta query and a
   reverse ``PTR`` for its address, which is how an iPhone tells you it is "Alexs-iPhone";
3. follow-ups for the service types / instances a host announced, until SRV and TXT are in.

Answers are attributed by the address records they carry (a Bonjour sleep proxy answers
for sleeping devices) and otherwise by the source address.
"""

from __future__ import annotations

import contextlib
import ipaddress
import random
import select
import socket
import struct
import time
from dataclasses import dataclass, field

MDNS_ADDR = "224.0.0.251"
MDNS_PORT = 5353
META = "_services._dns-sd._udp.local"
T_A, T_PTR, T_TXT, T_AAAA, T_SRV, T_ANY = 1, 12, 16, 28, 33, 255
QU = 0x8000

INTERESTING = (
    "_airplay._tcp",
    "_raop._tcp",
    "_companion-link._tcp",
    "_apple-mobdev2._tcp",
    "_rdlink._tcp",
    "_mediaremotetv._tcp",
    "_sleep-proxy._udp",
    "_googlecast._tcp",
    "_androidtvremote2._tcp",
    "_amzn-wplay._tcp",
    "_spotify-connect._tcp",
    "_yandexio._tcp",
    "_esphomelib._tcp",
    "_hap._tcp",
    "_hap._udp",
    "_matter._tcp",
    "_meshcop._udp",
    "_home-assistant._tcp",
    "_ipp._tcp",
    "_ipps._tcp",
    "_printer._tcp",
    "_pdl-datastream._tcp",
    "_uscan._tcp",
    "_moonraker._tcp",
    "_octoprint._tcp",
    "_smb._tcp",
    "_afpovertcp._tcp",
    "_workstation._tcp",
    "_ssh._tcp",
    "_rfb._tcp",
    "_nvstream._tcp",
    "_dosvc._tcp",
    "_miio._udp",
    "_wled._tcp",
    "_shelly._tcp",
    "_hue._tcp",
    "_elg._tcp",
    "_sonos._tcp",
    "_http._tcp",
)


@dataclass
class Record:
    name: str
    rtype: int
    ttl: int
    value: object


@dataclass
class MdnsService:
    type: str  # "_airplay._tcp"
    name: str  # instance label, "Living Room"
    port: int | None = None
    target: str | None = None
    txt: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> dict[str, object]:
        return {"type": self.type, "name": self.name, "port": self.port, "txt": self.txt}


@dataclass
class MdnsHost:
    ip: str
    hostnames: list[str] = field(default_factory=list)
    services: dict[str, MdnsService] = field(default_factory=dict)  # by full instance name
    answered: bool = False  # this address itself sent an mDNS answer


# ── wire format ──────────────────────────────────────────────────────────────
def _encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        raw = label.encode("utf-8")[:63]
        out += bytes([len(raw)]) + raw
    return out + b"\0"


def build_query(questions: list[tuple[str, int]], qu: bool = True, qid: int = 0) -> bytes:
    body = b"".join(
        _encode_name(name) + struct.pack("!HH", qtype, 1 | (QU if qu else 0))
        for name, qtype in questions
    )
    return struct.pack("!HHHHHH", qid, 0, len(questions), 0, 0, 0) + body


def _read_name(data: bytes, offset: int, depth: int = 0) -> tuple[str, int]:
    labels: list[str] = []
    jumped_end: int | None = None
    while True:
        if offset >= len(data) or depth > 20:
            raise ValueError("bad name")
        length = data[offset]
        if length == 0:
            offset += 1
            break
        if length & 0xC0 == 0xC0:
            pointer = struct.unpack("!H", data[offset : offset + 2])[0] & 0x3FFF
            if jumped_end is None:
                jumped_end = offset + 2
            offset = pointer
            depth += 1
            continue
        offset += 1
        labels.append(data[offset : offset + length].decode("utf-8", errors="replace"))
        offset += length
    return ".".join(labels), (jumped_end if jumped_end is not None else offset)


def _parse_txt(raw: bytes) -> dict[str, str]:
    out: dict[str, str] = {}
    i = 0
    while i < len(raw):
        length = raw[i]
        item = raw[i + 1 : i + 1 + length].decode("utf-8", errors="replace")
        i += 1 + length
        if not item:
            continue
        key, _, value = item.partition("=")
        if key and key.lower() not in {k.lower() for k in out}:
            out[key] = value
    return out


def parse_message(data: bytes) -> list[Record]:
    """Every resource record (answers, authority, additional) of a DNS message."""
    if len(data) < 12:
        return []
    _qid, _flags, qd, an, ns, ar = struct.unpack("!HHHHHH", data[:12])
    offset = 12
    records: list[Record] = []
    try:
        for _ in range(qd):
            _name, offset = _read_name(data, offset)
            offset += 4
        for _ in range(an + ns + ar):
            name, offset = _read_name(data, offset)
            rtype, _rclass, ttl, rdlen = struct.unpack("!HHIH", data[offset : offset + 10])
            offset += 10
            rdata = data[offset : offset + rdlen]
            value: object = rdata
            if rtype == T_A and rdlen == 4:
                value = socket.inet_ntoa(rdata)
            elif rtype == T_PTR:
                value = _read_name(data, offset)[0]
            elif rtype == T_SRV and rdlen >= 7:
                _prio, _weight, port = struct.unpack("!HHH", rdata[:6])
                value = (port, _read_name(data, offset + 6)[0])
            elif rtype == T_TXT:
                value = _parse_txt(rdata)
            records.append(Record(name=name, rtype=rtype, ttl=ttl, value=value))
            offset += rdlen
    except (ValueError, struct.error, IndexError):
        pass
    return records


def reverse_name(ip: str) -> str:
    return ipaddress.IPv4Address(ip).reverse_pointer + ".local"


def _split_instance(full: str) -> tuple[str, str] | None:
    """'Living Room._airplay._tcp.local' -> ('Living Room', '_airplay._tcp')."""
    parts = full.split(".")
    for i in range(len(parts) - 2):
        if parts[i].startswith("_") and parts[i + 1] in ("_tcp", "_udp"):
            instance = ".".join(parts[:i])
            if instance:
                return instance, f"{parts[i]}.{parts[i + 1]}"
            return None
    return None


# ── browsing ─────────────────────────────────────────────────────────────────
class _Collector:
    def __init__(self) -> None:
        self.by_source: dict[str, list[Record]] = {}

    def add(self, src: str, records: list[Record]) -> None:
        self.by_source.setdefault(src, []).extend(records)


def _open_socket(own_ip: str | None) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 0))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    if own_ip:
        with contextlib.suppress(OSError):
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(own_ip))
    sock.setblocking(False)
    return sock


def _listen(sock: socket.socket, collector: _Collector, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while True:
        left = deadline - time.monotonic()
        if left <= 0:
            return
        ready, _, _ = select.select([sock], [], [], left)
        if not ready:
            continue
        while True:
            try:
                data, addr = sock.recvfrom(9000)
            except (BlockingIOError, InterruptedError):
                break
            except OSError:
                return
            collector.add(addr[0], parse_message(data))


def _send(sock: socket.socket, packet: bytes, dest: tuple[str, int]) -> None:
    with contextlib.suppress(OSError):
        sock.sendto(packet, dest)


def browse(
    candidates: list[str],
    own_ip: str | None = None,
    timeout: float = 4.5,
    exclude: frozenset[str] = frozenset(),
) -> dict[str, MdnsHost]:
    """Browse the LAN; return what each responding address announced."""
    sock = _open_socket(own_ip)
    collector = _Collector()
    qid = random.randint(1, 0xFFFF)
    targets = [ip for ip in candidates if ip not in exclude and ip != own_ip]
    try:
        # Round 1: multicast meta + interesting types; unicast meta + reverse to each host.
        multicast_q = [(META, T_PTR)] + [(f"{t}.local", T_PTR) for t in INTERESTING]
        for chunk in (multicast_q[:20], multicast_q[20:]):
            if chunk:
                _send(sock, build_query(chunk, qu=True, qid=qid), (MDNS_ADDR, MDNS_PORT))
        for ip in targets:
            _send(
                sock,
                build_query([(META, T_PTR), (reverse_name(ip), T_PTR)], qu=False, qid=qid),
                (ip, MDNS_PORT),
            )
        _listen(sock, collector, timeout * 0.4)

        # Round 2: ask each host for the service types it announced.
        types_by_host = _service_types(collector)
        for ip, types in types_by_host.items():
            if ip in exclude:
                continue
            questions = [(f"{t}.local", T_PTR) for t in sorted(types)][:30]
            if questions:
                _send(sock, build_query(questions, qu=False, qid=qid), (ip, MDNS_PORT))
        _listen(sock, collector, timeout * 0.35)

        # Round 3: SRV/TXT for instances that came without them.
        hosts = _assemble(collector)
        for ip, host in hosts.items():
            if ip in exclude:
                continue
            missing = [
                full for full, svc in host.services.items() if svc.port is None or not svc.txt
            ][:20]
            if missing:
                questions = [(full, T_ANY) for full in missing]
                _send(sock, build_query(questions, qu=False, qid=qid), (ip, MDNS_PORT))
        _listen(sock, collector, timeout * 0.25)
    finally:
        sock.close()
    return _assemble(collector)


def _service_types(collector: _Collector) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for src, records in collector.by_source.items():
        for rec in records:
            if (
                rec.rtype == T_PTR
                and rec.name.lower() == META.lower()
                and isinstance(rec.value, str)
            ):
                stype = rec.value.lower().removesuffix(".local")
                out.setdefault(src, set()).add(stype)
    return out


def _assemble(collector: _Collector) -> dict[str, MdnsHost]:
    hosts: dict[str, MdnsHost] = {}
    for src, records in collector.by_source.items():
        a_records: dict[str, str] = {}
        for rec in records:
            if rec.rtype == T_A and isinstance(rec.value, str):
                a_records[rec.name.lower()] = rec.value
        src_host = hosts.setdefault(src, MdnsHost(ip=src))
        src_host.answered = True

        def host_for(
            target: str | None, src: str = src, a_records: dict[str, str] = a_records
        ) -> MdnsHost:
            ip = a_records.get((target or "").lower(), src)
            return hosts.setdefault(ip, MdnsHost(ip=ip))

        for name, ip in a_records.items():
            host = hosts.setdefault(ip, MdnsHost(ip=ip))
            short = name.removesuffix(".local")
            if short and short not in host.hostnames:
                host.hostnames.append(short)
        srv: dict[str, tuple[int, str]] = {}
        txt: dict[str, dict[str, str]] = {}
        instances: set[str] = set()
        for rec in records:
            lname = rec.name
            if rec.rtype == T_PTR and isinstance(rec.value, str):
                if lname.endswith(".in-addr.arpa.local") or lname.endswith(".in-addr.arpa"):
                    short = rec.value.removesuffix(".local")
                    if short and short not in src_host.hostnames:
                        src_host.hostnames.append(short)
                elif lname.lower() != META.lower() and _split_instance(rec.value):
                    instances.add(rec.value)
            elif rec.rtype == T_SRV and isinstance(rec.value, tuple):
                srv[lname] = rec.value
                instances.add(lname)
            elif rec.rtype == T_TXT and isinstance(rec.value, dict):
                txt[lname] = rec.value
                if _split_instance(lname):
                    instances.add(lname)
        for full in instances:
            split = _split_instance(full)
            if not split:
                continue
            instance, stype = split
            port, target = srv.get(full, (None, None))
            host = host_for(target)
            svc = host.services.get(full) or MdnsService(type=stype, name=instance)
            if port is not None:
                svc.port, svc.target = port, target
            if txt.get(full):
                svc.txt = txt[full]
            host.services[full] = svc
            if target:
                short = target.removesuffix(".local")
                if short and short not in host.hostnames:
                    host.hostnames.append(short)
    return {ip: h for ip, h in hosts.items() if h.answered or h.services or h.hostnames}
