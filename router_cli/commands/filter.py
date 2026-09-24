"""filter — traffic filters: `filter ip`, `filter port` (rule tables), `filter mac` (list)."""

from __future__ import annotations

from .._errors import UsageError
from . import _area, _lists

NAME = "filter"
SUMMARY = "IP-range, port and MAC filters (filter ip|port|mac ...)"

_ip = _area.make("filter ip", "IP range filters (10 rules)", _area.fixed("ip-filter"))
_port = _area.make("filter port", "outbound port filters (10 rules)", _area.fixed("port-filter"))
_mac = _lists.make(
    "filter mac", "MAC addresses blocked from the internet", _lists.fixed("mac-filter")
)

USAGE = """\
usage: router filter ip   [show|keys|set rule1_start=20 rule1_end=30 rule1_enabled=yes]
       router filter port [show|keys|set rule1_start=25 rule1_end=25 rule1_protocol=tcp ...]
       router filter mac  [show|add <mac>|rm <mac>|clear]
every form takes --json; writes take --dry-run and --yes"""


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0
    kind, rest = argv[0], argv[1:]
    runner = {"ip": _ip, "port": _port, "mac": _mac}.get(kind)
    if runner is None:
        raise UsageError(what=f"unknown filter kind {kind!r}", why="", how="use ip, port or mac")
    return runner(rest)
