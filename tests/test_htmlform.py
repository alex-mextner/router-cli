"""The browser model: which controls a real browser would submit, in which order."""

from __future__ import annotations

import pytest
from helpers import ubee_page

from router_cli import htmlform
from router_cli._errors import UsageError


def test_static_lease_form_submits_exactly_what_a_browser_would() -> None:
    form = htmlform.parse(ubee_page("UbeeLanStaticLease.asp")).form("UbeeLanStaticLease")
    pairs = form.successful()
    names = [k for k, _ in pairs]
    assert len(pairs) == 8 * 7 + 3  # 8 slots x (6 octets + IP) + 3 hidden
    assert not any(n.startswith("tempClear") for n in names)  # unchecked boxes are not sent
    assert not any(n.startswith("ID_BUTTON") for n in names)
    assert names[-3:] == ["MY_POOL_START_IP", "MY_POOL_END_IP", "StaticLeaseStatusFlag"]
    assert ("IpAddStaticLease8IPX", "0.0.0.0") in pairs
    assert names[:7] == [f"MacAddStaticLease01MA{i}" for i in range(6)] + ["IpAddStaticLease1IPX"]


def test_disabled_octets_and_the_checked_radio_only() -> None:
    form = htmlform.parse(ubee_page("UbeeLanDhcp.asp")).form("UbeeLanDhcp")
    pairs = dict(form.successful())
    assert pairs["DhcpServerEnable"] == "0x1000"
    assert "DhcpServerDisable" not in pairs  # the unchecked radio of the pair
    assert "DhcpIpStart0" not in pairs and "DhcpIpStart3" in pairs  # disabled octets omitted
    assert form.raw_value("DhcpIpStart0") == "192"  # ...but still readable


def test_named_submit_button_only_when_clicked() -> None:
    page = htmlform.parse(ubee_page("UbeeWlanBasic.asp"))
    five = page.form("wlanRadio5G")
    assert "ID_BUTTON_APPLY" not in dict(five.successful())
    assert ("ID_BUTTON_APPLY", "Apply") in five.successful("ID_BUTTON_APPLY")
    # The dangerous "Restore Wireless Defaults" button is never sent unless clicked.
    assert "ID_BUTTON_RESET_DEFAULT" not in dict(page.form("wlanRadio").successful())


def test_select_semantics() -> None:
    html = """<form name=f action=/goform/x>
      <select name=a><option value=1>one<option value=2>two</select>
      <select name=b><option value=1>one<option value=2 selected>two</select>
      <select name=c size=5><option value=1>one</select>
      <select name=d disabled><option value=1 selected>one</select>
      <select name=e><option vlue=0>No filters entered.</select>
    </form>"""
    form = htmlform.parse(html).form("f")
    assert form.successful() == [("a", "1"), ("b", "2"), ("e", "No filters entered.")]
    form.set("a", "two")  # by label
    assert dict(form.successful())["a"] == "2"
    with pytest.raises(UsageError):
        form.set("a", "3")


def test_comments_hide_controls_and_mangled_attributes() -> None:
    html = """<form name=f action=/goform/x>
      <!-- <input name="Ghost" value="boo"> -->
      <input type="radio" name="R" value"0" CHECKED>
      <input type="checkbox" name="C" value=0x01>
      <input name=T value= Broadcom >
    </form>"""
    form = htmlform.parse(html).form("f")
    assert not form.has("Ghost")
    assert form.successful() == [("R", "on"), ("T", "Broadcom")]


def test_tables_and_kv() -> None:
    page = htmlform.parse(ubee_page("UbeeSysInfo.asp"))
    kv = page.kv()
    assert kv["ID_LABEL_TABLE_MODEL"] == "EVW32C-0N"
    assert kv["ID_LABEL_TABLE_CABLE_MODEM_SERIAL_NUMBER"] == "EVW32C0N00000000"


def test_json_vars() -> None:
    page = htmlform.parse(ubee_page("UbeeWlanSecurity.asp"))
    state = page.json_vars["web_item_data_wireless_setup_jsonData"]
    assert state["wireless_2g_auth_mode"] == 4
    assert state["wireless_2g_sec_wpap_preshare_key"] == "testtesttest"
