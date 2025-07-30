# Main Max> Config
# Install Dependencies - pip3 install prompt_toolkit pyyaml requests dotenv

import json
import sys
import traceback
import logging
import os
import shlex
import shutil # Import shutil
import html # Import the html module
from typing import Any
from prompt_toolkit import PromptSession, print_formatted_text, HTML
# from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from headroom.utils import load_config, query_llm, interpret_user_intent, get_user_data_dir, get_user_config_dir
from headroom.max_display import print_agent_response
from headroom.tools import execute_command
from headroom.user_preferences import load_user_preferences, save_user_preferences
from headroom.tool_registry import TOOL_REGISTRY
from headroom.first_run import first_run_setup

# --- Constants for magic strings ---
ALLOW_ONCE = "allow_once"
ALLOW_ALWAYS = "allow_always"
CANCEL = "cancel"
NEVER_ALLOWED_KEY = "never_allowed_commands"
ALWAYS_ALLOWED_KEY = "always_allowed_commands"

# Initialize logging
DATA_DIR = get_user_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = DATA_DIR / "max_agent.log"
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,  # Change to logging.DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(message)s"
)


SHELL_COMMANDS = {"ls", "cat", "rm", "touch", "cp", "mv", "grep", "find", "chmod", "chown", "echo", "pwd", "head", "tail", "du", "df", "ps", "kill", "mkdir", "rmdir", "tar", "zip", "unzip", "ping", "whoami", "uptime", "df", "free", "top", "less", "more"}

def is_shell_command(user_input):
    """Detect if the input is a direct shell command."""
    if not user_input.strip():
        return False

    try:
        # Use shlex to correctly split the command, especially with quoted arguments
        parts = shlex.split(user_input.strip())
        if not parts:
            return False
        first_word = parts[0]
    except ValueError:
        # shlex.split can raise ValueError for unmatched quotes, etc.
        # In such a case, it's unlikely to be a simple shell command we want to auto-detect.
        return False

    # Prioritize the explicit list of common shell commands
    if first_word in SHELL_COMMANDS:
        return True

    # If not in the explicit list, check if it's an executable in PATH
    # This helps detect other valid commands without needing them all in SHELL_COMMANDS
    if shutil.which(first_word):
        return True

    return False

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

def get_and_handle_confirmation(
    session: PromptSession | None,
    proposed_action: str,
    action_name_for_approval: str,
    user_preferences: dict,
    always_allow_manager,
    action_to_execute: str | None = None, # For shell commands
    tool_info: dict | None = None, # For tool use
    tool_arguments: dict | None = None # For tool use
) -> str:
    """
    Gets user confirmation for a proposed action and handles the response.

    Args:
        session: The prompt_toolkit session.
        proposed_action: A string describing the action being proposed to the user.
        action_name_for_approval: The name used for the 'always allow' list.
        user_preferences: The user preferences dictionary.
        always_allow_manager: The AlwaysAllowManager instance.
        action_to_execute: The shell command string to execute (if applicable).
        tool_info: The tool information dictionary (if applicable).
        tool_arguments: The arguments for the tool (if applicable).

    Returns:
        The confirmation choice ("allow_once", "allow_always", or "cancel").
    """
    # If not in a TTY (e.g., piped input, some test environments), default to allow once.
    # This also handles the case where a confirmation prompt cannot be shown.
    if not sys.stdin.isatty():
        logging.info("Non-interactive mode detected for confirmation. Automatically allowing action once.")
        return ALLOW_ONCE

    # Escape all dynamic string parts that will be embedded in HTML
    escaped_proposed_action = html.escape(proposed_action, quote=True)
    print_formatted_text(HTML(f'<ansigreen>\nProposed action: {escaped_proposed_action}</ansigreen>'))

    escaped_action_name_for_approval = html.escape(action_name_for_approval, quote=True)

    # Show extra info if available
    if tool_info:
        print_formatted_text(HTML(f"<ansicyan>Tool: {escaped_action_name_for_approval}</ansicyan>"))
        if "args" in tool_info:
            print_formatted_text(HTML(f"<ansicyan>Required args: {html.escape(str(tool_info['args']), quote=True)}</ansicyan>"))
        if "optional_args" in tool_info:
            print_formatted_text(HTML(f"<ansicyan>Optional args: {html.escape(str(tool_info['optional_args']), quote=True)}</ansicyan>"))
        if "confirmation_prompt" in tool_info: # This is the description from TOOL_REGISTRY
            # The confirmation_prompt is often a format string.
            # The arguments inserted into it via .format() in handle_tool_use should also be escaped there if from user.
            # Here, we escape the template itself if it were to contain special chars, though unlikely for fixed templates.
            print_formatted_text(HTML(f"<ansicyan>Description: {html.escape(tool_info['confirmation_prompt'], quote=True)}</ansicyan>"))
    if tool_arguments:
        print_formatted_text(HTML(f"<ansicyan>Arguments: {html.escape(str(tool_arguments), quote=True)}</ansicyan>"))
    if action_to_execute:
        escaped_action_to_execute = html.escape(action_to_execute, quote=True)
        print_formatted_text(HTML(f"<ansiyellow>Shell command to execute: {escaped_action_to_execute}</ansiyellow>"))

    # This check is now redundant due to the one at the beginning of the function.
    # if not sys.stdin.isatty():
    #     logging.info("Non-interactive mode detected. Automatically allowing action.")
    #     return ALLOW_ONCE

    if action_name_for_approval in user_preferences.get(ALWAYS_ALLOWED_KEY, []):
        logging.info(f"Action category '{action_name_for_approval}' is always allowed. Executing automatically.")
        return ALLOW_ONCE

    confirm_session = PromptSession(HTML('<ansigreen>Enter choice (1/2/3): </ansigreen>'))

    while True:
        print_formatted_text(HTML('<ansigreen>Allow execution?</ansigreen>'))
        print_formatted_text(HTML(
            f'<ansiyellow>  1. Yes, allow once\n'
            f'  2. Yes, always allow \'{escaped_action_name_for_approval}...\'\n' # Also escape here
            '  3. Cancel execution</ansiyellow>'
        ))
        choice = confirm_session.prompt().strip()
        if choice == '1':
            return ALLOW_ONCE
        elif choice == '2':
            return ALLOW_ALWAYS
        elif choice == '3':
            return CANCEL
        else:
            print_formatted_text(HTML('<ansired>Invalid choice. Please enter 1, 2, or 3.</ansired>'))

