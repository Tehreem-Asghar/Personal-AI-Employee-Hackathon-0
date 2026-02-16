<!--
Sync Impact Report:
- Version change: 1.2.0 -> 1.3.0
- Added sections: Expanded Silver Tier requirements
- Modified principles: Shifted current focus from Bronze to Silver Tier.
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated for Silver)
-->

# Personal AI Employee (Digital FTE) Constitution

## Core Principles (Global)

### I. Local-First & Privacy-Centric
All personal and business data MUST remain in the local Obsidian vault. Secrets MUST reside in environment variables or local secrets managers.

### II. Agent-Driven Autonomy
The AI MUST monitor "Senses" (Watchers) 24/7 and use the "Ralph Wiggum" loop pattern for multi-step tasks.

### III. Human-in-the-Loop (HITL) Safety
Sensitive actions (payments/external comms) MUST require explicit human approval via `/Pending_Approval`.

### IV. Agent Engineering Architecture
All functionality MUST be implemented as "Agent Skills" or MCP servers.

### V. Transparency & Auditability
Every action MUST be logged in standardized JSON format in `/Logs`.

### VI. Resilience & Error Recovery
Critical processes MUST be managed by a process manager (PM2) with exponential backoff retry logic.

---

## Tier-Specific Roadmap & Constraints

### 🥉 Bronze Tier: The Foundation (Completed)
1. **Senses**: ONE working Watcher script (File System).
2. **Memory**: Obsidian vault structure verified.
3. **Essential Documentation**: `Dashboard.md` and `Company_Handbook.md` established.

### 🥈 Silver Tier: The Functional Assistant (Current Focus)
To achieve Silver status, the system MUST expand its capabilities beyond the local foundation:
1. **Expanded Senses**: Implement at least TWO more Watcher scripts (e.g., Gmail API and WhatsApp Web automation).
2. **External Action (Hands)**: Implement one working MCP server for external actions (e.g., sending actual emails via Gmail).
3. **Reasoning Loop**: Claude MUST generate structured `Plan.md` files in the `/Plans` folder before executing complex tasks.
4. **Social Integration**: Ability to automatically generate and/or post content to LinkedIn to support business goals.
5. **Operational HITL**: A formal human-approval workflow MUST be active for all outgoing communications to new contacts or any file deletion.
6. **Scheduling**: Implement basic task scheduling using `cron` (Linux) or `Task Scheduler` (Windows) to trigger periodic AI audits.

### 🥇 Gold Tier: The Autonomous Employee (Vision)
- Full cross-domain integration (Personal + Business).
- Odoo Accounting integration via MCP.
- Weekly Business and Accounting Audit with CEO Briefing generation.
- Ralph Wiggum loop for fully autonomous multi-step completion.

## Governance
This constitution supersedes all other practices. Silver Tier features MUST maintain compatibility with the Bronze foundation while introducing external integrations.

**Version**: 1.3.0 | **Ratified**: 2026-02-13 | **Last Amended**: 2026-02-17
