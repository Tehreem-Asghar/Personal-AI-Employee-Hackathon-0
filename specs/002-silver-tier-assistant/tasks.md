# Tasks: Silver Tier Functional Assistant

**Input**: Design documents from `specs/002-silver-tier-assistant/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: External API and environment configuration

- [ ] T001 Install dependencies: `google-api-python-client`, `google-auth-oauthlib`, `playwright`, `mcp`, `python-dotenv`.
- [ ] T002 [P] Initialize `.env` file with placeholders for Gmail and WhatsApp session paths (excluded from git).
- [ ] T003 Initialize Playwright: `playwright install chromium`.

---

## Phase 2: Foundational (Orchestration & Security)

**Purpose**: Core mechanisms for HITL and secure credential loading

**⚠️ CRITICAL**: Must be complete before any external actions (Email/Social) are implemented

- [ ] T004 Implement `credentials.py` in `src/utils/` to safely load environment variables.
- [ ] T005 Implement `approval_handler.py` in `src/handlers/` to monitor the `AI_Employee_Vault/Approved` folder.
- [ ] T006 Create `/Approved` and `/Plans` folders in the vault using `src/setup_vault.py`.

**Checkpoint**: Foundation ready - can now implement watchers and action servers.

---

## Phase 3: User Story 1 - Multi-Channel Perception (Priority: P1) 🎯 MVP

**Goal**: Implement Gmail and WhatsApp watchers with keyword filtering.

**Independent Test**: Verify `GMAIL_<id>.md` and `WHATSAPP_<id>.md` files appear in `/Needs_Action` for messages containing keywords.

### Implementation for User Story 1

- [ ] T007 [US1] Implement `gmail_watcher.py` in `src/watchers/` using Gmail API and OAuth2.
- [ ] T008 [US1] Implement keyword filtering logic in `gmail_watcher.py` based on categorized list.
- [ ] T009 [US1] Implement `whatsapp_watcher.py` in `src/watchers/` using Playwright with persistent context.
- [ ] T010 [US1] Implement keyword filtering logic in `whatsapp_watcher.py`.
- [ ] T011 [US1] Integrate `logger.py` to record every perception event in `/Logs`.

**Checkpoint**: AI can now "hear" and "see" external communications.

---

## Phase 4: User Story 2 - External Communication (Priority: P2)

**Goal**: Implement Email MCP server and approval loop.

**Independent Test**: Move a draft to `/Approved` and verify email receipt.

### Implementation for User Story 2

- [ ] T012 [US2] Implement `email_server.py` in `src/mcp/` to expose `send_email` tool.
- [ ] T013 [US2] Connect `approval_handler.py` to trigger `email_server.py` when an email draft is approved.
- [ ] T014 [US2] Implement task movement from `/Approved` to `/Done` after successful send.

---

## Phase 5: User Story 3 - Structured Reasoning (Priority: P3)

**Goal**: AI generates `Plan.md` before execution.

**Independent Test**: Trigger a task and check for a `PLAN_*.md` file.

### Implementation for User Story 3

- [ ] T015 [US3] Implement `planner.py` in `src/utils/` to format Claude's reasoning into markdown plans.
- [ ] T016 [US3] Configure Claude Agent Skill to always call `planner.py` for tasks in `/Needs_Action`.

---

## Phase 6: User Story 4 - Automated Social Presence (Priority: P4)

**Goal**: Draft LinkedIn posts based on vault activity.

**Independent Test**: Verify a `APPROVAL_LINKEDIN_*.md` file appears in `/Pending_Approval`.

### Implementation for User Story 4

- [ ] T017 [US4] Implement LinkedIn drafting logic in a new "Social Skill".
- [ ] T018 [US4] Extend `approval_handler.py` to support LinkedIn post publication (if using API) or manual confirmation.

---

## Phase 7: Polish & Automation

**Purpose**: System stabilization and 24/7 simulation.

- [ ] T019 [P] Create a PowerShell script to bundle all watchers for Task Scheduler.
- [ ] T020 Setup Windows Task Scheduler to run the system heartbeat every 15 minutes.
- [ ] T021 Final verification of HITL safety: Ensure NO email sends without move to `/Approved`.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 & 2**: MUST be complete before Phase 3 and 4.
- **Phase 3 (Senses)**: Can run in parallel with Phase 4 (Hands) once Phase 2 is done.
- **Phase 5 (Reasoning)**: Depends on Phase 3 data being available in the vault.

### Parallel Opportunities
- T007 (Gmail) and T009 (WhatsApp) can be developed in parallel.
- T012 (Email MCP) can be developed while watchers are being tested.

---

## Implementation Strategy

### MVP First
1. Complete Gmail Watcher (T007-T008).
2. Complete Approval Handler (T005).
3. Complete Email MCP (T012-T013).
4. **Result**: A working "Email Assistant" that can detect needs and send approved replies.

### Incremental Delivery
1. Add WhatsApp support.
2. Add Reasoning/Planner logic.
3. Add LinkedIn drafting.
4. Add Task Scheduler automation.
