"""drivers — the registry of router families, and model detection.

Adding a router family is one module here that subclasses :class:`base.BaseDriver`, plus one
line in ``DRIVERS``. ``detect`` asks each driver's ``probe`` in order (GET-only, no login)
and returns the first that recognises the host.
"""

from __future__ import annotations

from .._errors import NetworkError, RouterCliError, unknown_item
from ..http import Transport
from .base import BaseDriver, Capability
from .openwrt import OpenWrt
from .ubee_evw32c import UbeeEVW32C

DRIVERS: dict[str, type[BaseDriver]] = {
    UbeeEVW32C.name: UbeeEVW32C,
    OpenWrt.name: OpenWrt,
}

ALIASES: dict[str, str] = {
    "ubee": "ubee_evw32c",
    "ubee-evw32c": "ubee_evw32c",
    "evw32c": "ubee_evw32c",
    "evw32c-0n": "ubee_evw32c",
    "evw32c-0s": "ubee_evw32c",
    "luci": "openwrt",
}


def get(name: str) -> type[BaseDriver]:
    key = ALIASES.get(name.lower(), name.lower())
    if key not in DRIVERS:
        raise unknown_item("driver", name, list(DRIVERS))
    return DRIVERS[key]


def detect(transport: Transport) -> tuple[str, str] | None:
    """(driver name, model) for the first driver that recognises the host, else None."""
    for name, cls in DRIVERS.items():
        try:
            model = cls.probe(transport)
        except NetworkError:
            raise  # an unreachable host is not "an unknown router"
        except RouterCliError:
            model = None
        if model:
            return name, model
    return None


__all__ = ["ALIASES", "DRIVERS", "BaseDriver", "Capability", "detect", "get"]
