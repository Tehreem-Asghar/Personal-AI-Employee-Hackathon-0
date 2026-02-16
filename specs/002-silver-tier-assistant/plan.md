# Implementation Plan: Silver Tier Functional Assistant

**Branch**: `002-silver-tier-assistant` | **Date**: 2026-02-17 | **Spec**: [specs/002-silver-tier-assistant/spec.md]
**Input**: Feature specification for expanding the Digital FTE with Gmail, WhatsApp, and MCP capabilities.

## Summary

This phase transforms the Digital FTE from a local file observer into an active functional assistant. We will implement Gmail and WhatsApp watchers for incoming communications, an Email MCP server for outgoing replies, and a structured reasoning loop that generates `Plan.md` files for transparency. All external actions will follow a strict Human-in-the-Loop (HITL) approval workflow.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: `google-api-python-client` (Gmail), `playwright` (WhatsApp), `mcp` (Model Context Protocol), `python-dotenv`  
**Storage**: Obsidian Vault (Markdown), Local `.env` for secrets, browser context for WhatsApp session.  
**Testing**: Mocked API responses for Gmail; Headless/Headed browser testing for WhatsApp; Manual verification of the `/Approved` workflow.  
**Target Platform**: Windows (win32)  
**Project Type**: Background services managed via Windows Task Scheduler.  
**Performance Goals**: Watcher detection < 2 mins (on schedule); 100% audit logging of external calls.  
**Constraints**: Credentials MUST stay out of the vault; Mandatory HITL for all outgoing content.  
**Scale/Scope**: Silver Tier Assistant.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Privacy Gate**: PASS. Credentials stored in `.env` (excluded by `.gitignore`).
2. **Autonomy Gate**: PASS. Scheduled perception via Task Scheduler.
3. **Safety Gate**: PASS. Implements the `/Pending_Approval` to `/Approved` folder logic.
4. **Resilience Gate**: PASS. Uses persistent browser context for WhatsApp to survive restarts.
5. **Transparency Gate**: PASS. Standardized JSON logging for all API and browser actions.

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-tier-assistant/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── watchers/
│   ├── gmail_watcher.py     # Gmail API implementation
│   └── whatsapp_watcher.py  # Playwright-based automation
├── mcp/
│   └── email_server.py      # MCP server for sending emails
├── utils/
│   ├── planner.py           # Logic for creating Plan.md files
│   └── credentials.py       # Secure env-based credential loader
└── handlers/
    └── approval_handler.py  # Orchestrator for /Approved folder movements

tests/
├── unit/
│   ├── test_gmail_logic.py
│   └── test_planner.py
└── integration/
    └── test_approval_flow.py
```

**Structure Decision**: Modular source structure following the Watchers/MCP/Orchestrator pattern defined in the architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
