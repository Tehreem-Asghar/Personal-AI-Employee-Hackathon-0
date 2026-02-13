from pathlib import Path
import pytest
import sys

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.utils.paths import find_vault_root, get_inbox_path, get_needs_action_path, get_done_path, get_logs_path

# Fixture to create a dummy vault structure for testing
@pytest.fixture
def dummy_vault(tmp_path):
    vault_root = tmp_path / "AI_Employee_Vault"
    vault_root.mkdir()
    (vault_root / "Inbox").mkdir()
    (vault_root / "Needs_Action").mkdir()
    (vault_root / "Done").mkdir()
    (vault_root / "Logs").mkdir()
    return vault_root

def test_find_vault_root_found_in_current_dir(dummy_vault):
    # Test if vault is found in the current directory
    assert find_vault_root(dummy_vault) == dummy_vault

def test_find_vault_root_found_in_parent_dir(dummy_vault):
    # Test if vault is found in a parent directory
    sub_dir = dummy_vault / "sub" / "sub2"
    sub_dir.mkdir(parents=True)
    assert find_vault_root(sub_dir) == dummy_vault

def test_find_vault_root_not_found(tmp_path):
    # Test if vault is not found
    with pytest.raises(FileNotFoundError):
        find_vault_root(tmp_path)

def test_get_paths(dummy_vault):
    assert get_inbox_path(dummy_vault) == dummy_vault / "Inbox"
    assert get_needs_action_path(dummy_vault) == dummy_vault / "Needs_Action"
    assert get_done_path(dummy_vault) == dummy_vault / "Done"
    assert get_logs_path(dummy_vault) == dummy_vault / "Logs"
