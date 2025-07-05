---
title: Src Documentation
description: Documentation and guides for the Src module.
author: Knowledge Base Team
created_at: '2025-07-05'
updated_at: '2025-07-05'
version: 1.0.0
---

# Backend API Documentation — Knowledge Base Assistant

This backend powers the cross-platform AI assistant with advanced automation, networking, and multimodal features.

## API Endpoints

### Knowledge Base & AI
- `/search` — Search the local knowledge base for relevant files/snippets.
- `/categories` — List available knowledge base categories.
- `/generate_code` — Generate code from a prompt (AI-powered).
- `/analyze_multimodal` — Analyze uploaded images/audio/files (multimodal AI).

### Web Search & Scraping
- `/web-search` — Anonymous web search (Tor/Brave/DuckDuckGo/SerpAPI).
- `/extract-content` — Extract and parse content from a web page.
- `/scrape` — (Planned) Advanced web scraping and data extraction.

### Web Automation
- `/automate` (POST) — Run browser automation tasks (Playwright/Selenium):
  - **Payload:** `{ url, actions, selectors, script, headless, use_playwright }`
  - **Actions:** `goto`, `fill_form`, `click`, `screenshot`, `run_script`, `get_content`
  - **Returns:** logs, screenshot (base64), HTML, errors

### Networking & Security
- `/vpn/connect` (POST) — Connect to a VPN (OpenVPN/WireGuard)
- `/dns/set` (POST) — Set DNS servers (system/DoH/DoT)
- `/voip/start` (POST) — Start a VOIP client (SIP/WebRTC, stub)
- `/network/status` (GET) — Get network diagnostics

### System & Status
- `/` — API root/status and feature list

## Modules
- `main.py` — FastAPI app, all endpoints
- `web_search.py` — Tor/Brave/Decentralized search, content extraction
- `web_scraper.py` — Advanced scraping and data analysis
- `web_automation.py` — Browser automation (Playwright/Selenium)
- `networking.py` — VPN, DNS, VOIP, diagnostics

## Setup & Usage
- Requires Python 3.9+, FastAPI, Playwright/Selenium, requests, etc.
- For VPN/DNS/VOIP, external binaries or system permissions may be needed.
- See each module for advanced usage and extension points.

## Security & Privacy
- CORS enabled for cross-platform clients
- Tor and VPN support for anonymous/secure operations
- No authentication by default (add before production)

## Extending
- Add new endpoints in `main.py`
- Implement new search/automation/networking modules as needed
- Cross-link with frontend/mobile/desktop clients for full-stack integration

---

For detailed developer guides, see `/docs/` and module-level docstrings.
