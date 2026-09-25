"""base — the driver contract every router family implements.

A driver turns one router family's web interface into the normalized models in
:mod:`router_cli.models`. It declares what it can do in ``capabilities``; the CLI checks
that set before calling anything, so an unsupported feature is a diagnosed error
(exit code 6), never an AttributeError.

READS return models. WRITES never touch the router directly: they return a
:class:`WritePlan` — the exact requests that would be sent — which the CLI prints for
``--dry-run``, gates behind ``--yes`` when ``destructive``, and otherwise hands to
:func:`execute`. That split is what makes every write reviewable before it happens and
testable without a router.

SETTINGS AREAS
    Most of a router's pages are "a handful of settings with an Apply button". Rather than a
    method per page, a driver exposes named *areas* (``lan``, ``dhcp``, ``wifi``,
    ``firewall``, ...): ``area_keys`` describes the settable keys, ``read_area`` returns the
    current values, ``plan_area`` turns ``{key: value}`` changes into a plan. List-shaped
    settings (a MAC filter, a keyword block list) use ``list_items``/``plan_list_edit``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Protocol

from .._errors import unsupported
from ..http import HttpRequest, Transport
from ..models import Device, Lease, PortForward, Reservation, RouterInfo, Status


class Capability(StrEnum):
    STATUS = "status"
    DEVICES = "devices"
    LEASES = "leases"
    RESERVE = "reserve"
    PORT_FORWARD = "port-forward"
    PORT_FORWARD_ADD = "port-forward-add"
    SETTINGS = "settings"
    LISTS = "lists"
    PASSWORD = "password"
    REBOOT = "reboot"
    DOCSIS = "docsis"
    TELEPHONY = "telephony"
    LOGIN = "login"
    RAW = "raw"


CredentialSource = Callable[[], tuple[str, str] | None]


@dataclass
class SettingSpec:
    """One settable (or read-only) key of a settings area."""

    key: str
    help: str
    choices: list[str] | None = None
    secret: bool = False
    writable: bool = True


@dataclass
class Deferred:
    """A step whose request can only be built after the previous one ran (multi-page flows).

    ``build`` receives the transport and the previous step's response body.
    """

    description: str
    build: Callable[[Transport, str], list[HttpRequest]]


Step = HttpRequest | Deferred


@dataclass
class WritePlan:
    summary: str
    steps: list[Step] = field(default_factory=list)
    destructive: bool = False
    notes: list[str] = field(default_factory=list)
    verified: bool = True  # False: the request shape is inferred, not seen in a capture

    @property
    def requests(self) -> list[HttpRequest]:
        return [s for s in self.steps if isinstance(s, HttpRequest)]

    @property
    def deferred(self) -> list[Deferred]:
        return [s for s in self.steps if isinstance(s, Deferred)]


def execute(plan: WritePlan, transport: Transport) -> list[str]:
    """Send every step of a plan in order; return the router's responses."""
    responses: list[str] = []
    for step in plan.steps:
        if isinstance(step, HttpRequest):
            responses.append(transport.send(step))
        else:
            previous = responses[-1] if responses else ""
            for request in step.build(transport, previous):
                responses.append(transport.send(request))
    return responses


class Driver(Protocol):
    """What the CLI needs from a driver (implemented by subclassing :class:`BaseDriver`)."""

    name: ClassVar[str]
    title: ClassVar[str]
    capabilities: ClassVar[frozenset[Capability]]
    transport: Transport

    def info(self) -> RouterInfo: ...
    def status(self) -> Status: ...
    def devices(self) -> list[Device]: ...
    def leases(self) -> list[Lease]: ...
    def reservations(self) -> list[Reservation]: ...


