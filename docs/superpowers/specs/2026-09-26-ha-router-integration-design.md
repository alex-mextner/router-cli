# ha-router: Home Assistant integration on top of router-cli — design

Date: 2026-09-26
Status: approved in conversation, pending written-spec review

## Goal

Turn router-cli into a universal CLI **and library** for home routers, and ship a
full Home Assistant integration (`ha-router`, installed via HACS) built on that library.
Anyone installs the integration directly in any Home Assistant; nothing depends on the
author's host machine. Supported routers are listed as a capability table; further
routers are a published roadmap, not implied scope.

## Decisions (from the design conversation)

| # | Question | Decision |
|---|----------|----------|
| 1 | Who is the integration for | Public, for everyone (HACS). Talks to routers itself. |
| 2 | Packaging | Separate repo `ha-router`; router-cli published to PyPI as `router-cli`; the integration pins `router-cli==X.Y` in `manifest.json`. netprint stays vendored inside router-cli. |
| 3 | Several routers in one home | One config entry per router device + one shared "Network" layer that merges clients from all routers by MAC. |
| 4 | UI | Sidebar panel "Network" (full page) + a compact Lovelace card (online now / new devices). |
| 5 | Existing host setup | One-off migration performed manually by the maintainer (throwaway script, never committed); afterwards the host timers, bridge endpoints and the old card are decommissioned. New users just install the integration. |

## Positioning and docs

- router-cli repo description: "Universal CLI and library for home routers" (plus the
  existing agent/`--json`/`--dry-run` points). No wording that ties the project to a
  specific router.
- README (router-cli and ha-router): a support table
  `router / capabilities / verified on (live device / emulator / fixtures)` and a
  separate "Roadmap" section (Keenetic, ASUS, TP-Link, FRITZ!Box, MikroTik).
- Currently supported drivers: Ubee EVW32C (cable gateway), Xiaomi MiWiFi / Mesh
  (AX3000 NE and family), OpenWrt (rpcd/ubus).

## Components

### netprint (unchanged role)
Stdlib device-identification engine + JSON rules. Consumed by router-cli.

### router-cli → PyPI `router-cli`
- Split into **core library** and **CLI wrapper**. Logic currently inside `commands/`
  moves into an importable API (`router_cli.api`) with no argv parsing and no printing:
  `detect(host)`, `connect(driver, host, credentials)`, `snapshot(router)` (clients,
  leases, status, topology, traffic where supported), `reserve/unreserve/replace`,
  `discover(interfaces)`, `classify(evidence)`, `scan(targets)`.
- Drivers stay synchronous (urllib); callers run them in an executor.
- Driver metadata: capabilities, default poll interval, and a `fragile` flag. A fragile
  router (Ubee) is never probed by discovery or scans and is polled no more often than its
  minimum interval; each operation is login → action → logout.
- Publishing: GitHub Actions release workflow builds sdist/wheel and publishes to PyPI via
  trusted publishing on tags.

### ha-router (new repo, HACS)
- **Router config entry** (one per router): config flow = host → auto-detect model → login
  (credentials stored in the config entry). Reauth flow on bad credentials (no retries
  that could lock the account). Per-driver `DataUpdateCoordinator` interval (Ubee 1 h +
  manual refresh; Xiaomi / OpenWrt 5 min). Router entities: status, WAN, uptime, firmware,
  refresh button.
- **Network layer** (one per HA instance, created with the first router entry):
  - merges clients from all routers by MAC; field precedence: IP / reservations from the
    DHCP-serving router, band / RSSI / traffic / node from the Wi-Fi router, presence from
    the freshest source;
  - passive discovery every 5 min (mDNS, SSDP, ARP/ping) on the adapters enabled in HA's
    network settings;
  - netprint classification, recomputed only when evidence changes;
  - storage: own SQLite file under `/config/.storage/ha_router/` with hourly buckets for
    presence and traffic, 90-day retention (not the HA recorder, to keep it small);
  - entities: one `device_tracker` per MAC (enabled by default only for reserved or
    user-named devices; others created disabled, so rotating private MACs don't flood the
    registry), sensors "online now", "new in 24 h", "IP conflicts";
  - services: `pin`, `unpin`, `pin_replace`, `alias` (name / icon), `scan`, `refresh`.
- **Frontend**: sidebar panel "Network" (evolution of the current card: filters, search,
  copy-on-click, grouping by access point, evidence, history and traffic charts, icon
  gallery, pin / replace flows) and a compact Lovelace card. Data via the integration's
  websocket commands and a "network updated" event, never via `/local` or rest_command.
  Both are shipped and registered by the integration itself.

## Data flow

1. A router coordinator calls `router_cli.api.snapshot()` in an executor.
2. The network layer merges the snapshot into the unified device list.
3. Discovery adds presence and evidence; netprint updates identity.
4. Hourly buckets are written; retention job trims > 90 days.
5. A websocket event notifies the panel/card; they re-render changed rows only.
6. Writes (pin etc.) go through services: per-router lock → write → one lease re-read →
   event. Fragile routers keep their login → action → logout discipline.

## Error handling

- Router unreachable: its entities go `unavailable`; the device list keeps working from
  discovery and last-known data. Exponential backoff, except fragile routers, which just
  wait for the next interval.
- Invalid credentials: HA reauth flow; no repeated login attempts.
- Reservation slots full: service error with the slot list; the panel offers replacement.
- IP conflict: sensor + HA Repairs issue.
- Classification failure for a device: that device shows as "unknown"; others unaffected.

## Testing

- router-cli: existing pytest suite on synthetic fixtures + tests for `router_cli.api`.
- **OpenWrt on real firmware**: CI job boots an official OpenWrt x86 image (QEMU, or rootfs
  in Docker) with rpcd/ubus and runs login, clients, leases, reserve/unreserve against it.
- Xiaomi: fixtures from the real mesh + a manual live run before release (read-only; the
  test mesh runs in AP mode, reservations live on the gateway).
- ha-router: `pytest-homeassistant-custom-component` — config flow incl. reauth,
  coordinators with fake drivers, merging, services, storage; hassfest + HACS validation
  in CI.
- Live acceptance at the maintainer's home: Ubee + Xiaomi mesh added via UI; migration
  verified (device count, aliases, icons, history compared before/after); panel checked in
  the browser; host timers / bridge / old card disabled only after that check.

## Migration (maintainer only, not shipped)

A throwaway script imports aliases, icons, notes and presence/traffic history from the
host router-cli SQLite DB into the integration storage, then compares counts. After
verification: stop and disable `router-inventory-update`, `router-scan`, `router-discover`
timers, remove `/network/*` bridge endpoints and rest_commands, remove the old card and
its view. The CLI stays installed for manual use.

## Out of scope

New router drivers (roadmap only), new monitoring features, changes to the host
infrastructure.
