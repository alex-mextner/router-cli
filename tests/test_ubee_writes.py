"""Ubee EVW32C write plans: the exact requests, built from the page, never sent here."""

from __future__ import annotations

import urllib.parse

import pytest
from helpers import UbeeFake, creds

from router_cli._errors import MissingTargetError, UsageError
from router_cli.drivers import ubee_areas as A
from router_cli.drivers.base import execute
from router_cli.drivers.ubee_evw32c import UbeeEVW32C
from router_cli.http import HttpRequest, render_requests
from router_cli.models import PortForward


def driver(fake: UbeeFake | None = None) -> UbeeEVW32C:
    return UbeeEVW32C(fake or UbeeFake(), creds())


def only_request(plan_requests: list[HttpRequest]) -> HttpRequest:
    assert len(plan_requests) == 1
    return plan_requests[0]


def test_reserve_fills_the_first_free_slot() -> None:
    fake = UbeeFake()
    plan = driver(fake).plan_reserve("02:00:00:00:00:01", "192.168.0.250", "test")
    req = only_request(plan.requests)
    assert (req.method, req.path, req.kind) == ("POST", "/goform/UbeeLanStaticLease", "write")
    fields = list(req.fields)
    assert len(fields) == 59
    slot8 = [
        (k, v)
        for k, v in fields
        if k.startswith("MacAddStaticLease08") or k == "IpAddStaticLease8IPX"
    ]
    assert slot8 == [
        ("MacAddStaticLease08MA0", "02"),
        ("MacAddStaticLease08MA1", "00"),
        ("MacAddStaticLease08MA2", "00"),
        ("MacAddStaticLease08MA3", "00"),
        ("MacAddStaticLease08MA4", "00"),
        ("MacAddStaticLease08MA5", "01"),
        ("IpAddStaticLease8IPX", "192.168.0.250"),
    ]
    assert fields[-3:] == [
        ("MY_POOL_START_IP", "192.168.0.10"),
        ("MY_POOL_END_IP", "192.168.0.254"),
        ("StaticLeaseStatusFlag", "0"),
    ]
    # untouched slots are resent exactly as rendered
    assert ("IpAddStaticLease1IPX", "192.168.0.39") in fields
    assert not plan.destructive
    assert any("local alias" in n for n in plan.notes)
    assert fake.sent == []  # planning sends nothing
    body = req.body().decode()
    assert body.endswith(
        "MY_POOL_START_IP=192.168.0.10&MY_POOL_END_IP=192.168.0.254&StaticLeaseStatusFlag=0"
    )
    assert urllib.parse.parse_qsl(body) == fields


def test_reserve_updates_an_existing_mac_and_is_idempotent() -> None:
    d = driver()
    same = d.plan_reserve("02:00:00:00:01:01", "192.168.0.39", None)
    assert same.steps == [] and "nothing to do" in same.summary
    moved = d.plan_reserve("02:00:00:00:01:01", "192.168.0.240", None)
    fields = dict(only_request(moved.requests).fields)
    assert fields["IpAddStaticLease1IPX"] == "192.168.0.240"
    assert fields["IpAddStaticLease8IPX"] == "0.0.0.0"


@pytest.mark.parametrize("ip", ["192.168.0.10", "192.168.1.50", "192.168.0.255", "10.0.0.5"])
def test_reserve_respects_the_pages_range_check(ip: str) -> None:
    with pytest.raises(UsageError):
        driver().plan_reserve("02:00:00:00:00:09", ip, None)


def test_reserve_refuses_a_taken_ip_and_full_table() -> None:
    d = driver()
    with pytest.raises(UsageError, match="already reserved"):
        d.plan_reserve("02:00:00:00:00:09", "192.168.0.39", None)
    fake = UbeeFake()
    full = UbeeEVW32C(fake, creds())
    page = fake.get("/UbeeLanStaticLease.asp").replace("value=0.0.0.0", "value=192.168.0.99")
    page = page.replace(
        'MacAddStaticLease08MA5" size="1" maxlength="2" value=00',
        'MacAddStaticLease08MA5" size="1" maxlength="2" value=99',
    )
    fake.overrides["UbeeLanStaticLease.asp"] = page
    with pytest.raises(UsageError, match="slots are in use"):
        full.plan_reserve("02:00:00:00:00:09", "192.168.0.200", None)


