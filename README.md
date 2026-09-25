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
that), and installs shell completion for bash (and zsh / fish when present;
`ROUTER_NO_COMPLETION=1` skips it):

```bash
router completion bash > ~/.local/share/bash-completion/completions/router
router completion zsh  > ~/.local/share/zsh/site-functions/_router   # a dir in your $fpath
router completion fish > ~/.config/fish/completions/router.fish
```

Completion covers commands, verbs, flags and their choices, and device names, MACs and IPs
from the local inventory database — pressing TAB never sends anything to the router.

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
router reserve <device> [ip] [--name N] [--dry-run]   # no ip: pin its current address
router unreserve <device> [--dry-run]
```

Wherever a command wants a device (`reserve`, `unreserve`, `alias`, `scan --ip`, `oui`,
`wifi-acl add|rm`, `filter mac add|rm`, `lists add|rm` of a MAC list) it takes any of:

- a MAC in any common spelling: `aa:bb:cc:dd:ee:ff`, `AA-BB-CC-DD-EE-FF`, `aa_bb_cc_dd_ee_ff`,
  `aabb.ccdd.eeff`, `aabbccddeeff`, any case;
- a current IP (`192.168.0.25`: the device the inventory has at that address);
- a name — the local alias, the router's host name or any name the inventory has seen —
  case-insensitive, exact match first, then a unique prefix (`router reserve print`). An
  ambiguous name is an error that lists the candidates.

Names and IPs are looked up in the local inventory (`router inventory update` fills it), never
on the router.

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

A router only knows who is connected *now*. router-cli keeps a local SQLite database
(`~/.local/share/router-cli/inventory.sqlite3`, or `$ROUTER_CLI_DB`) that remembers every MAC:
first and last seen, every IP and name it has had, its static lease, the manufacturer (IEEE OUI
registry, shipped, `router oui update` refreshes it), whether the MAC is randomised, the web
UIs `router scan` found on it, what it announces about itself on the LAN, how it is connected,
a presence sample every few minutes and its traffic counters.

Two things fill it:

- **`router inventory update`** polls the router (its client table and static leases). Some
  gateways — the Ubee EVW32C — hang when polled often: run this hourly, not every minute.
- **`router discover`** sweeps the LAN *from this machine* and never talks to the router's web
  server: an ICMP echo sweep with reply TTLs plus the kernel ARP table (presence), mDNS/DNS-SD
  (multicast and direct unicast questions, reverse lookups), SSDP + UPnP descriptions, NetBIOS
  names, the public `init_info` and `topo_graph` of Xiaomi mesh nodes (model, firmware,
  placement), Moonraker's `/printer/info`, a health check of every known web service, a web-UI
  scan of devices that came back online since the last scan, and — with credentials — the
  Xiaomi mesh client list (node, band, signal, traffic). Home Assistant's device registry
  (`--ha-config` / `ROUTER_CLI_HA_CONFIG`, read-only) adds what you already told HA: names,
  rooms, models, firmware — matched by MAC, by a device id the device announces (Cast UUID,
  Yandex Station id, UPnP UDN), by the address in the integration's config (also onto the
  private MAC a Chromecast uses on Wi-Fi), or by the companion app's name. About 10 s; meant
  for a 5-minute timer. Once it runs, sweeps (not router polls) decide who is online, and the
  machine running it is always online.

```bash
router discover [--json] [--ha-config ~/homeassistant]    # the 5-minute sweep
router inventory update [--resolve]      # poll the router (hourly)
router inventory list --json [--filter recent|active|all|reserved|new] [--since 24h]
                         [--no-favicons] [--all-interfaces]
