"""Shared test doubles: fixture-backed transports for the Ubee pages and OpenWrt's /ubus.

Every fixture is SYNTHETIC: generated from a capture with every MAC mapped to 02:00:00:*,
public addresses to 192.0.2.0/24 / 198.51.100.0/24, and keys, serials and names replaced.
``test_fixtures_are_synthetic`` keeps it that way.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from router_cli._errors import RouterError
from router_cli.http import HttpRequest, check_path

FIXTURES = Path(__file__).parent / "fixtures"
UBEE = FIXTURES / "ubee"
BASE = "http://192.168.0.1"


def ubee_page(name: str) -> str:
    path = UBEE / name
    if not path.is_file():
        raise RouterError(what=f"GET /{name} answered HTTP 404", why="Not Found", how="")
    return path.read_text(encoding="utf-8", errors="replace")


class UbeeFake:
    """Serves the captured pages; the login page while 'logged out'; records everything sent."""

    def __init__(self, logged_in: bool = True, password: str = "secret") -> None:
        self.base_url = BASE
        self.logged_in = logged_in
        self.password = password
        self.overrides: dict[str, str] = {}
        self.gets: list[str] = []
        self.sent: list[HttpRequest] = []

    def get(self, path: str) -> str:
        check_path(path)
        self.gets.append(path)
        name = path.lstrip("/")
        if name in self.overrides:
            return self.overrides[name]
        if not self.logged_in and name.endswith(".asp"):
            return ubee_page("login.asp")
        return ubee_page(name)

    def send(self, request: HttpRequest) -> str:
        self.sent.append(request)
        if request.kind == "login":
            self.logged_in = dict(request.fields).get("loginPassword") == self.password
        return ""


class UbusFake:
    """A minimal rpcd: answers JSON-RPC calls from a handler table keyed by (object, method)."""

    def __init__(self, handlers: dict[tuple[str, str], Callable[[dict[str, Any]], Any]]) -> None:
        self.base_url = "http://192.0.2.1"
        self.handlers = handlers
        self.sent: list[HttpRequest] = []
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.session = "0123456789abcdef0123456789abcdef"

    def get(self, path: str) -> str:
        check_path(path)
        return '<html><meta http-equiv="refresh" content="0; URL=cgi-bin/luci/" /></html>'

    def send(self, request: HttpRequest) -> str:
        self.sent.append(request)
        body = request.json_body
        sid, obj, method, args = body["params"]
        self.calls.append((obj, method, args))
        if (obj, method) == ("session", "login"):
            if args.get("password") != "secret":
                return json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": [6]})
            data: Any = {"ubus_rpc_session": self.session, "expires": 300}
        elif sid != self.session:
            return json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": body["id"],
                    "error": {"code": -32002, "message": "Access denied"},
                }
            )
        elif (obj, method) in self.handlers:
            data = self.handlers[(obj, method)](args)
        else:
            return json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": [4]})
        return json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": [0, data]})


def creds(user: str = "admin", password: str = "secret") -> Callable[[], tuple[str, str] | None]:
    return lambda: (user, password)
