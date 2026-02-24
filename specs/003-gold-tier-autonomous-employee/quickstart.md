# Quickstart: Gold Tier - Autonomous Employee

## 1. Odoo Community Setup
To achieve Gold Tier status, you MUST have a local Odoo instance running.

1.  **Install Odoo v19+**:
    - Download Odoo Community Edition (Docker or Installer).
    - Run on `http://localhost:8069`.
2.  **Database Configuration**:
    - Create a database named `ai_employee`.
    - Install the `Invoicing` and `Accounting` modules.
3.  **API Credentials**:
    - Create a user for the AI (e.g., `ai_agent`).
    - Note down: `db_name`, `username`, and `password`.

## 2. Social Media API Keys
Obtain official developer credentials for all channels:

- **LinkedIn**: [LinkedIn Developer Portal](https://www.linkedin.com/developers/) (Marketing Developer Platform)
- **Twitter (X)**: [X Developer Portal](https://developer.twitter.com/en/portal/dashboard) (API v2)
- **Facebook/Instagram**: [Meta for Developers](https://developers.facebook.com/) (Graph API)

## 3. Environment Variables (`.env`)
Add the following to your root `.env` file (NOT in the vault):

```env
# Odoo Credentials
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USER=ai_agent
ODOO_PASS=your_password

# Twitter/X API
X_API_KEY=...
X_API_SECRET=...
X_BEARER_TOKEN=...

# Meta Graph API
FB_ACCESS_TOKEN=...
FB_PAGE_ID=...
IG_USER_ID=...

# LinkedIn API
LI_CLIENT_ID=...
LI_CLIENT_SECRET=...
LI_ACCESS_TOKEN=...
```

## 4. Launch Sequence

1.  **Install Dependencies**:
    ```bash
    pip install odoorpc tweepy facebook-sdk python-linkedin-v2 psutil
    ```
2.  **Start Odoo**: Ensure your local Odoo service is active.
3.  **Start Watchdog**:
    ```bash
    python src/watchers/watchdog.py
    ```
4.  **Start Orchestrator**:
    ```bash
    python src/agents/orchestrator.py
    ```

## 5. Verification
1.  **Financial**: Post a test transaction via Odoo and verify it appears in `AI_Employee_Vault/Logs/`.
2.  **Social**: Create a `SOCIAL_test.md` in `/Needs_Action` and verify a draft appears in `/Pending_Approval`.
3.  **Resilience**: Manually kill the `gmail_watcher.py` process and verify the `watchdog.py` restarts it within 60 seconds.