def test_unreserve_mimics_the_clear_checkbox() -> None:
    plan = driver().plan_unreserve("02:00:00:00:01:03")
    fields = dict(only_request(plan.requests).fields)
    assert [fields[f"MacAddStaticLease03MA{i}"] for i in range(6)] == ["00"] * 6
    assert fields["IpAddStaticLease3IPX"] == "0"  # literally "0", as the page's JavaScript sets it
    with pytest.raises(MissingTargetError):
        driver().plan_unreserve("02:00:00:00:00:77")


def test_dhcp_set() -> None:
    plan = driver().plan_area("dhcp", {"lease_time": "7200", "start": "100"})
    fields = dict(only_request(plan.requests).fields)
    assert fields["LeaseTime"] == "7200" and fields["DhcpIpStart3"] == "100"
    assert fields["ApplyAction"] == "1" and fields["DhcpServerEnable"] == "0x1000"
    assert "DhcpIpStart0" not in fields
    off = driver().plan_area("dhcp", {"enabled": "no"})
    fields = dict(only_request(off.requests).fields)
    assert "DhcpServerEnable" not in fields and fields["DhcpServerDisable"] == "0x1000"
    assert off.destructive
    with pytest.raises(UsageError):
        driver().plan_area("dhcp", {"lease_time": "abc"})


def test_wifi_basic_and_security() -> None:
    plan = driver().plan_area("wifi-5g", {"channel": "44", "psk": "a-new-passphrase"})
    assert plan.destructive
    form_req, json_req = plan.requests
    fields = dict(form_req.fields)
    assert form_req.path == "/goform/UbeeWlanBasic"
    assert fields["ChannelNumber5G"] == "44"
    assert fields["commitwlanRadio5G"] == "1" and fields["restoreWirelessDefaults5G"] == "0"
    assert fields["ID_BUTTON_APPLY"] == "Apply"
    assert "ServiceSetIdentifier" not in fields  # only the 5 GHz form
    assert json_req.path == "/goform/ubee_post"
    assert json_req.json_body == {
        "wireless_5g_auth_mode": 4,
        "wireless_5g_sec_encrypt_type": 4,
        "wireless_5g_sec_wpap_preshare_key": "a-new-passphrase",
    }
    shown = render_requests(plan.requests, "http://192.168.0.1", show_secrets=False)
    assert "a-new-passphrase" not in shown and "<redacted>" in shown


def test_wifi_security_json_modes() -> None:
    state = {
        "wireless_2g_auth_mode": 4,
        "wireless_2g_sec_encrypt_type": 4,
        "wireless_2g_sec_wpap_preshare_key": "x" * 10,
    }
    assert A.wifi_security_json(state, "2g", {"security": "none"}) == {
        "wireless_2g_auth_mode": 0,
        "wireless_2g_sec_encrypt_type": 0,
    }
    body = A.wifi_security_json(state, "2g", {"wpa_version": "wpa2", "encryption": "aes"})
    assert body["wireless_2g_auth_mode"] == 3 and body["wireless_2g_sec_encrypt_type"] == 3
    ent = A.wifi_security_json(
        state, "2g", {"security": "wpa-enterprise", "radius_ip": "192.0.2.5", "radius_secret": "s"}
    )
    assert ent["wireless_2g_auth_mode"] == 7 and ent["wireless_2g_sec_wpae_radius_port"] == 1812
    with pytest.raises(UsageError):
        A.wifi_security_json(state, "2g", {"psk": "short"})
    with pytest.raises(UsageError):
        A.wifi_security_json(state, "2g", {"security": "wep-64"})


def test_wps_json_quirks() -> None:
    assert A.wps_json("enable", "2g", enabled=True) == {
        "wireless_2g_wps_enable": "1",
        "wireless_5g_wps_enable": "1",
    }
    assert A.wps_json("connect", "2g", mode="pbc") == {"wireless_2g_wps_trigger": 1}
    assert A.wps_json("connect", "5g", mode="pin") == {
        "wireless_5g_wps_trigger": 1,
        "wireless_5g_wps_mode": "1",
    }
    assert A.wps_json("mode", "5g", mode="pin", pin="12345670") == {
        "wireless_5g_wps_mode": "1",
        "wireless_5g_wps_pin": "12345670",
    }


def test_dmz_by_address() -> None:
    plan = driver().plan_area("dmz", {"host": "192.168.0.50"})
    fields = dict(only_request(plan.requests).fields)
    assert fields == {"AdvDmzHostIP3": "50", "ApplyAdvDMZAction": "1"}
    with pytest.raises(UsageError):
        driver().plan_area("dmz", {"host": "10.0.0.50"})


def test_firewall_checkboxes() -> None:
    plan = driver().plan_area("firewall", {"level": "high", "port_scan_detection": "yes"})
    fields = dict(only_request(plan.requests).fields)
    assert fields == {"AdvFirewall": "3", "AdvPortScanDetection": "0x4000"}


