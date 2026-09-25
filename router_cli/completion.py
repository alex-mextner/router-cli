"""completion — shell completion for bash, zsh and fish, computed in one place.

HOW IT WORKS
    The shell scripts (``router completion bash|zsh|fish``) are thin: on TAB they call
    ``router completion complete ...`` with the words typed so far, and print what it
    answers. All the logic lives here, once, for every shell:

    - command names come from the self-registering command catalog;
    - verbs, flags and flag choices come from each command's own argparse parser, captured
      by running the command with ``parse_args`` swapped for a trap (nothing else runs:
      no router, no network, no files);
    - an argument whose metavar is ``DEVICE`` completes device names, MACs and IPs from the
      LOCAL inventory database — completion never talks to the router.

    Commands that dispatch by hand before parsing (``filter ip|port|mac``) expose their
    sub-runners as ``SUBCOMMANDS`` so the walk can follow them.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import shlex
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

DEVICE = "DEVICE"


@dataclass
class Flag:
    takes_value: bool
    choices: list[str] | None = None
    device: bool = False


@dataclass
class Node:
    """One level of the command line: its verbs, flags and positionals."""

    flags: dict[str, Flag] = field(default_factory=dict)
    verbs: dict[str, Node] = field(default_factory=dict)
    positionals: list[Flag] = field(default_factory=list)  # takes_value is always True
    default_verb: str | None = None
    lazy: dict[str, Callable[[], Node]] = field(default_factory=dict)

    def verb(self, name: str) -> Node | None:
        if name not in self.verbs and name in self.lazy:
            self.verbs[name] = self.lazy[name]()
        return self.verbs.get(name)

    def verb_names(self) -> list[str]:
        return sorted({*self.verbs, *self.lazy})


# ── introspection ─────────────────────────────────────────────────────────────
class _Captured(Exception):
    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super().__init__("captured")
        self.parser = parser


def capture_parser(run: Callable[[list[str]], int]) -> argparse.ArgumentParser | None:
    """The parser ``run`` builds, caught at ``parse_args`` before it does anything else."""
    original = argparse.ArgumentParser.parse_args

    def trap(self: argparse.ArgumentParser, *args: Any, **kwargs: Any) -> Any:
        raise _Captured(self)

    argparse.ArgumentParser.parse_args = trap  # type: ignore[method-assign]
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            run(["--help"])
    except _Captured as captured:
        return captured.parser
    except BaseException:  # a command that cannot be introspected completes nothing
        return None
    finally:
        argparse.ArgumentParser.parse_args = original  # type: ignore[method-assign]
    return None


def describe(parser: argparse.ArgumentParser) -> Node:
    node = Node()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, sub in action.choices.items():
                node.verbs[name] = describe(sub)
            continue
        choices = [str(c) for c in action.choices] if action.choices else None
        device = action.metavar == DEVICE
        if action.option_strings:
            spec = Flag(takes_value=action.nargs != 0, choices=choices, device=device)
            for option in action.option_strings:
                node.flags[option] = spec
        elif action.nargs != argparse.SUPPRESS:
            node.positionals.append(Flag(True, choices, device))
    for default in ("show", "list", "pages"):
        if default in node.verbs:
            node.default_verb = default
            break
    return node


def command_node(module_name: str) -> Node:
    module = importlib.import_module(module_name)
    subcommands = getattr(module, "SUBCOMMANDS", None)
    if isinstance(subcommands, dict):
        node = Node(flags={"--help": Flag(False)})
        for name, run in subcommands.items():
            parser = capture_parser(run)
            node.verbs[name] = describe(parser) if parser else Node()
        return node
    parser = capture_parser(module.run)
    node = describe(parser) if parser else Node(flags={"--help": Flag(False)})
    # A command that picks between two parsers by its first word (wifi-acl: show/keys/set
    # vs add/rm/clear) names a word that reaches the second one; its verbs are merged in.
    command_run: Callable[[list[str]], int] = module.run
    for probe in getattr(module, "COMPLETION_PROBES", ()):
        extra = capture_parser(_prefixed(command_run, str(probe)))
        if extra is not None:
            for name, child in describe(extra).verbs.items():
                node.verbs.setdefault(name, child)
    return node


def _prefixed(run: Callable[[list[str]], int], word: str) -> Callable[[list[str]], int]:
    return lambda argv: run([word, *argv])


def _lazy(module_name: str) -> Callable[[], Node]:
    return lambda: command_node(module_name)


def root() -> Node:
    from .cli import _discover

    node = Node(flags={"--help": Flag(False), "--version": Flag(False)})
    for name, (module_name, _summary) in _discover().items():
        node.lazy[name] = _lazy(module_name)
    return node


# ── candidates ────────────────────────────────────────────────────────────────
def device_candidates() -> list[str]:
    """Names, MACs and IPs from the local inventory; [] when there is no database yet."""
    from .config import db_path

    if not db_path().is_file():
        return []
    from .inventory import Inventory

    out: list[str] = []
    try:
        with Inventory() as inv:
            rows = inv.selector_rows()
    except Exception:  # a broken DB must not break the shell
        return []
    for row in rows:
        for value in (*row["names"][:2], row["mac"], row["ip"]):
            if value and value not in out:
                out.append(str(value))
    return out


def _slot_values(slot: Flag, devices: Callable[[], list[str]]) -> list[str]:
    if slot.choices:
        return list(slot.choices)
    if slot.device:
        return devices()
    return []


def complete(
    words: list[str],
    current: str,
    tree: Node | None = None,
    devices: Callable[[], list[str]] = device_candidates,
) -> list[str]:
    """Candidates for ``current`` after ``words`` (``words[0]`` is the program name)."""
    node = tree or root()
    pending: Flag | None = None
    position = 0  # positionals consumed at the current node
    after_dashdash = False
    for word in words[1:]:
        if pending is not None:
            pending = None
            continue
        if word == "--":
            after_dashdash = True
            continue
        if word.startswith("-") and not after_dashdash:
            name, has_value, _ = word.partition("=")
            flag = _flag(node, name)
            if flag and flag.takes_value and not has_value:
                pending = flag
            continue
        if position == 0 and node.verb_names():
            child = node.verb(word)
            if child is not None:
                node = child
                continue
            default = node.verb(node.default_verb) if node.default_verb else None
            if default is not None:
                # `router dhcp foo` means `router dhcp show foo`: the word is its positional.
                node = default
        position += 1

    values: list[str]
    if pending is not None:
        values = _slot_values(pending, devices)
    elif current.startswith("-") and not after_dashdash:
        name, has_value, _ = current.partition("=")
        if has_value:
            flag = _flag(node, name)
            values = [f"{name}={v}" for v in _slot_values(flag, devices)] if flag else []
        else:
            values = sorted(_all_flags(node))
    elif position == 0 and node.verb_names():
        values = node.verb_names()
    elif position < len(node.positionals):
        values = _slot_values(node.positionals[position], devices)
    else:
        values = []
    return _matching(values, current)


def _flag(node: Node, name: str) -> Flag | None:
    if name in node.flags:
        return node.flags[name]
    default = node.verb(node.default_verb) if node.default_verb else None
    return default.flags.get(name) if default else None


def _all_flags(node: Node) -> set[str]:
    flags = set(node.flags)
    default = node.verb(node.default_verb) if node.default_verb else None
    if default:
        flags |= set(default.flags)
    return {f for f in flags if f.startswith("--") or f == "-h"}


def _matching(values: list[str], current: str) -> list[str]:
    exact = [v for v in values if v.startswith(current)]
    if exact or not current:
        return _unique(exact)
    folded = current.casefold()
    return _unique([v for v in values if v.casefold().startswith(folded)])


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def split_line(line: str) -> tuple[list[str], str]:
    """Words before the cursor and the word being typed, from bash's ``COMP_LINE``."""
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    words: list[str] = []
    try:
        words.extend(lexer)
    except ValueError:  # an unclosed quote while typing: what is inside it is the word
        return words, lexer.token
    if not line or line[-1].isspace():
        return words, ""
    return words[:-1], words[-1] if words else ""


