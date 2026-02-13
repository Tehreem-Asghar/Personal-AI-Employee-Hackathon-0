import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure basic logging for the base watcher
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseWatcher(ABC):
    def __init__(self, vault_path: Path, check_interval: int = 60):
        self.vault_path = vault_path
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.needs_action_path.mkdir(parents=True, exist_ok=True) # Ensure directory exists

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__} watcher...')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    action_file_path = self.create_action_file(item)
                    self.logger.info(f"Created action file: {action_file_path}")
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            time.sleep(self.check_interval)

if __name__ == "__main__":
    # Example usage (for testing BaseWatcher features, not meant to be run directly)
    class DummyWatcher(BaseWatcher):
        def __init__(self, vault_path: Path, check_interval: int = 5):
            super().__init__(vault_path, check_interval)
            self.counter = 0

        def check_for_updates(self) -> list:
            self.counter += 1
            if self.counter % 2 == 0:
                self.logger.info("DummyWatcher: Found updates.")
                return [f"item_{self.counter}"]
            self.logger.info("DummyWatcher: No updates.")
            return []

        def create_action_file(self, item) -> Path:
            dummy_file = self.needs_action_path / f"{item}.md"
            dummy_file.write_text(f"Content for {item}")
            return dummy_file

    # Create a dummy AI_Employee_Vault in the current directory for testing
    dummy_vault_path = Path("AI_Employee_Vault")
    dummy_vault_path.mkdir(exist_ok=True)
    (dummy_vault_path / "Needs_Action").mkdir(exist_ok=True) # Ensure Needs_Action exists for the dummy

    print(f"Running DummyWatcher in: {dummy_vault_path}")
    dummy_watcher = DummyWatcher(dummy_vault_path)
    # To test, uncomment the line below and run this script directly.
    # It will run indefinitely, creating dummy files every 10 seconds.
    # dummy_watcher.run()
    print("DummyWatcher setup for testing. To run, uncomment dummy_watcher.run()")
    print("Delete the 'AI_Employee_Vault' folder when done testing.")
