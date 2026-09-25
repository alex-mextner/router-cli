"""ssdp — SSDP M-SEARCH and UPnP device descriptions.

One multicast ``M-SEARCH * HTTP/1.1`` (``ssdp:all``, sent twice) collects answers for a few
seconds; each answer's ``LOCATION`` names the device description XML, which is fetched with a
plain GET — only from the address that answered, never from an excluded address (the main
router: its web server must not be touched), at most 64 KiB, and parsed with regular
expressions (no XML parser on untrusted input).
"""

from __future__ import annotations

import contextlib
import html
import http.client
import re
import select
import socket
import time
import urllib.parse
from dataclasses import dataclass, field

from ..http import check_path

SSDP_ADDR = ("239.255.255.250", 1900)
MAX_XML = 64 * 1024
FIELDS = {
    "friendly_name": "friendlyName",
    "manufacturer": "manufacturer",
    "model_name": "modelName",
    "model_number": "modelNumber",
    "model_description": "modelDescription",
    "device_type": "deviceType",
}


@dataclass
class SsdpAnswer:
    st: str | None = None
    usn: str | None = None
    server: str | None = None
    location: str | None = None


@dataclass
class SsdpHost:
    ip: str
    answers: list[SsdpAnswer] = field(default_factory=list)
    descriptions: dict[str, dict[str, str]] = field(default_factory=dict)  # by location

    def devices(self) -> list[dict[str, str | None]]:
        """netprint-shaped SSDP devices: one per distinct LOCATION (headers + description)."""
        out: list[dict[str, str | None]] = []
        seen: set[str] = set()
        for ans in self.answers:
            key = ans.location or f"{ans.st}|{ans.usn}"
            desc = self.descriptions.get(ans.location or "", {})
            item: dict[str, str | None] = {
                "server": ans.server,
                "st": ans.st,
                "usn": ans.usn,
                "location": ans.location,
                **desc,
            }
            if key in seen:
                # keep every distinct search target: a TV answers for several
                if ans.st and not any(o.get("st") == ans.st for o in out):
                    out.append(item)
                continue
            seen.add(key)
            out.append(item)
        return out[:12]


def _msearch(st: str = "ssdp:all", mx: int = 2) -> bytes:
    return (
        "M-SEARCH * HTTP/1.1\r\n"
        f"HOST: {SSDP_ADDR[0]}:{SSDP_ADDR[1]}\r\n"
        'MAN: "ssdp:discover"\r\n'
        f"MX: {mx}\r\n"
        f"ST: {st}\r\n"
        "USER-AGENT: router-cli/1 UPnP/1.1 discover\r\n\r\n"
    ).encode("ascii")


def parse_answer(data: bytes) -> SsdpAnswer | None:
    text = data.decode("utf-8", errors="replace")
    lines = text.split("\r\n") if "\r\n" in text else text.split("\n")
    if not lines or not re.match(r"^(HTTP/1\.[01] 200|NOTIFY)", lines[0], re.I):
        return None
    headers: dict[str, str] = {}
    for line in lines[1:]:
        key, sep, value = line.partition(":")
        if sep:
            headers[key.strip().lower()] = value.strip()
    return SsdpAnswer(
        st=headers.get("st") or headers.get("nt"),
        usn=headers.get("usn"),
        server=headers.get("server"),
        location=headers.get("location"),
    )


def search(own_ip: str, timeout: float = 3.0) -> dict[str, SsdpHost]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    hosts: dict[str, SsdpHost] = {}
    try:
        sock.bind((own_ip, 0))  # the LAN interface only: answers come back to this address
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        if own_ip:
            with contextlib.suppress(OSError):
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(own_ip))
        sock.setblocking(False)
        for i, st in enumerate(("ssdp:all", "upnp:rootdevice", "ssdp:all")):
            with contextlib.suppress(OSError):
                sock.sendto(_msearch(st), SSDP_ADDR)
            if i == 0:
                time.sleep(0.3)
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
                    data, addr = sock.recvfrom(4096)
                except (BlockingIOError, InterruptedError):
                    break
                except OSError:
                    break
                answer = parse_answer(data)
                if answer is None:
                    continue
                host = hosts.setdefault(addr[0], SsdpHost(ip=addr[0]))
                if not any(
                    a.st == answer.st and a.location == answer.location for a in host.answers
                ):
                    host.answers.append(answer)
    finally:
        sock.close()
    return hosts


def parse_description(xml: str) -> dict[str, str]:
    """The root device's fields (the first occurrence of each tag)."""
    out: dict[str, str] = {}
    for key, tag in FIELDS.items():
        match = re.search(rf"<{tag}>\s*(.*?)\s*</{tag}>", xml, re.S | re.I)
        if match:
            value = html.unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", match.group(1)))
            value = " ".join(value.split())[:120]
            if value:
                out[key] = value
    return out


def fetch_description(ip: str, location: str, timeout: float = 2.0) -> dict[str, str] | None:
    """GET the description XML — only from ``ip`` itself, plain HTTP, 64 KiB at most."""
    url = urllib.parse.urlsplit(location)
    if url.scheme != "http" or url.hostname != ip:
        return None
    path = url.path or "/"
    if url.query:
        path += "?" + url.query
    try:
        check_path(path)
    except Exception:
        return None
    conn = http.client.HTTPConnection(ip, url.port or 80, timeout=timeout)
    try:
        # codeql[py/partial-ssrf]
        # Justified: the device that answered our SSDP search named this path on itself; only
        # that address is contacted, with a GET, and the reply is size-capped.
        conn.request("GET", path, headers={"User-Agent": "router-cli discover"})
        response = conn.getresponse()
        if response.status != 200:
            return None
        body = response.read(MAX_XML + 1)[:MAX_XML]
    except (OSError, http.client.HTTPException):
        return None
    finally:
        conn.close()
    return parse_description(body.decode("utf-8", errors="replace"))


def describe(
    hosts: dict[str, SsdpHost],
    exclude: frozenset[str] = frozenset(),
    cached: dict[str, dict[str, str]] | None = None,
    timeout: float = 2.0,
) -> None:
    """Fill ``descriptions`` for every host not in ``exclude`` (cache hits are not refetched)."""
    cached = cached or {}
    for ip, host in hosts.items():
        if ip in exclude:
            continue
        for location in {a.location for a in host.answers if a.location}:
            if location in cached:
                host.descriptions[location] = cached[location]
                continue
            desc = fetch_description(ip, location, timeout)
            if desc:
                host.descriptions[location] = desc
