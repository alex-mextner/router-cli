"""cli — the command dispatcher.

SELF-REGISTERING COMMANDS
    Every module in ``router_cli/commands/`` that exposes ``NAME``, ``SUMMARY`` and
    ``run(argv) -> int`` becomes a subcommand. Adding one is dropping a file in; nothing
    here changes. Modules starting with ``_`` are shared helpers.

IMPORT-CLEAN AT THE TOP
    Everything is standard library, so ``router --help`` costs nothing and works on a bare
    machine; command modules are imported to build the help text.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from collections.abc import Callable

from . import palette
from ._errors import EXIT_OK, RouterCliError, guard, unknown_item

_RunFn = Callable[[list[str]], int]


def _discover() -> dict[str, tuple[str, str]]:
    """Map command name -> (module, one-line summary) by scanning the commands package."""
    from . import commands

    found: dict[str, tuple[str, str]] = {}
    for info in pkgutil.iter_modules(commands.__path__):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{commands.__name__}.{info.name}")
        name = getattr(module, "NAME", None)
        summary = getattr(module, "SUMMARY", "")
        if name:
            found[name] = (f"{commands.__name__}.{info.name}", summary)
    return dict(sorted(found.items()))


_HEADLINE = "router — the home router from the command line (Ubee EVW32C, OpenWrt)"
_CLOSING = "every command takes --json; every write takes --dry-run. `router <command> --help`."

_COMMAND_COLUMN = 16
_EXAMPLE_COLUMN = 44

_GROUPS = (
    ("setup", ("login", "logout", "doctor", "detect", "drivers", "install-skill")),
    ("look", ("status", "devices", "leases", "wan", "cm", "telephony")),
    ("inventory", ("inventory", "scan", "alias", "oui")),
    ("change", ("reserve", "unreserve", "dhcp", "lan", "wifi", "wifi-acl", "wps", "port-forward")),
    ("security", ("firewall", "filter", "dmz", "options", "parental", "password")),
    ("more", ("vpn", "nas", "settings", "lists", "reboot", "raw")),
)

_GETTING_STARTED = (
    ("router login", "store the admin password (prompted)"),
    ("router doctor", "check everything"),
    ("router devices", "who is connected"),
    ("router reserve <mac> <ip> --dry-run", "pin an IP; see the exact request"),
    ("router inventory update", "poll into the local device DB"),
    ("router inventory list --json", "the Home Assistant / agent contract"),
)


def _usage(catalog: dict[str, tuple[str, str]]) -> str:
    paint = palette.for_help()
    lines = [
        _HEADLINE,
        "",
        f"{paint.heading}usage:{paint.reset}",
        f"  {paint.prog}router{paint.reset} <command> [args]",
    ]
    listed: set[str] = set()
    for title, names in _GROUPS:
        present = [n for n in names if n in catalog]
        if not present:
            continue
        lines += ["", f"{paint.heading}{title}:{paint.reset}"]
        for name in present:
            listed.add(name)
            lines.append(
                _row(f"{paint.action}{name}{paint.reset}", name, catalog[name][1], _COMMAND_COLUMN)
            )
    rest = [n for n in catalog if n not in listed]
    if rest:
        lines += ["", f"{paint.heading}other:{paint.reset}"]
        lines += [
            _row(f"{paint.action}{n}{paint.reset}", n, catalog[n][1], _COMMAND_COLUMN) for n in rest
        ]
    lines += ["", f"{paint.heading}getting started:{paint.reset}"]
    for invocation, summary in _GETTING_STARTED:
        prog, _, tail = invocation.partition(" ")
        lines.append(
            _row(f"{paint.prog}{prog}{paint.reset} {tail}", invocation, summary, _EXAMPLE_COLUMN)
        )
    lines += ["", _CLOSING]
    return "\n".join(lines)


def _row(shown: str, plain: str, summary: str, column: int) -> str:
    """Indent *shown*, then pad to *column* — measured on *plain*, since colour is not wide."""
    if not summary:
        return f"  {shown}"
    return f"  {shown}{' ' * max(1, column - len(plain))}{summary}"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    return guard(lambda: _dispatch(args))


def _dispatch(args: list[str]) -> int:
    catalog = _discover()
    if not args or args[0] in {"-h", "--help", "help"}:
        print(_usage(catalog))
        return EXIT_OK
    head = args[0]
    if head in {"-V", "--version", "version"}:
        from . import __version__

        print(f"router {__version__}")
        return EXIT_OK
    if head not in catalog:
        raise unknown_item("command", head, list(catalog))
    return _load(catalog[head][0])(args[1:])


def _load(module_name: str) -> _RunFn:
    module = importlib.import_module(module_name)
    run = getattr(module, "run", None)
    if run is None:  # pragma: no cover - only reachable from a malformed command module
        raise RouterCliError(
            what=f"{module_name} is not a valid command module",
            why="it does not define run(argv) -> int",
            how="this is a bug in router-cli; please open an issue",
        )
    return run  # type: ignore[no-any-return]


if __name__ == "__main__":
    raise SystemExit(main())
