import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from headroom import max as max_module
from prompt_toolkit.formatted_text import FormattedText

MOCK_CONFIG = {
    "llm": {"provider": "mock_provider", "model": "mock_model"},
    # Added dummy commands to prevent potential errors if main() expects it
    "commands": {}
}

def test_shell_command_with_special_chars_confirmation(tmp_path):
    """Test that shell commands with special HTML characters are escaped for confirmation."""
    user_input_command = "echo 'hello && world <tag>'"
    expected_full_escaped_cmd = "echo &#x27;hello &amp;&amp; world &lt;tag&gt;&#x27;"

    with patch('headroom.max.load_config', return_value=MOCK_CONFIG), \
         patch('headroom.max.load_user_preferences', return_value={}), \
         patch('headroom.max.execute_command') as mock_exec, \
         patch('headroom.max.PromptSession') as mock_session_class, \
         patch('headroom.max.first_run_setup'), \
         patch('headroom.max.show_logo_ascii'), \
         patch('headroom.max.get_user_config_dir', return_value=tmp_path / ".config" / "headroom"), \
         patch('sys.stdin.isatty', return_value=True), \
         patch('headroom.max.HTML') as MockHTMLClass:

            MockHTMLClass.side_effect = lambda text_input: FormattedText([('', text_input)])

            with patch('headroom.max.print_formatted_text'):
                mock_session_instance = mock_session_class.return_value
                mock_session_instance.prompt.side_effect = [user_input_command, "1", "exit"]

                with pytest.raises(SystemExit): # Expect SystemExit due to "exit" command
                    max_module.main()

                mock_exec.assert_any_call(user_input_command)

                found_matching_call = False
                for call_args in MockHTMLClass.call_args_list:
                    arg_str = call_args[0][0]
                    if ("Proposed action:" in arg_str or "Shell command to execute:" in arg_str) and \
                       expected_full_escaped_cmd in arg_str:
                        found_matching_call = True
                        break

                assert found_matching_call, \
                    f"HTML constructor not called with expected fully escaped command string: '{expected_full_escaped_cmd}'. Actual calls: {[c[0][0] for c in MockHTMLClass.call_args_list]}"

def test_trivial(): # Keep the trivial test to ensure the file is runnable
    assert True
