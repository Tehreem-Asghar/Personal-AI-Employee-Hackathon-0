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
