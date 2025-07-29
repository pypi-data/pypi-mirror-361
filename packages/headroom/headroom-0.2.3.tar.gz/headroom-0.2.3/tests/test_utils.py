import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from pathlib import Path
from headroom.utils import truncate_history, prune_old_entries, interpret_user_intent

def test_truncate_history_with_excess_entries():
    """Test that history is truncated to the max number of entries."""
    history = [{"prompt": str(i), "response": str(i)} for i in range(20)]
    truncated = truncate_history(history, max_entries=5)
    assert len(truncated) == 5
    assert truncated == history[-5:]

def test_truncate_history_within_limit():
    """Test that history is not truncated if it's within the max limit."""
    history = [{"prompt": str(i), "response": str(i)} for i in range(3)]
    truncated = truncate_history(history, max_entries=5)
    assert len(truncated) == 3
    assert truncated == history

def test_prune_old_entries():
    """Test that entries older than the max age are pruned."""
    now = datetime.now(timezone.utc)
    history = [
        {"timestamp": (now - timedelta(hours=48)).isoformat()}, # Should be pruned
        {"timestamp": (now - timedelta(hours=12)).isoformat()}, # Should be kept
        {"timestamp": (now - timedelta(minutes=10)).isoformat()}, # Should be kept
        {"timestamp": (now - timedelta(days=3)).isoformat()}, # Should be pruned
    ]
    pruned = prune_old_entries(history, max_age_hours=24)
    assert len(pruned) == 2
    assert pruned[0]["timestamp"] == history[1]["timestamp"]
    assert pruned[1]["timestamp"] == history[2]["timestamp"]

@pytest.mark.parametrize("prompt, expected_intent", [
    ("install htop", {"intent": "tool_use", "tool_name": "install_package", "arguments": {"package_name": "htop", "package_manager": None}}),
    ("install the package htop using apt", {"intent": "tool_use", "tool_name": "install_package", "arguments": {"package_name": "htop", "package_manager": "apt"}}),
    ("remove nano", {"intent": "tool_use", "tool_name": "remove_package", "arguments": {"package_name": "nano", "package_manager": None}}),
    ("show me the contents of /etc/hosts", {"intent": "command", "command": "raw_shell_command", "arguments": {"command_string": "cat /etc/hosts"}}),
    ("delete /tmp/test.txt", {"intent": "tool_use", "tool_name": "delete_file", "arguments": {"path": "/tmp/test.txt"}}),
    ("delete /tmp/mydir recursively", {"intent": "tool_use", "tool_name": "remove_directory", "arguments": {"path": "/tmp/mydir", "recursive": True}}),
    ("what is the meaning of life?", None), # Should fall through to LLM
])

def test_interpret_user_intent(prompt, expected_intent):
    """Test the intent interpreter with various prompts."""
    # Mock get_user_config_dir for the 'change max_entries' case if you add it
    with patch('headroom.utils.get_user_config_dir', return_value=Path("/fake/dir")):
        intent = interpret_user_intent(prompt)
        assert intent == expected_intent