"""scan — find the web UIs running on LAN devices: port, title, server, favicon, health.

Two passes, both concurrent and on short timeouts so a whole home network takes seconds:

1. TCP connect to a list of popular web ports on every target, plus the non-web
   *fingerprint* ports the device classifier looks at (ESPHome's 6053, iOS's 62078, Tuya's
   6668, ...: connect only, nothing is sent), plus every port a web service was found on
   before.
2. For each open web port, one HTTP(S) GET of ``/`` (HTTPS first on the usual TLS ports,
   certificate NOT verified — LAN devices use self-signed certificates), reading at most
   256 KiB: ``<title>``, the ``Server`` header, well-known product markers in the body, and
   the favicon (``<link rel=icon>`` or ``/favicon.ico``) as a ``data:`` URL capped at 32 KiB.

Every service carries its health: ``reachable`` (an HTTP answer of any status came back),
``http_status`` and ``error`` (``refused``, ``timeout``, ``tls``, ``reset``, ``unreachable``,
``http``). A service seen before that no longer answers is kept with ``reachable: false`` so
a dashboard can show it as down instead of silently dropping it.

Only plain GETs of ``/`` and the favicon are ever sent to a device.
"""

from __future__ import annotations

import base64
import concurrent.futures
import errno
import hashlib
import html
import http.client
import re
import socket
import ssl
import urllib.parse
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ._vendor.netprint import find_markers, fingerprint_ports

DEFAULT_PORTS = (
    80, 443, 8080, 8443, 8000, 8001, 8008, 8081, 8088, 8123, 8888, 9000, 9090, 5000, 5001,
    3000, 32400, 1880, 6052, 7125, 4408, 9999, 631, 8200, 49152, 8096, 8006, 9443, 10000,
    2283, 8384, 5601, 3001, 8989, 7878, 9117, 8086, 4533, 4409, 81,
)  # fmt: skip
TLS_FIRST = frozenset({443, 8443, 5001, 9443, 8006, 10000})
# Ports that never speak HTTP (or whose HTTP answer says nothing): connect-only.
NOT_HTTP = frozenset({22, 53, 139, 445, 515, 548, 554, 1883, 3389, 5555, 6053, 6668, 8883,
                      9100, 62078, 55443, 1400, 1961, 8554, 5357, 2869, 7680})  # fmt: skip
MAX_BODY = 256 * 1024
MAX_ICON = 32 * 1024
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_LINK = re.compile(r"<link\b[^>]*>", re.I)
_ATTR = re.compile(r"""(\w[\w-]*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""")


def fingerprint_only_ports() -> tuple[int, ...]:
    """Fingerprint ports that are not already web ports."""
    return tuple(p for p in fingerprint_ports() if p not in DEFAULT_PORTS)


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
    reachable: bool | None = True
    error: str | None = None
    markers: list[str] = field(default_factory=list)
    favicon_hash: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "port": self.port,
            "scheme": self.scheme,
            "url": self.url,
            "title": self.title,
            "server": self.server,
            "favicon_data_url": self.favicon_data_url,
            "checked_at": self.checked_at,
            "reachable": self.reachable,
            "http_status": self.status,
            "error": self.error,
            "markers": self.markers,
            "favicon_hash": self.favicon_hash,
        }


@dataclass
class HostResult:
    ip: str
    mac: str | None = None
    open_ports: list[int] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    banners: dict[str, str] = field(default_factory=dict)  # port -> first line the server sent


# Ports whose server speaks first: its greeting names the software ("SSH-2.0-OpenSSH_9.6p1
# Ubuntu-3ubuntu13"). Nothing is sent; the first line is read and the connection closed.
BANNER_PORTS = frozenset({22})


def read_banner(ip: str, port: int, timeout: float) -> str | None:
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            data = sock.recv(256)
    except OSError:
        return None
    line = data.decode("latin-1", errors="replace").splitlines()[0] if data else ""
    return line.strip()[:160] or None


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def classify_error(exc: BaseException) -> str:
    """A short, stable reason for a failed connection / request."""
    if isinstance(exc, ssl.SSLError):
        return "tls"
    if isinstance(exc, ConnectionRefusedError):
        return "refused"
    if isinstance(exc, ConnectionResetError | BrokenPipeError | ConnectionAbortedError):
        return "reset"
    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, http.client.HTTPException):
        return "http"
    if isinstance(exc, OSError) and exc.errno in (
        errno.EHOSTUNREACH,
        errno.ENETUNREACH,
        errno.EHOSTDOWN,
    ):
        return "unreachable"
    return "error"


