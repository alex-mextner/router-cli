"""lists — every list-shaped setting of the router by name (MAC filter, keywords, ...)."""

from __future__ import annotations

import argparse

from .._errors import unknown_item
from ..drivers.base import BaseDriver
from . import _common as C
from . import _lists

NAME = "lists"
SUMMARY = "show/add/rm/clear list settings (mac-filter, keywords, domains, ...)"


def _named(driver: BaseDriver, args: argparse.Namespace) -> str:
    if args.name not in driver.lists:
        raise unknown_item("list", args.name, sorted(driver.lists))
    return str(args.name)


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in (*_lists.VERBS, "-h", "--help"):
        p = C.parser(NAME, SUMMARY)
        C.add_router_args(p)
        args = p.parse_args(argv)
        driver = C.open_driver(args)
        if args.json:
            C.emit_json(driver.lists)
        else:
            print(C.table(["list", "what"], sorted(driver.lists.items())))
        return 0
    top = C.parser(NAME, SUMMARY)
    sub = top.add_subparsers(dest="verb")
    for verb in _lists.VERBS:
        p = sub.add_parser(verb)
        p.add_argument("name")
        if verb in ("add", "rm"):
            p.add_argument("value")
        C.add_router_args(p)
        if verb != "show":
            C.add_write_args(p)
    return _lists.run_list(top.parse_args(argv), _named)
