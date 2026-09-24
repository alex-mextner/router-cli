"""htmlform — read a router's web page the way a browser would, and submit it the same way.

WHY A BROWSER MODEL AND NOT FIELD LISTS
    Consumer-router firmware validates almost nothing server-side and trusts that the POST
    looks exactly like what its own page would have produced. Getting that right by hand for
    thirty pages is where tools break a router: a missing hidden flag and the page does
    nothing, an extra one and it does something else. So every write here starts from the
    page's CURRENT form, parsed with a browser's rules for which controls are "successful":

    - ``disabled`` controls are never sent (the Ubee's fixed ``192.168.0`` octets are);
    - an unchecked checkbox or radio is never sent; a checked one sends its ``value``
      (``"on"`` when the attribute is missing — or mangled, like ``value"0"``);
    - a single-choice ``<select>`` sends its selected option, or its first when none is
      marked; a list box (``size > 1``) or ``multiple`` sends only what is selected;
    - buttons (``submit``, ``button``, ``reset``, ``image``) are never sent. A browser sends
      the ONE submit button that was clicked, and some of these pages name the dangerous
      one (``ID_BUTTON_RESET_DEFAULT``); an explicit ``clicked=`` is the only way in;
    - controls inside HTML comments do not exist (the Ubee keeps "need comments to generate
      enums" blocks full of inputs).

    A caller then changes only the fields it means to change and submits the rest untouched.

ALSO HERE
    Tables (rows of cell text, grouped per ``<table>``, tolerant of the missing ``</td>`` and
    ``</tr>`` this HTML is full of) and the ``var x_jsonData = ' {...} '`` blobs the newer
    pages embed their state in.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any

from ._errors import UsageError

BUTTON_TYPES = frozenset({"submit", "button", "reset", "image"})
_WS = re.compile(r"\s+")


def clean_text(text: str) -> str:
    return _WS.sub(" ", html.unescape(text).replace("\xa0", " ")).strip()


@dataclass
class Option:
    value: str
    text: str
    selected: bool = False
    disabled: bool = False


@dataclass
class Control:
    """One form control, with its CURRENT state (which a caller may change)."""

    tag: str  # input | select | textarea
    type: str  # text/password/hidden/checkbox/radio/submit/... ; "select" for <select>
    name: str
    value: str = ""
    checked: bool = False
    disabled: bool = False
    options: list[Option] = field(default_factory=list)
    multiple: bool = False
    size: int = 1
    attrs: dict[str, str] = field(default_factory=dict)

    @property
    def is_button(self) -> bool:
        return self.tag == "input" and self.type in BUTTON_TYPES

    def selected_values(self) -> list[str]:
        chosen = [o.value for o in self.options if o.selected and not o.disabled]
        if self.multiple:
            return chosen
        if chosen:
            return chosen[-1:]  # several `selected` on a single select: the last one wins
        if self.size > 1:
            return []  # a list box with nothing highlighted submits nothing
        enabled = [o.value for o in self.options if not o.disabled]
        return enabled[:1]  # a drop-down always shows (and submits) something

    def successful(self) -> list[tuple[str, str]]:
        """What a browser would submit for this control (possibly nothing)."""
        if not self.name or self.disabled or self.is_button:
            return []
        if self.tag == "select":
            return [(self.name, v) for v in self.selected_values()]
        if self.type in ("checkbox", "radio"):
            return [(self.name, self.value)] if self.checked else []
        if self.type == "file":
            return []
        return [(self.name, self.value)]


@dataclass
class Form:
    name: str
    action: str
    method: str
    controls: list[Control] = field(default_factory=list)

    def all(self, name: str) -> list[Control]:
        return [c for c in self.controls if c.name == name]

    def control(self, name: str) -> Control:
        found = self.all(name)
        if not found:
            raise UsageError(
                what=f"form {self.name or self.action!r} has no field {name!r}",
                why="the page layout differs from what this driver expects",
                how="run `router raw form <page>` to see the fields this firmware renders",
            )
        return found[0]

    def has(self, name: str) -> bool:
        return any(c.name == name for c in self.controls)

    def value(self, name: str) -> str:
        """The value this field would submit right now ('' if it would submit nothing)."""
        for control in self.all(name):
            sent = control.successful()
            if sent:
                return sent[0][1]
        return ""

    def raw_value(self, name: str) -> str:
        """The field's value attribute, even when disabled (e.g. fixed IP octets)."""
        control = self.control(name)
        if control.tag == "select":
            chosen = [o.value for o in control.options if o.selected]
            return chosen[0] if chosen else ""
        return control.value

    def is_checked(self, name: str) -> bool:
        return any(c.checked for c in self.all(name))

    def set(self, name: str, value: str) -> None:
        """Set a text/hidden/password field, or choose a select option by value or label."""
        control = self.control(name)
        if control.tag == "select":
            match = [o for o in control.options if o.value == value]
            if not match:
                lowered = value.strip().lower()
                match = [o for o in control.options if o.text.strip().lower() == lowered]
            if not match:
                choices = ", ".join(f"{o.value} ({o.text})" for o in control.options)
                raise UsageError(
                    what=f"{value!r} is not a valid choice for {name}",
                    why=f"the page offers: {choices}",
                    how="pick one of those values",
                )
            for option in control.options:
                option.selected = option is match[0]
            return
        if control.type in ("checkbox", "radio"):
            raise UsageError(what=f"{name} is a {control.type}; use check()", why="", how="")
        control.value = value

    def check(self, name: str, on: bool = True, value: str | None = None) -> None:
        """Tick or untick a checkbox, or pick a radio (by value when several share a name)."""
        controls = self.all(name)
        if not controls:
            self.control(name)  # raises the diagnosed error
        if controls[0].type == "radio" and value is not None:
            for c in controls:
                c.checked = on and c.value == value
            return
        for c in controls:
            c.checked = on

    def enable(self, name: str) -> None:
        for c in self.all(name):
            c.disabled = False

    def add_hidden(self, name: str, value: str) -> None:
        """Append a control the page's JavaScript would have added before submitting."""
        if self.has(name):
            self.set(name, value)
            return
        self.controls.append(Control(tag="input", type="hidden", name=name, value=value))

    def successful(self, clicked: str | None = None) -> list[tuple[str, str]]:
        """The ordered (name, value) pairs a browser would POST."""
        pairs: list[tuple[str, str]] = []
        for control in self.controls:
            if clicked and control.is_button and control.name == clicked:
                pairs.append((control.name, control.value))
                continue
            pairs.extend(control.successful())
        return pairs

    def describe(self) -> list[dict[str, Any]]:
        """A machine-readable list of fields (for `router raw form`)."""
        out: list[dict[str, Any]] = []
        for c in self.controls:
            item: dict[str, Any] = {"name": c.name, "type": c.type}
            if c.tag == "select":
                item["options"] = [
                    {"value": o.value, "text": o.text, "selected": o.selected} for o in c.options
                ]
                if c.multiple or c.size > 1:
                    item["listbox"] = True
            else:
                item["value"] = c.value
            if c.type in ("checkbox", "radio"):
                item["checked"] = c.checked
            if c.disabled:
                item["disabled"] = True
            if c.is_button:
                item["button"] = True
            out.append(item)
        return out


