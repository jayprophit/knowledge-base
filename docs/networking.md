# Networking Module — Backend API

> **See also:** [backend/src/networking.md](../backend/src/networking.md)

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
- See [`networking.py`](../backend/src/networking.py) for code and extension points.
- See [backend/src/networking.md](../backend/src/networking.md) for full details and examples.

---

**For more, see the main [backend API documentation](backend_api.md) and `/docs/` for advanced usage.**
