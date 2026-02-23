# Personal AI Employee Hackathon - Bronze Tier Foundation

This repository contains the foundational implementation for the "Personal AI Employee Hackathon" focusing on the Bronze Tier deliverables. The goal is to set up a local-first, agent-driven system that proactively manages personal and business affairs.

## Bronze Tier Deliverables (Minimum Viable)

The Bronze Tier establishes the core local infrastructure:

-   **Obsidian Vault Structure**: Standardized folders (`Inbox`, `Needs_Action`, `Done`, `Logs`).
-   **Essential Documents**: `Dashboard.md` and `Company_Handbook.md`.
-   **Watcher Script**: A working File System Watcher to monitor the `Inbox`.
-   **Claude Integration**: Claude Code successfully reads from and writes to the vault (simulated via file creation/modification).
-   **Agent Skills**: All AI functionality (watchers, setup scripts) are structured as modular components.

## Architecture Overview (Bronze Tier Focus)

The Bronze Tier focuses on the "Memory/GUI" (Obsidian) and "Senses" (Watchers) components of the overall AI Employee architecture.

-   **Memory/GUI (Obsidian)**: Acts as the primary knowledge base and dashboard. All processed information and tasks reside here.
-   **Senses (File System Watcher)**: A Python script that continuously monitors the vault's `Inbox` for new files. When a file is detected, it's moved to `Needs_Action` and a metadata `.md` file is created for processing.
-   **Claude Code (Implicit)**: In this tier, Claude's role is simulated by the watcher creating actionable files that Claude would theoretically process.

## Setup Instructions

### Prerequisites

-   **Python**: Version 3.13 or higher.
-   **Obsidian**: Installed on your system.
-   **Obsidian Vault**: A new Obsidian vault named `AI_Employee_Vault` (or similar, ensure `src/utils/paths.py` is configured to find it) at the root of your project or in a parent directory.

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone [repository_url]
    cd personal-ai-employee-hackathon-0
    ```
2.  **Create Virtual Environment**:
    ```bash
    python -m venv .venv
    ```
3.  **Activate Virtual Environment**:
    -   **Windows (PowerShell)**:
        ```bash
        .\.venv\Scripts\Activate.ps1
        ```
    -   **macOS/Linux**:
        ```bash
        source ./.venv/bin/activate
        ```
4.  **Install Dependencies**:
    ```bash
    .\.venv\Scripts\pip.exe install -r requirements.txt # (If you have one, or install individually)
    .\.venv\Scripts\pip.exe install watchdog
    ```
    *Note: `watchdog` is the primary dependency for the File System Watcher.*
5.  **Setup Vault Structure**:
    ```bash
    python src/setup_vault.py
    ```
    This script will create the necessary folders (`Inbox`, `Needs_Action`, `Done`, `Logs`) and initial documents (`Dashboard.md`, `Company_Handbook.md`) within your `AI_Employee_Vault`.

## Running the File System Watcher

1.  **Ensure Virtual Environment is Active**:
    (If not, follow step 3 in Installation)
2.  **Start the Watcher**:
    ```bash
    python src/watchers/fs_watcher.py
    ```
    The watcher will start monitoring your `AI_Employee_Vault/Inbox` folder.

## Verification

1.  **Run Vault Setup**: `python src/setup_vault.py`
2.  **Check Folders**: Verify `AI_Employee_Vault/Inbox`, `AI_Employee_Vault/Needs_Action`, `AI_Employee_Vault/Done`, `AI_Employee_Vault/Logs` exist.
3.  **Check Documents**: Verify `AI_Employee_Vault/Dashboard.md` and `AI_Employee_Vault/Company_Handbook.md` exist and contain initial content.
4.  **Test Watcher**:
    -   Start the watcher: `python src/watchers/fs_watcher.py`
    -   Drop a new text file (e.g., `new_idea.txt`) into `AI_Employee_Vault/Inbox`.
    -   Verify that `new_idea.txt` is moved to `AI_Employee_Vault/Needs_Action/FILE_new_idea.txt`.
    -   Verify `AI_Employee_Vault/Needs_Action/FILE_new_idea.md` is created with metadata.
    -   Check `AI_Employee_Vault/Logs/YYYY-MM-DD.json` for corresponding log entries.

---

## 🥈 Silver Tier: Functional Assistant

Silver Tier introduces external communication and structured reasoning.

### 1. External Authentication (One-time Setup)

- **Gmail**: 
  1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
  2. Enable Gmail API and download `credentials.json` to the project root.
  3. Run `python src/watchers/gmail_watcher.py` and log in via browser. This creates `token.json`.
- **WhatsApp**:
  1. Run `python src/watchers/whatsapp_watcher.py --headed`.
  2. Scan the QR code. The session is saved in `.playwright_context/`.

### 2. External Action (Email MCP)

The system now includes an **Email MCP Server** (`src/mcp/email_server.py`). 
- Claude can use the `send_email` tool.
- **Safety**: Claude will draft the email in `AI_Employee_Vault/Pending_Approval`.
- **Approval**: Move the file to `AI_Employee_Vault/Approved`. The `ApprovalHandler` will detect it and send the email.

### 3. Automated Heartbeat (Windows)

To run the system every 5 minutes automatically, run this in an **Administrator PowerShell**:

# 1. Create Action (Hidden PowerShell Execution)
```powershell
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"D:\Personal AI Employee Hackathon 0\personal-ai-employee-hackathon-0\src\run_senses.ps1`""
```
# 2. Create Repeating Trigger (Every 5 Minutes)
```powershell
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
```
# 3. Create Startup Trigger
```powershell
$StartupTrigger = New-ScheduledTaskTrigger -AtStartup
```
# 4. Register Task (Runs under current logged-in user)
```powershell
Register-ScheduledTask -TaskName "AI_Employee_Heartbeat" -Action $Action -Trigger @($Trigger,$StartupTrigger) -Description "Digital FTE Perception & Action Loop"
```

---

## 🛠️ Claude CLI Skills

This project leverages specialized Claude Code skills to manage the vault and generate creative content.

### 1. Vault Audit (`vault-audit`)
Provides a high-level summary of your workload and vault status.
```bash
# View current status report
python .claude/skills/vault-audit/vault_audit.py
```

### 2. Social Expert (`social-expert`)
Drafts 3 versions of a LinkedIn post based on your input.
```bash
# Generate 3 drafts (Professional, Storytelling, Punchy)
python .claude/skills/social-expert/social_expert.py "Your project update here"
```

### 3. Briefing Genius (`briefing-genius`)
Analyzes completed work and generates a Daily CEO Briefing.
```bash
# Generate today's briefing
python .claude/skills/briefing-genius/briefing_genius.py

# Generate briefing for a specific date
python .claude/skills/briefing-genius/briefing_genius.py --date 2026-02-22

# Preview briefing in console without saving
python .claude/skills/briefing-genius/briefing_genius.py --preview

# Use a custom vault path
python .claude/skills/briefing-genius/briefing_genius.py --vault-path "D:\path\to\AI_Employee_Vault"
```

# Temporary Stop commands of Task Scheduler  

```powershell
Stop-ScheduledTask -TaskName "AI_Employee_Heartbeat"
```
```powershell
Disable-ScheduledTask -TaskName "AI_Employee_Heartbeat"
```

```powershell
Enable-ScheduledTask -TaskName "AI_Employee_Heartbeat"
```