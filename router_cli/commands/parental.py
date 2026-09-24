"""parental — parental control switch and override password.

The keyword / domain lists are list settings: `router lists show keywords`,
`router lists add blocked-domains example.com`. Users and time policies are raw-field
areas: `router settings show parental-users`, `router settings show parental-time`.
"""

from __future__ import annotations

from . import _area

NAME = "parental"
SUMMARY = "show/set parental control (lists: `router lists`)"
run = _area.make(
    NAME,
    SUMMARY,
    _area.fixed("parental"),
    epilog=(
        "lists:  router lists show keywords|blocked-domains|allowed-domains|trusted-computers\n"
        "users:  router settings show parental-users\n"
        "time:   router settings show parental-time"
    ),
)
