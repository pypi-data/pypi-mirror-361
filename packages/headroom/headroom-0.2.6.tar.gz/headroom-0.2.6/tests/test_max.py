import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path # Import Path
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
        "provider": "mock_provider",
        "model": "mock_model"  # Added missing model key
    }
}

def test_main_loop_exit_command(tmp_path):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG),         patch('headroom.max.load_user_preferences', return_value={}),         patch('headroom.max.save_user_preferences'),         patch('headroom.max.execute_command', return_value={"success": True, "output": "Command executed."}),         patch('headroom.max.query_llm'),         patch('headroom.max.PromptSession') as mock_session_class,         patch('headroom.max.first_run_setup'),         patch('headroom.max.show_logo_ascii'),         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"),         patch('sys.stdin.isatty', return_value=False),         patch('sys.stdin.readline') as mock_stdin_readline,         patch('prompt_toolkit.shortcuts.print_formatted_text'):

        mock_stdin_readline.side_effect = ["exit\n", "quit\n"]

        # Test 'exit'
        with pytest.raises(SystemExit):
             max_module.main()

        # Test 'quit'
        with pytest.raises(SystemExit):
             max_module.main()

def test_main_loop_shell_command_handling(tmp_path):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG),         patch('headroom.max.load_user_preferences', return_value={}),         patch('headroom.max.execute_command') as mock_exec,         patch('headroom.max.query_llm') as mock_query_llm,  \
         patch('headroom.max.PromptSession') as mock_session_class,         patch('headroom.max.first_run_setup'),         patch('headroom.max.show_logo_ascii'),         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"),         patch('sys.stdin.isatty', return_value=False),         patch('sys.stdin.readline') as mock_stdin_readline,         patch('prompt_toolkit.shortcuts.print_formatted_text'):

        mock_stdin_readline.side_effect = ["ls -la\n", "1\n", "exit\n"]
        mock_query_llm.return_value = '{"intent": "chat", "response": "Mocked LLM response after shell"}'

        with pytest.raises(SystemExit):
            max_module.main()

        # Check that execute_command was called with the correct command
        mock_exec.assert_called_with("ls -la")

def test_main_loop_llm_chat_handling(tmp_path):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG),         patch('headroom.max.load_user_preferences', return_value={}),         patch('headroom.max.query_llm') as mock_query,         patch('headroom.max.PromptSession') as mock_session_class,         patch('headroom.max.first_run_setup'),         patch('headroom.max.show_logo_ascii'),         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"),         patch('sys.stdin.isatty', return_value=False),         patch('sys.stdin.readline') as mock_stdin_readline,         patch('prompt_toolkit.shortcuts.print_formatted_text'):

        mock_stdin_readline.side_effect = ["what is the capital of France?\n", "exit\n"]
        # Mock the LLM response to be a simple chat intent
        mock_query.return_value = '{"intent": "chat", "response": "Paris"}'

        with pytest.raises(SystemExit):
            max_module.main()

        # Check that query_llm was called with the user's prompt
        mock_query.assert_called_with("what is the capital of France?", MOCK_CONFIG)


def test_startup_message(capsys):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('headroom.max.first_run_setup') as mock_first_run_setup, \
         patch('headroom.max.show_logo_ascii'), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.PromptSession.prompt', side_effect=["exit"]), \
         patch('pathlib.Path.exists', return_value=True) as mock_path_exists, \
         patch('headroom.max.print_formatted_text') as mock_print_formatted_text:

        # Ensure Path.exists is specific to the .env file check if needed,
        # though for this test, a general True should be fine if first_run_setup is fully mocked.
        # If get_user_config_dir() is called by main, mock_path_exists might need to be more specific
        # or ensure get_user_config_dir returns a consistent path that can be checked.

        with pytest.raises(SystemExit):
            max_module.main()

        # Check that the startup message is printed via the mocked print_formatted_text
        found_startup_message = False
        for call_args in mock_print_formatted_text.call_args_list:
            args, _ = call_args
            if args and isinstance(args[0], max_module.HTML) and "Type 'help' for a list of commands. New commands include: 'log', 'config', 'tools'." in args[0].value:
                found_startup_message = True
                break
        assert found_startup_message, "Startup message not found in print_formatted_text calls"
        mock_first_run_setup.assert_not_called() # Ensure first_run_setup isn't called due to .env existing

