"""scan — find the web UIs running on LAN devices: port, title, server, favicon.

Two passes, both concurrent and on short timeouts so a whole home network takes seconds:

1. TCP connect to a list of popular web ports on every target.
2. For each open port, one HTTP(S) GET of ``/`` (HTTPS first on the usual TLS ports,
   certificate NOT verified — LAN devices use self-signed certificates), reading at most
   256 KiB: ``<title>``, the ``Server`` header, and the favicon (``<link rel=icon>`` or
   ``/favicon.ico``) as a ``data:`` URL capped at 32 KiB.

Only plain GETs of ``/`` and the favicon are ever sent to a device.
"""

from __future__ import annotations

import base64
import concurrent.futures
import html
import http.client
import re
import socket
import ssl
import urllib.parse
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

DEFAULT_PORTS = (
    80, 443, 8080, 8443, 8000, 8001, 8008, 8081, 8088, 8123, 8888, 9000, 9090, 5000, 5001,
    3000, 32400, 1880, 6052, 7125, 4408, 9999, 631, 8200, 49152, 8096, 8006, 9443, 10000,
    2283, 8384, 5601, 3001, 8989, 7878, 9117, 8086, 4533,
)  # fmt: skip
TLS_FIRST = frozenset({443, 8443, 5001, 9443, 8006, 10000})
MAX_BODY = 256 * 1024
MAX_ICON = 32 * 1024
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_LINK = re.compile(r"<link\b[^>]*>", re.I)
_ATTR = re.compile(r"""(\w[\w-]*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""")


@dataclass
class Service:
    port: int
    scheme: str
    url: str
    title: str | None = None
    server: str | None = None
    favicon_data_url: str | None = None
    checked_at: str = ""
    status: int | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "port": self.port,
            "scheme": self.scheme,
            "url": self.url,
            "title": self.title,
            "server": self.server,
            "favicon_data_url": self.favicon_data_url,
            "checked_at": self.checked_at,
        }


@dataclass
class HostResult:
    ip: str
    mac: str | None = None
    open_ports: list[int] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def port_open(ip: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def _context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    # codeql[py/insecure-protocol]
    # Justified: `router scan` only reads the title/favicon of LAN devices' own web UIs, which
    # use self-signed certificates; nothing sensitive is sent and nothing received is trusted.
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get(
    scheme: str, ip: str, port: int, path: str, timeout: float, limit: int
) -> tuple[int, dict[str, str], bytes]:
    conn: http.client.HTTPConnection
    if scheme == "https":
        conn = http.client.HTTPSConnection(ip, port, timeout=timeout, context=_context())
    else:
        conn = http.client.HTTPConnection(ip, port, timeout=timeout)
    try:
        # codeql[py/partial-ssrf]
        # Justified: the user asked to scan these LAN addresses (--ip / the inventory); only a
        # GET of `/` or the device's own favicon path is ever sent.
        conn.request("GET", path, headers={"User-Agent": "router-cli scan", "Accept": "*/*"})
        response = conn.getresponse()
        body = response.read(limit + 1)
        headers = {k.lower(): v for k, v in response.getheaders()}
        return response.status, headers, body
    finally:
        conn.close()


def _decode(body: bytes, headers: dict[str, str]) -> str:
    charset = "utf-8"
    match = re.search(r"charset=([\w-]+)", headers.get("content-type", ""), re.I)
    if match:
        charset = match.group(1)
    try:
        return body[:MAX_BODY].decode(charset, errors="replace")
    except LookupError:
        return body[:MAX_BODY].decode("utf-8", errors="replace")


def title_of(text: str) -> str | None:
    match = _TITLE.search(text)
    if not match:
        return None
    title = " ".join(html.unescape(match.group(1)).split())
    return title[:200] or None


def icon_href(text: str) -> str | None:
    best: tuple[int, str] | None = None
    for tag in _LINK.findall(text):
        attrs = {
            m.group(1).lower(): (m.group(3) or m.group(4) or m.group(5) or "")
            for m in _ATTR.finditer(tag)
        }
        rel = attrs.get("rel", "").lower()
        href = attrs.get("href")
        if not href or "icon" not in rel or "mask-icon" in rel:
            continue
        rank = 0 if rel in ("icon", "shortcut icon") else 1
        if best is None or rank < best[0]:
            best = (rank, href)
    return best[1] if best else None


def _guess_type(path: str, header: str) -> str:
    header = header.split(";")[0].strip().lower()
    if header.startswith("image/"):
        return header
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {
        "png": "image/png",
        "svg": "image/svg+xml",
        "gif": "image/gif",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }.get(ext, "image/x-icon")


def favicon(scheme: str, ip: str, port: int, page: str, timeout: float) -> str | None:
    href = icon_href(page) or "/favicon.ico"
    if href.startswith("data:"):
        return href if len(href) <= MAX_ICON * 4 // 3 + 64 else None
    base = f"{scheme}://{ip}:{port}/"
    url = urllib.parse.urlsplit(urllib.parse.urljoin(base, href))
    if url.hostname not in (ip, None) or (url.port or port) != port:
        return None  # only ever fetch from the device itself
    path = url.path or "/favicon.ico"
    if url.query:
        path += "?" + url.query
    try:
        status, headers, body = _get(url.scheme or scheme, ip, port, path, timeout, MAX_ICON)
    except (OSError, http.client.HTTPException, ssl.SSLError):
        return None
    if status != 200 or not body or len(body) > MAX_ICON:
        return None
    ctype = _guess_type(path, headers.get("content-type", ""))
    if "html" in ctype:
        return None
    return f"data:{ctype};base64,{base64.b64encode(body).decode('ascii')}"


def probe_http(ip: str, port: int, timeout: float, with_icon: bool = True) -> Service | None:
    order = ("https", "http") if port in TLS_FIRST else ("http", "https")
    for scheme in order:
        try:
            status, headers, body = _get(scheme, ip, port, "/", timeout, MAX_BODY)
        except ssl.SSLError:
            continue
        except (OSError, http.client.HTTPException):
            continue
        text = _decode(body, headers)
        default_port = 443 if scheme == "https" else 80
        url = f"{scheme}://{ip}/" if port == default_port else f"{scheme}://{ip}:{port}/"
        service = Service(
            port=port,
            scheme=scheme,
            url=url,
            title=title_of(text),
            server=headers.get("server"),
            checked_at=_now(),
            status=status,
        )
        if with_icon:
            service.favicon_data_url = favicon(scheme, ip, port, text, timeout)
        return service
    return None


def scan_hosts(
    targets: list[tuple[str, str | None]],
    ports: tuple[int, ...] = DEFAULT_PORTS,
    connect_timeout: float = 0.6,
    http_timeout: float = 3.0,
    workers: int = 64,
    with_icons: bool = True,
) -> list[HostResult]:
    results = {ip: HostResult(ip=ip, mac=mac) for ip, mac in targets}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(port_open, ip, port, connect_timeout): (ip, port)
            for ip in results
            for port in ports
        }
        for future in concurrent.futures.as_completed(futures):
            ip, port = futures[future]
            if future.result():
                results[ip].open_ports.append(port)
        http_futures = {
            pool.submit(probe_http, r.ip, port, http_timeout, with_icons): (r.ip, port)
            for r in results.values()
            for port in r.open_ports
        }
        for http_future in concurrent.futures.as_completed(http_futures):
            ip, _port = http_futures[http_future]
            service = http_future.result()
            if service is not None:
                results[ip].services.append(service)
    for r in results.values():
        r.open_ports.sort()
        r.services.sort(key=lambda s: s.port)
    return list(results.values())
