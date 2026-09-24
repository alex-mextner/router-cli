"""commands — one module per subcommand, discovered automatically.

A command module declares ``NAME`` (what the user types), ``SUMMARY`` (the one line shown
in ``router --help``) and ``run(argv) -> int``. The dispatcher finds it by scanning this
package, so a new command is a new file and nothing else. Modules starting with ``_`` are
shared helpers, not commands.
"""

from __future__ import annotations