def revoke_always_allowed_commands(
    session: PromptSession, 
    user_preferences: dict
) -> None:
    """
    Allows the user to revoke commands previously set to 'always allow'.
    """
    always_allowed = user_preferences.get(ALWAYS_ALLOWED_KEY, [])
    if not always_allowed:
        print("No commands are currently set to 'always allow'.")
        return

    print("\nCurrently 'always allowed' commands:")
    for i, cmd in enumerate(always_allowed):
        print(f"  {i+1}. {cmd}")

    while True:
        choice = session.prompt("Enter the number of the command to revoke, or 'q' to quit:").strip()
        if choice.lower() == 'q':
            print("Revocation cancelled.")
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(always_allowed):
                revoked_cmd = always_allowed.pop(index)
                user_preferences[ALWAYS_ALLOWED_KEY] = always_allowed
                save_user_preferences(user_preferences)
                print(f"Successfully revoked 'always allow' for: '{revoked_cmd}'")
                return
            else:
                print("Invalid number. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")

def print_help(config: dict) -> None:
    """Prints a formatted list of available commands and their descriptions."""
    print("\nMax Agent Help:")
    print("-----------------")
    print("Built-in commands:")
    print("  help                          - Shows this help message.")
    print("  log                           - Displays Max's log file.")
    print("  config                        - Allows reconfiguration of the LLM provider and settings.")
    print("  tools                         - Lists available tools and their descriptions.")
    print("  revoke                        - Manages commands that are 'always allowed'.")
    print("  exit/quit                     - Exits the application.")

    commands = config.get("commands", {})
    if commands:
        print("\nLLM-activated commands (ask in natural language):")
        max_len = max(len(name) for name in commands.keys()) if commands else 0
        for name in sorted(commands.keys()):
            details = commands[name]
            description = details.get("description", "No description available.")
            print(f"  {name:<{max_len}}  - {description}")
    print("\nYou can also ask general questions for a direct answer from the LLM.")

def display_log_file():
    """Reads and prints the content of the Max log file."""
    if not LOG_FILE.exists():
        print_formatted_text(HTML("<ansired>Log file not found.</ansired>"))
        return
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_content = f.read()
        # Use print_formatted_text to allow for potential HTML/ANSI escape sequences if any were logged,
        # though typically logs are plain text.
        print_formatted_text(log_content if log_content else "Log file is empty.")
    except Exception as e:
        print_formatted_text(HTML(f"<ansired>Error reading log file: {e}</ansired>"))

def reconfigure_llm():
    """Allows the user to re-run the LLM configuration process."""
    print_formatted_text(HTML("<ansiyellow>Starting LLM reconfiguration...</ansiyellow>"))
    first_run_setup(is_reconfiguration=True)
    print_formatted_text(HTML("<ansigreen>LLM reconfiguration complete.</ansigreen>"))

