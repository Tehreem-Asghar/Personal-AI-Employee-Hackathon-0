<!--
Sync Impact Report:
- Version change: 1.0.1 -> 1.2.0
- Added sections: Tier-Specific Roadmap (Bronze Focus)
- Modified principles: Merged global vision with Bronze Tier execution rules.
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
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

### 🥉 Bronze Tier: The Foundation (Current Focus)
To achieve Bronze status, the system MUST meet these specific criteria:
1. **Senses**: At least ONE working Watcher script (Gmail OR File System).
2. **Memory**: Obsidian vault with `/Inbox`, `/Needs_Action`, `/Done`, and `/Logs` structure.
3. **Brain-Vault Sync**: Claude Code MUST successfully read from and write to the vault.
4. **Essential Documentation**: `Dashboard.md` and `Company_Handbook.md` MUST exist and be actively updated by the AI.
5. **Skill Implementation**: All initial AI features MUST be "Agent Skills".

### 🥈 Silver Tier: The Assistant (Future)
- Multiple Watchers (Gmail + WhatsApp + LinkedIn).
- Automatic social media posting.
- Reasoning loop that creates `Plan.md` files.

### 🥇 Gold Tier: The Autonomous Employee (Vision)
- Full cross-domain integration (Personal + Business).
- Odoo Accounting integration via MCP.
- Weekly CEO Briefing generation.

## Governance
This constitution supersedes all other practices. Tiered progress MUST be validated before moving to the next level.

**Version**: 1.2.0 | **Ratified**: 2026-02-13 | **Last Amended**: 2026-02-13
