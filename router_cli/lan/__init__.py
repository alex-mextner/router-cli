"""lan — passive-ish discovery from the machine router-cli runs on, without asking the router.

Everything here talks to the LAN directly, never to the gateway's web server:

- :mod:`.netinfo`  this host's interface, address, subnet, gateway and MAC
- :mod:`.sweep`    ICMP echo sweep of the subnet (with reply TTLs) and the kernel ARP table
- :mod:`.mdns`     mDNS / DNS-SD browse (multicast + direct unicast queries to each host)
- :mod:`.ssdp`     SSDP M-SEARCH and UPnP device descriptions
- :mod:`.netbios`  NetBIOS node-status names

All of it is stdlib sockets; Linux only for the ARP table and interface details.
"""