def display_tools():
    """Displays available tools and their descriptions."""
    print_formatted_text(HTML("\n<ansicyan>Available Tools:</ansicyan>"))
    print_formatted_text(HTML("-----------------"))
    if not TOOL_REGISTRY:
        print_formatted_text(HTML("<ansiyellow>No tools are currently registered.</ansiyellow>"))
        return

    for tool_name, tool_info in TOOL_REGISTRY.items():
        description = tool_info.get("confirmation_prompt", "No description available.")
        # Attempt to remove argument placeholders like '{filename}' for a cleaner description
        import re
        cleaned_description = re.sub(r"\{[^}]+\}", "...", description)
        print_formatted_text(HTML(f"<ansigreen>  {tool_name}:</ansigreen> <ansiyellow>{cleaned_description}</ansiyellow>"))
    print_formatted_text(HTML("-----------------"))


def _coerce_and_validate_arg(value, expected_type, arg_name: str) -> tuple[Any, str | None]:
    """
    Coerces a value to the expected type and validates it.
    Returns (coerced_value, None) on success, or (original_value, error_message_string) on failure.
    """
    if expected_type == bool:
        if isinstance(value, bool):
            return value, None
        if isinstance(value, str):
            if value.lower() == "true":
                return True, None
            if value.lower() == "false":
                return False, None
        return value, f"Argument '{arg_name}' expected a boolean (true/false), got '{value}' (type: {type(value).__name__})."

    if expected_type == int:
        if isinstance(value, int):
            return value, None
        try:
            return int(value), None
        except (ValueError, TypeError):
            return value, f"Argument '{arg_name}' expected an integer, got '{value}' (type: {type(value).__name__})."

    if expected_type == str:
        if isinstance(value, str):
            return value, None
        # Allow simple coercion from int/float to str if LLM provides them as numbers
        if isinstance(value, (int, float)):
            return str(value), None
        return value, f"Argument '{arg_name}' expected a string, got '{value}' (type: {type(value).__name__})."

    if expected_type == list: # Basic list check, doesn't check item types yet
        if isinstance(value, list):
            return value, None
        # LLM might send a single string for a list of one item.
        # For now, require it to be an actual list. More complex coercion (e.g. comma-sep string) is harder.
        return value, f"Argument '{arg_name}' expected a list, got '{value}' (type: {type(value).__name__})."

    if expected_type == dict: # Basic dict check
        if isinstance(value, dict):
            return value, None
        return value, f"Argument '{arg_name}' expected a dictionary/object, got '{value}' (type: {type(value).__name__})."

    if expected_type is None: # Used for 'any' type in schema (e.g. for 'value' in update_json)
        return value, None

    # If type is not directly matched and no coercion rule, check instance
    if isinstance(value, expected_type):
        return value, None

    return value, f"Argument '{arg_name}' type mismatch. Expected {expected_type.__name__}, got {type(value).__name__} for value '{value}'."


 
def handle_tool_use(session: PromptSession | None, llm_response, user_preferences, always_allow_manager):
    tool_name = llm_response.get("tool_name")
    args = llm_response.get("arguments", {})

    if tool_name not in TOOL_REGISTRY:
        logging.warning(f"LLM proposed an unknown tool: '{tool_name}'. Data: {llm_response}")
        print_agent_response(f"I don't know how to use a tool called '{tool_name}'.")
        return

    tool_info = TOOL_REGISTRY[tool_name]
    tool_function = tool_info["function"]
    required_arg_names = tool_info.get("args", [])
    optional_arg_names = tool_info.get("optional_args", [])
    arg_schema = tool_info.get("arg_schema", {}) # Get the new schema
    confirmation_prompt_template = tool_info.get("confirmation_prompt")

    current_args = args.copy() # Work on a copy
    validation_errors = []

    # 1. Check for missing required arguments
    for arg_name in required_arg_names:
        if arg_name not in current_args:
            validation_errors.append(f"Missing required argument '{arg_name}'")

    if validation_errors:
        err_msg = (f"Error: Missing required arguments for tool '{tool_name}': {', '.join(validation_errors)}. "
                   f"Provided: {list(current_args.keys())}. Required: {required_arg_names}.")
        logging.warning(f"Tool '{tool_name}' missing arguments. {err_msg} LLM Data: {llm_response}")
        print_agent_response(err_msg)
        return

    # 2. Type checking, coercion, and default for optional booleans
    final_args = {}
    all_defined_args = set(required_arg_names + optional_arg_names)

    for arg_name in all_defined_args:
        expected_type = arg_schema.get(arg_name)

        if arg_name in current_args:
            value = current_args[arg_name]
            if expected_type:
                coerced_value, error = _coerce_and_validate_arg(value, expected_type, arg_name)
                if error:
                    validation_errors.append(error)
                else:
                    final_args[arg_name] = coerced_value
            else: # No type in schema, pass as is
                final_args[arg_name] = value
        elif arg_name in optional_arg_names:
            # Handle defaults for optionals not provided by LLM
            if expected_type == bool:
                final_args[arg_name] = False # Default optional booleans to False
            # Add other specific default logic here if needed, or rely on tool function defaults

    if validation_errors:
        err_msg = f"Error: Argument validation failed for tool '{tool_name}': {'; '.join(validation_errors)}"
        logging.warning(f"Tool '{tool_name}' argument validation failed. {err_msg} LLM Data: {llm_response}")
        print_agent_response(err_msg)
        return

    # 3. Warn about unexpected arguments (those in `args` but not in schema or defined args)
    unexpected_args = [arg for arg in current_args if arg not in all_defined_args]
    if unexpected_args:
        warn_msg = (f"Warning: Unexpected arguments for tool '{tool_name}': {', '.join(unexpected_args)}. "
                    f"Defined args: {list(all_defined_args)}.")
        logging.info(f"Tool '{tool_name}' received unexpected arguments. {warn_msg} LLM Data: {llm_response}")

    # Get and handle confirmation using the new function
    if confirmation_prompt_template:
        # Use final_args for formatting confirmation, as it contains coerced values and defaults
        proposed_action = confirmation_prompt_template.format(**final_args)
        confirmation_choice = get_and_handle_confirmation(
            session,
            proposed_action,
            tool_name,
            user_preferences,
            always_allow_manager,
            tool_info=tool_info,
            tool_arguments=args
        )

        if confirmation_choice == CANCEL:
            print_agent_response("Tool use cancelled.")
            return
        elif confirmation_choice == ALLOW_ALWAYS:
            always_allow_manager.add(tool_name)
            print(f"Tool '{tool_name}' added to always allowed list.")

    # Execute tool with error handling
    try:
        result = tool_function(**final_args) # Use final_args which has coerced values
    except Exception as e:
        logging.error(f"Error executing tool '{tool_name}' with args {final_args}. Exception: {e}", exc_info=True)
        print_agent_response(f"An error occurred while trying to use the tool '{tool_name}': {e}")
        return

    # Print result
    if result and result.get("output"):
        print_agent_response(f"Tool '{tool_name}' executed successfully. Output:\n{result['output']}")
    elif result and result.get("content"):
        print_agent_response(f"Tool '{tool_name}' executed successfully. Content:\n{result['content']}")
    elif result and result.get("success"):
        print_agent_response(f"Tool '{tool_name}' executed successfully.")

