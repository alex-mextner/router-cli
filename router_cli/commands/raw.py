"""raw — the escape hatch: list pages, fetch a page, dump its forms, post a form, call ubus.

    router raw pages                      every known page and what it shows
    router raw get <page>                 the page's HTML (secrets masked)
    router raw form <page>                its forms and fields, as a browser would submit them
    router raw post <page> k=v ...        submit a form with changes (--dry-run / --yes)
    router raw call <object> <method> [json-args]    OpenWrt: one read-only ubus call

`raw get` refuses logout/reboot/reset/restore/upgrade/backup pages, like everything else.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .. import htmlform
from .._errors import UsageError, unsupported
from ..drivers.base import Capability
from . import _common as C

NAME = "raw"
SUMMARY = "debug: list pages, get a page, dump/post its forms, call ubus"

VERBS = ("pages", "get", "form", "post", "call")

_PASSWORD_INPUT = re.compile(
    r"(<input\b[^>]*type=\"?password\"?[^>]*value=\s*)(\"[^\"]*\"|'[^']*'|[^\s>]*)", re.I
)
_SECRET_JSON = re.compile(r"(\"[\w]*(?:key|pass|secret|pin|psk)[\w]*\"\s*:\s*)\"[^\"]*\"", re.I)


def mask(text: str) -> str:
    text = _PASSWORD_INPUT.sub(r'\1"<redacted>"', text)
    return _SECRET_JSON.sub(r'\1"<redacted>"', text)


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in (*VERBS, "-h", "--help"):
        argv = ["pages", *argv]
    top = C.parser(NAME, SUMMARY)
    sub = top.add_subparsers(dest="verb")
    p = sub.add_parser("pages")
    C.add_router_args(p)
    p = sub.add_parser("get")
    p.add_argument("page")
    p.add_argument("--show-secrets", action="store_true")
    C.add_router_args(p)
    p = sub.add_parser("form")
    p.add_argument("page")
    C.add_router_args(p)
    p = sub.add_parser("post")
    p.add_argument("page")
    p.add_argument("assignments", nargs="*", metavar="field=value")
    p.add_argument("--form", help="form name or action (when the page has several)")
    p.add_argument("--clicked", help="name of the submit button to include")
    C.add_router_args(p)
    C.add_write_args(p)
    p = sub.add_parser("call")
    p.add_argument("object")
    p.add_argument("method")
    p.add_argument("args", nargs="?", default="{}", help="JSON object")
    C.add_router_args(p)
    args = top.parse_args(argv)

    driver = C.open_driver(args)
    driver.require(Capability.RAW, "raw access")
    if args.verb == "pages":
        pages = driver.raw_pages()
        if args.json:
            C.emit_json(pages)
        else:
            print(C.table(["page", "what"], sorted(pages.items())) if pages else "(no page map)")
        return 0
    if args.verb == "get":
        text = driver.raw_get(args.page)
        print(text if args.show_secrets else mask(text))
        return 0
    if args.verb == "form":
        page = htmlform.parse(driver.raw_get(args.page))
        forms: list[dict[str, Any]] = [
            {
                "name": f.name,
                "action": f.action,
                "method": f.method,
                "fields": f.describe(),
                "would_submit": f.successful(),
            }
            for f in page.forms
        ]
        for form in forms:
            for field in form["fields"]:
                if field.get("type") == "password" and field.get("value"):
                    field["value"] = "<redacted>"
            form["would_submit"] = [
                [
                    k,
                    "<redacted>"
                    if any(
                        fd["name"] == k and fd.get("type") == "password" for fd in form["fields"]
                    )
                    else v,
                ]
                for k, v in form["would_submit"]
            ]
        if args.json:
            C.emit_json({"title": page.title, "forms": forms, "json_vars": sorted(page.json_vars)})
            return 0
        print(f"{page.title}")
        for form in forms:
            print(f"\nform {form['name'] or '(unnamed)'} -> {form['method']} {form['action']}")
            for field in form["fields"]:
                extra = ""
                if "options" in field:
                    extra = (
                        " ["
                        + ", ".join(
                            ("*" if o["selected"] else "") + f"{o['value']}={o['text']}"
                            for o in field["options"]
                        )
                        + "]"
                    )
                flags = "".join(
                    f" {k}" for k in ("disabled", "checked", "button", "listbox") if field.get(k)
                )
                value = f" = {field['value']!r}" if "value" in field else ""
                print(f"  {field['name'] or '(no name)'} ({field['type']}){value}{extra}{flags}")
        if page.json_vars:
            print(f"\nembedded JSON: {', '.join(sorted(page.json_vars))}")
        return 0
    if args.verb == "post":
        plan = driver.plan_raw_form(
            args.page, args.form, C.parse_assignments(args.assignments), args.clicked
        )
        return C.run_plan(driver, plan, args)
    call = getattr(driver, "raw_call", None)
    if call is None:
        raise unsupported(driver.name, "ubus calls")
    try:
        call_args = json.loads(args.args)
    except ValueError as exc:
        raise UsageError(
            what="the call arguments are not JSON", why=str(exc), how='e.g. \'{"config":"dhcp"}\''
        ) from exc
    C.emit_json(call(args.object, args.method, call_args))
    return 0