class BaseDriver:
    """Defaults that raise a diagnosed "unsupported" error; drivers override what they can."""

    name: ClassVar[str] = ""
    title: ClassVar[str] = ""
    vendor: ClassVar[str] = ""
    capabilities: ClassVar[frozenset[Capability]] = frozenset()
    areas: ClassVar[dict[str, str]] = {}
    lists: ClassVar[dict[str, str]] = {}
    notes: ClassVar[list[str]] = []
    reservation_names: ClassVar[bool] = False  # can a static lease carry a name?

    def __init__(self, transport: Transport, credentials: CredentialSource | None = None) -> None:
        self.transport = transport
        self.credentials = credentials

    @property
    def host(self) -> str:
        """The base URL (``http://192.168.0.1``) requests go to."""
        return self.transport.base_url

    @property
    def bare_host(self) -> str:
        """The host as the user types it and credentials.json keys it (``192.168.0.1``)."""
        return self.transport.base_url.split("://", 1)[-1].rstrip("/")

    def supports(self, capability: Capability) -> bool:
        return capability in self.capabilities

    def require(self, capability: Capability, feature: str | None = None) -> None:
        if capability not in self.capabilities:
            raise unsupported(self.name, feature or capability.value)

    # ── detection / session ──────────────────────────────────────────────────
    @classmethod
    def probe(cls, transport: Transport) -> str | None:
        """Return a model string if the host looks like this family, else None. GET-only."""
        return None

    def login(self, user: str, password: str) -> None:
        raise unsupported(self.name, "login")

    def session_active(self) -> bool:
        return True

    def end_session(self) -> bool:
        """End an admin session THIS driver opened (no-op if it never logged in).

        Called by the CLI after every command unless ``--keep-session``. Returns whether a
        logout was sent. Best effort: a failure here never fails the command.
        """
        return False

    def list_is_mac(self, name: str) -> bool:
        """Whether the named list holds MAC addresses (so values take device selectors)."""
        return False

    # ── reads ────────────────────────────────────────────────────────────────
    def info(self) -> RouterInfo:
        return RouterInfo(driver=self.name, host=self.bare_host)

    def status(self) -> Status:
        raise unsupported(self.name, "status")

    def devices(self) -> list[Device]:
        raise unsupported(self.name, "devices")

    def leases(self) -> list[Lease]:
        raise unsupported(self.name, "leases")

    def reservations(self) -> list[Reservation]:
        raise unsupported(self.name, "static leases")

    def port_forwards(self) -> list[PortForward]:
        raise unsupported(self.name, "port forwarding")

    def area_keys(self, area: str) -> list[SettingSpec]:
        raise unsupported(self.name, f"the {area!r} settings")

    def read_area(self, area: str, show_secrets: bool = False) -> dict[str, Any]:
        raise unsupported(self.name, f"the {area!r} settings")

    def list_items(self, name: str) -> list[str]:
        raise unsupported(self.name, f"the {name!r} list")

    def raw_get(self, path: str) -> str:
        raise unsupported(self.name, "raw page access")

    def raw_pages(self) -> dict[str, str]:
        return {}

    # ── write plans ──────────────────────────────────────────────────────────
    def plan_reserve(self, mac: str, ip: str, name: str | None) -> WritePlan:
        raise unsupported(self.name, "static leases")

    def plan_unreserve(self, mac: str) -> WritePlan:
        raise unsupported(self.name, "static leases")

    def plan_area(self, area: str, changes: dict[str, str]) -> WritePlan:
        raise unsupported(self.name, f"changing the {area!r} settings")

    def plan_list_edit(self, name: str, action: str, value: str | None) -> WritePlan:
        raise unsupported(self.name, f"editing the {name!r} list")

    def plan_port_forward_add(self, rule: PortForward) -> WritePlan:
        raise unsupported(self.name, "adding port forwards")

    def plan_port_forward_remove(self, index: int | None) -> WritePlan:
        raise unsupported(self.name, "removing port forwards")

    def plan_password(self, user: str, old: str, new: str) -> WritePlan:
        raise unsupported(self.name, "changing the admin password")

    def plan_reboot(self) -> WritePlan:
        raise unsupported(self.name, "reboot")

    def plan_raw_form(
        self, page: str, form: str | None, changes: dict[str, str], clicked: str | None
    ) -> WritePlan:
        raise unsupported(self.name, "raw form posts")
