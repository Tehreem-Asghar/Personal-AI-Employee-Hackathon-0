from pathlib import Path
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent))

def find_vault_root(start_path: Path = Path.cwd()) -> Path:
    """
    Finds the root of the Obsidian vault by looking for a directory named 'AI_Employee_Vault'.
    Searches upwards from the start_path.
    """
    current_path = start_path
    while current_path != current_path.parent:
        if (current_path / "AI_Employee_Vault").is_dir():
            return current_path / "AI_Employee_Vault"
        current_path = current_path.parent
    
    # If not found going up, check current directory
    if (start_path / "AI_Employee_Vault").is_dir():
        return start_path / "AI_Employee_Vault"
        
    raise FileNotFoundError("Obsidian vault 'AI_Employee_Vault' not found.")

def get_inbox_path(vault_root: Path) -> Path:
    return vault_root / "Inbox"

def get_needs_action_path(vault_root: Path) -> Path:
    return vault_root / "Needs_Action"

def get_done_path(vault_root: Path) -> Path:
    return vault_root / "Done"

def get_logs_path(vault_root: Path) -> Path:
    return vault_root / "Logs"

if __name__ == "__main__":
    try:
        vault = find_vault_root()
        print(f"Vault Root: {vault}")
        print(f"Inbox: {get_inbox_path(vault)}")
        print(f"Needs Action: {get_needs_action_path(vault)}")
        print(f"Done: {get_done_path(vault)}")
        print(f"Logs: {get_logs_path(vault)}")
    except FileNotFoundError as e:
        print(e)