class AlwaysAllowManager:
    def __init__(self, user_preferences: dict):
        self.user_preferences = user_preferences

    def is_allowed(self, command_name: str) -> bool:
        return command_name in self.user_preferences.get(ALWAYS_ALLOWED_KEY, [])

    def add(self, command_name: str):
        if ALWAYS_ALLOWED_KEY not in self.user_preferences:
            self.user_preferences[ALWAYS_ALLOWED_KEY] = []
        if command_name not in self.user_preferences[ALWAYS_ALLOWED_KEY]:
            self.user_preferences[ALWAYS_ALLOWED_KEY].append(command_name)

def show_logo_ascii():
    try:
        # Load from the package directory using pathlib
        from pathlib import Path
        logo_path = Path(__file__).parent / "assets" / "Max_Logo_ASCII.txt"
        with open(logo_path, "r", encoding="utf-8") as f:
            logo = f.read()

        print_formatted_text(HTML(f'<ansimagenta>{logo}</ansimagenta>'))
    except Exception as e:
        print("Could not display ASCII logo:", e)

def process_builtin_commands(user_input_lower: str, session: PromptSession, config: dict, user_preferences: dict) -> bool:
    """
    Processes built-in CLI commands.
    Returns True if a command was handled, False otherwise.
    """
    if user_input_lower in ["exit", "quit"]:
        logging.debug("Processing 'exit' command...")
        logging.info("Exiting Max via exit/quit command.")
        logging.debug("Calling sys.exit()")
        logging.info("Exiting Max via exit/quit command.")
        sys.exit()  # Explicitly call sys.exit()

    if user_input_lower == "help":
        print_help(config)
        return True
    if user_input_lower == "revoke":
        revoke_always_allowed_commands(session, user_preferences)
        return True
    if user_input_lower == "log":
        display_log_file()
        return True
    if user_input_lower == "config":
        reconfigure_llm()
        return True
    if user_input_lower == "tools":
        display_tools()
        return True

    return False

