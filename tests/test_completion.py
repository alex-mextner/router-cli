"""Shell completion: the engine, the introspection of every command, the scripts."""

from __future__ import annotations

from pathlib import Path

import pytest

from router_cli import cli, completion
from router_cli.http import HttpTransport
from router_cli.inventory import FILTERS, Inventory
from router_cli.models import Device, RouterInfo

DEVICES = ["printer", "tv", "02:00:00:00:00:01", "192.168.0.220"]


def devices() -> list[str]:
    return list(DEVICES)


def c(*words: str, cur: str = "") -> list[str]:
    return completion.complete(["router", *words], cur, devices=devices)


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(self: HttpTransport, request: object) -> str:
        raise AssertionError("completion must never talk to a router")

    monkeypatch.setattr(HttpTransport, "_do", refuse)


def test_commands_verbs_flags_choices() -> None:
    assert c(cur="res") == ["reserve"]
    assert "completion" in c() and "inventory" in c()
    assert set(c("inventory")) >= {"update", "list"}
    assert c("inventory", "list", cur="--fi") == ["--filter"]
    assert c("inventory", "list", "--filter") == list(FILTERS)
    assert c("inventory", "list", cur="--filter=a") == ["--filter=active", "--filter=all"]
    assert "--keep-session" in c("status", cur="--")
    assert "--dry-run" in c("reserve", "printer", cur="--d")
    assert c("completion") == ["bash", "zsh", "fish", "devices"]


def test_device_slots() -> None:
    assert c("reserve") == DEVICES
    assert c("reserve", cur="pr") == ["printer"]
    assert c("reserve", cur="PR") == ["printer"]  # case-insensitive fallback
    assert c("reserve", "printer") == []  # the IP slot is free text
    assert c("unreserve", cur="02:") == ["02:00:00:00:00:01"]
    assert c("alias", "--name", "x") == DEVICES
    assert c("scan", "--ip", cur="19") == ["192.168.0.220"]
    assert c("filter") == ["ip", "mac", "port"]
    assert c("filter", "mac", "add") == DEVICES
    assert c("filter", "mac", "rm", cur="t") == ["tv"]
    assert set(c("wifi-acl")) >= {"show", "set", "add", "rm", "clear"}
    assert c("wifi-acl", "add", "--band") == ["2g", "5g", "all"]
    assert c("wifi-acl", "rm") == DEVICES
    assert c("oui") == DEVICES


def test_every_command_introspects_offline() -> None:
    tree = completion.root()
    for name in cli._discover():
        node = tree.verb(name)
        assert node is not None, name
        assert node.flags or node.verbs, name


def test_line_splitting_and_bash_colons() -> None:
    assert completion.split_line("router res") == (["router"], "res")
    assert completion.split_line("router reserve ") == (["router", "reserve"], "")
    assert completion.split_line("router alias 'Kitchen Ph") == (["router", "alias"], "Kitchen Ph")
    assert completion.split_line("router alias Kitchen\\ Ph") == (["router", "alias"], "Kitchen Ph")
    assert completion.for_bash(["02:00:00:00:00:01"], "02:00:") == ["00:00:00:01"]
    assert completion.for_bash(["--filter=all"], "--filter=a") == ["all"]
    assert completion.for_bash(["Kitchen Phone"], "Kit") == ["Kitchen\\ Phone"]


def test_device_candidates_from_the_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROUTER_CLI_DB", str(tmp_path / "none.sqlite3"))
    assert completion.device_candidates() == []  # no DB: nothing, and no DB is created
    assert not (tmp_path / "none.sqlite3").exists()
    path = tmp_path / "inv.sqlite3"
    monkeypatch.setenv("ROUTER_CLI_DB", str(path))
    with Inventory(path) as inv:
        inv.record_poll(
            RouterInfo(driver="ubee_evw32c", host="192.168.0.1"),
            [Device(mac="02:00:00:00:00:01", ip="192.168.0.220", hostname="printer")],
            None,
        )
    assert completion.device_candidates() == ["printer", "02:00:00:00:00:01", "192.168.0.220"]


def test_scripts_and_complete_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ROUTER_CLI_DB", str(tmp_path / "none.sqlite3"))
    for shell, marker in (
        ("bash", "complete -F _router_complete router"),
        ("zsh", "#compdef router"),
        ("fish", "complete -c router"),
    ):
        assert cli.main(["completion", shell]) == 0
        assert marker in capsys.readouterr().out
    assert cli.main(["completion", "complete", "--shell", "bash", "--line", "router inv"]) == 0
    assert capsys.readouterr().out.split() == ["inventory"]
    code = cli.main(
        ["completion", "complete", "--shell", "zsh", "--cur=up", "--", "router", "inventory"]
    )
    assert code == 0 and capsys.readouterr().out.split() == ["update"]
    code = cli.main(
        ["completion", "complete", "--shell", "fish", "--", "router", "inventory", "list"]
    )
    assert code == 0 and "--filter" not in capsys.readouterr().out  # no cur: positionals only
