"""icons — pick a Material Design Icon for a device from what is known about it.

The rules are data (``data/icon_rules.json``), tried in order; the first whose every
condition holds wins. A user file at ``<config dir>/icon_rules.json`` with the same shape is
tried BEFORE the shipped rules, so adding or overriding a rule never means editing the
package. A per-MAC icon set with ``router alias <mac> --icon`` beats every rule.

Conditions (all optional; a rule with none never matches):
    ``vendor``, ``hostname``, ``title``, ``server``  case-insensitive regex search
    ``ports``      any of these ports has an HTTP(S) service on the device
    ``random_mac`` the MAC is (or is not) locally administered
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from typing import Any

from ._errors import UsageError
from .config import config_dir

DEFAULT_ICON = "mdi:help-network"
_CONDITIONS = ("vendor", "hostname", "title", "server", "ports", "random_mac")


@dataclass
class Facts:
    """Everything a rule can look at."""

    vendor: str | None = None
    hostnames: list[str] = field(default_factory=list)
    titles: list[str] = field(default_factory=list)
    servers: list[str] = field(default_factory=list)
    ports: list[int] = field(default_factory=list)
    random_mac: bool = False


def _validate(rules: Any, origin: str) -> list[dict[str, Any]]:
    if not isinstance(rules, list):
        raise UsageError(what=f"{origin}: 'rules' must be a list", why="", how="")
    out = []
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict) or not isinstance(rule.get("icon"), str):
            raise UsageError(what=f"{origin}: rule {i} needs an 'icon'", why=str(rule), how="")
        for key in ("vendor", "hostname", "title", "server"):
            if key in rule:
                try:
                    re.compile(str(rule[key]))
                except re.error as exc:
                    raise UsageError(
                        what=f"{origin}: rule {i} {key} is not a regex", why=str(exc), how=""
                    ) from exc
        if not any(k in rule for k in _CONDITIONS):
            raise UsageError(what=f"{origin}: rule {i} has no condition", why=str(rule), how="")
        out.append(rule)
    return out


@lru_cache(maxsize=1)
def load_rules() -> tuple[list[dict[str, Any]], str]:
    """(rules in match order, default icon)."""
    shipped = json.loads(
        resources.files("router_cli").joinpath("data", "icon_rules.json").read_text("utf-8")
    )
    rules = _validate(shipped.get("rules"), "shipped icon_rules.json")
    default = str(shipped.get("default", DEFAULT_ICON))
    user_path = config_dir() / "icon_rules.json"
    if user_path.is_file():
        try:
            user = json.loads(user_path.read_text("utf-8"))
        except ValueError as exc:
            raise UsageError(
                what=f"could not parse {user_path}", why=str(exc), how="fix the JSON"
            ) from exc
        rules = _validate(user.get("rules", []), str(user_path)) + rules
        default = str(user.get("default", default))
    return rules, default


def _search(pattern: str, values: list[str]) -> bool:
    regex = re.compile(pattern, re.I)
    return any(regex.search(v) for v in values if v)


def matches(rule: dict[str, Any], facts: Facts) -> bool:
    if "vendor" in rule and not _search(str(rule["vendor"]), [facts.vendor or ""]):
        return False
    if "hostname" in rule and not _search(str(rule["hostname"]), facts.hostnames):
        return False
    if "title" in rule and not _search(str(rule["title"]), facts.titles):
        return False
    if "server" in rule and not _search(str(rule["server"]), facts.servers):
        return False
    if "ports" in rule and not set(int(p) for p in rule["ports"]) & set(facts.ports):
        return False
    return not ("random_mac" in rule and bool(rule["random_mac"]) != facts.random_mac)


def choose(facts: Facts) -> str:
    rules, default = load_rules()
    for rule in rules:
        if matches(rule, facts):
            return str(rule["icon"])
    return default


def _user_rules() -> tuple[dict[str, Any], ...]:
    user_path = config_dir() / "icon_rules.json"
    if not user_path.is_file():
        return ()
    try:
        user = json.loads(user_path.read_text("utf-8"))
    except ValueError as exc:
        raise UsageError(
            what=f"could not parse {user_path}", why=str(exc), how="fix the JSON"
        ) from exc
    return tuple(_validate(user.get("rules", []), str(user_path)))


def choose_user(facts: Facts) -> str | None:
    """The icon of the first matching rule from the USER's icon_rules.json, if any (these beat
    the device classifier; the shipped rules are only its fallback)."""
    for rule in _user_rules():
        if matches(rule, facts):
            return str(rule["icon"])
    return None