def test_log_command_displays_log_content(tmp_path, capsys):
    # Create a dummy log file
    dummy_log_content = "This is a test log entry."
    log_file_path = tmp_path / "max_agent.log"
    with open(log_file_path, "w") as f:
        f.write(dummy_log_content)

    with patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('headroom.max.get_user_data_dir', return_value=tmp_path), \
         patch('headroom.max.LOG_FILE', log_file_path), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.PromptSession.prompt', side_effect=["log", "exit"]), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('headroom.max.first_run_setup'): # Ensure first_run_setup is mocked

        with patch('headroom.max.print_formatted_text') as mock_pft:
            with pytest.raises(SystemExit):
                max_module.main()

            found_log_message = False
            for call_args in mock_pft.call_args_list:
                args, _ = call_args
                if args and isinstance(args[0], str) and dummy_log_content in args[0]: # Log content is printed as str
                    found_log_message = True
                    break
            assert found_log_message, f"Log content '{dummy_log_content}' not found in print_formatted_text calls"

def test_log_command_file_not_found(tmp_path, capsys):
    # Ensure no log file exists
    log_file_path = tmp_path / "max_agent.log"
    if log_file_path.exists():
        os.remove(log_file_path)

    mock_log_file = MagicMock(spec=Path)
    mock_log_file.exists.return_value = False
    # We also need to make sure it can be opened, or that open is not called if exists is False.
    # display_log_file checks .exists() first, so this should be fine.

    with patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('headroom.max.get_user_data_dir', return_value=tmp_path), \
         patch('headroom.max.LOG_FILE', mock_log_file), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.PromptSession.prompt', side_effect=["log", "exit"]), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('headroom.max.first_run_setup'), \
         patch('headroom.max.print_formatted_text') as mock_pft:

        with pytest.raises(SystemExit):
            max_module.main()

        found_message = False
        for call_args in mock_pft.call_args_list:
            args, _ = call_args
            if args and isinstance(args[0], max_module.HTML) and "Log file not found." in args[0].value:
                found_message = True
                break
        assert found_message, "'Log file not found.' message not found in print_formatted_text calls"


def test_config_command_calls_first_run_setup(tmp_path):
    # This mock will be for the call made by the 'config' command via reconfigure_llm
    with patch('headroom.max.first_run_setup') as mock_reconfig_first_run_setup, \
         patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.PromptSession.prompt', side_effect=["config", "exit"]), \
         patch.object(Path, 'exists', return_value=True) as mock_path_exists_main:

        # mock_path_exists_main will ensure that env_file.exists() in main returns True,
        # preventing the initial call to first_run_setup.

        # We also need to ensure that if max.py's main() itself calls first_run_setup
        # due to the .env check, that call is distinct or handled.
        # The patch('pathlib.Path.exists', return_value=True) should prevent the *initial* call.

        with pytest.raises(SystemExit):
            max_module.main()

        # We expect first_run_setup to be called once by the 'config' command's logic
        mock_reconfig_first_run_setup.assert_called_once_with(is_reconfiguration=True)


MOCK_TOOL_REGISTRY = {
    "tool_one": {
        "function": lambda: None,
        "confirmation_prompt": "Description for tool one {arg1}."
    },
    "tool_two": {
        "function": lambda: None,
        "confirmation_prompt": "Description for tool two."
    }
}

def test_tools_command_displays_tools(capsys):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('headroom.max.TOOL_REGISTRY', MOCK_TOOL_REGISTRY), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.PromptSession.prompt', side_effect=["tools", "exit"]), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('headroom.max.first_run_setup'): # Ensure first_run_setup is mocked

        with patch('headroom.max.print_formatted_text') as mock_pft:
            with pytest.raises(SystemExit):
                max_module.main()

            call_texts = " ".join([call_args[0][0].value if isinstance(call_args[0][0], max_module.HTML) else str(call_args[0][0]) for call_args in mock_pft.call_args_list if call_args[0]])
            assert "Available Tools:" in call_texts
            assert "tool_one:" in call_texts
            assert "Description for tool one ..." in call_texts
            assert "tool_two:" in call_texts
            assert "Description for tool two." in call_texts

def test_help_command_includes_new_commands(capsys):
    with patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.PromptSession.prompt', side_effect=["help", "exit"]), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('headroom.max.first_run_setup'): # Ensure first_run_setup is mocked

        with pytest.raises(SystemExit):
            max_module.main()

        captured = capsys.readouterr()
        assert "Max Agent Help:" in captured.out
        assert "log                           - Displays Max's log file." in captured.out
        assert "config                        - Allows reconfiguration of the LLM provider and settings." in captured.out
        assert "tools                         - Lists available tools and their descriptions." in captured.out