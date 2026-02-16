# Feature Specification: Silver Tier Functional Assistant

**Feature Branch**: `002-silver-tier-assistant`  
**Created**: 2026-02-17  
**Status**: Draft  
**Input**: User description: "Silver Tier Functional Assistant implementation based on hackathon requirements"

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-02-17
- Q: How should the WhatsApp Watcher handle authentication? → A: Manual QR scan once (saved via persistent browser context)
- Q: How should the AI decide which WhatsApp/Gmail messages to process? → A: Search for unread messages containing expanded keywords (Financial: invoice, payment, pricing; Scheduling: meeting, schedule; Operational: project, task; Urgency: urgent, asap; Support: help, question)
- Q: How should LinkedIn posts be handled before publication? → A: Generate draft `.md` in `/Pending_Approval` for review

### User Story 1 - Multi-Channel Perception (Priority: P1)

As a Digital FTE owner, I want my AI to monitor my Gmail and WhatsApp so that it can respond to client inquiries without me manually checking my inbox.

**Why this priority**: Core "Functional Assistant" capability. Expands the AI's awareness to the most critical communication channels.

**Independent Test**: Send an email or WhatsApp message with a keyword (e.g., "invoice") and verify a corresponding `.md` file appears in `/Needs_Action`.

**Acceptance Scenarios**:

1. **Given** a new unread Gmail message, **When** the Gmail Watcher runs, **Then** an actionable `.md` file is created in `/Needs_Action` with email headers and snippet.
2. **Given** a new WhatsApp message containing "help", **When** the WhatsApp Watcher runs, **Then** an actionable `.md` file is created in `/Needs_Action`.

---

### User Story 2 - External Communication (Priority: P2)

As a user, I want the AI to be able to send emails on my behalf after I approve its draft so that I can delegate administrative replies.

**Why this priority**: Demonstrates the "Hands" (MCP) layer. Allows the AI to close the loop on tasks.

**Independent Test**: Move a file from `/Pending_Approval` to `/Approved` and verify an actual email is sent.

**Acceptance Scenarios**:

1. **Given** a draft reply file in `/Pending_Approval`, **When** I move it to `/Approved`, **Then** the Email MCP server sends the message via Gmail API.
2. **Given** a sent email, **When** complete, **Then** the task file is moved to `/Done` and logged in `/Logs`.

---

### User Story 3 - Structured Reasoning (Priority: P3)

As a project manager, I want the AI to create a `Plan.md` file before starting complex tasks so that I can audit its proposed logic.

**Why this priority**: Essential for transparency and safety in more complex workflows.

**Independent Test**: Trigger a task and verify a `PLAN_*.md` file is created in the `/Plans` folder with numbered steps.

**Acceptance Scenarios**:

1. **Given** a new task in `/Needs_Action`, **When** Claude processes it, **Then** a structured `Plan.md` is created with an objective and checkboxes for steps.

---

### User Story 4 - Automated Social Presence (Priority: P4)

As a business owner, I want the AI to generate and suggest LinkedIn posts based on my business activity so that I can maintain a social presence with minimal effort.

**Why this priority**: Core Silver Tier requirement for business growth.

**Independent Test**: Add a "business milestone" file to `/Inbox` and verify a LinkedIn post draft appears in `/Pending_Approval`.

---

## Privacy & Safety *(mandatory)*

- **Data Privacy**: Gmail and WhatsApp credentials MUST NOT be stored in the vault. They must be managed via local `.env` files or session tokens stored outside the vault directory.
- **HITL Compliance**: ALL outgoing emails and social media posts MUST require explicit human approval via the `/Approved` folder move rule.
- **Auditability**: Every external API call (Gmail, WhatsApp, LinkedIn) MUST be logged in the JSON audit trail.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include a Gmail Watcher using the Gmail API that filters for unread messages containing expanded keywords across categories (Maaliyat, Scheduling, Operational, Urgency, Support).
- **FR-002**: System MUST include a WhatsApp Watcher using Playwright-based automation with a persistent browser context to maintain the session after a manual QR scan, filtering for messages with the same expanded keyword categories.
- **FR-003**: System MUST implement an Email MCP server for sending messages.
- **FR-004**: System MUST generate structured `Plan.md` files for any task requiring more than 2 steps.
- **FR-005**: System MUST provide a mechanism to draft LinkedIn posts as `.md` files in the `/Pending_Approval` folder for human review.
- **FR-006**: System MUST use Windows Task Scheduler to run watchers every 15-30 minutes.

### Key Entities *(include if feature involves data)*

- **Communication Object**: Abstract representation of email/message data.
- **Plan**: A markdown file defining the execution path for a task.
- **Approval Request**: A file-based gate for external actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gmail watcher detects new messages within 2 minutes of arrival (during scheduled run).
- **SC-002**: 100% of outgoing emails are logged in the audit trail with a "success" or "failure" status.
- **SC-003**: Plans are generated for 100% of tasks originating from communication watchers.
- **SC-004**: User can approve/reject a draft in under 10 seconds via simple file move.