def process_sudo_command(user_input: str, words: list[str], session: PromptSession, user_preferences: dict, always_allow_manager: AlwaysAllowManager) -> bool:
    """
    Processes sudo commands.
    Returns True if a sudo command was identified and processed (or skipped due to permissions), False otherwise.
    """
    if not (words and words[0] == "sudo"):
        return False

    sudo_cmd = f"sudo {words[1]}" if len(words) > 1 else "sudo"
    never_allowed = user_preferences.get(NEVER_ALLOWED_KEY, [])
    if sudo_cmd in never_allowed:
        print(f"Command '{sudo_cmd}' is set to never allow. Skipping execution.")
        return True # Command identified and handled (by skipping)

    if always_allow_manager.is_allowed(sudo_cmd):
        execute_command(user_input)
        return True

    confirmation_choice = get_and_handle_confirmation(
        session,
        user_input,
        sudo_cmd,
        user_preferences,
        always_allow_manager,
        action_to_execute=user_input
    )
    if confirmation_choice == ALLOW_ONCE:
        execute_command(user_input)
    elif confirmation_choice == ALLOW_ALWAYS:
        always_allow_manager.add(sudo_cmd)
        print(f"Command '{sudo_cmd}' added to always allowed list.")
        execute_command(user_input)
    elif confirmation_choice == CANCEL:
        print("Execution cancelled.")
    else:
        print("Command not executed.")

    print() # For consistent spacing after command execution/cancellation messages
    sys.stdout.flush()
    return True # Sudo command was identified and processed

def process_shell_command(user_input: str, session: PromptSession, user_preferences: dict, always_allow_manager: AlwaysAllowManager) -> bool:
    """
    Processes direct shell commands (non-sudo).
    Returns True if a shell command was identified and processed (or skipped), False otherwise.
    """
    if not is_shell_command(user_input):
        return False

    base_cmd = user_input.strip().split()[0]
    never_allowed = user_preferences.get(NEVER_ALLOWED_KEY, [])
    if base_cmd in never_allowed:
        print(f"Command '{base_cmd}' is set to never allow. Skipping execution.")
        return True # Command identified and handled (by skipping)

    if always_allow_manager.is_allowed(base_cmd):
        execute_command(user_input)
        return True

    confirmation_choice = get_and_handle_confirmation(
        session,
        user_input,
        base_cmd,
        user_preferences,
        always_allow_manager,
        action_to_execute=user_input
    )
    if confirmation_choice == ALLOW_ONCE:
        execute_command(user_input)
    elif confirmation_choice == ALLOW_ALWAYS:
        always_allow_manager.add(base_cmd)
        print(f"Command '{base_cmd}' added to always allowed list.")
        execute_command(user_input)
    elif confirmation_choice == CANCEL:
        print("Execution cancelled.")
    else:
        print("Command not executed.")

    print() # For consistent spacing
    sys.stdout.flush()
    return True # Shell command identified and processed

def process_natural_language_input(user_input: str, session: PromptSession, config: dict, user_preferences: dict, always_allow_manager: AlwaysAllowManager):
    """
    Handles natural language input by querying the LLM and then dispatching to specific intent handlers.
    """
    llm_response_str = ""
    llm_response_data = {}

    local_intent = interpret_user_intent(user_input)

    if local_intent:
        llm_response_data = local_intent
    else:
        llm_response_str = query_llm(user_input, config)
        try:
            llm_response_data = json.loads(llm_response_str)
        except json.JSONDecodeError as e:
            logging.error(f"LLM response JSONDecodeError: {e}\nRaw response: {llm_response_str}")
            print_agent_response("The AI's response was not in a recognizable format. Please try rephrasing your request.")
            return
        except Exception as e: # Catch other potential errors during parsing
            logging.error(f"Error processing LLM response: {e}\nRaw response: {llm_response_str}")
            print_agent_response("An unexpected error occurred while processing the AI's response.")
            return

    if not llm_response_data: # Should be caught by above, but as a safeguard
        logging.error(f"LLM response data is empty after parsing. Raw response: {llm_response_str}")
        print_agent_response("The AI's response was empty or unreadable. Please try again.")
        # The following except Exception block seems misplaced and might catch errors from the above if not structured carefully.
        # It's better to handle specific cases or ensure this block is correctly scoped.
        # For now, assuming it was intended as a fallback if llm_response_str itself was problematic before json.loads
        # However, the initial json.loads errors are already caught.
        # If llm_response_data is empty, we should just return.
        return

    if "intent" not in llm_response_data:
        # If 'intent' is missing, try to see if it's a simple chat response.
        if "response" in llm_response_data:
            print_agent_response(llm_response_data["response"])
        elif llm_response_str: # Fallback to raw string if parsing gave data but no intent/response
             try:
                 # Attempt to parse again, in case the structure was unusual but valid JSON
                 parsed_fallback = json.loads(llm_response_str)
                 if isinstance(parsed_fallback, dict) and "response" in parsed_fallback:
                     print_agent_response(parsed_fallback["response"])
                 else:
                     # If it's some other JSON structure, it's an unexpected format.
                     logging.warning(f"LLM response was valid JSON but not a recognized chat format. Data: {llm_response_data}. Raw: {llm_response_str}")
                     print_agent_response("The AI's response was not in a recognizable chat format. Please try rephrasing.")
             except json.JSONDecodeError:
                 # If it's not JSON at all, print the raw string (as it might be a direct non-JSON LLM output)
                 print_agent_response(llm_response_str.strip())
        else:
            # This case implies local_intent was also null and query_llm returned nothing or unparsable
            logging.warning(f"LLM response was empty or unreadable and no local_intent. Raw: {llm_response_str}")
            print_agent_response("I'm not sure how to handle that. The AI response was empty or unreadable.")
        return

    intent = llm_response_data.get("intent") # This will be None if "intent" was not in llm_response_data

    # This block handles cases where 'intent' key might exist but is None/empty,
    # OR if the above block decided to proceed because 'intent' key was present but perhaps empty.
    # The primary filtering for "no intent key at all" is handled by the block above.
    if not intent:
        # If there's no intent, but there is a 'response' field, treat it as a chat.
        # This case should ideally be caught by the "intent not in llm_response_data" block if intent key is missing.
        # If intent key IS present but empty/None, this will catch it.
        if "response" in llm_response_data:
            handle_llm_chat_intent(llm_response_data)
        else:
            # This means 'intent' key might be present but empty, AND 'response' key is also missing.
            logging.warning(f"LLM response missing 'intent' or intent is empty, and no 'response' field. Data: {llm_response_data}. Raw: {llm_response_str}")
            print_agent_response("The AI provided a response, but I couldn't understand its purpose. Please try rephrasing.")
        return

    # Dispatch to specific handlers (Step 5 of the plan will fully implement these)
    if intent == "command":
        # Placeholder: In Step 5, this will call: handle_llm_command_intent(llm_response_data, session, config, user_preferences, always_allow_manager)
        # For now, to keep tests passing and functionality intact, we temporarily use the old logic or a direct call.
        # This will be properly refactored in the next step.
        handle_llm_command_intent(llm_response_data, session, config, user_preferences, always_allow_manager)
    elif intent == "chat":
        handle_llm_chat_intent(llm_response_data)
    elif intent == "plan":
        handle_llm_plan_intent(llm_response_data, session, user_preferences, always_allow_manager)
    elif intent == "tool_use":
        handle_llm_tool_use_intent(llm_response_data, session, user_preferences, always_allow_manager)
    else:
        print_agent_response(f"I received an unknown intent from the LLM: '{intent}'.")

