import pytest
import time
import shutil
from pathlib import Path
import json
import threading
import sys
from datetime import datetime

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.watchers.fs_watcher import FileSystemWatcher
from src.utils.paths import find_vault_root, get_inbox_path, get_needs_action_path, get_logs_path
from src.utils.logger import log_event

# Fixture to set up a temporary vault for integration tests
@pytest.fixture
def integration_vault(tmp_path):
    vault_root = tmp_path / "AI_Employee_Vault"
    (vault_root / "Inbox").mkdir(parents=True)
    (vault_root / "Needs_Action").mkdir(parents=True)
    (vault_root / "Logs").mkdir(parents=True)
    return vault_root

# Mock for find_vault_root to ensure tests use the temporary vault
@pytest.fixture
def mock_find_vault_root_for_integration(integration_vault, monkeypatch):
    def mock_find(*args, **kwargs):
        return integration_vault
    monkeypatch.setattr('src.utils.paths.find_vault_root', mock_find)

@pytest.fixture
def mock_log_event(monkeypatch):
    mock_calls = []
    def mock_log(*args, **kwargs):
        mock_calls.append({'args': args, 'kwargs': kwargs})
    monkeypatch.setattr('src.watchers.fs_watcher.log_event', mock_log) # Patch where it's used
    return mock_calls

class TestFileSystemWatcherIntegration:

    @pytest.fixture
    def watcher_thread(self, integration_vault, mock_find_vault_root_for_integration):
        fs_watcher = FileSystemWatcher(integration_vault, check_interval=0.1)
        thread = threading.Thread(target=fs_watcher.run, daemon=True) # Keep daemon=True for test process to exit
        thread.start()
        yield fs_watcher # Yield the watcher instance
        fs_watcher.observer.stop()
        fs_watcher.observer.join(timeout=2) # Give it a bit more time to stop


    def test_file_drop_move_and_metadata_creation(self, integration_vault, watcher_thread, mock_find_vault_root_for_integration, mock_log_event):
        inbox = get_inbox_path(integration_vault)
        needs_action = get_needs_action_path(integration_vault)

        test_file = inbox / "test_document.txt"
        test_file.write_text("This is a test document.")

        time.sleep(0.5)  # Give the watcher time to detect and process the event

        moved_file = needs_action / "FILE_test_document.txt"
        metadata_file = needs_action / "FILE_test_document.md"

        assert moved_file.exists()
        assert metadata_file.exists()
        assert not test_file.exists() # Original file should be moved

        with open(metadata_file, 'r') as f:
            content = f.read()
            assert "type: file_drop" in content
            assert "original_name: test_document.txt" in content
            assert "status: new" in content
        
        # Verify log entry by checking mock_log_event calls
        assert len(mock_log_event) >= 2 # At least one for file_move, one for metadata_create
        assert any(call['kwargs']['action_type'] == 'file_move' and call['kwargs']['target'] == str(moved_file) for call in mock_log_event)
        assert any(call['kwargs']['action_type'] == 'metadata_create' and call['kwargs']['target'] == str(metadata_file) for call in mock_log_event)

    def test_file_moved_into_inbox(self, integration_vault, watcher_thread, mock_find_vault_root_for_integration, mock_log_event):
        inbox = get_inbox_path(integration_vault)
        needs_action = get_needs_action_path(integration_vault)

        # Create file outside inbox and move it in
        temp_file = integration_vault / "temp_file_for_move.log"
        temp_file.write_text("This file will be moved.")
        
        shutil.move(str(temp_file), str(inbox / temp_file.name))

        time.sleep(0.5)

        moved_file = needs_action / f"FILE_{temp_file.name}"
        metadata_file = needs_action / f"FILE_{temp_file.name.replace('.log', '.md')}"

        assert moved_file.exists()
        assert metadata_file.exists()
        assert not temp_file.exists()
        
        # Verify log entry by checking mock_log_event calls
        assert len(mock_log_event) >= 2 # At least one for file_move, one for metadata_create
        assert any(call['kwargs']['action_type'] == 'file_move' and call['kwargs']['target'] == str(moved_file) for call in mock_log_event)
        assert any(call['kwargs']['action_type'] == 'metadata_create' and call['kwargs']['target'] == str(metadata_file) for call in mock_log_event)