router inventory history <device> --json [--days 7] [--bucket 1h]
router inventory stats --json [--days 7]
router scan --all-online --json          # web UIs + fingerprint ports of every online device
router scan --ip 192.168.0.50            # or --ip <mac or name>
router alias 02:00:00:00:00:05 --name "3D printer" --icon mdi:printer-3d
```

The gateway (and any interface of it, recognised by its neighbouring MAC) only ever gets ARP
and ping from `discover`; `scan --all-online` skips it and `scan --ip <gateway>` needs
`--force`. An address two devices answer for (an IP conflict) is detected from the sweeps and
reported by `stats`; an mDNS/SSDP answer from it is attributed only when exactly one of the
devices sharing it has the brand the answer names (a Yandex Station and a Xiaomi node on one
address: the `_yandexio` answer is the Yandex's). A Xiaomi mesh node whose IPv4 address is
shared is asked for its public topology over IPv6 link-local instead (its EUI-64 address).

### What each device is

Every device is classified by [netprint](https://github.com/alex-mextner/netprint) (vendored in
`router_cli/_vendor/netprint`, refreshed with `scripts/vendor-netprint.sh`): ~580 data-driven
rules over the OUI vendor, randomised MACs, host names, mDNS services and TXT records (Apple
model ids, ESPHome, Cast, Yandex, Moonraker, HomeKit...), UPnP descriptions, web titles and
page markers, open ports (a connect-only probe of the ports the rules know: 62078 iOS, 6053
ESPHome, 6668 Tuya, 1961 Yandex, 7125 Moonraker, ...), SSH banners, TTL, NetBIOS, Xiaomi mesh
facts and the Home Assistant registry. Each device gets a `category`, an `icon`, a
`confidence`, the `evidence` behind it, its identity — `brand` (from what the device says,
not only the OUI: a private-MAC Chromecast is Google), `product`, `model`, `model_id`, `os`,
`firmware`, `friendly_name`, `location` (a mesh node's placement, or the Home Assistant room)
— and a `display_name` composed from them: "Google Chromecast «Living room»", "Apple MacBook
Pro 16″ «Sam's MBP»" (the friendly name is shown when it says something the model does not).
`router alias --name` sets the friendly name; `--icon` beats every icon; rules in
`~/.config/router-cli/icon_rules.json` (legacy shape) beat the classifier's icon.

One physical device with several MACs (this machine's Ethernet + Wi-Fi, a TV's two NICs, the
gateway's second interface) is listed once, with every MAC in `interfaces`.

### Wi-Fi topology and traffic (Xiaomi mesh)

A Xiaomi / Redmi mesh in access-point mode knows every Wi-Fi client — node, band, signal — and
per-client traffic counters; the gateway sees bridged Wi-Fi clients as "LAN" and has no
per-client counters. With the mesh's admin password stored, `discover` reads it every run:

```bash
router login --driver miwifi --host 192.168.31.1 --no-default   # the main mesh node
```

(An access point never becomes the default router. Xiaomi firmware redirects its web API to
HTTPS with a self-signed certificate: router-cli follows that same-host upgrade and does not
verify certificates of private addresses.) Even without a password, every node's public
`topo_graph` gives its placement ("Bedroom" — the `location` field), its backhaul and the
node names used as `connection.via_name`. Without it, `connection` is a heuristic
(`source: "heuristic"`: randomised MAC or phone/IoT category → Wi-Fi, motherboard NIC → wired,
else unknown) and `traffic` is `null`.

### The JSON contract

`inventory list --json` is a stable contract (Home Assistant dashboards read it); keys are only
ever added:

```json
{
  "generated_at": "2026-01-01T12:00:00+00:00",
  "last_poll": "2026-01-01T11:00:00+00:00",
  "last_discover": "2026-01-01T11:58:00+00:00",
  "router": {"driver": "ubee_evw32c", "model": "EVW32C-0N", "host": "192.168.0.1"},
  "devices": [{
    "mac": "02:00:00:00:00:05", "ip": "192.168.0.50", "hostname": "3D printer",
    "names": ["3D printer"], "vendor": "AMPAK", "random_mac": false, "interface": "lan",
    "online": true, "first_seen": "...", "last_seen": "...", "reserved_ip": "192.168.0.50",
    "ip_history": [{"ip": "192.168.0.50", "first_seen": "...", "last_seen": "..."}],
    "icon": "mdi:printer-3d-nozzle",
    "services": [{"port": 7125, "scheme": "http", "url": "http://192.168.0.50:7125/",
                  "title": "Moonraker", "server": "TornadoServer/6.2",
                  "favicon_data_url": null, "checked_at": "...",
                  "reachable": true, "http_status": 200, "error": null}],
    "category": "3d-printer", "confidence": 0.99, "label": "Klipper printer (Moonraker)",
    "evidence": [{"source": "ports", "detail": "port 7125 (Moonraker)", "weight": 0.9}],
    "alternatives": [{"category": "raspberry-pi", "confidence": 0.2}],
    "display_name": "3D printer", "pinnable": true, "is_network_gear": false, "is_self": false,
    "connection": {"type": "wifi", "via": "02:00:00:00:00:a1", "via_name": "hall node",
                   "band": "5", "rssi": -58, "source": "miwifi"},
    "traffic": {"rx_bytes": 123456, "tx_bytes": 7890, "rx_rate": 1200, "tx_rate": 300,
                "updated_at": "...", "source": "miwifi"},
    "interfaces": [{"mac": "02:00:00:00:00:05", "ip": "192.168.0.50", "online": true,
                    "name": null, "type": "wifi"}],
    "same_device_as": null,
    "brand": "Snapmaker", "product": "Snapmaker U1", "model": "Snapmaker U1",
    "model_id": null, "friendly_name": "3D printer", "location": "Workshop",
    "os": "Klipper", "firmware": "1.4.1", "oui_vendor": "AMPAK"
  }]
}
```

- `vendor` is the `brand` when one is known (else the OUI vendor); `oui_vendor` is always the
  raw OUI vendor (`null` for a randomised MAC).
- `services[].expected: true` marks a web UI the kind of device is known to serve (a Creality
  printer's `:80`) that no scan confirmed yet; an offline device keeps its services with
  `reachable: false, error: "offline"`. `ip` falls back to the reserved address of a device
  never seen online.

- `pinnable` is false for randomised MACs (a reservation would not survive the next rotation).
- `services[].reachable/http_status/error` come from the last scan or the 5-minute health
  check: `error` is `refused`, `timeout`, `tls`, `reset`, `unreachable` or `http`; a service
  that stops answering stays listed with `reachable: false`.
- `connection.type` is `wired`, `wifi` or `unknown`; `band` is `"2.4"`, `"5"`, `"6"` or null.

`inventory history <device> --json` → `{"mac", "days", "bucket_s", "buckets": [{"t",
"online_ratio", "samples", "rx_bytes", "tx_bytes"}]}`: the share of sweeps in each bucket that
saw the device (`null` when no sweep ran) and the bytes counted in it (`null` without traffic
data).

`inventory stats --json` → `{"online_now", "online_avg", "per_hour": [{"t", "online",
"samples"}], "top_traffic": [{"mac", "display_name", "rx_bytes", "tx_bytes"}], "network_gear":
[{"mac", "ip", "display_name", "category", "role", "online"}], "unexpected_network_gear",
"ip_conflicts": [{"ip", "macs", "flips", "source"}], "sweeps", "since"}`. `role` is `gateway`,
`mesh-node` or `other`: a non-zero `unexpected_network_gear` means someone plugged in another
router or access point.

`scan` only ever sends a GET for `/` and for the favicon to each open web port (HTTPS first on
the usual TLS ports, certificates not verified — LAN devices are self-signed); fingerprint
ports are connect-only, except that the first line an SSH server sends by itself (its banner:
"SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13") is read. Favicons are stored as `data:` URLs capped
at 32 KiB.

### Timers

`contrib/systemd/` has user units: `router-discover.timer` (every 5 min),
`router-inventory-update.timer` (hourly router poll) and `router-scan.timer` (every 6 h):

```bash
cp contrib/systemd/router-* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now router-discover.timer router-inventory-update.timer router-scan.timer
```

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
| Xiaomi / Redmi routers and mesh systems (LuCI JSON API; access-point mode too) | `miwifi` (alias `xiaomi`) | read-only: Wi-Fi clients, mesh node, band, signal, per-client traffic; login verified by fixtures only |

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
