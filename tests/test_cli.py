"""The dispatcher and end-to-end command runs against the fixture router (no network)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from helpers import FIXTURES, UbeeFake, creds

from router_cli import __version__, cli
from router_cli.commands import _common
from router_cli.drivers.ubee_evw32c import UbeeEVW32C


@pytest.fixture
def fake_router(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> UbeeFake:
    fake = UbeeFake()
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("ROUTER_CLI_DB", str(tmp_path / "inv.sqlite3"))
    monkeypatch.setattr(_common, "open_driver", lambda args: UbeeEVW32C(fake, creds()))
    return fake


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str]:
    code = cli.main(list(argv))
    return code, capsys.readouterr().out


def test_help_version_unknown(capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "--help")
    assert code == 0 and "reserve" in out and "inventory" in out
    code, out = run(capsys, "--version")
    assert out.strip() == f"router {__version__}"
    assert cli.main(["reserv"]) == 4


def test_every_command_has_help(capsys: pytest.CaptureFixture[str]) -> None:
    for name in cli._discover():
        try:
            code: object = cli.main([name, "--help"])
        except SystemExit as exc:
            code = exc.code
        assert code == 0, name
    capsys.readouterr()


def test_drivers_json(capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "drivers", "--json")
    data = json.loads(out)
    assert code == 0 and set(data) == {"ubee_evw32c", "openwrt"}
    assert "ubee" in data["ubee_evw32c"]["aliases"]


def test_reserve_dry_run_json(fake_router: UbeeFake, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(
        capsys,
        "reserve",
        "02:00:00:00:00:01",
        "192.168.0.250",
        "--name",
        "test",
        "--dry-run",
        "--json",
    )
    data = json.loads(out)
    assert code == 0 and data["dry_run"] is True and data["executed"] is False
    (req,) = data["requests"]
    assert req["url"] == "http://192.168.0.1/goform/UbeeLanStaticLease"
    assert ["IpAddStaticLease8IPX", "192.168.0.250"] in req["fields"]
    assert not [r for r in fake_router.sent if r.kind == "write"]


def test_destructive_write_needs_yes(
    fake_router: UbeeFake, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli.main(["reboot"])
    assert code == 3
    assert not [r for r in fake_router.sent if r.kind == "write"]
    capsys.readouterr()


def test_read_commands_json(fake_router: UbeeFake, capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (
        ["status"],
        ["devices"],
        ["leases"],
        ["dhcp"],
        ["wifi"],
        ["wifi", "--band", "5g"],
        ["wifi-acl"],
        ["wps"],
        ["port-forward", "list"],
        ["firewall"],
        ["filter", "port"],
        ["filter", "mac"],
        ["lists", "show", "keywords"],
        ["settings", "show", "parental-users"],
        ["telephony"],
        ["cm"],
        ["raw", "form", "UbeeLanDhcp.asp"],
    ):
        code, out = run(capsys, *argv, "--json")
        assert code == 0, argv
        json.loads(out)
    code, out = run(capsys, "wifi", "--json")
    assert "testtesttest" not in out


def test_inventory_update_and_list(
    fake_router: UbeeFake, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out = run(capsys, "inventory", "update", "--json")
    summary = json.loads(out)
    assert code == 0 and summary["seen"] == 20 and summary["reservations"] == 7
    code, out = run(capsys, "inventory", "list", "--json", "--filter", "all")
    data: dict[str, Any] = json.loads(out)
    assert set(data) == {"generated_at", "last_poll", "router", "devices"}
    assert data["router"] == {"driver": "ubee_evw32c", "model": "EVW32C-0N", "host": "192.168.0.1"}
    assert re.match(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00$", data["generated_at"])
    assert len(data["devices"]) == 24  # 20 seen + 4 reservation-only
    code, out = run(
        capsys, "alias", "02:00:00:00:01:01", "--name", "Server", "--icon", "mdi:server", "--json"
    )
    assert json.loads(out)["hostname"] == "Server"


def test_raw_get_masks_secrets(fake_router: UbeeFake, capsys: pytest.CaptureFixture[str]) -> None:
    _, out = run(capsys, "raw", "get", "UbeeParentalBasic.asp")
    assert "changeme" not in out and "<redacted>" in out
    _, out = run(capsys, "raw", "get", "UbeeWlanSecurity.asp")
    assert "testtesttest" not in out
    _, out = run(capsys, "raw", "get", "UbeeNasControl.asp")
    assert "fixture-nas-pass" not in out


def test_fixtures_are_synthetic() -> None:
    """Guard: fixtures may only carry synthetic MACs and documentation/private addresses."""
    mac_re = re.compile(r"(?<![0-9A-Fa-f:])([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})(?![0-9A-Fa-f:])")
    ip_re = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])")
    allowed_ip = re.compile(r"^(192\.168\.0\.|192\.0\.2\.|198\.51\.100\.|10\.|0\.0\.0\.0$|255\.)")
    for path in FIXTURES.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for mac in mac_re.findall(text):
            assert mac.lower().startswith("02:00:00") or mac == "00:00:00:00:00:00", (path, mac)
        for ip in ip_re.findall(text):
            assert allowed_ip.match(ip), (path, ip)
