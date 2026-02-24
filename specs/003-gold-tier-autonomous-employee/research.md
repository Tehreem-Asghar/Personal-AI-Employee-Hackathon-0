# Research: Gold Tier - Autonomous Employee

## 1. Odoo JSON-RPC Integration
**Decision**: Use the `odoorpc` Python library.
**Rationale**: It provides a high-level, pythonic interface over Odoo's `jsonrpc` and `xmlrpc` endpoints, simplifying authentication and model interactions (CRUD).
**Alternatives considered**: 
- `xmlrpc.client`: Too low-level, requires manual handling of session IDs and error parsing.
- `Odoo official web services`: Good documentation, but `odoorpc` wraps this effectively for Python.

## 2. Multi-Channel Social APIs
**Decision**: Use `tweepy` (Twitter/X), `facebook-sdk` (Meta), and `python-linkedin-v2`.
**Rationale**: These are the most mature and widely-supported libraries for their respective platforms. They handle OAuth flows and rate limiting better than custom `requests` implementations.
**Alternatives considered**:
- `Ayrshare/Buffer APIs`: Rejected because they introduce a 3rd party dependency and potential costs/privacy concerns.
- `Playwright Web Automation`: Rejected for Gold Tier (except for banking) as official APIs are more stable for social posting.

## 3. Ralph Wiggum Loop Persistence
**Decision**: State Machine stored in `AI_Employee_Vault/.system/state.json`.
**Rationale**: Keeping state in a JSON file within the vault allows the AI to "see" its progress between restarts using standard file tools. The `.system/` prefix keeps it hidden from general vault browsing while remaining local-first.
**Alternatives considered**:
- `SQLite`: Overkill for simple task state; JSON is more human-readable for debugging.
- `Environment Variables`: Inadequate for multi-step task tracking and history.

## 4. Watchdog Process Management
**Decision**: Custom `watchdog.py` using `psutil`.
**Rationale**: `psutil` allows cross-platform process monitoring (PID checking, CPU/Memory usage) and is lightweight compared to installing full process managers like PM2 in a Python-heavy environment.
**Alternatives considered**:
- `PM2`: Great for Node, but requires an extra runtime. `watchdog.py` keeps the stack purely Python/Shell.
- `Systemd/Windows Services`: Too platform-specific; `watchdog.py` is portable across Win/Mac/Linux.
