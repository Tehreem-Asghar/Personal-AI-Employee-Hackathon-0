# Research: Bronze Tier Foundation

## Decision: Watchdog Library for Perception
- **Rationale**: The `watchdog` library is the industry standard for cross-platform file system events in Python. It provides reliable monitoring of directory changes (created, modified, moved) which is essential for the `/Inbox` watcher.
- **Alternatives considered**: 
    - `pathlib` polling: Rejected due to high CPU usage and latency.
    - Windows API (`ReadDirectoryChangesW`): Rejected because it's too low-level and less portable.

## Decision: Standardized JSON Logging (Section 6.3)
- **Rationale**: Strict adherence to the hackathon's schema ensures that logs can be parsed by future "Audit" skills in the Gold tier.
- **Implementation**: A custom logging handler will be written to format all `watcher` events into the required JSON structure.

## Decision: Vault Path Management
- **Rationale**: Using `pathlib` for all vault interactions ensures robust handling of Windows-style paths and prevents issues with relative directory shifts.
