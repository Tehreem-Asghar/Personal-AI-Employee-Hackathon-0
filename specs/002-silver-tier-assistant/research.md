# Research: Silver Tier Functional Assistant

## Decision: Gmail API with OAuth2
- **Rationale**: The Gmail API is the most secure and robust way to monitor mail. We will use a `credentials.json` file (stored locally, not in vault) to generate a `token.json` session.
- **Filtering**: We will use the `q` parameter in the `list` method (e.g., `is:unread {invoice help pricing pricing meeting schedule project task urgent asap}`) to minimize API overhead and latency.

## Decision: Playwright Persistent Context for WhatsApp
- **Rationale**: WhatsApp Web does not have a public API for personal accounts. Playwright allows us to launch a browser with a `--user-data-dir`, meaning the user only scans the QR code once. Subsequent runs will remain logged in.
- **Detection**: We will look for elements with the "unread" aria-label and scan the snippet text for keywords.

## Decision: Model Context Protocol (MCP) for Hands
- **Rationale**: MCP is the standard for connecting AI models to external tools. An MCP server for Email will expose a `send_email` tool that Claude can call.
- **Workflow**: 
    1. Claude creates a draft in `/Pending_Approval`.
    2. User moves it to `/Approved`.
    3. An `ApprovalHandler` script (orchestrator) detects the file and triggers the MCP tool.

## Decision: Windows Task Scheduler for "Heartbeat"
- **Rationale**: To simulate 24/7 operation without a server, we will configure Task Scheduler to run the Python scripts every 15 minutes. This ensures the "Senses" are checked regularly even if the terminal is closed.

## Decision: Planner Logic
- **Rationale**: A utility will be created to wrap Claude's reasoning into a consistent `Plan.md` template. This ensures that every task follows a predictable format: Objective → Steps → Approval status.
