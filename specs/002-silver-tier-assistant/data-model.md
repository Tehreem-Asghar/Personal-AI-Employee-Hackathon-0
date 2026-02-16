# Data Model: Silver Tier Functional Assistant

## Entities

### Plan (`PLAN_<id>.md`)
- **Metadata**:
    - `created_at`: ISO 8601
    - `source_task`: File path to the originating /Needs_Action file.
    - `status`: pending / in_progress / blocked / complete
- **Content**:
    - `Objective`: Clear goal of the task.
    - `Steps`: List of checkboxes representing the execution path.

### Approval Request (`APPROVAL_<type>_<id>.md`)
- **Metadata**:
    - `type`: email / linkedin_post
    - `target`: recipient_email / "LinkedIn"
    - `action`: send_email / post_update
- **Content**:
    - `Body`: The drafted content for review.
    - `Instructions`: How to approve (e.g., "Move to /Approved to send").

### Communication Object (Internal)
- **Fields**:
    - `platform`: gmail / whatsapp
    - `sender`: string
    - `subject`: string (Gmail only)
    - `snippet`: string
    - `timestamp`: timestamp
    - `thread_id`: platform-specific ID

## Relationships
- A `Watcher Event` (in /Logs) creates a `Needs_Action` file.
- A `Needs_Action` file triggers a `Plan`.
- A `Plan` may result in one or more `Approval Requests`.
- An `Approved` file triggers an `Audit Log` entry upon execution.
