# Ubee EVW32C: LAN DNS written with `router lan set` does not stay

**Status: not fixed, not fixable from router-cli as far as the evidence shows.** The request
router-cli sends is what a browser sends; the gateway accepts it and, within minutes, shows the
operator's DNS servers again. Nothing in router-cli changes that value afterwards.

Firmware 2.4.1015-SIP (EVW32C-0N), cable operator with DHCP-provisioned DNS. One evening, two
attempts, local times. "Restart" means the gateway's "System Up Time" counter reset.

## What was observed

| Time | Event |
| --- | --- |
| 23:02:31 | `lan set dns1=dns2=dns3=<LAN resolver>`: accepted, immediate read-back shows the new values |
| ~23:03:19 | restart A (reconstructed: uptime 374 s read at ~23:09:33) |
| by 23:14:14 | the read before the second attempt shows the operator's three DNS servers again |
| 23:20:12 | `lan set dns1=<LAN resolver> dns2=0.0.0.0 dns3=0.0.0.0`: accepted, immediate read-back matches |
| 23:20:22 to 23:21:07 | four reads in a row fail (the web server does not answer) |
| 23:20:57 | restart B (read at 23:32:54: uptime 717 s) |
| 23:21:21 to 23:21:42 | three reads show the new DNS (24 to 45 s after restart B) |
| 23:21:54 | read shows the operator's DNS again (57 s after restart B); NetworkManager on this host reports internet lost the same second and regained at 23:22:58 |
| 23:38:32 to 23:39:33 | internet lost on this host again; no write |
| 23:41:42 | restart C, **no write** (read at 23:47:10: uptime 328 s) |
| 23:54:38 to 23:56:46 | internet lost on this host again; no write |
| 00:03:20 | restart D, **no write** (read at 00:28:32: uptime 25 min 12 s) |

Read-only checks made afterwards (one login each, logged out again):

* The LAN Setup page read with an independent parser and read through the driver agree on
  `dns1..3`, every time.
* The set of successful controls a browser would submit for the LAN Setup form equals the field
  list router-cli logged for the write.
* DOCSIS side when read (23:50 and 00:28): 24/24 downstream channels locked, SNR about 40 dB,
  no uncorrectable codewords, upstream power 43 to 46 dBmV, 6 of 8 upstream channels locked.
  A snapshot says nothing about the earlier restarts.

## What that means, and what it does not

* **Read side and write side of router-cli are not the cause.** Both match an independent
  model of the page, and the gateway acted on the request (the read-back changed, and after the
  second write the new value was still shown 24 to 45 s after restart B).
* **Four restarts within an hour** (intervals of about 18, 21 and 22 minutes), two of them with
  no write. The kernel logged no link change on this host's interface (it may sit behind a
  switch). Any LAN DNS written through this form should be treated as lasting only until the
  next restart, whatever its cause. Why the gateway restarts, and whether on a schedule, is
  unknown.
* **Inferences, not observations:** that the value reached the gateway's stored configuration
  (it was only seen on the page), and that the gateway replaced it when its WAN side came back
  (the timing matches an internet loss seen from this host). The first write has no reading
  between its restart and the revert.
* **Not proven:** that Apply itself restarts the gateway (the two writes were each followed by a
  restart 48 and 45 s later, but restarts also happen unprompted), and whether the operator's
  provisioning or the gateway's own WAN handling puts the DNS back. Telling those apart needs
  another write on purpose or the cable modem's console, neither of which is a read.

## Checking that a DNS write stuck

The read-back printed by `router lan set` is taken a second after Apply and proves nothing.
To check later, with no write:

```bash
router status --json     # uptime_s: has the gateway restarted since the write?
router lan show          # dns1..3 as the page renders them now
router wan               # the DNS servers the WAN side learned
```

## If a durable LAN resolver is needed

None of these has been tried; each changes the network and needs the owner's decision.

* Run DHCP elsewhere: turn the gateway's DHCP server off (`router dhcp set enabled=no --yes`)
  and hand out the resolver from that DHCP server. The gateway's DNS field is then not involved.
* Put the gateway in bridge mode behind a router that keeps its own DNS setting.
* Ask the operator why the gateway restarts every 20 minutes or so, and whether the DNS in the
  provisioning can be left to the customer.
