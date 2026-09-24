"""_errors — structured errors and stable exit codes for router-cli.

WHY THIS EXISTS
    Every failure a user (or an agent) can hit should say three things: WHAT went wrong, WHY
    it went wrong, and HOW to fix it. A bare traceback or a lone ``exit(1)`` says none of
    them. The exit codes match the numbers the sibling personal CLIs (stt, rig, review)
    already use, so a script can branch on ``$?`` the same way across all of them.

CONTRACT
    - Stdlib-only, so the dispatcher can import it at module top with zero cost.
    - Raise a subclass; let :func:`guard` render it and return the code.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import NoReturn

EXIT_OK = 0
EXIT_INTERNAL = 1  # an unexpected failure / bug in router-cli itself
EXIT_USAGE = 2  # invalid argument or malformed value
EXIT_CONFIRM = 3  # a destructive write was refused because --yes was not given
EXIT_UNKNOWN_ITEM = 4  # a name that doesn't exist (unknown command, driver, page, key)
EXIT_MISSING_TARGET = 5  # a referenced thing is gone (no such lease, no such MAC)
EXIT_UNSUPPORTED = 6  # the driver for this router cannot do that
EXIT_NETWORK = 7  # the router (or a device) could not be reached
EXIT_PERMISSION = 8  # not logged in / credentials rejected
EXIT_ROUTER = 10  # the router answered, but not with anything we could use
EXIT_MISSING_DEP = 127  # a required external tool isn't installed

EXIT_NAMES: dict[int, str] = {
    EXIT_OK: "ok",
    EXIT_INTERNAL: "internal error",
    EXIT_USAGE: "usage error",
    EXIT_CONFIRM: "confirmation required",
    EXIT_UNKNOWN_ITEM: "unknown item",
    EXIT_MISSING_TARGET: "missing target",
    EXIT_UNSUPPORTED: "unsupported by driver",
    EXIT_NETWORK: "network error",
    EXIT_PERMISSION: "permission error",
    EXIT_ROUTER: "router error",
    EXIT_MISSING_DEP: "missing dependency",
}


class RouterCliError(Exception):
    """A diagnosed failure: WHAT happened, WHY, and HOW to fix it."""

    exit_code = EXIT_INTERNAL

    def __init__(self, what: str, why: str = "", how: str = "") -> None:
        super().__init__(what)
        self.what = what
        self.why = why
        self.how = how

    def render(self) -> str:
        lines = [f"router: {self.what}"]
        if self.why:
            lines.append(f"  why:  {self.why}")
        if self.how:
            lines.append(f"  fix:  {self.how}")
        return "\n".join(lines)


class UsageError(RouterCliError):
    exit_code = EXIT_USAGE


class ConfirmationRequired(RouterCliError):
    exit_code = EXIT_CONFIRM


class UnknownItemError(RouterCliError):
    exit_code = EXIT_UNKNOWN_ITEM


class MissingTargetError(RouterCliError):
    exit_code = EXIT_MISSING_TARGET


class UnsupportedError(RouterCliError):
    exit_code = EXIT_UNSUPPORTED


class NetworkError(RouterCliError):
    exit_code = EXIT_NETWORK


class NotLoggedInError(RouterCliError):
    exit_code = EXIT_PERMISSION


class RouterError(RouterCliError):
    exit_code = EXIT_ROUTER


class SafetyError(RouterCliError):
    """A request router-cli refuses to send at all (logout, reboot pages, stray writes)."""

    exit_code = EXIT_USAGE


class MissingDependencyError(RouterCliError):
    exit_code = EXIT_MISSING_DEP


def unknown_item(
    kind: str, name: str, known: list[str], *, plural: str | None = None
) -> UnknownItemError:
    """Build an unknown-<kind> error with a did-you-mean hint drawn from ``known``."""
    import difflib

    many = plural or f"{kind}s"
    close = difflib.get_close_matches(name, known, n=3, cutoff=0.5)
    hint = f"did you mean: {', '.join(close)}?" if close else f"known {many}: {', '.join(known)}"
    return UnknownItemError(
        what=f"unknown {kind}: {name!r}",
        why=f"{name!r} is not one of the known {many}",
        how=hint,
    )


def unsupported(driver: str, feature: str) -> UnsupportedError:
    return UnsupportedError(
        what=f"the {driver} driver does not support {feature}",
        why="this router's web interface (or the driver) has no equivalent of that feature",
        how="run `router drivers` for the capability matrix",
    )


def guard(fn: Callable[[], int]) -> int:
    """Run ``fn``, rendering any diagnosed error to stderr and returning its exit code."""
    try:
        return fn()
    except RouterCliError as exc:
        print(exc.render(), file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("router: interrupted", file=sys.stderr)
        return 130
    except BrokenPipeError:  # `router devices | head` — not an error worth a traceback
        return EXIT_OK


def internal(msg: str) -> NoReturn:
    raise RouterCliError(what=msg, why="this is a bug in router-cli", how="please open an issue")
