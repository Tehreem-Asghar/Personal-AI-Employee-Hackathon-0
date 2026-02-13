import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.paths import get_logs_path, find_vault_root

def log_event(action_type: str, actor: str, target: str, result: str, details: Dict[str, Any] = None):
    """
    Logs an event in JSON format to a daily log file within the vault's /Logs folder.
    Schema based on Section 6.3 of the architecture document.
    """
    try:
        vault_root = find_vault_root()
        logs_path = get_logs_path(vault_root)
        logs_path.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "result": result,
        }
        if details:
            log_entry["details"] = details
        
        log_file_name = f"{datetime.now().strftime('%Y-%m-%d')}.json"
        log_file_path = logs_path / log_file_name

        # Read existing logs, append new entry, and write back
        logs_data = []
        if log_file_path.exists():
            with open(log_file_path, 'r', encoding='utf-8') as f:
                try:
                    logs_data = json.load(f)
                except json.JSONDecodeError:
                    logs_data = [] # Handle malformed JSON

        logs_data.append(log_entry)

        with open(log_file_path, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, indent=2)

    except FileNotFoundError as e:
        print(f"ERROR: Could not log event. Vault root not found: {e}")
    except Exception as e:
        print(f"ERROR: Failed to write log entry: {e}")

if __name__ == "__main__":
    # This will only run if AI_Employee_Vault exists in the current directory or parent
    # For testing, ensure you have a structure like:
    # current_dir/AI_Employee_Vault/Logs/
    
    # Create a dummy AI_Employee_Vault/Logs for testing
    try:
        vault = find_vault_root(Path.cwd().parent) # Assuming vault is a sibling
    except FileNotFoundError:
        # If not found, create a dummy one in current working dir
        Path("AI_Employee_Vault/Logs").mkdir(parents=True, exist_ok=True)
    
    log_event("test_action", "test_actor", "test_target", "success", {"key": "value"})
    print("Test log entry created. Check AI_Employee_Vault/Logs/YYYY-MM-DD.json")
