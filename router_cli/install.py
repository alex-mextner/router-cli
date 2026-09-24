"""install — register the ``router`` agent skill so harnesses discover the tool by themselves.

Three layers, matching the sibling personal CLIs (stt, tg) so every tool is discoverable
the same way:

1. ``~/.agents/skills/router/SKILL.md`` — the Agent Skills standard file, read by Claude
   Code, Codex, opencode, Gemini and Cursor.
2. A one-line blurb appended (between markers, so re-running replaces rather than
   duplicates) into each *detected* harness's global instruction file.
3. A ``SessionStart`` hook that prints every installed agent CLI at the top of a session.

Everything here is idempotent, and nothing rewrites config it did not write. A settings file
that cannot be parsed is left completely alone rather than clobbered.
"""

from __future__ import annotations

import contextlib
import json
import re
import shutil
from pathlib import Path

SKILL_NAME = "router"

SKILL_MD = """\
---
name: router
description: >-
  Inspect and manage the home router from the shell: connected devices, DHCP leases,
  static IP reservations, Wi-Fi, port forwarding, firewall, DOCSIS status, and a
  device inventory with web-UI discovery. Ubee EVW32C cable gateways and OpenWrt.
  Every command has --json; every write has --dry-run.
metadata:
  author: alex-mextner
  repo: https://github.com/alex-mextner/router-cli
---

# router — the home router from the command line

## Invocation
```
router status --json                      # model, firmware, uptime, WAN, DOCSIS summary
router devices --json                     # who is connected (mac, ip, hostname, wifi/lan)
router leases --json                      # DHCP leases + static reservations
router reserve <mac> <ip> --name N --dry-run   # pin an IP (shows the exact request)
router unreserve <mac> --dry-run
router inventory update && router inventory list --json --filter active
router scan --all-online --json           # web UIs on the LAN: title, server, favicon
router wifi --json                        # radios, SSIDs, channels (keys hidden)
router port-forward list --json
router settings                           # every settings area; `router settings show <area>`
router doctor                             # what works and how to fix what doesn't
```

## Rules for agents
- READ freely. For ANY change run it with `--dry-run` first and show the user the
  printed request; only then run it for real. Destructive changes also need `--yes` —
  never add `--yes` without the user's explicit go-ahead.
- `router login` is for the HUMAN (it prompts for the password). If a command says
  "no active admin session", ask the user to run `router login`; do not ask for the
  password in chat.
- Never try to fetch logout/reboot/reset pages; the tool refuses them anyway. There is no
  factory reset.
- `--show-secrets` reveals Wi-Fi keys and passwords: only when the user asks for them.
- Exit codes: 0 ok, 2 usage, 3 needs --yes, 4 unknown item, 5 not found, 6 unsupported
  by this router, 7 unreachable, 8 not logged in, 10 router answered nonsense.
"""

SKILL_BLURB = (
    "`router` — home router CLI (Ubee EVW32C, OpenWrt): `router devices --json`, "
    "`router leases`, `router reserve <mac> <ip> --dry-run`, `router inventory list --json`, "
    "`router scan --all-online --json`, `router wifi`, `router port-forward list`. "
    "Writes: always `--dry-run` first; `--yes` only with the user's go-ahead."
)

_HOOK_MARKER = "# agent-tools-awareness"
_HOOK_COMMAND = (
    'sh -c \'d="$HOME/.agents/skills/.blurbs"; ls "$d"/*.md >/dev/null 2>&1 && '
    '{ printf "Agent CLI tools installed on this machine (prefer them):\\n"; '
    'cat "$d"/*.md; }\' ' + _HOOK_MARKER
)

_HARNESSES = (
    ("claude", Path(".claude") / "CLAUDE.md", ("~/.claude",)),
    ("codex", Path(".codex") / "AGENTS.md", ("~/.codex",)),
    ("opencode", Path(".config") / "opencode" / "AGENTS.md", ("~/.config/opencode",)),
    ("gemini", Path(".gemini") / "GEMINI.md", ("~/.gemini",)),
)


def install_skill(home: Path | None = None) -> int:
    """Write every layer, reporting each target. Safe to run repeatedly."""
    home = home or Path.home()
    written: list[str] = [_write_skill_file(home)]
    _write_blurb_file(home)
    _link_for_claude(home)
    written += _write_harness_blurbs(home)
    if _ensure_sessionstart_hook(home):
        written.append("SessionStart hook -> ~/.claude/settings.json")
    for target in written:
        print(f"  ✓ {target}")
    print(
        f"{SKILL_NAME}: install-skill done ({len(written)} target(s)). Idempotent — re-run anytime."
    )
    return 0


def _write_skill_file(home: Path) -> str:
    skill_dir = home / ".agents" / "skills" / SKILL_NAME
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(SKILL_MD, encoding="utf-8")
    return str(path)


def _write_blurb_file(home: Path) -> None:
    blurbs = home / ".agents" / "skills" / ".blurbs"
    blurbs.mkdir(parents=True, exist_ok=True)
    (blurbs / f"{SKILL_NAME}.md").write_text(f"- {SKILL_BLURB}\n", encoding="utf-8")


def _link_for_claude(home: Path) -> None:
    """Claude Code also scans ~/.claude/skills; a symlink keeps one source of truth."""
    skills = home / ".claude" / "skills"
    if not skills.is_dir():
        return
    link = skills / SKILL_NAME
    if link.exists() or link.is_symlink():
        return
    with contextlib.suppress(OSError):
        link.symlink_to(Path("..") / ".." / ".agents" / "skills" / SKILL_NAME)


def _write_harness_blurbs(home: Path) -> list[str]:
    written = []
    for command, relative, hints in _HARNESSES:
        if _detected(home, command, *hints):
            path = home / relative
            _append_marked(path, SKILL_NAME, SKILL_BLURB)
            written.append(str(path))
    return written


def _detected(home: Path, command: str, *dirs: str) -> bool:
    if shutil.which(command):
        return True
    return any((home / d.removeprefix("~/")).is_dir() for d in dirs)


def _append_marked(path: Path, tool: str, blurb: str) -> None:
    """Replace this tool's marked block, leaving everything else in the file untouched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    start, end = f"<!-- skill:{tool} -->", f"<!-- /skill:{tool} -->"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    existing = re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", "", existing, flags=re.S)
    block = f"{start}\n{blurb}\n{end}\n"
    body = (existing.rstrip() + "\n\n" + block) if existing.strip() else block
    path.write_text(body, encoding="utf-8")


def _ensure_sessionstart_hook(home: Path) -> bool:
    """Add the shared awareness hook to Claude Code's settings, or leave them alone entirely."""
    settings = home / ".claude" / "settings.json"
    if not settings.parent.is_dir():
        return False
    try:
        data = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    hooks = data.setdefault("hooks", {})
    session_start = hooks.setdefault("SessionStart", []) if isinstance(hooks, dict) else None
    if not isinstance(session_start, list):
        return False
    if _hook_present(session_start):
        return False
    session_start.append({"hooks": [{"type": "command", "command": _HOOK_COMMAND}]})
    if settings.exists():
        settings.with_suffix(".json.bak").write_text(settings.read_text("utf-8"), encoding="utf-8")
    settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def _hook_present(session_start: list[object]) -> bool:
    for group in session_start:
        entries = group.get("hooks", []) if isinstance(group, dict) else []
        for entry in entries:
            if isinstance(entry, dict) and _HOOK_MARKER in str(entry.get("command", "")):
                return True
    return False