def test_list_edits() -> None:
    add = driver().plan_list_edit("mac-filter", "add", "02:00:00:00:00:aa")
    fields = dict(only_request(add.requests).fields)
    assert fields["NewMacFilter"] == "02:00:00:00:00:AA" and fields["MacFilterAction"] == "1"
    assert "MacFilterList" not in fields  # the empty list box submits nothing
    rm = driver().plan_list_edit("keywords", "remove", "anonymizer")
    fields = dict(only_request(rm.requests).fields)
    assert fields["KeywordList"] == "1" and fields["KeywordAction"] == "2"
    with pytest.raises(MissingTargetError):
        driver().plan_list_edit("keywords", "remove", "nothing-here")
    acl = driver().plan_list_edit("wifi-acl-5g", "add", "02:00:00:00:00:bb")
    fields = dict(only_request(acl.requests).fields)
    assert fields["WirelessMac5G01"] == "02:00:00:00:00:BB" and fields["commitwlanAccess5G"] == "1"


def test_port_forward_remove_and_add() -> None:
    rm = driver().plan_port_forward_remove(0)
    assert dict(only_request(rm.requests).fields) == {
        "PortForwardingCreateRemove": "3",
        "PortForwardingTable": "0",
    }
    assert rm.destructive
    with pytest.raises(MissingTargetError):
        driver().plan_port_forward_remove(5)
    rule = PortForward(-1, "192.168.0.60", 443, 443, None, 8443, 8443, "tcp", "web", True)
    add = driver().plan_port_forward_add(rule)
    assert not add.verified and len(add.deferred) == 1
    assert dict(add.requests[0].fields)["PortForwardingCreateRemove"] == "1"
    edit_form = "\n".join(
        [
            '<form action=/goform/UbeeAdvancedPortForwarding method=POST name="PF">',
            '<input name="PortForwardingLocalIp" value="">',
            '<input name="PortForwardingLocalStartPort" value="">',
            '<input name="PortForwardingLocalEndPort" value="">',
            '<input name="PortForwardingExtIp" value="">',
            '<input name="PortForwardingExtStartPort" value="">',
            '<input name="PortForwardingExtEndPort" value="">',
            '<select name="PortForwardingProtocol">',
            "<option value=4>TCP<option value=3>UDP<option value=254>Both</select>",
            '<input name="PortForwardingDesc" value="">',
            '<input type=checkbox name="PortForwardingEnabled" value=1>',
            '<input type=hidden name="PortForwardingApply" value=0>',
            '<input type=button value="Apply" onclick="applyCommitForwarding(2)">',
            '<input type=button value="Cancel" onclick="applyCommitForwarding(1)"></form>',
        ]
    )
    fake = UbeeFake()
    d = driver(fake)
    fake.send = lambda request: (fake.sent.append(request), edit_form)[1]  # type: ignore[method-assign]
    execute(add, fake)
    step2 = dict(fake.sent[-1].fields)
    assert (
        step2["PortForwardingLocalIp"] == "192.168.0.60"
        and step2["PortForwardingExtStartPort"] == "8443"
    )
    assert step2["PortForwardingProtocol"] == "4" and step2["PortForwardingDesc"] == "web"
    assert step2["PortForwardingEnabled"] == "1" and step2["PortForwardingApply"] == "2"
    assert d is not None
    with pytest.raises(UsageError):
        driver().plan_port_forward_add(PortForward(-1, "192.168.0.60", 22, 22, None, 22, 22, "tcp"))


def test_password_and_reboot() -> None:
    plan = driver().plan_password("admin", "old-secret", "new-secret")
    req = only_request(plan.requests)
    assert dict(req.fields) == {
        "OldPassword": "old-secret",
        "Password": "new-secret",
        "PasswordReEnter": "new-secret",
    }
    shown = render_requests(plan.requests, "http://192.168.0.1", show_secrets=False)
    assert "secret" not in shown.replace("<redacted>", "")
    assert "old-secret" not in str(req.to_dict("http://192.168.0.1"))
    reboot = driver().plan_reboot()
    assert dict(only_request(reboot.requests).fields) == {
        "ResetYes": "0x01",
        "ResetFactoryNo": "0x00",
    }
    assert reboot.destructive


def test_raw_form_refuses_factory_reset() -> None:
    with pytest.raises(UsageError):
        driver().plan_raw_form("UbeeConfiguration.asp", None, {"ResetFactoryYes": "yes"}, None)
