# Backend API — Knowledge Base Assistant

> **See also:** [backend/src/README.md](../backend/src/README.md)

This document summarizes the backend API endpoints, modules, and integration points for the cross-platform AI assistant.

## API Endpoints
- `/search`, `/categories`, `/generate_code`, `/analyze_multimodal`
- `/web-search`, `/extract-content`, `/scrape` *(planned)*
- `/automate` — Web automation (Playwright/Selenium)
- `/vpn/connect`, `/dns/set`, `/voip/start`, `/network/status`

See [backend/src/README.md](../backend/src/README.md) for full endpoint descriptions and usage examples.

## Related Modules
- [`web_search.py`](../backend/src/web_search.py) — Tor/Brave/Decentralized search
- [`web_scraper.py`](../backend/src/web_scraper.py) — Advanced scraping
- [`web_automation.py`](../backend/src/web_automation.py) — Browser automation
- [`networking.py`](../backend/src/networking.py) — VPN, DNS, VOIP, diagnostics

## Networking
See [networking.md](networking.md) for VPN, DNS, VOIP, and diagnostics API details.

## Usage & Security
- CORS enabled for cross-platform clients
- Tor/VPN for privacy
- No authentication by default — add before production

---

**For developer guides and advanced usage, see the `/docs/` folder and module-level docstrings.**