@dataclass
class Row:
    table: int
    cells: list[str]
    ids: list[str]
    attrs: dict[str, str]


@dataclass
class Page:
    """A parsed router page."""

    title: str
    forms: list[Form]
    orphans: list[Control]
    rows: list[Row]
    json_vars: dict[str, Any]
    text: str

    def form(self, name_or_action: str) -> Form:
        for form in self.forms:
            if form.name == name_or_action:
                return form
        for form in self.forms:
            if form.action.rstrip("/").split("/")[-1] == name_or_action:
                return form
        known = [f.name or f.action for f in self.forms]
        raise UsageError(
            what=f"no form {name_or_action!r} on this page",
            why=f"forms present: {', '.join(known) or 'none'}",
            how="the firmware may differ; run `router raw form <page>`",
        )

    def tables(self) -> dict[int, list[Row]]:
        grouped: dict[int, list[Row]] = {}
        for row in self.rows:
            grouped.setdefault(row.table, []).append(row)
        return grouped

    def table_with(self, label_id: str) -> list[Row]:
        """All rows of the (innermost) table whose header row carries this label id."""
        for rows in self.tables().values():
            if any(label_id in row.ids for row in rows):
                return rows
        return []

    def kv(self) -> dict[str, str]:
        """Two-column "label | value" rows, keyed by the label's id (else its text)."""
        out: dict[str, str] = {}
        for row in self.rows:
            cells = [c for c in row.cells]
            while cells and not cells[0]:
                cells = cells[1:]
            if len(cells) != 2:
                continue
            key = row.ids[0] if row.ids else cells[0].rstrip(": ").strip()
            if key and key not in out:
                out[key] = cells[1]
        return out


_JSON_VAR = re.compile(r"var\s+(\w+)\s*=\s*'(.*?)'\s*;", re.S)


