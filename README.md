# router

The home router from the command line — every page of its web UI as a command, with
`--json` for agents and Home Assistant, and `--dry-run` for every change so you see the exact
request before it is sent.

```bash
router devices                                   # who is connected right now
router leases                                    # DHCP leases + static reservations
router reserve 02:00:00:00:00:01 192.168.0.250 --name printer --dry-run
router wifi                                      # radios, SSIDs, channels (keys hidden)
router status                                    # model, firmware, uptime, WAN, DOCSIS
router inventory update && router inventory list --json --filter active
router scan --all-online                         # which devices run a web UI, and what
```

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/alex-mextner/router-cli/main/install.sh | bash
router login        # asks for the admin password, checks it, stores it (0600)
router doctor       # what works, what does not, and how to fix it
```

Python 3.11+ and nothing else: the package has zero third-party dependencies (HTTP is
`urllib`, HTML is `html.parser`, storage is `sqlite3`). The installer also registers
`router` as an agent skill so coding agents find it on their own (`ROUTER_NO_SKILL=1` skips
that).

## What it actually fixes

**The web UI is the only API.** Consumer gateways like the Ubee EVW32C have no API at all —
thirty-odd `.asp` pages, each with a form that posts to `/goform/<Page>`, validated mostly
by the page's own JavaScript. `router` reads those pages and submits those forms the way a
browser would, so "pin this IP", "open this port" or "turn off WPS" is one command instead
of five clicks through a UI from 2013.

**Writes you can review first.** Every change is computed from the page's *current* form —
never from a remembered field list — and `--dry-run` prints the exact request:

```
$ router reserve 02:00:00:00:00:01 192.168.0.250 --dry-run
DRY RUN - nothing was sent.
plan: reserve 192.168.0.250 for 02:00:00:00:00:01 in static lease slot 8
  note: the page submits all eight slots at once; untouched slots are resent as-is

POST http://192.168.0.1/goform/UbeeLanStaticLease
Content-Type: application/x-www-form-urlencoded

  MacAddStaticLease01MA0=02
  ...
  MacAddStaticLease08MA0=02
  ...
  IpAddStaticLease8IPX=192.168.0.250
  MY_POOL_START_IP=192.168.0.10
  MY_POOL_END_IP=192.168.0.254
  StaticLeaseStatusFlag=0
```

Changes that can cut you off or expose a device (Wi-Fi, LAN address, DHCP off, port
forwards, DMZ, reboot) also need `--yes`. Passwords and keys are redacted in every output unless `--show-secrets`.

**Things you must never do by accident, you cannot do at all.** No read ever touches a
path containing `logout`, `reboot`, `reset`, `restore`, `factory`, `default`, `upgrade` or
`backup` on a GET. There is no factory reset command. The one deliberate exception is the
session logout below, sent as its own request kind that may name `logout` and nothing else.

**It closes the door behind itself.** The Ubee's admin session is *global*: while anyone is
logged in, every device on the LAN can open the admin pages without a password. So when a
command had to log in, `router` logs out again when it ends (success or error). When a
session was already open — someone else is logged in — it reads through that session and
leaves it alone. `--keep-session` (or `ROUTER_CLI_KEEP_SESSION=1`) skips the logout, e.g.
for a burst of commands.

**One JSON shape for every router.** Devices, leases, status and the inventory come out the
same from an Ubee cable gateway and an OpenWrt box, so a dashboard or an agent is written
once.

## Devices, leases, reservations

```bash
router devices --json      # mac, ip, hostname, interface (wifi/lan), band, rssi, online
router leases              # kind: dynamic | reservation | static (device-side static IP)
router reserve <mac> <ip> [--name N] [--dry-run]
router unreserve <mac> [--dry-run]
```

On the Ubee a static lease has no name field; `--name` is kept as a local alias in the
inventory instead (and shows up as the device's `hostname` there).

## Settings

Every settings page is an *area* with the same three verbs:

```bash
router dhcp                          # show
router dhcp keys                     # what can be set, with choices
router dhcp set lease_time=7200 --dry-run
router wifi set --band 5g channel=44 --dry-run
router wifi set --band 2g security=wpa-personal psk=... --dry-run --yes
```

| Command | What |
| --- | --- |
| `lan` | LAN address, DNS handed to clients, domain |
| `dhcp` | DHCP server on/off, pool, lease time |
| `wan` | WAN address, gateway, DNS (read-only) |
| `wifi` | radios, SSIDs, mode, channel, width, power, security (`--band 2g/5g`) |
| `wifi-acl` | per-band MAC access control: mode, `add/rm/clear` |
| `wps` | WPS on/off, PBC/PIN mode, press Connect |
| `port-forward` | `list`, `add <ext> <ip> [<int>]`, `rm <n>`, `clear` |
| `filter ip/port/mac` | IP-range, port and MAC filters |
| `firewall` | firewall level, fragment / port-scan / flood protection |
| `dmz` | DMZ host (`set host=192.168.0.50` / `host=off`) |
| `options` | UPnP, multicast, IPSec/PPTP passthrough, WAN ping blocking |
| `parental` | parental control; lists via `router lists` |
| `vpn` | IPSec endpoint, tunnels |
| `nas` | USB sharing: Samba, FTP, DLNA, credentials |
| `telephony`, `cm` | MTA status; DOCSIS channels, levels, provisioning |
| `password` | admin password (prompted; updates the stored one) |
| `reboot` | reboot (always `--yes`) |
| `settings` | every area by name, including raw-field pages (`parental-users`, `vpn-ipsec`, ...) |
| `lists` | every list setting by name (`mac-filter`, `keywords`, `blocked-domains`, ...) |
| `raw` | `pages`, `get <page>`, `form <page>`, `post <page> k=v`, `call <obj> <method>` |

`router raw form <page>` shows every field of a page exactly as a browser would submit it —
the fastest way to add support for a setting this tool does not name yet.

## Inventory and discovery

A router only knows who is connected *now*. `router inventory update` merges each poll into a
local SQLite database (`~/.local/share/router-cli/inventory.sqlite3`, or `$ROUTER_CLI_DB`)
that remembers every MAC: first and last seen, every IP and name it has had, its static
lease, the manufacturer (from the IEEE OUI registry, shipped and refreshable with
`router oui update`), whether the MAC is randomised, and the web UIs `router scan` found on
it.

```bash
router inventory update [--resolve]      # poll; --resolve adds reverse-DNS/mDNS names
router inventory list --json [--filter recent|active|all|reserved|new] [--since 24h]
router scan --all-online --json          # probe popular web ports on every online device
router scan --ip 192.168.0.50
router alias 02:00:00:00:00:05 --name "3D printer" --icon mdi:printer-3d
```

`inventory list --json` is a stable contract (Home Assistant dashboards read it):

```json
{
  "generated_at": "2026-01-01T12:00:00+00:00",
  "router": {"driver": "ubee_evw32c", "model": "EVW32C-0N", "host": "192.168.0.1"},
  "devices": [{
    "mac": "02:00:00:00:00:05", "ip": "192.168.0.50", "hostname": "3D printer",
    "names": ["3D printer"], "vendor": "Raspberry Pi Trading", "random_mac": false, "interface": "lan",
    "online": true, "first_seen": "...", "last_seen": "...", "reserved_ip": "192.168.0.50",
    "ip_history": [{"ip": "192.168.0.50", "first_seen": "...", "last_seen": "..."}],
    "icon": "mdi:printer-3d",
    "services": [{"port": 7125, "scheme": "http", "url": "http://192.168.0.50:7125/",
                  "title": "Moonraker", "server": "TornadoServer/6.2",
                  "favicon_data_url": null, "checked_at": "..."}]
  }]
}
```

`icon` is a Material Design Icon chosen by a data-driven rule table
(`router_cli/data/icon_rules.json`): open services and page titles first (8123 → Home
Assistant, 7125/Moonraker/fluidd → 3D printer, 32400 → Plex, 631 → printer, ESPHome →
chip), then host name patterns, then the manufacturer, and finally "randomised MAC → phone".
Add or override rules in `~/.config/router-cli/icon_rules.json` (same shape, tried first);
`router alias <mac> --icon` beats every rule.

`scan` only ever sends a GET for `/` and for the favicon to each open port (HTTPS first on the
usual TLS ports, certificates not verified — LAN devices are self-signed). Favicons are
stored as `data:` URLs capped at 32 KiB.

## Credentials

`router login` asks for the password (getpass — never argv or the environment), verifies it
by logging in, and writes `~/.config/router-cli/credentials.json`:

```json
{"routers": {"192.168.0.1": {"driver": "ubee_evw32c", "username": "admin", "password": "..."}},
 "default": "192.168.0.1"}
