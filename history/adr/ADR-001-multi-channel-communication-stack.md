# ADR-001: Multi-Channel Communication Stack

- **Status:** Accepted
- **Date:** 2026-02-17
- **Feature:** silver-tier-assistant
- **Context:** The Digital FTE needs to monitor and respond to client inquiries across multiple channels (Gmail and WhatsApp) while maintaining security and reliability.

## Decision

We will implement a modular perception layer using:
- **Gmail**: Official Gmail API with OAuth2 for secure, reliable access.
- **WhatsApp**: Playwright-based browser automation using a persistent browser context to maintain the session after a manual QR scan.
- **Filtering**: Keyword-based filtering (Financial, Scheduling, Operational, Urgency, Support) applied at the watcher level to minimize noise.

## Consequences

### Positive
- **Security**: Gmail API avoids password storage; Playwright persistent context avoids repeated QR scans.
- **Reliability**: Using official APIs for Gmail ensures long-term stability.
- **Relevance**: Keyword filtering ensures the AI only processes actionable business data.

### Negative
- **Complexity**: Playwright requires browser dependencies and handling of async DOM changes.
- **Maintenance**: WhatsApp Web UI changes may break the automation periodically.

## Alternatives Considered
- **Twilio WhatsApp API**: Rejected due to cost and requirement for a Business Profile.
- **IMAP for Gmail**: Rejected in favor of API for better security and searching capabilities.

## References
- Feature Spec: [specs/002-silver-tier-assistant/spec.md]
- Implementation Plan: [specs/002-silver-tier-assistant/plan.md]
- Research: [specs/002-silver-tier-assistant/research.md]
