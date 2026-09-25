# router-cli — agent guide

The home router from the command line: Ubee EVW32C cable gateways and OpenWrt. Python 3.11+,
fully typed (mypy strict), zero third-party runtime dependencies.

## Run it

```
./bin/router --help
./bin/router doctor                    # credentials, database, OUI table, router reachability
./bin/router devices --json
./bin/router reserve 02:00:00:00:00:01 192.168.0.250 --dry-run
```

## Layout

| Module | Responsibility |
| --- | --- |
| `cli.py` | dispatcher; commands self-register from `commands/` |
| `commands/` | one file per subcommand (`NAME`, `SUMMARY`, `run(argv) -> int`); `_`-prefixed files are helpers |
| `commands/_common.py` | shared options, router/driver/user resolution, output, and `run_plan` — the ONLY path a write takes |
| `commands/_area.py`, `_lists.py` | the generic `show / keys / set k=v` and `show / add / rm / clear` commands |
| `device_selector.py` | device arguments: MAC (any format) / current IP / name or unique prefix, resolved in the local DB |
| `completion.py` | shell completion engine (introspects each command's argparse parser) + bash/zsh/fish scripts |
| `http.py` | `HttpRequest` (read/login/logout/write kinds), `HttpTransport` (urllib, write gate, path guard), `DryRunTransport`, request rendering + redaction |
| `htmlform.py` | browser-accurate HTML form model (successful controls), tables, embedded `var x = '{json}'` blobs |
| `drivers/base.py` | `Capability`, `BaseDriver` (unsupported defaults), `WritePlan`/`Deferred`, `execute` |
| `drivers/ubee_evw32c.py` | the Ubee driver: session handling, parsers, write plans |
| `drivers/ubee_areas.py` | the Ubee web UI as data: pages, forms, field maps, apply flags, list pages, Wi-Fi/WPS JSON |
| `drivers/openwrt.py` | OpenWrt via rpcd `/ubus` JSON-RPC (session, luci-rpc, iwinfo, uci) |
| `drivers/__init__.py` | driver registry, aliases, GET-only `detect` |
| `models.py` | normalized dataclasses + MAC/IP helpers |
| `credentials.py` | `credentials.json` (0600/0700, keyed by host, `default`), optional OS keyrings |
| `inventory.py` | SQLite inventory, poll merging, the HA JSON contract |
| `scan.py` | concurrent port probe + HTTP title/server/favicon |
| `icons.py` + `data/icon_rules.json` | MDI icon rule engine |
| `oui.py` + `data/oui.tsv.gz` | IEEE MA-L vendor table (shipped; `router oui update` refreshes) |
| `install.py` | agent-skill registration (`router install-skill`) |
| `config.py` | XDG paths, env overrides, default gateway |

## Invariants

- **No read ever GETs a path containing logout/reboot/reset/restore/factory/default/
  upgrade/backup.** `http.check_path` enforces it for every transport, including test fakes.
  The only exception is a `kind="logout"` request (`BaseDriver.end_session`), which may name
  `logout` and nothing else from that list.
- **Close what you open.** On the Ubee the admin session is global to the LAN (an open
  session lets anyone use the admin pages). A driver that had to log in logs out when the
  command ends: every driver goes through `_common.open_driver`/`_common.track`, and
  `cli._dispatch` calls `_common.end_sessions()` in a `finally`. A session the driver found
  already open is someone else's and is left alone. `--keep-session` /
  `ROUTER_CLI_KEEP_SESSION=1` opts out.
- **Device arguments are selectors.** Anything that takes a device (`reserve`, `unreserve`,
  `alias`, `scan --ip`, `oui`, MAC lists) resolves it with `device_selector` — MAC in any
  format, current IP, or a name/unique prefix — against the local DB only, and gives the
  positional `metavar="DEVICE"` so shell completion offers inventory devices.
- **Drivers never send writes.** A write method returns a `WritePlan`; only
  `commands/_common.run_plan` executes one, and only after `--dry-run` was not given and,
  for `destructive` plans, `--yes` was. `HttpTransport` refuses `kind="write"` unless
  `run_plan` opened it. Logins are `kind="login"`; OpenWrt's ubus reads are `kind="read"`.
- **Writes start from the live page.** Parse the current form, change only the requested
  fields, submit `Form.successful()` — browser semantics: disabled controls, unchecked boxes
  and unclicked buttons are not sent. Never hand-build a field list for a form page.
- **Secrets never reach output unredacted.** Password-type fields, PSKs, RADIUS secrets, WPS
  PINs and ubus session ids are masked in `render_requests`, `to_dict`, `raw get/form` and
  every `show` unless `--show-secrets`. Credentials never go through argv or env.
- **The inventory JSON contract is stable.** Keys of `inventory list --json` (see
  `inventory.py` docstring) are consumed by a Home Assistant dashboard. Add fields only after
  agreeing with its consumer; never rename or drop one.
- **`router.host` / `RouterInfo.host` is the bare host** (`192.168.0.1`), the same key
  `credentials.json` uses.
- **Every failure is a `RouterCliError`** subclass with what/why/how and a stable exit code.
- **Stdlib only.** Do not add a runtime dependency.

## Test fixtures are synthetic — keep them that way

`tests/fixtures/ubee/*.asp` were generated from a real capture by a sanitizer that is NOT in
this repo: every MAC became `02:00:00:*`, public addresses `192.0.2.0/24`/`198.51.100.0/24`,
keys/serials/names replaced. `test_fixtures_are_synthetic` fails on any other MAC or IPv4.
Never commit a raw page from a real router; if you capture a new page, sanitize it the same
way (including per-octet IP inputs, which the guard cannot see).

## Adding things

- **A command**: drop a module in `commands/` with `NAME`, `SUMMARY`, `run(argv)`. A
  settings page is usually `run = _area.make(NAME, SUMMARY, _area.fixed("<area>"))`.
- **An Ubee setting**: add an `Area` (or a field `F`) in `drivers/ubee_areas.py`. Use
  `router raw form <Page>.asp` to see the fields and the page's JavaScript for the hidden
  apply flags.
- **A router family**: subclass `BaseDriver` in `drivers/`, declare `capabilities`, implement
  a GET-only `probe`, register in `drivers/__init__.py`, add synthetic fixtures and tests.
- **An icon rule**: `data/icon_rules.json` (first match wins).

## Checks

```
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
uv run --extra dev mypy router_cli
uv run --extra test pytest -q
```

Tests need no router and no network. Read the exit code of pytest itself, not of a pipe:
`pytest -q > /tmp/out.txt 2>&1; echo "PYTEST=$?"; tail -2 /tmp/out.txt`.

Live checks against a real router are GET-only (`status`, `devices`, `leases`, any `show`,
`inventory update`, `scan`) plus `--dry-run` for writes. Do not run a real write against
someone's router to "test" it.
