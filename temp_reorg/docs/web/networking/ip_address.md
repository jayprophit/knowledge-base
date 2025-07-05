---
id: web-networking-ip-address
title: IP Address Fundamentals
description: Documentation on IP address concepts, types, and usage in networked systems
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
- ip_address
- networking
- system_design
relationships:
  prerequisites: []
  successors: []
  related:
  - dns.md
  - proxy.md
  - http.md
---

# IP Address Fundamentals

## Overview

An IP address is a unique identifier assigned to devices on a network. It enables communication between hosts on the internet or local networks.

## Types of IP Addresses
- **IPv4:** 32-bit address, e.g., 192.168.1.1
- **IPv6:** 128-bit address, e.g., 2001:0db8:85a3:0000:0000:8a2e:0370:7334

## Classes and Ranges
- **Class A:** 1.0.0.0 to 126.255.255.255
- **Class B:** 128.0.0.0 to 191.255.255.255
- **Class C:** 192.0.0.0 to 223.255.255.255
- **Private Ranges:** 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16

## Subnetting
Subnetting divides a network into smaller segments for security and efficiency.

## Example: Get Local IP in Python
```python
import socket
print(socket.gethostbyname(socket.gethostname()))
```

## Best Practices
- Use private IPs for internal networks
- Implement NAT for internet access
- Use IPv6 for future-proofing

## Related Topics
- [DNS](dns.md)
- [Proxy](proxy.md)
- [HTTP](http.md)

## References
- [Wikipedia: IP Address](https://en.wikipedia.org/wiki/IP_address)
- [IETF IPv6 Spec](https://datatracker.ietf.org/doc/html/rfc8200)
