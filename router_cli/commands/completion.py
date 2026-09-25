"""completion — print a shell completion script (bash, zsh, fish).

    router completion bash > ~/.local/share/bash-completion/completions/router
    router completion zsh  > ~/.local/share/zsh/site-functions/_router   (a dir in $fpath)
    router completion fish > ~/.config/fish/completions/router.fish
    router completion devices            what DEVICE arguments complete to

Completes commands, verbs, flags, flag choices, and device names / MACs / IPs from the
local inventory database (never from the router). `install.sh` installs the scripts.
"""

from __future__ import annotations

import argparse

from .. import completion
from . import _common as C

NAME = "completion"
SUMMARY = "print a bash/zsh/fish completion script (devices complete from the local DB)"


def run(argv: list[str]) -> int:
    if argv and argv[0] == "complete":
        return _complete(argv[1:])
    p = C.parser(NAME, SUMMARY, epilog=__doc__.split("\n\n", 1)[1] if __doc__ else None)
    p.add_argument("shell", choices=("bash", "zsh", "fish", "devices"))
    args = p.parse_args(argv)
    if args.shell == "devices":
        print("\n".join(completion.device_candidates()))
    else:
        print(completion.SCRIPTS[args.shell], end="")
    return 0


def _complete(argv: list[str]) -> int:
    """What the scripts call on TAB (not meant to be typed):

    bash:       complete --shell bash --line "<COMP_LINE up to the cursor>"
    zsh, fish:  complete --shell zsh|fish --cur=<word being typed> -- <words before it>
    """
    p = argparse.ArgumentParser(prog="router completion complete")
    p.add_argument("--shell", default="bash", choices=("bash", "zsh", "fish"))
    p.add_argument("--line")
    p.add_argument("--cur", default="")
    p.add_argument("words", nargs="*")
    args = p.parse_args(argv)
    if args.line is not None:
        words, current = completion.split_line(args.line)
    else:
        words, current = list(args.words), args.cur
    candidates = completion.complete(words, current)
    if args.shell == "bash":
        candidates = completion.for_bash(candidates, current)
    if candidates:
        print("\n".join(candidates))
    return 0
