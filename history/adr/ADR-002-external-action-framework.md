# ADR-002: External Action Framework (MCP + Orchestrator)

- **Status:** Accepted
- **Date:** 2026-02-17
- **Feature:** silver-tier-assistant
- **Context:** Claude Code needs a standardized way to interact with external tools (like sending emails) while strictly adhering to Human-in-the-Loop (HITL) safety rules.

## Decision

We will use the **Model Context Protocol (MCP)** as the primary interface between the AI and external tools, coordinated by a file-based orchestration pattern:
- **MCP Server**: A dedicated Node.js/Python server exposing tool capabilities (e.g., `send_email`).
- **HITL Orchestration**: Claude writes a draft file to `/Pending_Approval`. A local `ApprovalHandler` monitors the `/Approved` folder and executes the corresponding MCP tool call only when the file is moved there.
- **Audit Trail**: Every execution results in a standardized JSON log entry in `/Logs`.

## Consequences

### Positive
- **Standardization**: MCP is an emerging standard, making the system interoperable with other AI agents.
- **Safety**: The physical movement of files in the vault acts as a hard gate for AI actions.
- **Transparency**: Clear separation between drafting, approval, and execution.

### Negative
- **Latency**: File-based handoffs and human approval introduce significant time delays.
- **Overhead**: Requires running an MCP server alongside the watchers.

## Alternatives Considered
- **Direct API Calls from Agent Skills**: Rejected as it bypasses the standardized tool interface and makes HITL harder to enforce consistently.
- **Interactive Prompts for Approval**: Rejected as it requires Claude to be constantly running and active.

## References
- Feature Spec: [specs/002-silver-tier-assistant/spec.md]
- Implementation Plan: [specs/002-silver-tier-assistant/plan.md]
- Research: [specs/002-silver-tier-assistant/research.md]
