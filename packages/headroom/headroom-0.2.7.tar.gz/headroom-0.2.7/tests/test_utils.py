import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, mock_open # Import mock_open
import yaml # Import yaml
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

# Tests for Configuration Management (Validation - config.yaml)
from headroom import utils as utils_module # To allow patching utils.Path

@patch('headroom.utils.load_dotenv') # Mock environment loading
@patch('shutil.copy') # Mock copying of default config
@patch('headroom.utils.Path.exists')
@patch('builtins.open', new_callable=mock_open)
@patch('yaml.safe_load')
@patch('logging.error')
@patch('logging.warning')
@patch('builtins.print') # To capture print calls for error messages
def test_load_config_valid(mock_print, mock_log_warn, mock_log_err, mock_safe_load, mock_file_open, mock_path_exists, mock_shutil_copy, mock_load_env, tmp_path):
    # Simulate .env and config.yaml existing and being valid
    mock_path_exists.return_value = True
    mock_safe_load.return_value = {
        "commands": {
            "test_cmd": {"command": "echo test", "description": "A test command"}
        },
        "conversation": {"max_entries": 15}
    }
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "test", "OLLAMA_ENDPOINT": "http://test"}):
        config = utils_module.load_config()

    assert config is not None
    assert config['llm']['provider'] == "ollama"
    assert config['conversation']['max_entries'] == 15
    assert config['conversation']['max_age_hours'] == 24 # Default
    assert "test_cmd" in config['commands']
    mock_log_err.assert_not_called()
    # Check if any "Error:" print was made. Specific default config creation print is ok.
    error_prints = [call for call in mock_print.call_args_list if call[0][0].startswith("Error:")]
    assert not error_prints, f"Expected no error prints, but got: {error_prints}"


@patch('headroom.utils.load_dotenv')
@patch('shutil.copy')
@patch('headroom.utils.Path.exists')
@patch('builtins.open', new_callable=mock_open)
@patch('yaml.safe_load')
@patch('logging.error')
@patch('builtins.print')
def test_load_config_bad_yaml_not_dict(mock_print, mock_log_err, mock_safe_load, mock_file_open, mock_path_exists, mock_shutil_copy, mock_load_env, tmp_path):
    mock_path_exists.return_value = True
    mock_safe_load.return_value = "This is not a dictionary" # Invalid top-level type

    mock_config_dir_path = tmp_path / "test_config_dir_bad_yaml"
    expected_config_file_path = mock_config_dir_path / "config.yaml"

    with patch('headroom.utils.get_user_config_dir', return_value=mock_config_dir_path):
        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "test", "OLLAMA_ENDPOINT": "http://test"}):
            config = utils_module.load_config()

    assert config is None
    mock_log_err.assert_any_call(f"Config file {expected_config_file_path} did not load as a dictionary.")
    mock_print.assert_any_call(f"Error: {expected_config_file_path} is not a valid YAML dictionary.")


@patch('headroom.utils.load_dotenv')
@patch('shutil.copy')
@patch('headroom.utils.Path.exists')
@patch('builtins.open', new_callable=mock_open)
@patch('yaml.safe_load')
@patch('logging.error')
@patch('builtins.print')
def test_load_config_invalid_commands_section(mock_print, mock_log_err, mock_safe_load, mock_file_open, mock_path_exists, mock_shutil_copy, mock_load_env, tmp_path):
    mock_path_exists.return_value = True
    mock_safe_load.return_value = {"commands": "not a dict"}

    mock_config_dir_path = tmp_path / "test_config_dir_invalid_commands"
    expected_config_file_path = mock_config_dir_path / "config.yaml"

    with patch('headroom.utils.get_user_config_dir', return_value=mock_config_dir_path):
        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "test", "OLLAMA_ENDPOINT": "http://test"}):
            config = utils_module.load_config()

    assert config is None
    mock_log_err.assert_any_call("'commands' section in config.yaml is not a dictionary.")
    mock_print.assert_any_call(f"Error: 'commands' section in {expected_config_file_path} must be a dictionary.")