def for_bash(candidates: list[str], current: str) -> list[str]:
    """bash splits words at ':' and '=' (COMP_WORDBREAKS): answer only past the last one."""
    cut = max(current.rfind(":"), current.rfind("=")) + 1
    return [c[cut:].replace(" ", "\\ ") for c in candidates]


# ── scripts ───────────────────────────────────────────────────────────────────
BASH = r"""# bash completion for router (router-cli) — generated by `router completion bash`
# Install: router completion bash > ~/.local/share/bash-completion/completions/router
_router_complete() {
    local IFS=$'\n'
    COMPREPLY=($(command router completion complete --shell bash \
        --line "${COMP_LINE:0:COMP_POINT}" 2>/dev/null))
}
complete -F _router_complete router
"""

ZSH = r"""#compdef router
# zsh completion for router (router-cli) — generated by `router completion zsh`
# Install: router completion zsh > "${fpath[1]}/_router"  (or: source <(router completion zsh))
_router() {
    local -a reply
    reply=("${(@f)$(command router completion complete --shell zsh \
        --cur="${words[CURRENT]}" -- "${(@)words[1,CURRENT-1]}" 2>/dev/null)}")
    reply=(${reply:#})
    (( ${#reply} )) && compadd -a reply
}
if [[ "${funcstack[1]}" == "_router" ]]; then
    _router "$@"
else
    compdef _router router
fi
"""

FISH = r"""# fish completion for router (router-cli) — generated by `router completion fish`
# Install: router completion fish > ~/.config/fish/completions/router.fish
function __router_complete
    # An empty --cur=(...) vanishes in fish; the command then defaults it to "".
    command router completion complete --shell fish --cur=(commandline -ct) \
        -- (commandline -opc) 2>/dev/null
end
complete -c router -f -a '(__router_complete)'
"""

SCRIPTS = {"bash": BASH, "zsh": ZSH, "fish": FISH}
