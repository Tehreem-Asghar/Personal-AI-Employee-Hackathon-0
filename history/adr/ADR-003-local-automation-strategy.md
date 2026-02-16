# ADR-003: Local Automation Strategy

- **Status:** Accepted
- **Date:** 2026-02-17
- **Feature:** silver-tier-assistant
- **Context:** The system needs to run periodically to monitor inputs without a constant cloud server presence, maintaining the "Local-First" principle.

## Decision

We will use the native **Windows Task Scheduler** to provide a "heartbeat" for the system:
- **Interval**: Scheduled to run every 15 minutes.
- **Scope**: Triggers all active Watchers (Gmail, WhatsApp, File System) and the `ApprovalHandler`.
- **Environment**: Scripts run within the existing `.venv` using `python.exe`.

## Consequences

### Positive
- **Simplicity**: No need for complex process managers or container orchestration.
- **Resource Efficiency**: Scripts only use CPU/RAM when active, rather than idling 24/7.
- **Reliability**: Uses a stable, native OS feature.

### Negative
- **Gap Time**: Up to 15 minutes of latency for detecting new messages.
- **OS Coupling**: This specific implementation is coupled to Windows.

## Alternatives Considered
- **PM2 / systemd**: Rejected for this tier to keep dependencies minimal, though recommended for future tiers.
- **Cloud Function / Lambda**: Rejected to maintain the "Local-First" data privacy principle.

## References
- Feature Spec: [specs/002-silver-tier-assistant/spec.md]
- Implementation Plan: [specs/002-silver-tier-assistant/plan.md]
- Research: [specs/002-silver-tier-assistant/research.md]
