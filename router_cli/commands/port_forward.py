"""port-forward — list, add and remove port forwarding rules."""

from __future__ import annotations

from .._errors import UsageError
from ..drivers.base import Capability
from ..models import PortForward, validate_ipv4
from . import _common as C

NAME = "port-forward"
SUMMARY = "list/add/rm port forwarding rules"

EPILOG = """\
examples:
  router port-forward list
  router port-forward add 8443 192.168.0.25 443 --proto tcp --description web --dry-run
  router port-forward rm 0 --yes
  router port-forward clear --yes"""

VERBS = ("list", "add", "rm", "clear")


def _range(text: str) -> tuple[int, int]:
    try:
        start, _, end = text.partition("-")
        lo, hi = int(start), int(end or start)
    except ValueError as exc:
        raise UsageError(
            what=f"{text!r} is not a port or port range", why="", how="e.g. 8080 or 6000-6010"
        ) from exc
    if not 1 <= lo <= hi <= 65535:
        raise UsageError(what=f"bad port range {text!r}", why="ports are 1-65535", how="")
    return lo, hi


def _fmt(start: int, end: int) -> str:
    return str(start) if start == end else f"{start}-{end}"


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in (*VERBS, "-h", "--help"):
        argv = ["list", *argv]
    top = C.parser(NAME, SUMMARY, EPILOG)
    sub = top.add_subparsers(dest="verb")
    p_list = sub.add_parser("list")
    C.add_router_args(p_list)
    p_add = sub.add_parser("add")
    p_add.add_argument("external", help="external port or range (e.g. 8443 or 6000-6010)")
    p_add.add_argument("ip", help="LAN address to forward to")
    p_add.add_argument("internal", nargs="?", help="internal port or range (default: same)")
    p_add.add_argument("--proto", choices=("tcp", "udp", "both"), default="tcp")
    p_add.add_argument("--description", default="")
    p_add.add_argument("--disabled", action="store_true")
    C.add_router_args(p_add)
    C.add_write_args(p_add)
    p_rm = sub.add_parser("rm")
    p_rm.add_argument("index", type=int, help="rule number from `list`")
    C.add_router_args(p_rm)
    C.add_write_args(p_rm)
    p_clear = sub.add_parser("clear")
    C.add_router_args(p_clear)
    C.add_write_args(p_clear)
    args = top.parse_args(argv)

    driver = C.open_driver(args)
    driver.require(Capability.PORT_FORWARD, "port forwarding")
    if args.verb == "list":
        rules = driver.port_forwards()
        if args.json:
            C.emit_json(rules)
            return 0
        if not rules:
            print("(no port forwarding rules)")
            return 0
        rows = []
        for r in rules:
            external = _fmt(r.external_start, r.external_end)
            if r.external_ip:
                external = f"{r.external_ip}:{external}"
            rows.append(
                [
                    r.index,
                    external,
                    f"{r.local_ip}:{_fmt(r.local_start, r.local_end)}",
                    r.protocol,
                    "yes" if r.enabled else "no",
                    r.description,
                ]
            )
        print(C.table(["#", "external", "to", "proto", "enabled", "description"], rows))
        return 0
    if args.verb == "add":
        driver.require(Capability.PORT_FORWARD_ADD, "adding port forwards")
        ext = _range(args.external)
        loc = _range(args.internal) if args.internal else ext
        if loc[1] - loc[0] != ext[1] - ext[0]:
            raise UsageError(what="external and internal ranges differ in size", why="", how="")
        rule = PortForward(
            index=-1,
            local_ip=validate_ipv4(args.ip),
            local_start=loc[0],
            local_end=loc[1],
            external_ip=None,
            external_start=ext[0],
            external_end=ext[1],
            protocol=args.proto,
            description=args.description,
            enabled=not args.disabled,
        )
        plan = driver.plan_port_forward_add(rule)
    elif args.verb == "rm":
        plan = driver.plan_port_forward_remove(args.index)
    else:
        plan = driver.plan_port_forward_remove(None)
    return C.run_plan(driver, plan, args, after=driver.port_forwards)