# Definitions for handle_llm_command_intent, handle_llm_chat_intent, etc., will be added in Step 5.
# For now, let's add stubs or temporarily copy the logic if needed for this step to be "complete"
# in terms of `process_natural_language_input` calling them.
# For this step, the focus is on `process_natural_language_input` itself.
# The actual moving of logic into these handlers is the *next* step.

# Temporary stubs for now, to be fleshed out in Step 5

def handle_llm_command_intent(response_data: dict, session: PromptSession, config: dict, user_preferences: dict, always_allow_manager: AlwaysAllowManager):
    """
    Handles the 'command' intent from the LLM.
    Executes raw shell commands or pre-defined commands from config.yaml after user confirmation.
    """
    command_name = response_data.get("command")
    arguments = response_data.get("arguments", {})
    if not command_name:
        logging.warning(f"LLM command intent missing 'command' field. Data: {response_data}")
        print_agent_response("The AI proposed a command, but it was incomplete. Please try again.")
        return

    final_command = ""
    command_name_for_approval = ""

    if command_name == "raw_shell_command":
        final_command = arguments.get("command_string", "").strip()
        if not final_command:
            logging.warning(f"LLM raw_shell_command intent missing 'command_string'. Data: {response_data}")
            print_agent_response("The AI proposed a shell command, but didn't specify what to run. Please try again.")
            # Removed duplicate print_agent_response here
            return
        command_name_for_approval = final_command.split(' ')[0].strip()
    elif command_name in config.get("commands", {}):
        command_template = config["commands"][command_name]["command"]
        try:
            final_command = command_template.format(**arguments)
        except KeyError as e:
            logging.warning(f"LLM command intent for '{command_name}' missing argument {e} for formatting. Args: {arguments}, Template: {command_template}")
            print_agent_response(f"The AI proposed command '{command_name}', but was missing some information ({e}). Please try again.")
            return
        command_name_for_approval = command_name
    else:
        # This handles unknown commands. The previous structure had a duplicated `else` condition.
        logging.warning(f"LLM command intent for unknown command '{command_name}'. Data: {response_data}")
        print_agent_response(f"The AI proposed an unknown command: '{command_name}'.")
        # If it's an unknown command, we cannot format it with a template.
        # We should probably not proceed with execution or ask for confirmation of an unknown template.
        # For now, returning, as executing an unknown command based on a non-existent template is problematic.
        return


    confirmation_choice = get_and_handle_confirmation(
        session,
        final_command, # Propose the final command string
        command_name_for_approval if command_name_for_approval else "unknown_command_operation", # Use a placeholder if approval name is empty
        user_preferences,
        always_allow_manager,
        action_to_execute=final_command
    )

    if confirmation_choice in [ALLOW_ONCE, ALLOW_ALWAYS]:
        if confirmation_choice == ALLOW_ALWAYS:
            if isinstance(command_name_for_approval, str) and command_name_for_approval:
                always_allow_manager.add(command_name_for_approval)
                print_agent_response(f"Command '{command_name_for_approval}' added to always allowed list.") # Standardized to print_agent_response
            else:
                # Using print_agent_response for consistency, though this is more of a debug/warning state.
                print_agent_response("Warning: Command name for approval is not a valid string. Skipping always allow addition.")
        print_agent_response(f"Executing: {final_command}") # Standardized
        result = execute_command(final_command)
        if not result["success"]:
            print_agent_response(f"Command '{final_command}' failed: {result['output']}") # Standardized
        else:
            print_agent_response(f"Command '{final_command}' executed successfully.") # Standardized
    else:
        print_agent_response("Execution cancelled.") # Standardized
    logging.debug(f"Completed LLM command intent for: {command_name}")


