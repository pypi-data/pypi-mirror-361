# Main Max> Config
# Install Dependencies - pip3 install prompt_toolkit pyyaml requests dotenv

import json
import sys
import traceback
import logging
import os
import shlex
from prompt_toolkit import PromptSession, print_formatted_text, HTML
# from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from .utils import load_config, query_llm, interpret_user_intent, get_user_data_dir, get_user_config_dir
from .max_display import print_agent_response
from .tools import execute_command
from .user_preferences import load_user_preferences, save_user_preferences
from .tool_registry import TOOL_REGISTRY
from .first_run import first_run_setup

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
    first_word = shlex.split(user_input.strip())[0]
    return first_word in SHELL_COMMANDS

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
    if not sys.stdin.isatty():
        logging.info("Non-interactive mode detected for confirmation. Automatically allowing action once.")
        return ALLOW_ONCE

    print_formatted_text(HTML(f'<ansigreen>\nProposed action: {proposed_action}</ansigreen>'))

    # Show extra info if available
    if tool_info:
        print_formatted_text(HTML(f"<ansicyan>Tool: {action_name_for_approval}</ansicyan>"))
        if "args" in tool_info:
            print_formatted_text(HTML(f"<ansicyan>Required args: {tool_info['args']}</ansicyan>"))
        if "optional_args" in tool_info:
            print_formatted_text(HTML(f"<ansicyan>Optional args: {tool_info['optional_args']}</ansicyan>"))
        if "confirmation_prompt" in tool_info:
            print_formatted_text(HTML(f"<ansicyan>Description: {tool_info['confirmation_prompt']}</ansicyan>"))
    if tool_arguments:
        print_formatted_text(HTML(f"<ansicyan>Arguments: {tool_arguments}</ansicyan>"))
    if action_to_execute:
        print_formatted_text(HTML(f"<ansiyellow>Shell command to execute: {action_to_execute}</ansiyellow>"))

    if not sys.stdin.isatty():
        logging.info("Non-interactive mode detected. Automatically allowing action.")
        return ALLOW_ONCE

    if action_name_for_approval in user_preferences.get(ALWAYS_ALLOWED_KEY, []):
        logging.info(f"Action category '{action_name_for_approval}' is always allowed. Executing automatically.")
        return ALLOW_ONCE

    confirm_session = PromptSession(HTML('<ansigreen>Enter choice (1/2/3): </ansigreen>'))

    while True:
        print_formatted_text(HTML('<ansigreen>Allow execution?</ansigreen>'))
        print_formatted_text(HTML(
            f'<ansiyellow>  1. Yes, allow once\n'
            f'  2. Yes, always allow \'{action_name_for_approval}...\'\n'
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

def handle_tool_use(session: PromptSession | None, llm_response, user_preferences, always_allow_manager):
    tool_name = llm_response.get("tool_name")
    args = llm_response.get("arguments", {})

    if tool_name not in TOOL_REGISTRY:
        print_agent_response(f"Unknown tool: {tool_name}")
        return

    tool_info = TOOL_REGISTRY[tool_name]
    tool_function = tool_info["function"]
    required_args = tool_info.get("args", [])
    optional_args = tool_info.get("optional_args", [])
    confirmation_prompt_template = tool_info.get("confirmation_prompt")

    # Validate required arguments
    missing_args = [arg for arg in required_args if arg not in args]
    if missing_args:
        print_agent_response(
            f"Error: Missing required arguments for tool '{tool_name}': {', '.join(missing_args)}. "
            f"Required: {required_args}. Optional: {optional_args if optional_args else 'None'}"
        )
        return

    # Warn about unexpected arguments
    all_valid_args = set(required_args + optional_args)
    unexpected_args = [arg for arg in args if arg not in all_valid_args]
    if unexpected_args:
        print_agent_response(
            f"Warning: Unexpected arguments for tool '{tool_name}': {', '.join(unexpected_args)}. "
            f"Expected: {required_args} + optional {optional_args if optional_args else 'None'}"
        )

    # Fill in optional arguments with defaults if not provided
    for opt in optional_args:
        if opt not in args:
            # Provide sensible defaults for common optional args
            if opt == "recursive":
                args[opt] = False
            elif opt == "exist_ok":
                args[opt] = True

    # Get and handle confirmation using the new function
    if confirmation_prompt_template:
        proposed_action = confirmation_prompt_template.format(**args)
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
        result = tool_function(**args)
    except Exception as e:
        print_agent_response(f"Error executing tool '{tool_name}': {e}")
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
        except Exception:
            print_agent_response(llm_response_str.strip())
            return

    if not llm_response_data or "intent" not in llm_response_data:
        try:
            if llm_response_str and isinstance(json.loads(llm_response_str), dict) and "response" in json.loads(llm_response_str):
                 print_agent_response(json.loads(llm_response_str)["response"])
            elif not local_intent:
                print_agent_response(llm_response_str.strip() if llm_response_str else "I could not process your request.")
            elif local_intent and "response" in local_intent :
                print_agent_response(local_intent["response"])
            else:
                print_agent_response("I'm not sure how to handle that.")
        except Exception:
             if not local_intent:
                print_agent_response(llm_response_str.strip() if llm_response_str else "I could not process your request.")
             else:
                print_agent_response("I'm not sure how to handle that.")
        return

    intent = llm_response_data.get("intent")

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
def handle_llm_command_intent(response_data, session, config, user_preferences, always_allow_manager):
    command_name = response_data.get("command")
    arguments = response_data.get("arguments", {})
    if not command_name:
        print("Max: I received a command intent, but for an unknown or unparseable command 'None'.")
        return

    final_command = ""
    command_name_for_approval = ""

    if command_name == "raw_shell_command":
        final_command = arguments.get("command_string", "").strip()
        if not final_command:
            print_agent_response("I received a raw shell command intent, but no command string was provided by the LLM.")
            return
        command_name_for_approval = final_command.split(' ')[0].strip()
    elif command_name in config.get("commands", {}):
        command_template = config["commands"][command_name]["command"]
        final_command = command_template.format(**arguments) # Using SafeDict might be good here if not already applied
        command_name_for_approval = command_name
    else:
        print_agent_response(f"I received a command intent, but for an unknown or unparseable command '{command_name}'.")
        return

    confirmation_choice = get_and_handle_confirmation(
        session,
        final_command,
        command_name_for_approval if command_name_for_approval is not None else "",
        user_preferences,
        always_allow_manager,
        action_to_execute=final_command
    )

    if confirmation_choice in [ALLOW_ONCE, ALLOW_ALWAYS]:
        if confirmation_choice == ALLOW_ALWAYS:
            if isinstance(command_name_for_approval, str) and command_name_for_approval:
                always_allow_manager.add(command_name_for_approval)
                print(f"Command '{command_name_for_approval}' added to always allowed list.")
            else:
                print("Warning: Command name for approval is not a valid string. Skipping always allow addition.")
        print(f"Executing: {final_command}")
        result = execute_command(final_command)
        if not result["success"]:
            print(f"Command '{final_command}' failed: {result['output']}")
        else:
            print(f"Command '{final_command}' executed successfully.")
    else:
        print("Execution cancelled.")
    print("-" * 60)


def handle_llm_chat_intent(response_data):
    chat_response = response_data.get("response", "I'm not sure how to respond to that.")
    print_agent_response(chat_response)

def handle_llm_plan_intent(response_data, session, user_preferences, always_allow_manager):
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
            print(f"\n--- Step {i+1}/{len(steps)}: {step_description} ---")
            if not sys.stdin.isatty():
                logging.info("Non-interactive mode detected. Automatically allowing command.")
                confirmation_choice = ALLOW_ONCE
            else:
                step_command_category = step_command.split(' ')[0].strip()
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
                    print(f"Command category '{step_command_category}' (from plan) added to always allowed list.")
                print(f"Executing: {step_command}")
                result = execute_command(step_command)
                if not result.get("success"):
                    print(f"Step failed: {result['output']}")
                    if not sys.stdin.isatty():
                        logging.info("Non-interactive mode. Aborting plan due to failed step.")
                        break
                    while True: # Loop for retry/skip/abort
                        print("\nStep failed. Options:")
                        print("  1. Retry this step")
                        print("  2. Skip this step")
                        print("  3. Abort plan")
                        fail_choice = session.prompt("Enter choice (1/2/3):").strip()
                        if fail_choice == '1':
                            print("Retrying step...")
                            # Do not increment i, retry current step
                            break
                        elif fail_choice == '2':
                            print("Skipping step...")
                            i += 1 # Move to next step
                            break
                        elif fail_choice == '3':
                            print("Aborting plan.")
                            # To exit the outer while loop for steps
                            i = len(steps) # or use a flag and break outer
                            break
                        else:
                            print("Invalid choice. Please enter 1, 2, or 3.")
                    if i == len(steps): # If aborted from inner loop
                        break
                    if fail_choice == '1': # If retry, continue to next iteration of outer loop for same step
                        continue
                else: # Step succeeded
                    print(f"Step {i+1} executed successfully.")
                    i += 1
            else: # Execution cancelled for this step
                print("Plan cancelled by user.")
                break
        elif step_tool_name:
            print(f"\n--- Step {i+1}/{len(steps)}: {step_description} ---")
            if not sys.stdin.isatty():
                logging.info("Non-interactive mode detected. Automatically allowing tool use.")
                # Directly call handle_tool_use, assuming it won't prompt if session is None
                handle_tool_use(None, {"tool_name": step_tool_name, "arguments": step_arguments}, user_preferences, always_allow_manager)
                i += 1
            else:
                print_agent_response(f"I am proposing to use the tool '{step_tool_name}' with arguments: {step_arguments}")
                tool_info = TOOL_REGISTRY.get(step_tool_name)
                # Use get_and_handle_confirmation for tool steps as well
                confirmation_choice = get_and_handle_confirmation(
                    session,
                    tool_info.get("confirmation_prompt", f"Use tool '{step_tool_name}'").format(**step_arguments),
                    step_tool_name, # action_name_for_approval
                    user_preferences,
                    always_allow_manager,
                    tool_info=tool_info,
                    tool_arguments=step_arguments
                )
                if confirmation_choice in [ALLOW_ONCE, ALLOW_ALWAYS]:
                    if confirmation_choice == ALLOW_ALWAYS:
                         always_allow_manager.add(step_tool_name)
                         print(f"Tool '{step_tool_name}' (from plan) added to always allowed list.")
                    handle_tool_use(session, {"tool_name": step_tool_name, "arguments": step_arguments}, user_preferences, always_allow_manager)
                    # Assuming handle_tool_use result doesn't need retry/skip logic here,
                    # or that such logic is internal to handle_tool_use if critical.
                    # For simplicity, we assume tool use either succeeds or its failure is just reported.
                    i += 1
                else: # Tool use cancelled
                    print_agent_response("Tool use cancelled. Aborting plan.")
                    break
        else: # Step has no command or tool
            print(f"Step {i+1} has no command or tool. Skipping.")
            i += 1
            continue # Ensure loop continues correctly
    print("-" * 60)

def handle_llm_tool_use_intent(response_data, session, user_preferences, always_allow_manager):
    # This is the same as the top-level handle_tool_use function,
    # but called specifically for "tool_use" intent from the LLM.
    # The original handle_tool_use was designed for this.
    handle_tool_use(session, response_data, user_preferences, always_allow_manager)
    print("-" * 60)


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

        print_formatted_text(HTML("<ansigreen>Type 'help' for a list of commands. New commands include: 'log', 'config', 'tools'.</ansigreen>"))

        while True:
            if not sys.stdin.isatty():
                user_input = sys.stdin.readline().strip()
                if not user_input:
                    break
            else:
                user_input = session.prompt()

            if not user_input.strip() or user_input.strip().lower() in {'n', 'y'}:
                continue

            user_input_lower = user_input.lower()
            if process_builtin_commands(user_input_lower, session, config, user_preferences):
                continue
            if user_input.lower() == "log":
                display_log_file()
                continue
            if user_input.lower() == "config":
                reconfigure_llm()
                continue
            if user_input.lower() == "tools":
                display_tools()
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