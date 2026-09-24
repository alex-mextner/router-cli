#!/usr/bin/env bash
# install.sh — install the `router` CLI (Linux, macOS; Python 3.11+)
#
# Works from a local clone (./install.sh) and piped from curl:
#   curl -fsSL https://raw.githubusercontent.com/alex-mextner/router-cli/main/install.sh | bash
#
# router has ZERO third-party Python dependencies (urllib, html.parser, sqlite3), so the
# install is fast and cannot be broken by a wheel that will not build. With uv or pipx it
# goes into an isolated environment; without either it is a symlink to the clone, which
# works just as well.
set -euo pipefail

TOOL="router"
REPO="router-cli"
GITHUB_USER="alex-mextner"
ENTRY="bin/router"
CLONE_BASE="${XDG_DATA_HOME:-$HOME/.local/share}"

say()  { printf '%s\n' "$*"; }
warn() { printf '%s\n' "$*" >&2; }

# ── python ────────────────────────────────────────────────────────────────────
PY="$(command -v python3 || true)"
if [[ -z "$PY" ]]; then
  warn "ERROR: python3 not found. Install Python 3.11 or newer, then re-run."
  exit 1
fi
if ! "$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
  warn "ERROR: $("$PY" --version) is too old; router needs Python 3.11 or newer."
  exit 1
fi

# ── locate the source ─────────────────────────────────────────────────────────
_script_dir=""
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "bash" ]]; then
  _script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [[ -n "$_script_dir" && -f "$_script_dir/$ENTRY" ]]; then
  SRC="$_script_dir"
  say "router: using local clone at $SRC"
else
  mkdir -p "$CLONE_BASE"
  CLONE_DIR="$CLONE_BASE/$REPO"
  EXPECT_URL="https://github.com/$GITHUB_USER/$REPO.git"
  if [[ -d "$CLONE_DIR/.git" ]]; then
    actual_url="$(git -C "$CLONE_DIR" remote get-url origin 2>/dev/null || echo "")"
    if [[ "$actual_url" != "$EXPECT_URL" ]]; then
      warn "ERROR: $CLONE_DIR exists but its origin is '$actual_url', not $EXPECT_URL."
      warn "       Remove that directory or fix its remote, then re-run."
      exit 1
    fi
    say "router: updating existing clone at $CLONE_DIR"
    git -C "$CLONE_DIR" pull --ff-only
  else
    say "router: cloning $EXPECT_URL into $CLONE_DIR"
    git clone "$EXPECT_URL" "$CLONE_DIR"
  fi
  SRC="$CLONE_DIR"
fi

# ── install the CLI ───────────────────────────────────────────────────────────
BIN="${PIPX_BIN_DIR:-$HOME/.local/bin}"
mkdir -p "$BIN"

ROUTER_BIN=""
INSTALL_MODE=""
if command -v uv >/dev/null 2>&1; then
  INSTALL_MODE="uv"
  say "router: installing via uv tool (isolated environment)"
  uv tool install --force "$SRC"
  ROUTER_BIN="$(command -v "$TOOL" 2>/dev/null || echo "$HOME/.local/bin/$TOOL")"
elif command -v pipx >/dev/null 2>&1; then
  INSTALL_MODE="pipx"
  say "router: installing via pipx (isolated environment)"
  pipx install --force "$SRC"
  ROUTER_BIN="$(command -v "$TOOL" 2>/dev/null || echo "$BIN/$TOOL")"
else
  INSTALL_MODE="symlink"
  say "router: neither uv nor pipx found — installing a symlink to the clone."
  say "        (router needs no Python packages, so this works fine.)"
  chmod +x "$SRC/$ENTRY"
  ln -sfn "$SRC/$ENTRY" "$BIN/$TOOL"
  ROUTER_BIN="$BIN/$TOOL"
fi

if [[ -z "$ROUTER_BIN" || ! -x "$ROUTER_BIN" ]]; then
  warn "ERROR: install reported success but '$TOOL' is not executable at '$ROUTER_BIN'."
  exit 1
fi
say "router: installed $ROUTER_BIN (via $INSTALL_MODE)"

# ── PATH sanity ───────────────────────────────────────────────────────────────
if [[ ":$PATH:" != *":$BIN:"* ]]; then
  warn ""
  warn "  NOTE: $BIN is not on your PATH. Add this to your shell profile and restart it:"
  warn "    export PATH=\"$BIN:\$PATH\""
  warn ""
fi

RESOLVED="$(command -v "$TOOL" 2>/dev/null || true)"
if [[ -n "$RESOLVED" && "$RESOLVED" != "$ROUTER_BIN" ]]; then
  warn ""
  warn "  WARNING: another '$TOOL' shadows this install on PATH:"
  warn "      installed:   $ROUTER_BIN"
  warn "      resolves to: $RESOLVED"
  warn ""
fi

# ── register the agent skill ──────────────────────────────────────────────────
# This writes OUTSIDE the project: a SKILL.md under ~/.agents/skills, a marked line in each
# detected harness's global instruction file, and a SessionStart hook in
# ~/.claude/settings.json. That is a real change to the user's environment, so it is
# reported rather than done quietly, and ROUTER_NO_SKILL=1 skips it. Absolute path on
# purpose: a PATH shadow would otherwise run a different binary.
if [[ -n "${ROUTER_NO_SKILL:-}" ]]; then
  say "router: skipping agent-skill registration (ROUTER_NO_SKILL is set)."
  say "        Run 'router install-skill' later if you want coding agents to discover router."
else
  say ""
  say "router: registering the agent skill so coding agents can discover this tool."
  say "        This writes to ~/.agents/skills and your harness config. Skip with ROUTER_NO_SKILL=1."
  if ! "$ROUTER_BIN" install-skill; then
    warn "  WARNING: 'router install-skill' failed — router works, but coding agents may not"
    warn "           discover it. Re-run 'router install-skill' to fix."
  fi
fi

# ── done ──────────────────────────────────────────────────────────────────────
if [[ -z "$RESOLVED" ]]; then
  warn ""
  warn "  router is installed at $ROUTER_BIN but does NOT resolve by name (PATH)."
  warn "  Until you fix PATH, run it by full path: $ROUTER_BIN"
  exit 1
fi

say ""
say "  router is installed (via $INSTALL_MODE)."
say ""
say "  Next:   router login         store the admin password (prompted, verified)"
say "          router doctor        check everything"
say "          router devices       who is connected"
say ""
