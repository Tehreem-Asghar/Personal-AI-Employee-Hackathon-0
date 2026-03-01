import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages the persistence of the Ralph Wiggum loop state.
    """
    def __init__(self, vault_path: Path):
        self.state_file = vault_path / ".system" / "state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self.save_state({})

    def load_state(self) -> Dict:
        """Loads the current state from disk."""
        try:
            return json.loads(self.state_file.read_text(encoding='utf-8'))
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return {}

    def save_state(self, state: Dict):
        """Saves the current state to disk."""
        try:
            self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def get_task_state(self, task_id: str) -> Optional[Dict]:
        """Retrieves state for a specific task."""
        state = self.load_state()
        return state.get(task_id)

    def update_task_state(self, task_id: str, updates: Dict):
        """Updates state for a specific task."""
        state = self.load_state()
        if task_id not in state:
            state[task_id] = {
                "iteration_count": 0,
                "status": "active",
                "history": []
            }
        state[task_id].update(updates)
        self.save_state(state)

    def mark_completed(self, task_id: str):
        """Marks a task as completed."""
        self.update_task_state(task_id, {"status": "completed"})
