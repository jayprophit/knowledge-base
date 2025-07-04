---
id: web-networking-dns
title: DNS (Domain Name System)
description: Documentation on DNS principles, resolution process, and implementation examples
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
  - dns
  - networking
  - system_design
relationships:
  prerequisites: []
  successors: []
  related:
    - ip_address.md
    - proxy.md
    - http.md
---

# DNS (Domain Name System)

## Overview

DNS translates human-readable domain names (e.g., example.com) into IP addresses that computers use to identify each other on the network.

## How DNS Works
1. User enters a domain in the browser.
2. Browser checks local cache, then OS cache, then router, then ISP DNS server.
3. If not cached, ISP DNS server queries root, TLD, and authoritative DNS servers.
4. IP address is returned and used for connection.

## Record Types
- **A:** Maps domain to IPv4 address
- **AAAA:** Maps domain to IPv6 address
- **CNAME:** Alias for another domain
- **MX:** Mail exchange server
- **TXT:** Arbitrary text data (often for verification)

## Example: Lookup IP in Python
```python
import socket
print(socket.gethostbyname('example.com'))
```

## Best Practices
- Use reputable DNS providers
- Implement DNSSEC for security
- Use short TTLs for dynamic content

## Related Topics
- [IP Address](ip_address.md)
- [Proxy](temp_reorg/docs/web/system_design/proxy.md)
- [HTTP](http.md)

## References
- [Wikipedia: DNS](https://en.wikipedia.org/wiki/Domain_Name_System)
- [IETF DNS Spec](https://datatracker.ietf.org/doc/html/rfc1035)
