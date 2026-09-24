"""_area — one implementation behind every "show / set key=value / keys" command.

``router dhcp``, ``router lan``, ``router firewall`` ... are the same three verbs over a
different settings area of the driver:

    router <cmd> [show]            current values (``--json`` for agents)
    router <cmd> keys              what can be set, with choices
    router <cmd> set k=v [k=v]     change; ``--dry-run`` prints the exact request

A command module is then two lines: ``NAME``/``SUMMARY`` and ``run = make(...)``.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any

from .._errors import UsageError, unsupported
from ..drivers.base import BaseDriver, Capability
from . import _common as C

Resolver = Callable[[BaseDriver, argparse.Namespace, bool], list[str]]


def fixed(area: str) -> Resolver:
    def resolve(driver: BaseDriver, args: argparse.Namespace, for_write: bool) -> list[str]:
        if area not in driver.areas:
            raise unsupported(driver.name, f"the {area!r} settings")
        return [area]

    return resolve


def make(
    name: str,
    summary: str,
    resolver: Resolver,
    *,
    writable: bool = True,
    extra_args: Callable[[argparse.ArgumentParser], None] | None = None,
    epilog: str | None = None,
) -> Callable[[list[str]], int]:
    verbs = ("show", "keys", "set") if writable else ("show", "keys")

    def run(argv: list[str]) -> int:
        if not argv or argv[0] not in (*verbs, "-h", "--help"):
            argv = ["show", *argv]
        top = C.parser(name, summary, epilog)
        sub = top.add_subparsers(dest="verb")
        for verb in verbs:
            p = sub.add_parser(
                verb,
                help={"show": "current values", "keys": "settable keys", "set": "change values"}[
                    verb
                ],
            )
            C.add_router_args(p)
            if extra_args:
                extra_args(p)
            if verb == "show":
                p.add_argument("--show-secrets", action="store_true", help="reveal passwords/keys")
            if verb == "set":
                p.add_argument("assignments", nargs="+", metavar="key=value")
                C.add_write_args(p)
        args = top.parse_args(argv)
        driver = C.open_driver(args)
        driver.require(Capability.SETTINGS, f"{name} settings")
        if args.verb == "keys":
            return _keys(driver, resolver(driver, args, False), args)
        if args.verb == "show":
            return _show(driver, resolver(driver, args, False), args)
        areas = resolver(driver, args, True)
        if len(areas) != 1:
            raise UsageError(
                what=f"say which one to change: {', '.join(areas)}", why="", how="add --band"
            )
        changes = C.parse_assignments(args.assignments)
        plan = driver.plan_area(areas[0], changes)
        return C.run_plan(driver, plan, args, after=lambda: driver.read_area(areas[0]))

    return run


def _show(driver: BaseDriver, areas: list[str], args: argparse.Namespace) -> int:
    data: dict[str, Any] = {
        a: driver.read_area(a, show_secrets=bool(args.show_secrets)) for a in areas
    }
    if args.json:
        C.emit_json(data[areas[0]] if len(areas) == 1 else data)
        return 0
    for i, area in enumerate(areas):
        if len(areas) > 1:
            print(("\n" if i else "") + f"[{area}]")
        print(C.kv_lines(data[area]))
    return 0


def _keys(driver: BaseDriver, areas: list[str], args: argparse.Namespace) -> int:
    out: dict[str, list[dict[str, Any]]] = {
        a: [
            {
                "key": s.key,
                "help": s.help,
                "choices": s.choices,
                "secret": s.secret,
                "writable": s.writable,
            }
            for s in driver.area_keys(a)
        ]
        for a in areas
    }
    if args.json:
        C.emit_json(out[areas[0]] if len(areas) == 1 else out)
        return 0
    for area, specs in out.items():
        if len(areas) > 1:
            print(f"[{area}]")
        rows = [
            [
                s["key"],
                "/".join(s["choices"]) if s["choices"] else "",
                s["help"] + ("" if s["writable"] else " (read-only)"),
            ]
            for s in specs
        ]
        print(C.table(["key", "choices", "meaning"], rows))
    return 0
