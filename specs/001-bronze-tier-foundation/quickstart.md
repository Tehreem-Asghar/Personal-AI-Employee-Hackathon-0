# Quickstart: Bronze Tier Foundation

## Prerequisites
- Python 3.13+
- Obsidian installed with a vault named `AI_Employee_Vault`

## Setup
1. **Initialize Vault**:
   Run the setup script to create folders and essential files:
   ```bash
   python src/setup_vault.py
   ```

2. **Start Watcher**:
   Launch the file system watcher:
   ```bash
   python src/watchers/fs_watcher.py
   ```

## Verification
1. Run `python src/setup_vault.py`.
2. Verify that `AI_Employee_Vault/Inbox`, `AI_Employee_Vault/Needs_Action`, `AI_Employee_Vault/Done`, `AI_Employee_Vault/Logs` folders exist.
3. Verify that `AI_Employee_Vault/Dashboard.md` and `AI_Employee_Vault/Company_Handbook.md` exist and contain initial content.
