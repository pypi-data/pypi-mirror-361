import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import inspect
from headroom.tool_registry import TOOL_REGISTRY
from headroom import system_tools

def test_tool_registry_structure_and_validity():
    """Validates the structure and content of the TOOL_REGISTRY. Ensures that all registered tools are correctly configured."""
    assert isinstance(TOOL_REGISTRY, dict)
    assert len(TOOL_REGISTRY) > 0

    for tool_name, tool_info in TOOL_REGISTRY.items():
        # 1. Check for required keys
        assert "function" in tool_info, f"Tool '{tool_name}' is missing 'function' key."

        # 2. Check that the function is a real, callable function from system_tools
        func = tool_info["function"]
        assert callable(func), f"Function for tool '{tool_name}' is not callable."
        assert hasattr(system_tools, func.__name__), f"Function '{func.__name__}' for tool '{tool_name}' not found in system_tools."

        # 3. Check that args and optional_args are lists if they exist
        if "args" in tool_info:
            assert isinstance(tool_info["args"], list), f"'args' for tool '{tool_name}' must be a list."

        if "optional_args" in tool_info:
            assert isinstance(tool_info["optional_args"], list), f"'optional_args' for tool '{tool_name}' must be a list."

        # 4. Check that the function signature matches the registered arguments
        func_spec = inspect.getfullargspec(func)

        required_args_from_spec = func_spec.args

        # Remove args with default values, as they are optional
        if func_spec.defaults:
            optional_args_count = len(func_spec.defaults)
            required_args_from_spec = func_spec.args[:-optional_args_count]

        registered_required = set(tool_info.get("args", []))

        assert set(required_args_from_spec) == registered_required, \
            f"Mismatched required args for tool '{tool_name}'. Spec: {required_args_from_spec}, Registry: {registered_required}"