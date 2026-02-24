# Implementation Plan: Gold Tier - Autonomous Employee

**Branch**: `003-gold-tier-autonomous-employee` | **Date**: 2026-02-24 | **Spec**: `/specs/003-gold-tier-autonomous-employee/spec.md`
**Input**: Gold Tier Specification

## Summary
Transform the AI assistant into an autonomous FTE by integrating Odoo ERP for accounting, official APIs for multi-channel social media, and a file-based state machine (Ralph Wiggum loop) to ensure task completion. The system will proactively generate executive-level briefings from financial and productivity logs.

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: `odoorpc`, `tweepy`, `facebook-sdk`, `python-linkedin-v2`, `psutil`  
**Storage**: Odoo (Local JSON-RPC), Obsidian Vault (Markdown + JSON state)  
**Testing**: `pytest` (Unit/Integration), `odoorpc-mock` for local ERP testing  
**Target Platform**: Windows 11 / Linux (Local Environment)
**Project Type**: Autonomous Agent Framework  
**Performance Goals**: Watchdog heartbeat < 60s, CEO Briefing generation < 2 mins  
**Constraints**: Local-first data, HITL for all financial/public actions  
**Scale/Scope**: Multi-channel (4 platforms), Full ERP integration

## Constitution Check
1. **Privacy Gate**: Secrets (Odoo/Social APIs) stored in `.env`. Vault only stores non-sensitive business data. ✅
2. **Autonomy Gate**: "Ralph Wiggum" loop implemented via `.system/state.json` persistence. ✅
3. **Safety Gate**: HITL mandatory for Odoo posting and social publishing via `/Pending_Approval`. ✅
4. **Resilience Gate**: `watchdog.py` health monitor with auto-restart and user notifications. ✅
5. **Transparency Gate**: Standardized JSON logging for all agent actions. ✅

## Project Structure

### Documentation (this feature)
```text
specs/003-gold-tier-autonomous-employee/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Odoo & State Machine schemas
├── quickstart.md        # Setup guide for Odoo/APIs
└── tasks.md             # (Next step) Implementation tasks
```

### Source Code Updates
```text
src/
├── mcp/
│   ├── odoo_server.py      # New: Odoo JSON-RPC MCP
│   └── social_server.py    # New: Multi-platform Social MCP
├── agents/
│   └── orchestrator.py     # Update: Ralph Wiggum logic
├── utils/
│   ├── odoo_client.py      # Odoo connection wrapper
│   └── social_client.py    # Multi-API wrapper
└── watchers/
    └── watchdog.py         # New: Health monitor
```

## Phase 0: Outline & Research (Completed)
- Odoo Integration: `odoorpc` chosen for pythonic JSON-RPC access.
- Social Media: Official SDKs selected for LinkedIn, Twitter, FB, and IG.
- Persistence: File-based JSON state machine inside `.system/` folder.

## Phase 1: Design & Contracts (Completed)
- Data Model defined for Odoo entities and Social Posts.
- Ralph Wiggum state machine schema established.
- CEO Briefing data sources mapped.

## Phase 2: Implementation Roadmap
1. **Odoo Foundation**: Setup local Odoo and implement `odoo-mcp`.
2. **Persistence Loop**: Upgrade `orchestrator.py` with state-tracking and re-injection logic.
3. **Social Expansion**: Build `social_server.py` and unify social drafting logic.
4. **Executive Brain**: Implement the `CEO_Briefing` generator using Odoo + Log data.
5. **Guardian**: Deploy `watchdog.py` to monitor all daemon processes.
