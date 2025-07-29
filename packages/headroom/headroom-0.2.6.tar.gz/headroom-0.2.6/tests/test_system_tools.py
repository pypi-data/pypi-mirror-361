import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

# Tests for new text file tools

def test_read_text_file_success(tmp_path):
    """Test successfully reading a text file."""
    file_path = tmp_path / "test.txt"
    expected_content = "Hello, World!\nThis is a test file."
    file_path.write_text(expected_content, encoding="utf-8")

    result = system_tools.read_text_file(str(file_path))
    assert result["success"] is True
    assert result["content"] == expected_content

def test_read_text_file_not_found(tmp_path):
    """Test reading a non-existent text file."""
    file_path = tmp_path / "non_existent.txt"
    result = system_tools.read_text_file(str(file_path))
    assert result["success"] is False
    assert "File not found" in result["error"]

def test_read_text_file_unicode_error(tmp_path):
    """Test reading a file with undecodable content (e.g., a binary file)."""
    file_path = tmp_path / "binary.dat"
    # Write some non-UTF-8 bytes (e.g., from latin-1 that are invalid in UTF-8)
    file_path.write_bytes(b'\x81\x00\x00\x00') # \x81 is invalid start byte in UTF-8

    result = system_tools.read_text_file(str(file_path))
    assert result["success"] is False
    assert "Cannot decode file" in result["error"]

def test_write_text_file_create_new(tmp_path):
    """Test writing content to a new text file."""
    file_path = tmp_path / "new_file.txt"
    content_to_write = "This is a new file."

    result = system_tools.write_text_file(str(file_path), content_to_write)
    assert result["success"] is True
    assert "Successfully wrote content" in result["output"]
    assert file_path.read_text(encoding="utf-8") == content_to_write

def test_write_text_file_overwrite_existing(tmp_path):
    """Test overwriting an existing text file."""
    file_path = tmp_path / "existing_file.txt"
    initial_content = "Initial content."
    file_path.write_text(initial_content, encoding="utf-8")

    new_content = "This content overwrites the old one."
    result = system_tools.write_text_file(str(file_path), new_content, overwrite=True)
    assert result["success"] is True
    assert file_path.read_text(encoding="utf-8") == new_content

def test_write_text_file_no_overwrite_fail(tmp_path):
    """Test that writing fails if file exists and overwrite is False."""
    file_path = tmp_path / "no_overwrite.txt"
    initial_content = "Do not overwrite."
    file_path.write_text(initial_content, encoding="utf-8")

    new_content = "Attempting to write."
    result = system_tools.write_text_file(str(file_path), new_content, overwrite=False)
    assert result["success"] is False
    assert "already exists" in result["error"]
    assert file_path.read_text(encoding="utf-8") == initial_content # Ensure not overwritten

def test_write_text_file_creates_parent_dirs(tmp_path):
    """Test that write_text_file creates parent directories if they don't exist."""
    dir_path = tmp_path / "parent" / "child"
    file_path = dir_path / "nested_file.txt"
    content = "Content in nested file."

    assert not dir_path.exists() # Ensure parent dirs don't exist initially
    result = system_tools.write_text_file(str(file_path), content)
    assert result["success"] is True
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content
    assert dir_path.exists() # Check that parent dirs were created

def test_read_multiple_text_files_success(tmp_path):
    """Test reading multiple existing text files."""
    file1_path = tmp_path / "file1.txt"
    file1_content = "Content of file 1"
    file1_path.write_text(file1_content, encoding="utf-8")

    file2_path = tmp_path / "file2.txt"
    file2_content = "Content of file 2"
    file2_path.write_text(file2_content, encoding="utf-8")

    paths_to_read = [str(file1_path), str(file2_path)]
    result = system_tools.read_multiple_text_files(paths_to_read)

    assert result["success"] is True
    assert len(result["files"]) == 2
    assert result["files"][0]["file_path"] == str(file1_path)
    assert result["files"][0]["status"] == "success"
    assert result["files"][0]["content"] == file1_content
    assert result["files"][1]["file_path"] == str(file2_path)
    assert result["files"][1]["status"] == "success"
    assert result["files"][1]["content"] == file2_content

def test_read_multiple_text_files_one_missing(tmp_path):
    """Test reading multiple files where one is missing."""
    file1_path = tmp_path / "file_exists.txt"
    file1_content = "This file exists."
    file1_path.write_text(file1_content, encoding="utf-8")

    missing_file_path = tmp_path / "missing.txt"

    paths_to_read = [str(file1_path), str(missing_file_path)]
    result = system_tools.read_multiple_text_files(paths_to_read)

    assert result["success"] is False # Overall success should be false
    assert len(result["files"]) == 2
    assert result["files"][0]["file_path"] == str(file1_path)
    assert result["files"][0]["status"] == "success"
    assert result["files"][0]["content"] == file1_content
    assert result["files"][1]["file_path"] == str(missing_file_path)
    assert result["files"][1]["status"] == "error"
    assert "File not found" in result["files"][1]["error"]

def test_read_multiple_text_files_empty_list(tmp_path):
    """Test reading an empty list of files."""
    result = system_tools.read_multiple_text_files([])
    assert result["success"] is True # Technically no failures
    assert len(result["files"]) == 0

def test_read_multiple_text_files_all_missing(tmp_path):
    """Test reading multiple files where all are missing."""
    paths_to_read = [str(tmp_path / "m1.txt"), str(tmp_path / "m2.txt")]
    result = system_tools.read_multiple_text_files(paths_to_read)
    assert result["success"] is False
    assert len(result["files"]) == 2
    assert result["files"][0]["status"] == "error"
    assert result["files"][1]["status"] == "error"