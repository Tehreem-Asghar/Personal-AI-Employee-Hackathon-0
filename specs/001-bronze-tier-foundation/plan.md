# Implementation Plan: Bronze Tier Foundation Setup

**Branch**: `001-bronze-tier-foundation` | **Date**: 2026-02-13 | **Spec**: [specs/001-bronze-tier-foundation/spec.md]
**Input**: Feature specification for initializing the Digital FTE local environment.

## Summary

The goal is to establish the "Foundational Layer" of the Personal AI Employee. This involves creating a standardized Obsidian vault structure, initializing essential "Memory" documents (`Dashboard.md`, `Company_Handbook.md`), and implementing a "Perception" layer via a Python-based File System watcher that monitors `/Inbox` and moves tasks to `/Needs_Action`.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: `watchdog` (for file system events), `logging`, `pathlib`  
**Storage**: Local Filesystem (Markdown/JSON) within Obsidian Vault  
**Testing**: Manual verification of file movements and content updates; Unit tests for logging and path handling.  
**Target Platform**: Windows (win32)  
**Project Type**: Python CLI / Background Service  
**Performance Goals**: Watcher response < 5s; Setup < 30s  
**Constraints**: Local-only; No cloud sync; Section 6.3 JSON logging schema.  
**Scale/Scope**: Bronze Tier (Foundation) only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Privacy Gate**: PASS. No secrets stored in vault; local-first approach.
2. **Autonomy Gate**: PASS. Watcher provides the "Senses" for proactive behavior.
3. **Safety Gate**: PASS. Includes `/Pending_Approval` for HITL.
4. **Resilience Gate**: PASS. Requires PM2 management and retry logic.
5. **Transparency Gate**: PASS. Mandates Section 6.3 JSON logging.

## Project Structure

### Documentation (this feature)

```text
specs/001-bronze-tier-foundation/
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
│   ├── base_watcher.py  # Abstract base class
│   └── fs_watcher.py    # File system implementation
├── utils/
│   ├── logger.py        # Section 6.3 JSON logger
│   └── paths.py         # Vault path management
└── setup_vault.py       # Initialization script

tests/
├── unit/                # Logger and path tests
└── integration/         # Watcher behavior tests
```

**Structure Decision**: Single project structure with modular watcher and utility components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