@patch('headroom.utils.load_dotenv')
@patch('shutil.copy')
@patch('headroom.utils.Path.exists')
@patch('builtins.open', new_callable=mock_open)
@patch('yaml.safe_load')
@patch('logging.error')
@patch('builtins.print')
def test_load_config_command_missing_command_string(mock_print, mock_log_err, mock_safe_load, mock_file_open, mock_path_exists, mock_shutil_copy, mock_load_env, tmp_path):
    mock_path_exists.return_value = True
    mock_safe_load.return_value = {
        "commands": {"my_cmd": {"description": "a cmd"}} # Missing "command" key
    }
    mock_config_dir_path = tmp_path / "test_config_dir_missing_cmd_str"
    expected_config_file_path = mock_config_dir_path / "config.yaml"

    with patch('headroom.utils.get_user_config_dir', return_value=mock_config_dir_path):
        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "test", "OLLAMA_ENDPOINT": "http://test"}):
            config = utils_module.load_config()

    assert config is None
    mock_log_err.assert_any_call("Command 'my_cmd' in config.yaml missing 'command' string.")
    mock_print.assert_any_call(f"Error: Command 'my_cmd' in {expected_config_file_path} must have a 'command' string.")

@patch('headroom.utils.load_dotenv')
@patch('shutil.copy')
@patch('headroom.utils.Path.exists', return_value=True) # Assume config exists
@patch('builtins.open', new_callable=mock_open)
@patch('yaml.safe_load')
@patch('logging.warning') # Check for warning on conversation
@patch('builtins.print')
def test_load_config_missing_conversation_section_uses_defaults(mock_print, mock_log_warn, mock_safe_load, mock_file_open, mock_shutil_copy, mock_load_env, tmp_path):
    mock_safe_load.return_value = {"commands": {}} # No "conversation" section

    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "test", "OLLAMA_ENDPOINT": "http://test"}):
        config = utils_module.load_config()

    assert config is not None
    assert config['conversation']['max_entries'] == 10 # Default
    assert config['conversation']['max_age_hours'] == 24 # Default
    mock_log_warn.assert_any_call("'conversation' section missing or invalid in config.yaml, using defaults.")

@patch('headroom.utils.load_dotenv')
@patch('shutil.copy')
@patch('headroom.utils.Path.exists')
@patch('builtins.open', new_callable=mock_open) # Use standard mock_open
@patch('yaml.safe_load', side_effect=yaml.YAMLError("YAML parsing failed badly")) # Mock safe_load to fail
@patch('builtins.print')
@patch('logging.error') # To check the log message as well
def test_load_config_yaml_error(mock_log_error, mock_print, mock_safe_load_err, mock_file_open, mock_path_exists, mock_shutil_copy, mock_load_env, tmp_path):
    # Simulate config.yaml exists but is malformed causing yaml.safe_load to fail
    mock_path_exists.return_value = True
    mock_config_dir_path = tmp_path / "test_config_dir_yaml_err"
    expected_config_file_path = mock_config_dir_path / "config.yaml"
    mock_file_open.return_value.read.return_value = "bad: yaml: content" # Provide some content for open to read

    with patch('headroom.utils.get_user_config_dir', return_value=mock_config_dir_path):
        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "test", "OLLAMA_ENDPOINT": "http://test"}):
            config = utils_module.load_config()

    assert config is None
    # The error message in load_config's `except yaml.YAMLError as e:` uses the message from the raised error
    mock_print.assert_any_call(f"Error loading configuration from config.yaml: YAML parsing failed badly")
    # Optionally, check that it was logged too, though the print to user is primary for this test type
    # mock_log_error.assert_any_call(f"Error loading configuration from {expected_config_file_path}: YAML parsing failed badly")