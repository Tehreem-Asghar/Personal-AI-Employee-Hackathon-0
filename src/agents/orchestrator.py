import os
import sys
import time
import logging
from pathlib import Path
from typing import List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root
from src.utils.state_manager import StateManager
from src.utils.logger import log_event

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    def __init__(self):
        self.vault_root = find_vault_root()
        self.state_manager = StateManager(self.vault_root)
        self.needs_action_path = self.vault_root / "Needs_Action"
        self.done_path = self.vault_root / "Done"
        self.in_progress_path = self.vault_root / "In_Progress"
        
        # Ensure directories exist
        for p in [self.needs_action_path, self.done_path, self.in_progress_path]:
            p.mkdir(parents=True, exist_ok=True)

    def scan_tasks(self) -> List[Path]:
        """Scans the /In_Progress folder for tasks that need execution logic."""
        # Orchestrator should only work on files already drafted or specifically assigned to it.
        return [f for f in self.in_progress_path.iterdir() if f.is_file() and f.suffix == ".md"]

    def process_task(self, task_file: Path):
        """
        Orchestrates the processing of a single task using the Ralph Wiggum loop logic.
        """
        task_id = task_file.name
        state = self.state_manager.get_task_state(task_id) or {
            "iteration_count": 0,
            "status": "active"
        }

        # 2. Logic: In a real standalone autonomous FTE, this script would now invoke
        # Claude Code via CLI: `claude "Process this task file: {current_task_path}"`
        # For the hackathon, we simulate the "Trigger" part.
        
        # We simulate reasoning progress by incrementing iteration count
        new_count = state["iteration_count"] + 1
        self.state_manager.update_task_state(task_id, {
            "iteration_count": new_count,
            "last_processed": time.time()
        })

        # 3. Check if task is finished (Simulation: If marked 'completed' in state)
        # In practice, Claude would move the file to /Done when finished.
        if (self.done_path / task_file.name).exists():
            logger.info(f"Task {task_id} confirmed in /Done. Terminating loop.")
            self.state_manager.mark_completed(task_id)
            log_event("task_completed", "orchestrator", str(task_id), "success")
        else:
            logger.info(f"Task {task_id} still active. Re-injecting into loop...")

    def run(self, once=False):
        logger.info("Autonomous Orchestrator (The Muscle) started.")
        while True:
            tasks = self.scan_tasks()
            if tasks:
                logger.info(f"Found {len(tasks)} new tasks.")
                for task in tasks:
                    self.process_task(task)
            
            if once: break
            time.sleep(30)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    
    orchestrator = Orchestrator()
    orchestrator.run(once=args.once)
