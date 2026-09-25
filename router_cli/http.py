"""http — the only door between router-cli and a router's web server.

ONE REQUEST TYPE, FOUR KINDS
    Every request a driver makes is an :class:`HttpRequest` with a ``kind``:

    ``read``   a GET, or a POST that only reads (OpenWrt's ``/ubus`` JSON-RPC is POST-only
               even for reads). Always allowed, subject to the path guard.
    ``login``  the form or RPC login. Allowed, because a driver has to be able to get a
               session back, and it changes nothing on the router.
    ``logout`` ending the admin session the driver itself opened (``end_session``). The
               ONLY request allowed to name a logout page; every other guarded word still
               applies to it.
    ``write``  anything that changes router state. Refused unless the transport was built
               with ``allow_writes=True`` — which the CLI only does after ``--dry-run`` was
               NOT given and, for destructive writes, ``--yes`` WAS.

THE PATH GUARD
    Some pages act on a plain GET. On consumer gateways ``logout.asp`` ends the (often
    global) admin session and pages named for reboot, reset, restore, factory defaults,
    upgrade or backup can do far worse. No read ever touches a path containing one of those
    words; there is no flag to turn that off. The single exception is a ``kind="logout"``
    request, which may contain "logout" (and nothing else from the list).

DRY RUN
    :class:`DryRunTransport` passes reads (and logins) through to the real router, because a
    write is always computed from the page's current state, and records writes instead of
    sending them. ``render`` prints each recorded request exactly as it would go on the
    wire, with password fields redacted unless asked otherwise.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from ._errors import NetworkError, RouterError, SafetyError

Kind = Literal["read", "login", "logout", "write"]

FORM = "application/x-www-form-urlencoded"
JSON = "application/json"

# Never GET a path containing any of these (case-insensitive), whatever asked for it.
DANGEROUS_PATH_WORDS = (
    "logout",
    "reboot",
    "reset",
    "restore",
    "factory",
    "default",
    "upgrade",
    "backup",
)

REDACTED = "<redacted>"


@dataclass(frozen=True)
class HttpRequest:
    """One HTTP request, fully described before it is sent (so it can be shown instead)."""

    method: str
    path: str
    kind: Kind = "read"
    fields: tuple[tuple[str, str], ...] = ()
    json_body: Any = None
    secret_fields: frozenset[str] = frozenset()
    note: str = ""

    @property
    def content_type(self) -> str:
        if self.method == "GET":
            return ""
        return JSON if self.json_body is not None else FORM

    def body(self) -> bytes:
        if self.method == "GET":
            return b""
        if self.json_body is not None:
            return json.dumps(self.json_body, separators=(",", ":")).encode("utf-8")
        return urllib.parse.urlencode(list(self.fields)).encode("ascii")

    def shown_fields(self, show_secrets: bool) -> list[tuple[str, str]]:
        if show_secrets:
            return list(self.fields)
        return [(k, REDACTED if k in self.secret_fields else v) for k, v in self.fields]

    def shown_json(self, show_secrets: bool) -> Any:
        if show_secrets or not isinstance(self.json_body, dict):
            return self.json_body
        shown = {k: (REDACTED if k in self.secret_fields else v) for k, v in self.json_body.items()}
        params = shown.get("params")
        if isinstance(params, list) and len(params) == 4:
            # JSON-RPC (OpenWrt ubus): [session, object, method, args]. Hide the live session
            # token and any secret option inside args.
            sid, obj, method, args = params
            if isinstance(sid, str) and re.fullmatch(r"[0-9a-f]{32}", sid) and set(sid) != {"0"}:
                sid = "<session>"
            if isinstance(args, dict):
                args = _redact_nested(args, self.secret_fields)
            shown["params"] = [sid, obj, method, args]
        return shown

    def shown_body(self, show_secrets: bool) -> str:
        if self.json_body is not None:
            return json.dumps(self.shown_json(show_secrets), separators=(",", ":"))
        return urllib.parse.urlencode(self.shown_fields(show_secrets), safe="<>")

    def to_dict(self, base_url: str, show_secrets: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {
            "method": self.method,
            "url": base_url + self.path,
            "kind": self.kind,
        }
        if self.method != "GET":
            out["content_type"] = self.content_type
            if self.json_body is not None:
                out["json"] = self.shown_json(show_secrets)
            else:
                out["fields"] = [[k, v] for k, v in self.shown_fields(show_secrets)]
            out["body"] = self.shown_body(show_secrets)
        if self.note:
            out["note"] = self.note
        return out


def _redact_nested(value: Any, secret_keys: frozenset[str]) -> Any:
    if isinstance(value, dict):
        return {
            k: (REDACTED if k in secret_keys else _redact_nested(v, secret_keys))
            for k, v in value.items()
        }
    return value


class Transport(Protocol):
    """What a driver talks to. Real HTTP in production, fixtures in tests."""

    base_url: str

    def get(self, path: str) -> str: ...

    def send(self, request: HttpRequest) -> str: ...


def check_path(path: str, allow_logout: bool = False) -> None:
    """Refuse any GET whose path could act on the router (logout, reboot, reset, ...).

    ``allow_logout`` (only for ``kind="logout"`` requests) lets "logout" through; every
    other word stays refused.
    """
    bare = urllib.parse.urlsplit(path).path.lower()
    for word in DANGEROUS_PATH_WORDS:
        if allow_logout and word == "logout":
            continue
        if word in bare:
            raise SafetyError(
                what=f"refusing to request {path!r}",
                why=f"paths containing {word!r} can change router state on a plain GET",
                how="router-cli never fetches logout/reboot/reset/restore/upgrade/backup pages",
            )


def normalize_base(host: str) -> str:
    host = host.strip().rstrip("/")
    if not host:
        return ""
    if "://" not in host:
        host = "http://" + host
    return host


@dataclass
class HttpTransport:
    """Plain urllib. No cookies: neither supported router family needs one."""

    base_url: str
    timeout: float = 8.0
    allow_writes: bool = False
    user_agent: str = "router-cli"
    sent: list[HttpRequest] = field(default_factory=list)

    def get(self, path: str) -> str:
        check_path(path)
        return self._do(HttpRequest("GET", path))

    def send(self, request: HttpRequest) -> str:
        if request.method == "GET":
            check_path(request.path, allow_logout=request.kind == "logout")
        if request.kind == "write" and not self.allow_writes:
            raise SafetyError(
                what=f"refusing to send a write to {request.path}",
                why="this transport was opened read-only",
                how="this is a bug in router-cli: writes must go through the write plan",
            )
        return self._do(request)

    def _do(self, request: HttpRequest) -> str:
        url = self.base_url + request.path
        data = request.body() if request.method != "GET" else None
        req = urllib.request.Request(url, data=data, method=request.method)
        req.add_header("User-Agent", self.user_agent)
        if data is not None:
            req.add_header("Content-Type", request.content_type)
        try:
            # codeql[py/full-ssrf]
            # Justified: talking to the router the user named (--host / credentials.json) is
            # the entire purpose of this CLI; the path is fixed by the driver or refused by
            # check_path, and nothing here runs server-side on behalf of a remote caller.
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw: bytes = response.read()
        except urllib.error.HTTPError as exc:
            raise RouterError(
                what=f"{request.method} {url} answered HTTP {exc.code}",
                why=str(exc.reason),
                how="check the host and driver (`router detect`)",
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            raise NetworkError(
                what=f"could not reach {self.base_url}",
                why=str(reason),
                how="check the router address (`--host`) and that this machine is on its LAN",
            ) from exc
        if request.kind == "write":
            self.sent.append(request)
        # Consumer firmware is not reliably UTF-8 (the Ubee's footers are Latin-1).
        return raw.decode("utf-8", errors="replace")


@dataclass
class DryRunTransport:
    """Reads go to the router; writes are recorded and never sent."""

    inner: Transport
    recorded: list[HttpRequest] = field(default_factory=list)

    @property
    def base_url(self) -> str:
        return self.inner.base_url

    def get(self, path: str) -> str:
        return self.inner.get(path)

    def send(self, request: HttpRequest) -> str:
        if request.kind == "write":
            self.recorded.append(request)
            return ""
        return self.inner.send(request)


def render_requests(requests: list[HttpRequest], base_url: str, show_secrets: bool) -> str:
    """Human-readable wire format for a list of requests (used by --dry-run)."""
    blocks = []
    for req in requests:
        lines = [f"{req.method} {base_url}{req.path}"]
        if req.method != "GET":
            lines.append(f"Content-Type: {req.content_type}")
            lines.append("")
            if req.json_body is not None:
                lines.append(json.dumps(req.shown_json(show_secrets), indent=2))
            else:
                for key, value in req.shown_fields(show_secrets):
                    lines.append(f"  {key}={value}")
                lines.append("")
                lines.append(f"body: {req.shown_body(show_secrets)}")
        if req.note:
            lines.append(f"# {req.note}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
