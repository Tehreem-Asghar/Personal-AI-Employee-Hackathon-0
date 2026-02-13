from pathlib import Path
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.watchers.base_watcher import BaseWatcher
from src.utils.paths import find_vault_root, get_inbox_path, get_needs_action_path
from src.utils.logger import log_event

class FileSystemWatcher(BaseWatcher):
    def __init__(self, vault_path: Path, check_interval: int = 5):
        super().__init__(vault_path, check_interval)
        self.inbox_path = get_inbox_path(vault_path)
        self.inbox_path.mkdir(parents=True, exist_ok=True) # Ensure Inbox exists

        self.observer = Observer()
        self.event_handler = self._create_event_handler()
        self.observed_events = [] # To store events for processing in check_for_updates

    def _create_event_handler(self):
        class Handler(FileSystemEventHandler):
            def __init__(self, watcher_instance):
                super().__init__()
                self.watcher = watcher_instance

            def on_created(self, event):
                if not event.is_directory:
                    self.watcher.observed_events.append(event)
                    self.watcher.logger.info(f"Detected new file: {event.src_path}")
            
            def on_moved(self, event):
                # Handle move event as creation in case of external move into inbox
                if not event.is_directory and Path(event.dest_path).parent == self.watcher.inbox_path:
                    self.watcher.observed_events.append(event)
                    self.watcher.logger.info(f"Detected moved file into inbox: {event.dest_path}")


        return Handler(self)

    def check_for_updates(self) -> list:
        # Process observed events
        events_to_process = self.observed_events
        self.observed_events = [] # Clear the list
        return events_to_process

    def create_action_file(self, event) -> Path:
        source_path = Path(event.src_path)
        # Handle move events where src_path is the original location
        if event.event_type == 'moved':
            source_path = Path(event.dest_path)

        if not source_path.is_file(): # Ensure it's a file
            return

        # Define destination path in Needs_Action folder
        file_name = source_path.name
        dest_file_name = f"FILE_{file_name}"
        dest_path_in_needs_action = self.needs_action_path / dest_file_name

        # Move the file
        try:
            shutil.move(str(source_path), str(dest_path_in_needs_action))
            self.logger.info(f"Moved '{source_path}' to '{dest_path_in_needs_action}'")
            log_event(
                action_type="file_move",
                actor="fs_watcher",
                target=str(dest_path_in_needs_action),
                result="success",
                details={"original_path": str(source_path)}
            )
        except Exception as e:
            self.logger.error(f"Failed to move file {source_path}: {e}")
            log_event(
                action_type="file_move",
                actor="fs_watcher",
                target=str(source_path),
                result="failure",
                details={"error": str(e)}
            )
            raise # Re-raise to be caught by run() method's error handling

        # Create metadata .md file
        meta_file_path = dest_path_in_needs_action.with_suffix('.md')
        meta_content = f"""---
type: file_drop
original_name: {file_name}
size: {source_path.stat().st_size if source_path.exists() else 'N/A'}
received: {datetime.now().isoformat()}
status: new
---
# File Drop: {file_name}

New file detected and moved for processing.
"""
        meta_file_path.write_text(meta_content)
        self.logger.info(f"Created metadata file: {meta_file_path}")
        log_event(
            action_type="metadata_create",
            actor="fs_watcher",
            target=str(meta_file_path),
            result="success",
            details={"original_file": str(dest_path_in_needs_action)}
        )

        return meta_file_path

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__} watcher for: {self.inbox_path}')
        self.observer.schedule(self.event_handler, str(self.inbox_path), recursive=False)
        self.observer.start()
        try:
            while True:
                # BaseWatcher's run loop now calls check_for_updates() and create_action_file()
                # The observer is just feeding events to self.observed_events
                super().run() 
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    try:
        vault_root = find_vault_root()
    except FileNotFoundError:
        # Create a dummy vault for testing if not found
        Path("AI_Employee_Vault/Inbox").mkdir(parents=True, exist_ok=True)
        Path("AI_Employee_Vault/Needs_Action").mkdir(parents=True, exist_ok=True)
        Path("AI_Employee_Vault/Logs").mkdir(parents=True, exist_ok=True)
        vault_root = find_vault_root() # Find it again now that it's created

    print(f"Monitoring: {get_inbox_path(vault_root)}")
    fs_watcher = FileSystemWatcher(vault_root)
    fs_watcher.run()
