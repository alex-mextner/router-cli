"""The guard rails: path denylist, the write gate, dry-run recording, credential file rules."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from router_cli import credentials
from router_cli._errors import SafetyError, UsageError
from router_cli.http import DryRunTransport, HttpRequest, HttpTransport, check_path


@pytest.mark.parametrize(
    "path",
    [
        "/logout.asp",
        "/UbeeManagementBackup.asp",
        "/cgi-bin/reboot",
        "/RgFactoryReset.asp",
        "/restoreDefaults.asp",
        "/UbeeUpgrade.asp?x=1",
    ],
)
def test_dangerous_paths_are_refused(path: str) -> None:
    with pytest.raises(SafetyError):
        check_path(path)


def test_safe_paths_pass() -> None:
    for path in ("/UbeeSysInfo.asp", "/RootDevice.xml", "/ubus", "/"):
        check_path(path)


def test_writes_need_an_explicitly_opened_transport() -> None:
    transport = HttpTransport("http://192.0.2.1")
    with pytest.raises(SafetyError):
        transport.send(
            HttpRequest("POST", "/goform/UbeeLanDhcp", kind="write", fields=(("a", "1"),))
        )
    with pytest.raises(SafetyError):
        transport.get("/logout.asp")


def test_dry_run_records_writes_and_passes_reads() -> None:
    class Inner:
        base_url = "http://192.0.2.1"

        def __init__(self) -> None:
            self.seen: list[str] = []

        def get(self, path: str) -> str:
            self.seen.append(path)
            return "page"

        def send(self, request: HttpRequest) -> str:
            self.seen.append("SEND " + request.path)
            return "ok"

    inner = Inner()
    dry = DryRunTransport(inner)
    assert dry.get("/x.asp") == "page"
    assert dry.send(HttpRequest("POST", "/goform/x", kind="write")) == ""
    assert dry.send(HttpRequest("POST", "/goform/login", kind="login")) == "ok"
    assert [r.path for r in dry.recorded] == ["/goform/x"]
    assert inner.seen == ["/x.asp", "SEND /goform/login"]


def test_session_token_is_redacted_in_display() -> None:
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call",
        "params": [
            "0123456789abcdef0123456789abcdef",
            "luci",
            "setPassword",
            {"username": "root", "password": "p"},
        ],
    }
    req = HttpRequest(
        "POST", "/ubus", kind="write", json_body=body, secret_fields=frozenset({"password"})
    )
    shown = req.shown_body(show_secrets=False)
    assert "<session>" in shown and "0123456789abcdef" not in shown and '"p"' not in shown
    assert "0123456789abcdef" in req.body().decode()  # the real request is untouched


@pytest.fixture
def config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("ROUTER_CLI_CONFIG_DIR", str(tmp_path / "cfg"))
    return tmp_path / "cfg"


def test_store_creates_private_file(config_dir: Path) -> None:
    where, path = credentials.store("http://192.168.0.1/", "ubee_evw32c", "admin", "pw-1")
    assert where == "file"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(config_dir.stat().st_mode) == 0o700
    data = credentials.load_file()
    assert data == {
        "routers": {
            "192.168.0.1": {"driver": "ubee_evw32c", "username": "admin", "password": "pw-1"}
        },
        "default": "192.168.0.1",
    }
    assert credentials.default_host() == "192.168.0.1"
    assert credentials.password_for("http://192.168.0.1", "ubee_evw32c", "admin") == "pw-1"
    assert credentials.password_for("192.168.0.1", "ubee_evw32c", "someone-else") is None
    assert credentials.remove("192.168.0.1") == ["file"]
    assert credentials.load_file()["routers"] == {}


def test_hand_written_file_is_read(config_dir: Path) -> None:
    config_dir.mkdir(mode=0o700)
    path = config_dir / "credentials.json"
    path.write_text(
        '{"routers": {"192.168.0.1": '
        '{"driver": "ubee_evw32c", "username": "admin", "password": "x"}},'
        ' "default": "192.168.0.1"}'
    )
    os.chmod(path, 0o600)
    entry = credentials.entry("192.168.0.1")
    assert entry is not None and entry.driver == "ubee_evw32c" and entry.password == "x"


def test_group_readable_file_is_refused(config_dir: Path) -> None:
    credentials.store("192.168.0.1", "ubee_evw32c", "admin", "pw")
    os.chmod(credentials.path(), 0o644)
    with pytest.raises(UsageError, match="readable by other users"):
        credentials.load_file()


def test_file_password_beats_keyring(config_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    credentials.store("192.168.0.1", "ubee_evw32c", "admin", "from-file")
    monkeypatch.setattr(credentials, "keyring_get", lambda key: "from-keyring")
    assert credentials.password_for("192.168.0.1", "ubee_evw32c", "admin") == "from-file"
    data = credentials.load_file()
    del data["routers"]["192.168.0.1"]["password"]
    credentials.save_file(data)
    assert credentials.password_for("192.168.0.1", "ubee_evw32c", "admin") == "from-keyring"