def handle_llm_chat_intent(response_data: dict):
    """
    Handles the 'chat' intent from the LLM.
    Prints the LLM's response directly to the user.
    """
    chat_response = response_data.get("response", "I'm not sure how to respond to that.")
    print_agent_response(chat_response)

def handle_llm_plan_intent(response_data: dict, session: PromptSession, user_preferences: dict, always_allow_manager: AlwaysAllowManager):
    """
    Handles the 'plan' intent from the LLM.
    Executes a sequence of steps (commands or tool uses) with user confirmation for each.
    """
    plan_description = response_data.get("plan_description", "I have a plan to complete your request.")
    steps = response_data.get("steps", [])
    print_agent_response(plan_description)
    print_agent_response(f"The plan has {len(steps)} steps. I will ask for approval for each one.")

    i = 0
    while i < len(steps):
        step = steps[i]
        step_description = step.get("description", "No description for this step.")
        step_command = step.get("command", "").strip()
        step_tool_name = step.get("tool_name")
        step_arguments = step.get("arguments", {})

        if step_command:
            print_agent_response(f"\n--- Step {i+1}/{len(steps)}: {step_description} ---") # Standardized
            step_command_category = step_command.split(' ')[0].strip()
            if not sys.stdin.isatty():
                logging.info("Non-interactive mode detected. Automatically allowing command.")
                confirmation_choice = ALLOW_ONCE
            else:
                confirmation_choice = get_and_handle_confirmation(
                    session,
                    step_command,
                    step_command_category,
                    user_preferences,
                    always_allow_manager,
                    action_to_execute=step_command
                )

            if confirmation_choice in [ALLOW_ONCE, ALLOW_ALWAYS]:
                if confirmation_choice == ALLOW_ALWAYS: # Ensure always_allow is handled for plan steps too
                    always_allow_manager.add(step_command_category)
                    print_agent_response(f"Command category '{step_command_category}' (from plan) added to always allowed list.") # Standardized
                print_agent_response(f"Executing: {step_command}") # Standardized
                result = execute_command(step_command)
                if not result.get("success"):
                    print_agent_response(f"Step failed: {result['output']}") # Standardized
                    if not sys.stdin.isatty():
                        logging.info("Non-interactive mode. Aborting plan due to failed step.")
                        break
                    while True: # Loop for retry/skip/abort
                        print_agent_response("\nStep failed. Options:") # Standardized
                        print_agent_response("  1. Retry this step") # Standardized
                        print_agent_response("  2. Skip this step") # Standardized
                        print_agent_response("  3. Abort plan") # Standardized
                        fail_choice = session.prompt("Enter choice (1/2/3):").strip()
                        if fail_choice == '1':
                            print_agent_response("Retrying step...") # Standardized
                            break
                        elif fail_choice == '2':
                            print_agent_response("Skipping step...") # Standardized
                            i += 1
                            break
                        elif fail_choice == '3':
                            print_agent_response("Aborting plan.") # Standardized
                            i = len(steps)
                            break
                        else:
                            print_agent_response("Invalid choice. Please enter 1, 2, or 3.") # Standardized
                    if i == len(steps):
                        break
                    if fail_choice == '1':
                        continue
                else: # Step succeeded
                    print_agent_response(f"Step {i+1} executed successfully.") # Standardized
                    i += 1
            else: # Execution cancelled for this step
                print_agent_response("Plan cancelled by user.") # Standardized
                break
        elif step_tool_name:
            print_agent_response(f"\n--- Step {i+1}/{len(steps)}: {step_description} ---") # Standardized
            if not sys.stdin.isatty():
                logging.info("Non-interactive mode detected. Automatically allowing tool use.")
                handle_tool_use(None, {"tool_name": step_tool_name, "arguments": step_arguments}, user_preferences, always_allow_manager)
                i += 1
            else:
                print_agent_response(f"I am proposing to use the tool '{step_tool_name}' with arguments: {step_arguments}")
                tool_info = TOOL_REGISTRY.get(step_tool_name)
                if not tool_info:
                    logging.warning(f"Plan included an unknown tool: '{step_tool_name}'. Skipping step.")
                    print_agent_response(f"The plan includes an unknown tool: '{step_tool_name}'. I will skip this step.")
                    i += 1
                    continue

                try:
                    proposed_action = tool_info.get("confirmation_prompt", f"Use tool '{step_tool_name}'").format(**step_arguments)
                except KeyError as e:
                    logging.warning(f"Plan step for tool '{step_tool_name}' missing argument {e} for formatting. Args: {step_arguments}")
                    print_agent_response(f"The plan for tool '{step_tool_name}' is missing some information ({e}). I will skip this step.")
                    i += 1
                    continue

                confirmation_choice = get_and_handle_confirmation(
                    session,
                    proposed_action,
                    step_tool_name,
                    user_preferences,
                    always_allow_manager,
                    tool_info=tool_info,
                    tool_arguments=step_arguments
                )
                if confirmation_choice in [ALLOW_ONCE, ALLOW_ALWAYS]:
                    if confirmation_choice == ALLOW_ALWAYS:
                         always_allow_manager.add(step_tool_name)
                         print_agent_response(f"Tool '{step_tool_name}' (from plan) added to always allowed list.") # Standardized
                    handle_tool_use(session, {"tool_name": step_tool_name, "arguments": step_arguments}, user_preferences, always_allow_manager)
                    i += 1
                else:
                    print_agent_response("Tool use cancelled. Aborting plan.")
                    break
        else:
            logging.warning(f"Plan step {i+1} has no command or tool_name. Step data: {step}")
            # print_formatted_text(HTML(f"<ansiyellow>Step {i+1} is invalid (missing action) and will be skipped.</ansiyellow>")) # This uses HTML, print_agent_response is preferred for plain text
            print_agent_response(f"Step {i+1} is invalid (missing action) and will be skipped.") # Standardized
            i += 1
            continue
    logging.debug("Completed LLM plan intent.") # Replaced print with logging

