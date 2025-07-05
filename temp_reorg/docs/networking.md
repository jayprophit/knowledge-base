---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Networking for networking.md
title: Networking
updated_at: '2025-07-04'
version: 1.0.0
---

# Networking Module — Backend API

> **See also:** [backend/src/networking.md](ai/networking.md)

This document covers the backend networking, VPN, DNS, and VOIP API for the AI assistant.

## Endpoints
- `POST /vpn/connect` — Connect to a VPN (OpenVPN/WireGuard)
- `POST /dns/set` — Set DNS servers (system/DoH/DoT)
- `POST /voip/start` — Start a VOIP client (stub)
- `GET /network/status` — Network diagnostics

## Usage
- For agent-driven secure networking and privacy controls.
- Requires backend permissions for real VPN/VOIP/DNS changes.

## Implementation
- See [`networking.py`](../../backend/src/networking.py) for code and extension points.
- See [backend/src/networking.md](ai/networking.md) for full details and examples.

---

**For more, see the main [backend API documentation](backend_api.md) and `/docs/` for advanced usage.**
