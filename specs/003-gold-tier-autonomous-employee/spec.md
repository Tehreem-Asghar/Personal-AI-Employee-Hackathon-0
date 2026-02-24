# Specification: Gold Tier - Autonomous Employee (Digital FTE)

## 1. Overview
The Gold Tier transforms the AI Employee from a reactive assistant into a proactive business unit. It introduces full cross-domain integration (Personal + Business), professional accounting via Odoo, and multi-channel social media management.

## 2. Strategic Objectives
- **Full Autonomy**: Implement the "Ralph Wiggum" loop to allow the agent to self-correct and iterate until tasks are marked as `/Done`.
- **Financial Integrity**: Integrate Odoo Community (v19+) for formal bookkeeping and transaction auditing.
- **Brand Presence**: Expand social media reach to Facebook, Instagram, and Twitter (X) with automated summaries.
- **Executive Visibility**: Deliver a weekly "Monday Morning CEO Briefing" that synthesizes logs and financial data into actionable insights.

## 3. Clarifications

### Session 2026-02-24
- Q: How will the AI connect to the Odoo instance? → A: Local JSON-RPC via http://localhost:8069.
- Q: Where will the 'Ralph Wiggum' loop state be stored? → A: Inside the Obsidian Vault (AI_Employee_Vault/.system/state.json).
- Q: How will the AI post to multiple social media channels? → A: Direct Platform APIs (Meta Graph API, X API v2, etc.).
- Q: How will the CEO Briefing be delivered to the user? → A: As a Markdown file in AI_Employee_Vault/Briefings/.
- Q: How should the user be notified if a critical process fails? → A: Notification via Email or WhatsApp after auto-restart.

## 4. Technical Requirements

### 4.1 Accounting & ERP (Odoo Integration)
- **MCP Server**: Create `odoo-mcp` using Odoo's JSON-RPC API.
- **Connection**: Connect to local-first Odoo Community instance via `http://localhost:8069`.
- **Capabilities**:
    - `get_revenue`: Fetch total earnings for a specific period.
    - `log_transaction`: Record new business expenses or income.
    - `audit_subscriptions`: Identify recurring payments for cost optimization.

### 4.2 Multi-Channel Social Media
- **Expansion**: Extend beyond LinkedIn to Facebook, Instagram, and Twitter (X).
- **Implementation**: Use direct official SDKs (e.g., `facebook-sdk`, `tweepy`, `python-linkedin-v2`) and official platform APIs.
- **Automation**: 
    - Generate platform-specific content (e.g., punchy for Twitter, visual-focused for IG).
    - Auto-drafting of posts into `/Pending_Approval`.
    - Automated summary generation of audience engagement (if API-accessible).

### 4.3 The "Ralph Wiggum" Loop (Persistence)
- **Pattern**: Implement a stop-hook that intercepts Claude's exit.
- **State Storage**: Persist state in `AI_Employee_Vault/.system/state.json`.
- **Mechanism**: 
    1. Read task from `/Needs_Action`.
    2. Execute steps.
    3. Check if file is in `/Done`.
    4. If NOT in `/Done`, re-inject prompt with current state and continue.
- **Safety**: Max 10 iterations per task to prevent infinite loops.

### 4.4 Monday Morning CEO Briefing
- **Trigger**: Automated Sunday night run.
- **Delivery**: Markdown report saved to `AI_Employee_Vault/Briefings/YYYY-MM-DD_CEO_Briefing.md`.
- **Data Sources**: Odoo (Revenue), `/Logs` (Productivity), `Business_Goals.md` (Objectives).
- **Report Sections**:
    - **Revenue**: Total earned vs. Monthly target.
    - **Bottlenecks**: Tasks taking > 48 hours or requiring > 3 iterations.
    - **Proactive Suggestions**: Cost-saving tips (e.g., redundant subscriptions) or growth opportunities.

### 4.5 Orchestration & Resilience
- **Watchdog Process**: A master `watchdog.py` that monitors the PIDs of all watchers (Gmail, WhatsApp, FS) and the orchestrator.
- **Auto-Restart**: Immediate restart of failed processes with logging.
- **Notification**: On process failure/restart, send an alert via Email or WhatsApp to the human supervisor.

## 5. Security & Safety
- **HITL Gatekeeping**: Payments > $50 and Public Social Posts MUST require human movement to `/Approved`.
- **Credential Isolation**: Odoo and Social API keys MUST be stored in `.env` (strictly excluded from git).
- **Audit Logging**: Standardized JSON logs for every external action for 90-day retention.

## 6. Success Criteria
1.  **Autonomous Flow**: A WhatsApp invoice request results in a generated invoice, an Odoo entry, and an email draft without manual intervention.
2.  **Financial Accuracy**: CEO Briefing revenue matches Odoo records exactly.
3.  **Resilience**: Killing a watcher process results in its automatic revival within 60 seconds.
