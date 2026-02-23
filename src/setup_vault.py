from pathlib import Path
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.paths import find_vault_root, get_inbox_path, get_needs_action_path, get_done_path, get_logs_path

def setup_vault_structure():
    """
    Creates the necessary folder structure within the Obsidian vault.
    """
    try:
        vault_root = find_vault_root()
        print(f"Obsidian Vault Root found: {vault_root}")

        folders_to_create = [
            get_inbox_path(vault_root),
            get_needs_action_path(vault_root),
            get_done_path(vault_root),
            get_logs_path(vault_root),
            vault_root / "Approved",
            vault_root / "Plans",
        ]

        for folder in folders_to_create:
            folder.mkdir(parents=True, exist_ok=True)
            print(f"Created/Ensured directory: {folder}")
        
        # Create Dashboard.md
        dashboard_path = vault_root / "Dashboard.md"
        if not dashboard_path.exists():
            dashboard_path.write_text("""# Dashboard
## Recent Activity
- Vault initialized: """ + Path(__file__).parent.parent.parent.name + """
## Bank Balance
(Connect a Financial Watcher in Silver Tier)
## Pending Messages
(Monitor with a Communication Watcher in Silver Tier)
""")
            print(f"Created initial Dashboard.md at: {dashboard_path}")
        else:
            print(f"Dashboard.md already exists at: {dashboard_path}")
            
        # Create Company_Handbook.md
        handbook_path = vault_root / "Company_Handbook.md"
        if not handbook_path.exists():
            handbook_path.write_text("""# Company Handbook

## Rules of Engagement
- Always be polite on WhatsApp.
- Flag any payment over $500 for my approval.

## AI Employee Directives
- Prioritize tasks marked 'urgent'.
- Always log actions in the /Logs folder.
""")
            print(f"Created initial Company_Handbook.md at: {handbook_path}")
        else:
            print(f"Company_Handbook.md already exists at: {handbook_path}")

        print("Vault structure setup complete.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure 'AI_Employee_Vault' exists in the current directory or a parent directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    setup_vault_structure()
