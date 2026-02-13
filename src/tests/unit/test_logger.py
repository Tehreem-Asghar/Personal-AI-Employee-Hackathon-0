import json
from datetime import datetime
from pathlib import Path
import pytest
from unittest.mock import patch
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.utils.logger import log_event
from src.utils.paths import find_vault_root # Import for mocking

# Fixture to create a dummy vault structure for testing
@pytest.fixture
def dummy_vault_for_logger(tmp_path):
    vault_root = tmp_path / "AI_Employee_Vault"
    (vault_root / "Logs").mkdir(parents=True)
    return vault_root

@patch('src.utils.paths.find_vault_root')
def test_log_event_creates_new_file(mock_find_vault_root, dummy_vault_for_logger):
    mock_find_vault_root.return_value = dummy_vault_for_logger
    
    log_event("test_action", "test_actor", "test_target", "success", {"key": "value"})
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    log_file_path = dummy_vault_for_logger / "Logs" / f"{today_str}.json"
    
    assert log_file_path.exists()
    with open(log_file_path, 'r', encoding='utf-8') as f:
        logs = json.load(f)
        assert len(logs) == 1
        assert logs[0]["action_type"] == "test_action"
        assert logs[0]["actor"] == "test_actor"
        assert logs[0]["target"] == "test_target"
        assert logs[0]["result"] == "success"
        assert logs[0]["details"]["key"] == "value"
        assert "timestamp" in logs[0]

@patch('src.utils.paths.find_vault_root')
def test_log_event_appends_to_existing_file(mock_find_vault_root, dummy_vault_for_logger):
    mock_find_vault_root.return_value = dummy_vault_for_logger

    # Create an initial log entry
    log_event("first_action", "actor1", "target1", "success")

    # Create a second log entry
    log_event("second_action", "actor2", "target2", "success")

    today_str = datetime.now().strftime('%Y-%m-%d')
    log_file_path = dummy_vault_for_logger / "Logs" / f"{today_str}.json"

    with open(log_file_path, 'r', encoding='utf-8') as f:
        logs = json.load(f)
        assert len(logs) == 2
        assert logs[0]["action_type"] == "first_action"
        assert logs[1]["action_type"] == "second_action"

@patch('src.utils.paths.find_vault_root')
def test_log_event_handles_file_not_found(mock_find_vault_root, capsys):
    mock_find_vault_root.side_effect = FileNotFoundError("Vault not found for test")
    
    log_event("action", "actor", "target", "fail")
    
    captured = capsys.readouterr()
    assert "ERROR: Could not log event. Vault root not found: Vault not found for test" in captured.out

@patch('src.utils.paths.find_vault_root')
def test_log_event_handles_malformed_json(mock_find_vault_root, dummy_vault_for_logger):
    mock_find_vault_root.return_value = dummy_vault_for_logger
    log_file_path = dummy_vault_for_logger / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    log_file_path.write_text("this is not json") # Write malformed JSON

    log_event("action", "actor", "target", "success") # This should still append

    with open(log_file_path, 'r', encoding='utf-8') as f:
        logs = json.load(f) # Should now be valid JSON with one entry
        assert len(logs) == 1
        assert logs[0]["action_type"] == "action"
