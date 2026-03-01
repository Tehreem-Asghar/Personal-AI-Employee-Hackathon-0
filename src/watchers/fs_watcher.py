import sys
import os
from pathlib import Path
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add the project root to the sys.path to allow imports from src
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.watchers.base_watcher import BaseWatcher
from src.utils.paths import find_vault_root, get_inbox_path, get_needs_action_path
from src.utils.logger import log_event

class FileSystemWatcher(BaseWatcher):
    def __init__(self, vault_path: Path, check_interval: int = 5):
        super().__init__(vault_path, check_interval)
        self.inbox_path = get_inbox_path(vault_path)
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        self.observer = Observer()
        self.event_handler = self._create_event_handler()
        self.observed_events = []

    def _create_event_handler(self):
        class Handler(FileSystemEventHandler):
            def __init__(self, watcher_instance):
                super().__init__()
                self.watcher = watcher_instance

            def on_created(self, event):
                if not event.is_directory:
                    self.watcher.observed_events.append(event)
            
            def on_moved(self, event):
                if not event.is_directory and Path(event.dest_path).parent == self.watcher.inbox_path:
                    self.watcher.observed_events.append(event)

        return Handler(self)

    def check_for_updates(self) -> list:
        events_to_process = self.observed_events
        self.observed_events = []
        return events_to_process

    def create_action_file(self, event) -> Path:
        source_path = Path(event.src_path if event.event_type != 'moved' else event.dest_path)
        if not source_path.is_file(): return None

        # UNIFIED WORKFLOW (Like Gmail): Merge metadata into the file
        file_name = source_path.name
        dest_name = f"FILE_{file_name}"
        if not dest_name.endswith(".md"): dest_name += ".md"
        
        dest_path = self.needs_action_path / dest_name

        try:
            # Read original content
            original_content = source_path.read_text(encoding='utf-8', errors='ignore')
            
            # Create professional metadata header (Gmail style)
            meta_header = f"""---
type: file_drop
from: local_system
original_name: {file_name}
received: {datetime.now().isoformat()}
status: new
---
# File Drop: {file_name}

{original_content}
"""
            # Write to single file in Needs_Action
            dest_path.write_text(meta_header, encoding='utf-8')
            
            # Delete original from Inbox
            source_path.unlink()
            
            self.logger.info(f"Processed: {file_name} -> {dest_name}")
            log_event("file_process", "fs_watcher", str(dest_path), "success")
            return dest_path
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None

    def run(self):
        self.logger.info(f'Starting FS watcher for: {self.inbox_path}')
        self.observer.schedule(self.event_handler, str(self.inbox_path), recursive=False)
        self.observer.start()
        try:
            while True:
                super().run()
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    try:
        vault_root = find_vault_root()
        fs_watcher = FileSystemWatcher(vault_root)
        if args.once:
            inbox = get_inbox_path(vault_root)
            from watchdog.events import FileCreatedEvent
            for file in inbox.iterdir():
                if file.is_file():
                    fs_watcher.create_action_file(FileCreatedEvent(str(file)))
        else:
            fs_watcher.run()
    except Exception as e:
        print(f"Error: {e}")
