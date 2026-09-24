"""drivers — the router families router-cli knows, and what each can do."""

from __future__ import annotations

import argparse

from .. import drivers
from ..drivers.base import Capability
from . import _common as C

NAME = "drivers"
SUMMARY = "list drivers and their capability matrix"


def run(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="router drivers", description=SUMMARY)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    out = {
        name: {
            "title": cls.title,
            "vendor": cls.vendor,
            "capabilities": sorted(c.value for c in cls.capabilities),
            "areas": cls.areas,
            "lists": cls.lists,
            "notes": cls.notes,
            "aliases": sorted(a for a, target in drivers.ALIASES.items() if target == name),
        }
        for name, cls in drivers.DRIVERS.items()
    }
    if args.json:
        C.emit_json(out)
        return 0
    for name, info in out.items():
        print(f"{name}: {info['title']}")
        if info["aliases"]:
            print(f"  aliases: {', '.join(info['aliases'])}")
        for note in info["notes"]:
            print(f"  note: {note}")
    print()
    names = list(out)
    rows = [
        [cap.value, *("yes" if cap.value in out[n]["capabilities"] else "-" for n in names)]
        for cap in Capability
    ]
    print(C.table(["capability", *names], rows))
    return 0