def handle_llm_tool_use_intent(response_data: dict, session: PromptSession, user_preferences: dict, always_allow_manager: AlwaysAllowManager):
    """
    Handles the 'tool_use' intent from the LLM.
    This typically involves calling the main `handle_tool_use` function.
    """
    handle_tool_use(session, response_data, user_preferences, always_allow_manager)
    logging.debug("Completed LLM tool use intent.") # Replaced print with logging


def main():
    # Check if the .env file exists in the user's config directory
    config_dir = get_user_config_dir()
    env_file = config_dir / ".env"
    if not env_file.exists():
        first_run_setup()

    show_logo_ascii()
    logging.info("Starting Max agent...")
    try:
        config = load_config()
        if not config:
            print("Failed to load configuration")
            logging.error("Failed to load configuration")
            return

        # Load user preferences
        user_preferences = load_user_preferences()

        # Add tab-completion for commands
        COMMANDS = list(TOOL_REGISTRY.keys()) + ["help", "exit", "quit", "revoke"]
        # command_completer = WordCompleter(COMMANDS, ignore_case=True)
        session = PromptSession("Max> ", completer=None, style=Style.from_dict({"prompt": "green"}))
        always_allow_manager = AlwaysAllowManager(user_preferences)

        print_formatted_text(HTML("<ansigreen>Type 'help' for a list of commands.</ansigreen>"))

        while True:
            if not sys.stdin.isatty():
                user_input = sys.stdin.readline().strip()
                logging.debug(f"Non-TTY input received: '{user_input}'")
                if not user_input:
                    break
            else:
                user_input = session.prompt()
                logging.debug(f"Interactive input received: '{user_input}'")

            if not user_input.strip() or user_input.strip().lower() in {'n', 'y'}:
                continue

            user_input_lower = user_input.lower()
            if process_builtin_commands(user_input_lower, session, config, user_preferences):
                continue

            words = user_input.strip().split() # Needed for sudo check, and potentially others

            if process_sudo_command(user_input, words, session, user_preferences, always_allow_manager):
                continue

            if process_shell_command(user_input, session, user_preferences, always_allow_manager):
                continue

            # --- LLM/NATURAL LANGUAGE HANDLING ---
            # This block will only be reached if none of the above handlers processed the input
            process_natural_language_input(user_input, session, config, user_preferences, always_allow_manager)

    except KeyboardInterrupt:
        print("\nExiting Max.")
        logging.info("Max exited by user (KeyboardInterrupt).")
    except Exception as e:
        print("Max crashed with exception:", e)
        traceback.print_exc()
        logging.error("An error occurred", exc_info=True)

if __name__ == "__main__":
    main()