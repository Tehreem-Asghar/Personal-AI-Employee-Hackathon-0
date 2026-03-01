# Tasks: Gold Tier - Autonomous Employee

**Input**: Design documents from `/specs/003-gold-tier-autonomous-employee/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Initialize Gold Tier environment and verify Odoo installation at http://localhost:8069
- [X] T002 [P] Install dependencies: `odoorpc`, `tweepy`, `facebook-sdk`, `python-linkedin-v2`, `psutil`
- [X] T003 [P] Configure `.env` with Odoo and Social API credentials per `quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T004 Create system directory `AI_Employee_Vault/.system/` for state persistence
- [X] T005 [P] Implement base `OdooClient` wrapper in `src/utils/odoo_client.py`
- [X] T006 [P] Implement base `SocialClient` wrapper in `src/utils/social_client.py`
- [X] T007 Setup environment variable loader for new Gold Tier secrets in `src/utils/credentials.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Odoo Financial Integration (Priority: P1) 🎯 MVP

**Goal**: Integrate with Odoo Community for formal bookkeeping and revenue tracking.

**Independent Test**: Successfully fetch revenue from Odoo using the `odoo-mcp` server.

### Implementation for User Story 1

- [X] T008 [US1] Create Odoo MCP server in `src/mcp/odoo_server.py`
- [X] T009 [US1] Implement `get_revenue` capability in `src/mcp/odoo_server.py`
- [X] T010 [US1] Implement `log_transaction` capability in `src/mcp/odoo_server.py`
- [X] T011 [US1] Implement `audit_subscriptions` capability in `src/mcp/odoo_server.py`
- [X] T012 [US1] Add HITL gate for Odoo `posted` state in `src/handlers/approval_handler.py`

**Checkpoint**: User Story 1 functional - Odoo integration verified.

---

## Phase 4: User Story 2 - Ralph Wiggum Autonomous Loop (Priority: P1) 🎯 MVP

**Goal**: Enable the agent to persist state and iterate until tasks are marked as `/Done`.

**Independent Test**: A multi-step task continues to iterate after a simulated Claude exit.

### Implementation for User Story 2

- [X] T013 [US2] Create state schema and persistence logic in `AI_Employee_Vault/.system/state.json`
- [X] T014 [US2] Upgrade `src/agents/orchestrator.py` with the Ralph Wiggum re-injection loop
- [X] T015 [US2] Implement iteration counter (Max 10) in `src/agents/orchestrator.py`
- [X] T016 [US2] Add `/Done` folder check to trigger loop termination in `src/agents/orchestrator.py`

**Checkpoint**: User Story 2 functional - AI now iterates autonomously.

---

## Phase 5: User Story 3 - Multi-Channel Social Expansion (Priority: P2)

**Goal**: Expand social media reach to Twitter, Facebook, and Instagram.

**Independent Test**: Successfully generate and draft posts for 4 platforms from a single trigger.

### Implementation for User Story 3

- [X] T017 [US3] Create Social MCP server in `src/mcp/social_server.py`
- [X] T018 [US3] Implement Twitter/X posting in `src/utils/social_client.py` using `tweepy`
- [X] T019 [US3] Implement Meta (FB/IG) posting in `src/utils/social_client.py` using `facebook-sdk`
- [X] T020 [US3] Unify social drafting logic in `src/utils/social_draft.py` to handle 4 platforms
- [X] T021 [US3] Update `src/agents/drafting_agent.py` to support multi-platform content generation

**Checkpoint**: User Story 3 functional - Multi-channel social drafting active.

---

## Phase 6: User Story 4 - Monday Morning CEO Briefing (Priority: P2)

**Goal**: Generate a proactive executive summary every Sunday night.

**Independent Test**: Generate a `YYYY-MM-DD_CEO_Briefing.md` containing Odoo revenue data.

### Implementation for User Story 4

- [X] T022 [US4] Implement CEO Briefing generator in `src/agents/briefing_agent.py` (upgrading Briefing Genius)
- [X] T023 [US4] Add Odoo revenue fetching to briefing logic in `src/agents/briefing_agent.py`
- [X] T024 [US4] Add productivity bottleneck analysis (cycle time > 48h) in `src/agents/briefing_agent.py`
- [X] T025 [US4] Configure Sunday night trigger in `src/run_senses.ps1`

**Checkpoint**: User Story 4 functional - Executive briefings active.

---

## Phase 7: User Story 5 - Guardian Watchdog & Notifications (Priority: P3)

**Goal**: Ensure system resilience with auto-restarts and human notifications.

**Independent Test**: Killing a watcher process triggers an auto-restart and an email alert.

### Implementation for User Story 5

- [X] T026 [US5] Implement master health monitor in `src/watchers/watchdog.py` using `psutil`
- [X] T027 [US5] Implement process restart logic for all watchers in `src/watchers/watchdog.py`
- [X] T028 [US5] Add Email/WhatsApp notification logic for failures in `src/utils/notifications.py`
- [X] T029 [US5] Integrate notifications into `src/watchers/watchdog.py`

**Checkpoint**: User Story 5 functional - System is now self-healing and communicative.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and documentation.

- [X] T030 [P] Update `AI_Employee_Vault/Company_Handbook.md` with Gold Tier rules
- [ ] T031 [P] Standardize all JSON audit logs across Odoo and Social MCPs
- [ ] T032 Run full `quickstart.md` validation on a clean environment
- [ ] T033 Final code cleanup and refactoring of `orchestrator.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1.
- **User Stories (Phase 3-7)**: All depend on Phase 2.
- **Polish (Phase 8)**: Depends on completion of all previous phases.

### User Story Parallelism

Once Phase 2 is complete, US1 (Odoo) and US2 (Ralph Wiggum) can proceed in parallel as they touch different parts of the system. US3 (Social) can also start in parallel with US1/US2.

---

## Implementation Strategy

### MVP First (Odoo + Ralph Wiggum)
1. Complete Setup and Foundational.
2. Complete Odoo Integration (US1) and Ralph Wiggum Loop (US2).
3. This creates a "Reasoning + Accounting" core which is the most valuable part of Gold Tier.

### Incremental Delivery
1. Foundation -> Core (US1+US2) -> Social (US3) -> Briefing (US4) -> Guardian (US5).
