"""wps — Wi-Fi Protected Setup: state, on/off, PBC/PIN mode, and the Connect button."""

from __future__ import annotations

from .._errors import unsupported
from . import _common as C

NAME = "wps"
SUMMARY = "show WPS state; enable/disable; set PBC/PIN mode; press Connect"

VERBS = ("show", "enable", "disable", "mode", "connect")


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in (*VERBS, "-h", "--help"):
        argv = ["show", *argv]
    top = C.parser(NAME, SUMMARY)
    sub = top.add_subparsers(dest="verb")
    p = sub.add_parser("show")
    C.add_router_args(p)
    p.add_argument("--show-secrets", action="store_true")
    for verb in ("enable", "disable"):
        p = sub.add_parser(verb)
        C.add_router_args(p)
        C.add_write_args(p)
    p = sub.add_parser("mode")
    p.add_argument("mode", choices=("pbc", "pin"))
    p.add_argument("--band", choices=("2g", "5g"), required=True)
    p.add_argument("--pin", help="client PIN (PIN mode)")
    C.add_router_args(p)
    C.add_write_args(p)
    p = sub.add_parser("connect", help="press the WPS button (pairing window opens)")
    p.add_argument("--band", choices=("2g", "5g"), required=True)
    p.add_argument("--mode", choices=("pbc", "pin"), default="pbc")
    C.add_router_args(p)
    C.add_write_args(p)
    args = top.parse_args(argv)

    driver = C.open_driver(args)
    if "wps" not in driver.areas:
        raise unsupported(driver.name, "WPS")
    if args.verb == "show":
        data = driver.read_area("wps", show_secrets=args.show_secrets)
        if args.json:
            C.emit_json(data)
        else:
            print(C.kv_lines(data))
        return 0
    plan_wps = getattr(driver, "plan_wps", None)
    if plan_wps is None:
        raise unsupported(driver.name, "changing WPS")
    if args.verb in ("enable", "disable"):
        plan = plan_wps("enable", "2g", None, None, args.verb == "enable")
    elif args.verb == "mode":
        plan = plan_wps("mode", args.band, args.mode, args.pin, None)
    else:
        plan = plan_wps("connect", args.band, args.mode, None, None)
    return C.run_plan(driver, plan, args, after=lambda: driver.read_area("wps"))