```

The directory is 0700, the file 0600, and `router` refuses to read the file if it ever becomes
group- or world-readable. `default` picks the router when `--host` is omitted. You may write
the file by hand. `router login --store keyring` puts the password in the OS keyring instead
(Secret Service via `secret-tool`, the macOS keychain, or Windows Credential Manager); a
password in the file always wins. `router logout` forgets the stored credentials; it sends
nothing to the router.

Drivers log in by themselves when there is no session, and log out again when the command
ends (see "It closes the door behind itself" above; `--keep-session` keeps it open). On the
Ubee the admin session is global, so while anything else is logged in, reads work without
any stored credentials — and router-cli leaves that other session alone.

Routers with exotic logins (captchas, JavaScript-computed tokens) could be supported by
capturing the session with a real browser (e.g. `agent-browser` or Chrome) — that would be the
way to write such a driver. Neither supported family needs it: the Ubee is a plain form login,
OpenWrt a JSON-RPC one.

## Supported routers

| Router | Driver | Status |
| --- | --- | --- |
| Ubee EVW32C-0N / EVW32C-0S (cable gateway, Broadcom firmware) | `ubee_evw32c` (alias `ubee`) | every page mapped; reads verified live; writes built from live forms, verified against captures |
| OpenWrt with LuCI (rpcd `/ubus` JSON-RPC) | `openwrt` | status, devices, leases, reservations, port forwards, uci areas; verified against fixtures only |

`router drivers` prints the full capability matrix; `router detect` identifies a host without
logging in.

### Adding a router

A driver is one module in `router_cli/drivers/` that subclasses `BaseDriver`, declares its
`capabilities`, and fills in the normalized models (`Device`, `Lease`, `Reservation`,
`Status`, ...). Writes return a `WritePlan` — the exact requests — never send anything
themselves. Register it in `drivers/__init__.py`, add a GET-only `probe()` so `router detect`
recognises it, and add synthetic page fixtures plus tests. See `AGENTS.md` for the module map
and the Ubee driver as the reference implementation (its whole UI is data in
`drivers/ubee_areas.py`).

## Exit codes

`0` ok · `2` bad usage · `3` needs `--yes` · `4` unknown command/driver/key · `5` no such
lease/rule/entry · `6` this router cannot do that · `7` router unreachable · `8` not logged
in / login rejected · `10` router answered something unusable.

## Requirements

Python 3.11+. Linux, macOS or Windows. A machine on the router's LAN.

MIT.
