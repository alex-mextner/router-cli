"""Device selectors: MAC in any format, current IP, or a (prefix of a) name — DB only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import UbeeFake, creds

from router_cli import cli, device_selector
from router_cli._errors import MissingTargetError, UsageError
from router_cli.commands import _common
from router_cli.drivers.ubee_evw32c import UbeeEVW32C
from router_cli.inventory import Inventory
from router_cli.models import Device, RouterInfo, normalize_mac

INFO = RouterInfo(driver="ubee_evw32c", host="192.168.0.1", model="EVW32C-0N")
PRINTER = "02:00:00:00:00:01"
TV = "02:00:00:00:00:02"
TV_BOX = "02:00:00:00:00:03"
PHONE_A = "02:00:00:00:00:04"
PHONE_B = "02:00:00:00:00:05"


@pytest.fixture
def db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "inv.sqlite3"
    monkeypatch.setenv("ROUTER_CLI_DB", str(path))
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    with Inventory(path) as inv:
        inv.record_poll(
            INFO,
            [
                Device(mac=PRINTER, ip="192.168.0.220", hostname="Printer-3D"),
                Device(mac=TV, ip="192.168.0.221", hostname="tv"),
                Device(mac=TV_BOX, ip="192.168.0.222", hostname="TV-Box"),
                Device(mac=PHONE_A, ip="192.168.0.223", hostname="android-phone"),
                Device(mac=PHONE_B, ip="192.168.0.224", hostname="android-tablet"),
            ],
            None,
        )
        inv.set_alias(PHONE_A, name="Kitchen Phone")
    return path


@pytest.mark.parametrize(
    "text",
    [
        "02:00:00:00:00:aa",
        "02-00-00-00-00-AA",
        "02_00_00_00_00_aa",
        "0200.0000.00aa",
        "0200000000AA",
        "02:00-00_00.00:Aa",
        " 02:00:00:00:00:aa ",
    ],
)
def test_mac_formats(text: str) -> None:
    assert normalize_mac(text) == "02:00:00:00:00:aa"
    # a MAC needs no database at all
    assert device_selector.resolve_mac(text, inv=None) == "02:00:00:00:00:aa"


def test_by_ip_and_name(db: Path) -> None:
    with Inventory(db) as inv:
        assert device_selector.resolve_mac("192.168.0.220", inv) == PRINTER
        assert device_selector.resolve_mac("printer-3d", inv) == PRINTER  # case-insensitive
        assert device_selector.resolve_mac("PRINT", inv) == PRINTER  # unique prefix
        assert device_selector.resolve_mac("tv", inv) == TV  # exact beats prefix of TV-Box
        assert device_selector.resolve_mac("tv-b", inv) == TV_BOX
        assert device_selector.resolve_mac("kitchen", inv) == PHONE_A  # the alias
        assert device_selector.resolve_mac("android-phone", inv) == PHONE_A  # router name too
        assert device_selector.resolve_target("print", inv) == ("192.168.0.220", PRINTER)
        assert device_selector.resolve_target("192.168.0.221", inv) == ("192.168.0.221", TV)


def test_ambiguous_lists_candidates(db: Path) -> None:
    with Inventory(db) as inv, pytest.raises(UsageError) as err:
        device_selector.resolve_mac("android", inv)
    assert "2 devices" in err.value.what
    assert PHONE_A in err.value.why and PHONE_B in err.value.why


def test_unknown(db: Path) -> None:
    with Inventory(db) as inv:
        with pytest.raises(MissingTargetError, match="no device matches"):
            device_selector.resolve_mac("fridge", inv)
        with pytest.raises(MissingTargetError, match="no device at"):
            device_selector.resolve_mac("192.168.0.199", inv)
        with pytest.raises(UsageError):
            device_selector.resolve_mac("  ", inv)


# ── through the commands ─────────────────────────────────────────────────────
@pytest.fixture
def fake(db: Path, monkeypatch: pytest.MonkeyPatch) -> UbeeFake:
    router = UbeeFake()
    monkeypatch.setattr(
        _common, "open_driver", lambda args: _common.track(UbeeEVW32C(router, creds()), args)
    )
    return router


def _json(capsys: pytest.CaptureFixture[str], *argv: str) -> dict[str, object]:
    assert cli.main(list(argv)) == 0
    return json.loads(capsys.readouterr().out)  # type: ignore[no-any-return]


def _fields(data: dict[str, object]) -> dict[str, str]:
    (req,) = data["requests"]  # type: ignore[misc]
    return {k: v for k, v in req["fields"]}


def test_reserve_by_name_pins_current_ip(
    fake: UbeeFake, capsys: pytest.CaptureFixture[str]
) -> None:
    data = _json(capsys, "reserve", "print", "--dry-run", "--json")
    values = set(_fields(data).values())
    assert "192.168.0.220" in values
    assert not [r for r in fake.sent if r.kind == "write"]


def test_reserve_by_ip_alone(fake: UbeeFake, capsys: pytest.CaptureFixture[str]) -> None:
    data = _json(capsys, "reserve", "192.168.0.221", "--dry-run", "--json")
    assert "192.168.0.221" in set(_fields(data).values())


def test_reserve_unknown_ip_needs_one(fake: UbeeFake, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["reserve", "02:00:00:00:00:99", "--dry-run"]) == 5
    assert "no current IP" in capsys.readouterr().err


def test_alias_and_lists_take_selectors(
    fake: UbeeFake, db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["alias", "TV-B", "--name", "Living room box"]) == 0
    capsys.readouterr()
    with Inventory(db) as inv:
        assert device_selector.resolve_mac("living", inv) == TV_BOX
    data = _json(capsys, "filter", "mac", "add", "living", "--dry-run", "--json")
    assert _fields(data)["NewMacFilter"] == TV_BOX.upper()
    data = _json(
        capsys, "wifi-acl", "add", "02_00_00_00_00_01", "--band", "5g", "--dry-run", "--json"
    )
    assert PRINTER.upper() in _fields(data).values()
