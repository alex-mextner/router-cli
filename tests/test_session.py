"""Session hygiene: close the (LAN-global) Ubee admin session router-cli had to open."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest
from helpers import UbeeFake, creds

from router_cli import cli
from router_cli._errors import RouterCliError, SafetyError
from router_cli.commands import _common
from router_cli.commands.inventory import poll_lock
from router_cli.drivers.ubee_evw32c import UbeeEVW32C
from router_cli.http import HttpRequest, HttpTransport, check_path


def logouts(fake: UbeeFake) -> list[HttpRequest]:
    return [r for r in fake.sent if r.kind == "logout"]


def test_logs_out_only_what_it_opened() -> None:
    fake = UbeeFake(logged_in=False)
    driver = UbeeEVW32C(fake, creds())
    driver.devices()  # had to log in
    assert driver.end_session() is True
    (req,) = logouts(fake)
    assert (req.method, req.path) == ("GET", "/logout.asp")
    assert fake.logged_in is False
    assert driver.end_session() is False  # nothing left to close

    someone_elses = UbeeFake(logged_in=True)
    driver = UbeeEVW32C(someone_elses, creds())
    driver.devices()  # read through the open session: no login
    assert driver.end_session() is False
    assert not logouts(someone_elses) and someone_elses.logged_in


def test_a_rejected_login_opens_nothing() -> None:
    fake = UbeeFake(logged_in=False, password="other")
    driver = UbeeEVW32C(fake, creds())
    with pytest.raises(RouterCliError):
        driver.devices()
    assert driver.end_session() is False and not logouts(fake)


def test_path_guard_lets_only_a_logout_request_through() -> None:
    check_path("/logout.asp", allow_logout=True)
    with pytest.raises(SafetyError):
        check_path("/logout.asp")
    with pytest.raises(SafetyError):
        check_path("/RgFactoryReset.asp", allow_logout=True)
    transport = HttpTransport("http://192.0.2.1")
    with pytest.raises(SafetyError):
        transport.send(HttpRequest("GET", "/logout.asp", kind="read"))
    with pytest.raises(SafetyError):
        transport.send(HttpRequest("GET", "/reboot.asp", kind="logout"))


@pytest.fixture
def logged_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> UbeeFake:
    fake = UbeeFake(logged_in=False)
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("ROUTER_CLI_DB", str(tmp_path / "inv.sqlite3"))
    monkeypatch.delenv("ROUTER_CLI_KEEP_SESSION", raising=False)
    monkeypatch.setattr(
        _common, "open_driver", lambda args: _common.track(UbeeEVW32C(fake, creds()), args)
    )
    return fake


def test_every_command_logs_out_afterwards(
    logged_out: UbeeFake, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["devices", "--json"]) == 0
    assert len(logouts(logged_out)) == 1
    assert cli.main(["inventory", "update", "--json"]) == 0
    assert len(logouts(logged_out)) == 2
    # even when the command fails after logging in
    assert cli.main(["reserve", "02:00:00:00:00:01", "10.9.9.9", "--dry-run"]) != 0
    assert len(logouts(logged_out)) == 3
    capsys.readouterr()


def test_keep_session(
    logged_out: UbeeFake, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["devices", "--keep-session"]) == 0
    assert not logouts(logged_out) and logged_out.logged_in
    logged_out.logged_in = False
    monkeypatch.setenv("ROUTER_CLI_KEEP_SESSION", "1")
    assert cli.main(["status"]) == 0
    assert not logouts(logged_out)
    capsys.readouterr()


def test_inventory_list_reports_last_poll(
    logged_out: UbeeFake, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["inventory", "list", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["last_poll"] is None
    assert cli.main(["inventory", "update", "--json"]) == 0
    at = json.loads(capsys.readouterr().out)["at"]
    assert cli.main(["inventory", "list", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["last_poll"] == at


def test_poll_lock_serializes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROUTER_CLI_DB", str(tmp_path / "inv.sqlite3"))
    held = threading.Event()
    release = threading.Event()

    def holder() -> None:
        with poll_lock() as first:
            assert first
            held.set()
            release.wait(5)

    thread = threading.Thread(target=holder)
    thread.start()
    held.wait(5)
    with pytest.raises(RouterCliError, match="still running"), poll_lock(wait=0.3):
        pass
    threading.Timer(0.3, release.set).start()
    started = time.monotonic()
    with poll_lock(wait=5) as first:
        assert first is False  # waited for the other poll and reuses its result
    assert time.monotonic() - started >= 0.2
    thread.join()
    with poll_lock() as first:
        assert first is True
