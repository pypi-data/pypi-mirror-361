import pytest
from unittest.mock import patch, mock_open
from headroom import system_tools

@patch('headroom.system_tools._run_command')

def test_check_command_exists(mock_run_command):
    """Test the command existence check using a mocked command runner."""
    # Case 1: Command exists
    mock_run_command.return_value = {"success": True, "output": "/usr/bin/ls"}
    result = system_tools.check_command_exists("ls")
    assert result["exists"] is True
    assert result["path"] == "/usr/bin/ls"
    mock_run_command.assert_called_once_with("command -v ls")

    # Case 2: Command does not exist
    mock_run_command.return_value = {"success": False, "output": ""}
    result = system_tools.check_command_exists("nonexistentcommand")
    assert result["exists"] is False

@patch('headroom.system_tools.os.listdir')
@patch('headroom.system_tools.os.path.isdir')

def test_list_directory(mock_isdir, mock_listdir):
    """Test directory listing with mocked filesystem calls."""
    mock_listdir.return_value = ["file.txt", "subdir"]
    # os.path.isdir needs to return True for subdir and False for file.txt
    mock_isdir.side_effect = lambda path: "subdir" in path

    result = system_tools.list_directory("/fake/path")

    assert result["success"] is True
    assert "[FILE] file.txt" in result["output"]
    assert "[DIR] subdir" in result["output"]

def test_read_json_file(tmp_path):
    """Test reading a JSON file from a temporary location."""
    json_path = tmp_path / "test.json"
    json_content = '{"key": "value"}'
    json_path.write_text(json_content)

    result = system_tools.read_json_file(str(json_path))
    assert result["success"] is True
    assert result["content"] == {"key": "value"}

    # Test file not found
    result_not_found = system_tools.read_json_file("/non/existent/file.json")
    assert result_not_found["success"] is False
    assert "not found" in result_not_found["output"]