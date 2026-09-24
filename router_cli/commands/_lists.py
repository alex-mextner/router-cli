"""_lists — one implementation behind every list-shaped setting (MAC filter, keywords, ...).

router <cmd> [show]         the current entries
router <cmd> add <value>    append (``--dry-run`` prints the exact request)
router <cmd> rm <value>     remove one entry
router <cmd> clear          remove all (destructive: needs ``--yes``)
"""

from __future__ import annotations

import argparse
from collections.abc import Callable

from .._errors import unsupported
from ..drivers.base import BaseDriver, Capability
from . import _common as C

ListResolver = Callable[[BaseDriver, argparse.Namespace], str]

VERBS = ("show", "add", "rm", "clear")


def fixed(name: str) -> ListResolver:
    def resolve(driver: BaseDriver, args: argparse.Namespace) -> str:
        if name not in driver.lists:
            raise unsupported(driver.name, f"the {name!r} list")
        return name

    return resolve


def make(
    name: str,
    summary: str,
    resolver: ListResolver,
    extra_args: Callable[[argparse.ArgumentParser], None] | None = None,
) -> Callable[[list[str]], int]:
    def run(argv: list[str]) -> int:
        if not argv or argv[0] not in (*VERBS, "-h", "--help"):
            argv = ["show", *argv]
        top = C.parser(name, summary)
        sub = top.add_subparsers(dest="verb")
        for verb in VERBS:
            p = sub.add_parser(verb)
            C.add_router_args(p)
            if extra_args:
                extra_args(p)
            if verb in ("add", "rm"):
                p.add_argument("value")
            if verb != "show":
                C.add_write_args(p)
        args = top.parse_args(argv)
        return run_list(args, resolver)

    return run


def run_list(args: argparse.Namespace, resolver: ListResolver) -> int:
    driver = C.open_driver(args)
    driver.require(Capability.LISTS, "list settings")
    list_name = resolver(driver, args)
    if args.verb == "show":
        items = driver.list_items(list_name)
        if args.json:
            C.emit_json({"list": list_name, "items": items})
        else:
            print("\n".join(items) if items else f"({list_name} is empty)")
        return 0
    action = {"add": "add", "rm": "remove", "clear": "clear"}[args.verb]
    plan = driver.plan_list_edit(list_name, action, getattr(args, "value", None))
    return C.run_plan(driver, plan, args, after=lambda: driver.list_items(list_name))
