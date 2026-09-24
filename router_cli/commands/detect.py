"""detect — which router is at this address? (GET-only probes, no login)."""

from __future__ import annotations

from .. import drivers
from ..http import HttpTransport
from . import _common as C

NAME = "detect"
SUMMARY = "identify the router model and driver at a host (no login)"


def run(argv: list[str]) -> int:
    p = C.parser(NAME, SUMMARY)
    p.add_argument("--host", help="router address (default: saved default, then gateway)")
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    base = C.resolve_host(args)
    found = drivers.detect(HttpTransport(base, timeout=args.timeout))
    result = {
        "host": base,
        "driver": found[0] if found else None,
        "model": found[1] if found else None,
        "title": drivers.get(found[0]).title if found else None,
    }
    if args.json:
        C.emit_json(result)
    elif found:
        print(f"{base}: {result['model']} -> driver {result['driver']} ({result['title']})")
    else:
        print(f"{base}: not recognised by any driver (see `router drivers`)")
    return 0 if found else 4
