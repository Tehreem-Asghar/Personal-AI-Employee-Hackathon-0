# Quickstart: Silver Tier Functional Assistant

## Prerequisites
- Google Cloud Project with Gmail API enabled.
- `credentials.json` downloaded from Google Cloud.
- Playwright browsers installed: `playwright install chromium`.

## Setup
1. **Gmail Authentication**:
   Place `credentials.json` in the root (it's ignored by Git). Run the watcher manually once to generate `token.json` via browser login:
   ```bash
   python src/watchers/gmail_watcher.py
   ```

2. **WhatsApp Authentication**:
   Run the WhatsApp watcher in headed mode once to scan the QR code:
   ```bash
   python src/watchers/whatsapp_watcher.py --headed
   ```
   The session will be saved in `.playwright_context/` (ignored by Git).

3. **Start the MCP Server**:
   Configure `mcp.json` in your Claude settings to point to `src/mcp/email_server.py`.

## Verification Workflow
1. **Detection**: Send an email to yourself with the subject "invoice help".
2. **Perception**: Verify `GMAIL_<id>.md` appears in `AI_Employee_Vault/Needs_Action`.
3. **Reasoning**: Claude should create `PLAN_GMAIL_<id>.md` in `/Plans`.
4. **Drafting**: Claude creates `APPROVAL_EMAIL_<id>.md` in `/Pending_Approval`.
5. **Action**: Move the file to `AI_Employee_Vault/Approved`.
6. **Confirmation**: Verify the email was actually sent and a log exists in `/Logs`.
