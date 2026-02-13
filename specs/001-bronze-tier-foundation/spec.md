# Feature Specification: Bronze Tier Foundation Setup

**Feature Branch**: `001-bronze-tier-foundation`  
**Created**: 2026-02-13  
**Status**: Draft  
**Input**: User description: "Bronze Tier Foundation Setup based on hackathon requirements"

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-02-13
- Q: Which specific folder should the File System watcher monitor by default? → A: `/Inbox` folder
- Q: What specific "standardized JSON format" should be used for audit logs? → A: Use Section 6.3 schema (timestamp, action_type, actor, etc.)
- Q: How should the watcher handle files found in the monitored folder? → A: Move to `/Needs_Action` and rename to `FILE_<name>.md`

### User Story 1 - Local Vault Initialization (Priority: P1)

As a Digital FTE owner, I want my local Obsidian vault to be structured with standard folders so that my AI employee can systematically organize its work.

**Why this priority**: Essential foundation for all other tiers. Without a structured vault, the AI cannot persist state or communicate via files.

**Independent Test**: Can be fully tested by verifying the existence of `/Inbox`, `/Needs_Action`, `/Done`, and `/Logs` folders in the vault.

**Acceptance Scenarios**:

1. **Given** a new Obsidian vault, **When** I run the setup script, **Then** all required folders are created.
2. **Given** the vault structure, **When** I check folder permissions, **Then** Claude Code has read/write access to all folders.

---

### User Story 2 - Essential Document Creation (Priority: P2)

As a project manager, I want the vault to contain `Dashboard.md` and `Company_Handbook.md` so that I can monitor AI activity and define rules of engagement.

**Why this priority**: Provides the "Memory" and "Rules" mentioned in the architecture. Essential for tracking progress.

**Independent Test**: Verify both files exist and contain the required initial templates.

**Acceptance Scenarios**:

1. **Given** the vault structure, **When** initialized, **Then** `Dashboard.md` exists with sections for "Bank Balance" and "Pending Messages".
2. **Given** the vault structure, **When** initialized, **Then** `Company_Handbook.md` exists with "Rules of Engagement".

---

### User Story 3 - Single Senses Integration (Priority: P3)

As a user, I want at least one working Watcher script (e.g., File System) to monitor for new inputs so that the AI can be triggered autonomously.

**Why this priority**: Demonstrates the "Perception" layer of the architecture. Moves the AI from reactive to proactive.

**Independent Test**: Drop a file into the watched folder and verify a corresponding `.md` file is created in `/Needs_Action`.

**Acceptance Scenarios**:

1. **Given** a running File System watcher, **When** I drop a text file into `/Inbox`, **Then** the file is moved to `/Needs_Action` and renamed to `FILE_<original_name>.md`.
2. **Given** a running watcher, **When** an error occurs, **Then** it uses exponential backoff to recover.

---

## Privacy & Safety *(mandatory)*

- **Data Privacy**: All data remains within the local Obsidian vault. No cloud sync is configured for the vault directory.
- **HITL Compliance**: Initial implementation identifies `/Pending_Approval` folder for future human-in-the-loop workflows.
- **Auditability**: All watcher and agent actions are logged in JSON format within the `/Logs` folder.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create the folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Logs`.
- **FR-002**: System MUST initialize `Dashboard.md` and `Company_Handbook.md`.
- **FR-003**: System MUST include a working Python-based File System watcher that monitors the `/Inbox` folder.
- **FR-004**: System MUST ensure Claude Code can successfully read and write to the vault files.
- **FR-005**: System MUST implement standardized JSON logging for every watcher event, following the schema defined in Section 6.3 of the architecture document.

### Key Entities *(include if feature involves data)*

- **Vault**: The local Obsidian knowledge base.
- **Action File**: A markdown file created by a watcher representing a task.
- **Audit Log**: A JSON record of system activities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Vault setup completes in under 30 seconds.
- **SC-002**: 100% of files dropped into the watch directory result in an action file within 5 seconds.
- **SC-003**: Claude Code successfully updates `Dashboard.md` with a summary of the action file.
- **SC-004**: System recovers from a temporary file system interruption within 60 seconds using backoff logic.
