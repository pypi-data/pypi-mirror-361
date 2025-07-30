from . import system_tools

TOOL_REGISTRY = {
    # System Information Tools
    "create_and_run_python_script": {
        "function": system_tools.create_and_run_python_script,
        "args": ["filename", "code"],
        "arg_schema": {"filename": str, "code": str},
        "confirmation_prompt": "I am proposing to create and run a script named '{filename}'."
    },
    # File/Directory Reading/Writing Tools
    "read_json_file": {
        "function": system_tools.read_json_file,
        "args": ["file_path"],
        "arg_schema": {"file_path": str},
    },
    "write_json_file": {
        "function": system_tools.write_json_file,
        "args": ["file_path", "content"],
        "arg_schema": {"file_path": str, "content": dict}, # Content should be a dict for JSON
        "confirmation_prompt": "Are you sure you want to write to '{file_path}'? This will overwrite existing content."
    },
    "update_json_file": {
        "function": system_tools.update_json_file,
        "args": ["file_path", "key_path", "value"],
        "arg_schema": {"file_path": str, "key_path": str, "value": None}, # Value can be any JSON-serializable type
        "confirmation_prompt": "Are you sure you want to update '{key_path}' in '{file_path}' with '{value}'?"
    },
    "read_yaml_file": {
        "function": system_tools.read_yaml_file,
        "args": ["file_path"],
        "arg_schema": {"file_path": str},
    },
    "write_yaml_file": {
        "function": system_tools.write_yaml_file,
        "args": ["file_path", "content"],
        "arg_schema": {"file_path": str, "content": None}, # Content can be various YAML-valid types
        "confirmation_prompt": "Are you sure you want to write to '{file_path}'? This will overwrite existing content."
    },
    "update_yaml_file": {
        "function": system_tools.update_yaml_file,
        "args": ["file_path", "key_path", "value"],
        "arg_schema": {"file_path": str, "key_path": str, "value": None}, # Value can be various YAML-valid types
        "confirmation_prompt": "Are you sure you want to update '{key_path}' in '{file_path}' with '{value}'?"
    },
    "read_env_file": {
        "function": system_tools.read_env_file,
        "args": ["file_path"],
        "arg_schema": {"file_path": str},
    },
    "update_env_file": {
        "function": system_tools.update_env_file,
        "args": ["file_path", "key", "value"],
        "arg_schema": {"file_path": str, "key": str, "value": str},
        "confirmation_prompt": "Are you sure you want to update '{key}' in '{file_path}' with '{value}'?"
    },
    "read_text_file": {
        "function": system_tools.read_text_file,
        "args": ["file_path"],
        "arg_schema": {"file_path": str},
        "confirmation_prompt": "Read content from file '{file_path}'?"
    },
    "write_text_file": {
        "function": system_tools.write_text_file,
        "args": ["file_path", "content"],
        "optional_args": ["overwrite"],
        "arg_schema": {"file_path": str, "content": str, "overwrite": bool},
        "confirmation_prompt": "Write content to file '{file_path}'? (Overwrite: {overwrite})"
    },
    "read_multiple_text_files": {
        "function": system_tools.read_multiple_text_files,
        "args": ["file_paths"],
        "arg_schema": {"file_paths": list}, # Specifically list[str] would be ideal if supported by coercion
        "confirmation_prompt": "Read content from multiple files: {file_paths}?"
    },
    "delete_file": {
        "function": system_tools.delete_file,
        "args": ["path"],
        "arg_schema": {"path": str},
        "confirmation_prompt": "Are you sure you want to delete the file '{path}'?"
    },
    "copy_file": {
        "function": system_tools.copy_file,
        "args": ["src", "dst"],
        "optional_args": ["recursive"],
        "arg_schema": {"src": str, "dst": str, "recursive": bool},
        "confirmation_prompt": "Copy '{src}' to '{dst}'? (recursive: {recursive})"
    },
    "move_file": {
        "function": system_tools.move_file,
        "args": ["src", "dst"],
        "arg_schema": {"src": str, "dst": str},
        "confirmation_prompt": "Move '{src}' to '{dst}'?"
    },
    "make_directory": {
        "function": system_tools.make_directory,
        "args": ["path"],
        "optional_args": ["exist_ok"],
        "arg_schema": {"path": str, "exist_ok": bool},
        "confirmation_prompt": "Create directory '{path}'? (exist_ok: {exist_ok})"
    },
    "remove_directory": {
        "function": system_tools.remove_directory,
        "args": ["path"],
        "optional_args": ["recursive"],
        "arg_schema": {"path": str, "recursive": bool},
        "confirmation_prompt": "Remove directory '{path}'? (recursive: {recursive})"
    },
    "change_permissions": {
        "function": system_tools.change_permissions,
        "args": ["path", "mode"],
        "arg_schema": {"path": str, "mode": str}, # Mode is string like "755"
        "confirmation_prompt": "Change permissions for '{path}' to '{mode}'?"
    },
    "change_owner": {
        "function": system_tools.change_owner,
        "args": ["path", "owner"],
        "arg_schema": {"path": str, "owner": str},
        "confirmation_prompt": "Change owner for '{path}' to '{owner}'?"
    },
    # Package Management Tools
    "install_package": {
        "function": system_tools.install_package,
        "args": ["package_name"],
        "optional_args": ["package_manager"],
        "arg_schema": {"package_name": str, "package_manager": str},
        "confirmation_prompt": "Install package '{package_name}'?"
    },
    "list_packages": {
        "function": system_tools.list_packages,
        "args": [],
        "optional_args": ["package_manager"],
        "arg_schema": {"package_manager": str}, # Optional, but if present, it's a string
        "confirmation_prompt": "List installed packages?"
    },
    "remove_package": {
        "function": system_tools.remove_package,
        "args": ["package_name"],
        "optional_args": ["package_manager"],
        "arg_schema": {"package_name": str, "package_manager": str},
        "confirmation_prompt": "Remove package '{package_name}'?"
    },
    "search_package": {
        "function": system_tools.search_package,
        "args": ["package_name"],
        "optional_args": ["package_manager"],
        "arg_schema": {"package_name": str, "package_manager": str},
        "confirmation_prompt": "Search for package '{package_name}'?"
    },
    # Service Management Tools
    "check_service_status": {
        "function": system_tools.check_service_status,
        "args": ["service_name"],
        "arg_schema": {"service_name": str},
    },
    "manage_service": {
        "function": system_tools.manage_service,
        "args": ["service_name", "action"],
        # Action could be an Enum: "start", "stop", "restart", "enable", "disable"
        "arg_schema": {"service_name": str, "action": str},
        "confirmation_prompt": "Are you sure you want to {action} service '{service_name}'?"
    },
    # File/Directory Operations Tools (excluding read/write)
    "list_directory": {
        "function": system_tools.list_directory,
        "args": ["path"],
        "arg_schema": {"path": str},
    },
    "search_file_content": {
        "function": system_tools.search_file_content,
        "args": ["pattern"],
        "optional_args": ["path", "include"],
        "arg_schema": {"pattern": str, "path": str, "include": str},
    },
    "glob_files": {
        "function": system_tools.glob_files,
        "args": ["pattern"],
        "optional_args": ["path"],
        "arg_schema": {"pattern": str, "path": str},
    },
    "replace_in_file": {
        "function": system_tools.replace_in_file,
        "args": ["file_path", "old_string", "new_string"],
        # expected_replacements could be added as optional int
        "arg_schema": {"file_path": str, "old_string": str, "new_string": str},
        "confirmation_prompt": "Are you sure you want to replace content in '{file_path}'?"
    },
    # Web Tools
    "web_search": {
        "function": system_tools.web_search,
        "args": ["query"],
        "arg_schema": {"query": str},
        "confirmation_prompt": "I am proposing to perform a web search for '{query}'."
    },
    "web_fetch": {
        "function": system_tools.web_fetch,
        "args": ["url"],
        "arg_schema": {"url": str},
        "confirmation_prompt": "I am proposing to fetch content from '{url}'."
    },
    # Command & Version Tools
    "check_command_exists": {
        "function": system_tools.check_command_exists,
        "args": ["command_name"],
        "arg_schema": {"command_name": str},
    },
}