def port_state(ip: str, port: int, timeout: float) -> str | None:
    """None if a TCP connect succeeds, else why it did not."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return None
    except OSError as exc:
        return classify_error(exc)


def port_open(ip: str, port: int, timeout: float) -> bool:
    return port_state(ip, port, timeout) is None


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


def favicon_hash(data_url: str | None) -> str | None:
    """md5 hex of the favicon bytes (what netprint's ``favicon`` rules match)."""
    if not data_url or ";base64," not in data_url:
        return None
    try:
        raw = base64.b64decode(data_url.split(";base64,", 1)[1], validate=False)
    except ValueError:
        return None
    return hashlib.md5(raw, usedforsecurity=False).hexdigest()


def _url(scheme: str, ip: str, port: int) -> str:
    default_port = 443 if scheme == "https" else 80
    return f"{scheme}://{ip}/" if port == default_port else f"{scheme}://{ip}:{port}/"


def probe_http(ip: str, port: int, timeout: float, with_icon: bool = True) -> Service | None:
    """The web service on an open port, or None if nothing there speaks HTTP(S)."""
    order = ("https", "http") if port in TLS_FIRST else ("http", "https")
    for scheme in order:
        try:
            status, headers, body = _get(scheme, ip, port, "/", timeout, MAX_BODY)
        except (OSError, http.client.HTTPException):
            continue
        text = _decode(body, headers)
        service = Service(
            port=port,
            scheme=scheme,
            url=_url(scheme, ip, port),
            title=title_of(text),
            server=headers.get("server"),
            checked_at=_now(),
            status=status,
            reachable=True,
            markers=find_markers(text),
        )
        if with_icon:
            service.favicon_data_url = favicon(scheme, ip, port, text, timeout)
            service.favicon_hash = favicon_hash(service.favicon_data_url)
        return service
    return None


def check_service(scheme: str, ip: str, port: int, timeout: float) -> tuple[int | None, str | None]:
    """(HTTP status, None) if the service answers, (None, reason) if not. One GET of ``/``."""
    try:
        status, _headers, _body = _get(scheme, ip, port, "/", timeout, 4096)
    except (OSError, http.client.HTTPException) as exc:
        return None, classify_error(exc)
    return status, None


def _gone(known: dict[str, Any], reason: str) -> Service:
    return Service(
        port=int(known["port"]),
        scheme=str(known.get("scheme") or "http"),
        url=str(known.get("url") or ""),
        title=known.get("title"),
        server=known.get("server"),
        favicon_data_url=known.get("favicon_data_url"),
        checked_at=_now(),
        status=None,
        reachable=False,
        error=reason,
        markers=list(known.get("markers") or []),
        favicon_hash=known.get("favicon_hash"),
    )


def scan_hosts(
    targets: list[tuple[str, str | None]],
    ports: tuple[int, ...] = DEFAULT_PORTS,
    connect_timeout: float = 0.6,
    http_timeout: float = 3.0,
    workers: int = 64,
    with_icons: bool = True,
    extra_ports: tuple[int, ...] = (),
    known: dict[str, list[dict[str, Any]]] | None = None,
) -> list[HostResult]:
    """Scan every (ip, mac) target. ``extra_ports`` are connect-only; ``known`` maps an ip to
    the services found on it before, which are re-checked and reported as down if gone."""
    known = known or {}
    results = {ip: HostResult(ip=ip, mac=mac) for ip, mac in targets}
    reasons: dict[tuple[str, int], str] = {}
    web_ports = set(ports)
    plan = {
        (ip, port)
        for ip in results
        for port in (*ports, *extra_ports, *(int(s["port"]) for s in known.get(ip, [])))
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(port_state, ip, port, connect_timeout): (ip, port) for ip, port in plan
        }
        for future in concurrent.futures.as_completed(futures):
            ip, port = futures[future]
            reason = future.result()
            if reason is None:
                results[ip].open_ports.append(port)
            else:
                reasons[(ip, port)] = reason
        http_futures = {
            pool.submit(probe_http, r.ip, port, http_timeout, with_icons): (r.ip, port)
            for r in results.values()
            for port in r.open_ports
            if port not in NOT_HTTP
            and (port in web_ports or any(int(s["port"]) == port for s in known.get(r.ip, [])))
        }
        banner_futures = {
            pool.submit(read_banner, r.ip, port, max(connect_timeout, 1.5)): (r.ip, port)
            for r in results.values()
            for port in r.open_ports
            if port in BANNER_PORTS
        }
        for http_future in concurrent.futures.as_completed(http_futures):
            ip, _port = http_futures[http_future]
            service = http_future.result()
            if service is not None:
                results[ip].services.append(service)
        for banner_future in concurrent.futures.as_completed(banner_futures):
            ip, port = banner_futures[banner_future]
            banner = banner_future.result()
            if banner:
                results[ip].banners[str(port)] = banner
    for r in results.values():
        found = {s.port for s in r.services}
        for old in known.get(r.ip, []):
            port = int(old["port"])
            if port not in found:
                r.services.append(_gone(old, reasons.get((r.ip, port), "http")))
        r.open_ports = sorted(set(r.open_ports))
        r.services.sort(key=lambda s: s.port)
    return list(results.values())
