import pytest
from unittest.mock import patch, MagicMock
from headroom import max as max_module

# Mock the config that would be loaded from utils.py
MOCK_CONFIG = {
    "commands": {
        "list_files": {
            "command": "ls -l",
            "description": "List files in long format."
        }
    },
    "conversation": {
        "max_entries": 10,
        "max_age_hours": 24
    },
    "llm": {
        "provider": "mock_provider"
    }
}

def test_main_loop_exit_command(tmp_path):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG),         patch('headroom.max.load_user_preferences', return_value={}),         patch('headroom.max.save_user_preferences'),         patch('headroom.max.execute_command', return_value={"success": True, "output": "Command executed."}),         patch('headroom.max.query_llm'),         patch('headroom.max.PromptSession') as mock_session_class,         patch('headroom.max.first_run_setup'),         patch('headroom.max.show_logo_ascii'),         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"),         patch('sys.stdin.isatty', return_value=False),         patch('sys.stdin.readline') as mock_stdin_readline:

        mock_stdin_readline.side_effect = ["exit\n", "quit\n"]

        # Test 'exit'
        with pytest.raises(SystemExit):
             max_module.main()

        # Test 'quit'
        with pytest.raises(SystemExit):
             max_module.main()

def test_main_loop_shell_command_handling(tmp_path):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG),         patch('headroom.max.load_user_preferences', return_value={}),         patch('headroom.max.execute_command') as mock_exec,         patch('headroom.max.PromptSession') as mock_session_class,         patch('headroom.max.first_run_setup'),         patch('headroom.max.show_logo_ascii'),         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"),         patch('sys.stdin.isatty', return_value=False),         patch('sys.stdin.readline') as mock_stdin_readline:

        mock_stdin_readline.side_effect = ["ls -la\n", "1\n", "exit\n"]

        with pytest.raises(SystemExit):
            max_module.main()

        # Check that execute_command was called with the correct command
        mock_exec.assert_called_with("ls -la")

def test_main_loop_llm_chat_handling(tmp_path):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG),         patch('headroom.max.load_user_preferences', return_value={}),         patch('headroom.max.query_llm') as mock_query,         patch('headroom.max.PromptSession') as mock_session_class,         patch('headroom.max.first_run_setup'),         patch('headroom.max.show_logo_ascii'),         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"),         patch('sys.stdin.isatty', return_value=False),         patch('sys.stdin.readline') as mock_stdin_readline:

        mock_stdin_readline.side_effect = ["what is the capital of France?\n", "exit\n"]
        # Mock the LLM response to be a simple chat intent
        mock_query.return_value = '{"intent": "chat", "response": "Paris"}'

        with pytest.raises(SystemExit):
            max_module.main()

        # Check that query_llm was called with the user's prompt
        mock_query.assert_called_with("what is the capital of France?", MOCK_CONFIG)

    