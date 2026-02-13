# Data Model: Bronze Tier Foundation

## Entities

### Vault Folder Structure
- **Inbox**: Raw files waiting for processing.
- **Needs_Action**: Actionable markdown files created by watchers.
- **Done**: Archive of completed tasks.
- **Logs**: Daily JSON files containing audit trails.
- **Pending_Approval**: HITL request files.

### Action File (`FILE_<name>.md`)
- **Metadata**:
    - `type`: email / file_drop / message
    - `original_name`: string
    - `size`: bytes
    - `received`: timestamp
- **Content**: Summary of the input.

### Audit Log (JSON)
- **Fields**:
    - `timestamp`: ISO 8601
    - `action_type`: watcher_event / file_move / vault_update
    - `actor`: fs_watcher / claude_code
    - `target`: file_path
    - `result`: success / failure