def json_vars(text: str) -> dict[str, Any]:
    """The ``var name = ' {json} ' ;`` blobs newer Ubee pages carry their state in."""
    out: dict[str, Any] = {}
    for match in _JSON_VAR.finditer(text):
        blob = match.group(2).strip()
        if not blob.startswith("{"):
            continue
        try:
            value = json.loads(blob)
        except ValueError:
            continue
        out[match.group(1)] = value
    return out


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.forms: list[Form] = []
        self.orphans: list[Control] = []
        self._form: Form | None = None
        self._select: Control | None = None
        self._option: Option | None = None
        self._textarea: Control | None = None
        self.rows: list[Row] = []
        self._table_depth = 0
        self._table_ids: list[int] = []
        self._table_counter = 0
        self._open_rows: list[tuple[int, Row, list[list[str]]]] = []

    # ── forms ─────────────────────────────────────────────────────────────────
    def _add(self, control: Control) -> None:
        (self._form.controls if self._form is not None else self.orphans).append(control)

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k.lower(): (v if v is not None else "") for k, v in attrs_list}
        if tag == "title":
            self._in_title = True
        elif tag == "form":
            self._form = Form(
                name=attrs.get("name", ""),
                action=attrs.get("action", ""),
                method=attrs.get("method", "get").upper(),
            )
            self.forms.append(self._form)
        elif tag == "input":
            kind = attrs.get("type", "text").lower() or "text"
            default = "on" if kind in ("checkbox", "radio") else ""
            self._add(
                Control(
                    tag="input",
                    type=kind,
                    name=attrs.get("name", ""),
                    value=attrs.get("value", default),
                    checked="checked" in attrs,
                    disabled="disabled" in attrs,
                    attrs=attrs,
                )
            )
        elif tag == "select":
            self._close_option()
            size = _int(attrs.get("size", "1"), 1)
            self._select = Control(
                tag="select",
                type="select",
                name=attrs.get("name", ""),
                disabled="disabled" in attrs,
                multiple="multiple" in attrs,
                size=size,
                attrs=attrs,
            )
            self._add(self._select)
        elif tag == "option" and self._select is not None:
            self._close_option()
            self._option = Option(
                value=attrs.get("value", "\x00text"),
                text="",
                selected="selected" in attrs,
                disabled="disabled" in attrs,
            )
            self._select.options.append(self._option)
        elif tag == "textarea":
            self._textarea = Control(
                tag="textarea",
                type="textarea",
                name=attrs.get("name", ""),
                disabled="disabled" in attrs,
                attrs=attrs,
            )
            self._add(self._textarea)
        # ── tables ──
        elif tag == "table":
            self._table_depth += 1
            self._table_counter += 1
            self._table_ids.append(self._table_counter)
        elif tag == "tr":
            self._close_rows_at(self._table_depth)
            table = self._table_ids[-1] if self._table_ids else 0
            row = Row(table=table, cells=[], ids=[], attrs=attrs)
            self._open_rows.append((self._table_depth, row, []))
        elif tag in ("td", "th"):
            top = self._top_row()
            if top is not None:
                top[2].append([])
        if "id" in attrs and tag in ("label", "td", "th", "b", "span", "font"):
            top = self._top_row()
            if top is not None:
                top[1].ids.append(attrs["id"])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "form":
            self._form = None
        elif tag == "select":
            self._close_option()
            self._select = None
        elif tag == "option":
            self._close_option()
        elif tag == "textarea":
            self._textarea = None
        elif tag == "table":
            self._close_rows_at(self._table_depth)
            if self._table_depth > 0:
                self._table_depth -= 1
            if self._table_ids:
                self._table_ids.pop()
        elif tag == "tr":
            self._close_rows_at(self._table_depth)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._option is not None:
            self._option.text += data
        if self._textarea is not None:
            self._textarea.value += data
        top = self._top_row()
        if top is not None and top[2]:
            top[2][-1].append(data)

    def _close_option(self) -> None:
        if self._option is not None:
            self._option.text = clean_text(self._option.text)
            if self._option.value == "\0text":
                self._option.value = self._option.text
            self._option = None

    def _top_row(self) -> tuple[int, Row, list[list[str]]] | None:
        if not self._open_rows:
            return None
        top = self._open_rows[-1]
        return top if top[0] == self._table_depth else None

    def _close_rows_at(self, depth: int) -> None:
        while self._open_rows and self._open_rows[-1][0] >= depth:
            _, row, cells = self._open_rows.pop()
            row.cells = [clean_text("".join(parts)) for parts in cells]
            if row.cells:
                self.rows.append(row)

    def close(self) -> None:
        super().close()
        self._close_option()
        self._close_rows_at(0)


def _int(text: str, default: int) -> int:
    try:
        return int(text)
    except ValueError:
        return default


def parse(text: str) -> Page:
    parser = _Parser()
    parser.feed(text)
    parser.close()
    return Page(
        title=clean_text(parser.title),
        forms=parser.forms,
        orphans=parser.orphans,
        rows=parser.rows,
        json_vars=json_vars(text),
        text=text,
    )
