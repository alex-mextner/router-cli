"""device_selector — what a user may type wherever a command wants "a device".

A DEVICE is any of:

    a MAC address in any common spelling   aa:bb:cc:dd:ee:ff  AA-BB-CC-DD-EE-FF  aa_bb_...
                                           aabb.ccdd.eeff  aabbccddeeff  (any case)
    a current IPv4 address                 192.168.0.25   (the device the inventory has there)
    a name                                 the local alias, the router-reported host name or
                                           any name the inventory has seen for it; matched
                                           case-insensitively, exact first, then a unique
                                           prefix ("print" for "Printer-3D")

Names and addresses are resolved against the LOCAL inventory database only — resolving a
selector never talks to the router. A MAC is accepted as-is even when the inventory has
never seen it (so you can reserve or filter a device before it first connects). An
ambiguous name is an error that lists the candidates, never a guess.
"""

from __future__ import annotations

from typing import Any

from ._errors import MissingTargetError, UsageError
from .inventory import Inventory
from .models import is_ipv4, is_mac, normalize_mac, validate_ipv4

HELP = "MAC (any format), current IP, or device name/alias (unique prefix OK)"


def resolve_mac(text: str, inv: Inventory | None = None) -> str:
    """The MAC a device selector names (see the module docstring)."""
    selector = (text or "").strip()
    if not selector:
        raise UsageError(what="empty device", why="", how=f"give a {HELP}")
    if is_mac(selector):
        return normalize_mac(selector)
    if inv is None:
        with Inventory() as own:
            return _lookup(selector, own)
    return _lookup(selector, inv)


def resolve_target(text: str, inv: Inventory | None = None) -> tuple[str, str | None]:
    """(ip, mac or None) for a selector that must end up at an address (e.g. `scan --ip`)."""
    selector = (text or "").strip()
    if is_ipv4(selector):
        ip = validate_ipv4(selector)
        if inv is None:
            with Inventory() as own:
                return ip, own.mac_for_ip(ip)
        return ip, inv.mac_for_ip(ip)
    if inv is None:
        with Inventory() as own:
            return _target(selector, own)
    return _target(selector, inv)


def current_ip(mac: str, inv: Inventory | None = None) -> str | None:
    if inv is None:
        with Inventory() as own:
            return own.ip_for_mac(mac)
    return inv.ip_for_mac(mac)


def _target(selector: str, inv: Inventory) -> tuple[str, str | None]:
    mac = resolve_mac(selector, inv)
    ip = inv.ip_for_mac(mac)
    if not ip:
        raise MissingTargetError(
            what=f"no known IP address for {selector!r} ({mac})",
            why="the inventory has never seen this device with an address",
            how="give the IP instead, or run `router inventory update` first",
        )
    return ip, mac


def _describe(row: dict[str, Any]) -> str:
    name = row["names"][0] if row["names"] else "-"
    state = "online" if row["online"] else "offline"
    return f"{name} ({row['mac']}, {row['ip'] or 'no ip'}, {state})"


def _lookup(selector: str, inv: Inventory) -> str:
    rows = inv.selector_rows()
    if is_ipv4(selector):
        ip = validate_ipv4(selector)
        mac = inv.mac_for_ip(ip)
        if mac:
            return mac
        raise MissingTargetError(
            what=f"no device at {ip} in the inventory",
            why="the local inventory has never seen a device with that address",
            how="run `router inventory update` (or give the MAC address)",
        )
    wanted = selector.casefold()
    exact = [r for r in rows if any(n.casefold() == wanted for n in r["names"])]
    matches = exact or [r for r in rows if any(n.casefold().startswith(wanted) for n in r["names"])]
    if len(matches) == 1:
        return str(matches[0]["mac"])
    if not matches:
        known = sorted({r["names"][0] for r in rows if r["names"]}, key=str.casefold)
        raise MissingTargetError(
            what=f"no device matches {selector!r}",
            why="it is not a MAC address, not an IPv4 address, and no inventory name starts "
            "with it",
            how=(
                f"known names: {', '.join(known[:15])}{' ...' if len(known) > 15 else ''}"
                if known
                else "run `router inventory update` first, or give the MAC address"
            ),
        )
    listed = "; ".join(_describe(r) for r in matches[:10])
    more = f" (+{len(matches) - 10} more)" if len(matches) > 10 else ""
    raise UsageError(
        what=f"{selector!r} matches {len(matches)} devices",
        why=f"candidates: {listed}{more}",
        how="type more of the name, or give the MAC or IP address",
    )
