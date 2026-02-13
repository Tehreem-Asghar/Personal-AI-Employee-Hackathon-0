# Tasks: Bronze Tier Foundation Setup

**Input**: Design documents from `specs/001-bronze-tier-foundation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create `src/watchers/`, `src/utils/`, `src/tests/unit/`, `src/tests/integration/` directories.
- [x] T002 Initialize Python project (e.g., `pyproject.toml`) and install `watchdog` dependency.
- [x] T003 [P] Configure linting (e.g., flake8) and formatting (e.g., black) tools.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `paths.py` in `src/utils/` for Obsidian vault path management.
- [x] T005 Implement `logger.py` in `src/utils/` for Section 6.3 JSON logging.
- [x] T006 Create `base_watcher.py` in `src/watchers/` as an abstract base class with `run()` and abstract methods `check_for_updates()`, `create_action_file()`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Local Vault Initialization (Priority: P1) 🎯 MVP

**Goal**: Create vault folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Logs`.

**Independent Test**: Verify the existence of `/Inbox`, `/Needs_Action`, `/Done`, and `/Logs` folders in the vault.

### Implementation for User Story 1

- [x] T007 [US1] Implement `setup_vault.py` in `src/` to create `/Inbox`, `/Needs_Action`, `/Done`, `/Logs` directories.
- [x] T008 [US1] Update `quickstart.md` with instructions to run `setup_vault.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Essential Document Creation (Priority: P2)

**Goal**: Create `Dashboard.md` and `Company_Handbook.md` with initial templates.

**Independent Test**: Verify both `Dashboard.md` and `Company_Handbook.md` exist and contain initial content.

### Implementation for User Story 2

- [x] T009 [US2] Modify `setup_vault.py` to initialize `Dashboard.md` with basic content.
- [x] T010 [US2] Modify `setup_vault.py` to initialize `Company_Handbook.md` with basic content.
- [x] T011 [US2] Update `quickstart.md` for `Dashboard.md` and `Company_Handbook.md` verification.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Single Senses Integration (Priority: P3)

**Goal**: Implement a File System Watcher that monitors `/Inbox` and moves files to `/Needs_Action` as `FILE_<name>.md`.

**Independent Test**: Drop a text file into `/Inbox` and verify it's moved and renamed, and a log entry is created.

### Tests for User Story 3 ⚠️

- [x] T012 [P] [US3] Write unit tests for `src/utils/paths.py` in `tests/unit/test_paths.py`.
- [x] T013 [P] [US3] Write unit tests for `src/utils/logger.py` (JSON format validation) in `tests/unit/test_logger.py`.

### Implementation for User Story 3

- [x] T014 [US3] Implement `fs_watcher.py` in `src/watchers/` inheriting from `base_watcher.py`.
- [x] T015 [US3] Integrate `src/utils/paths.py` for vault path resolution within `fs_watcher.py`.
- [x] T016 [US3] Integrate `src/utils/logger.py` for event logging in `fs_watcher.py`.
- [x] T017 [US3] Implement file movement and renaming logic (`/Inbox` to `/Needs_Action` as `FILE_<name>.md`) in `fs_watcher.py`.
- [x] T018 [US3] Implement basic error handling and exponential backoff in `fs_watcher.py`.
- [x] T019 [US3] Write integration tests for `fs_watcher.py` (file drop, move, log) in `tests/integration/test_fs_watcher.py`.
- [x] T020 [US3] Update `quickstart.md` with instructions to run `fs_watcher.py`.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 Review and update `README.md` with setup instructions and architecture overview.
- [x] T022 Final code cleanup and inline documentation across all new files.
- [x] T023 Verify all functional and success criteria are met through manual testing and quickstart.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 completion.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 completion.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD).
- Utility implementations before watcher integration.
- Story complete before moving to next priority.

### Parallel Opportunities

- All tasks marked [P] can run in parallel (e.g., T003, T012, T013).
- Different user stories can be worked on in parallel by different team members once Foundational phase is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently (vault structure).

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic vault structure!)
3. Add User Story 2 → Test independently → Deploy/Demo (Essential documents!)
4. Add User Story 3 → Test independently → Deploy/Demo (Working watcher!)
5. Each story adds value without breaking previous stories

---

## Notes

- All tasks include exact file paths for clarity.
- Tests for US3 (P3) are included as per best practices, even if not explicitly requested, given the nature of a watcher.
- Verify tests fail before implementing.
- Commit after each task or logical group.
