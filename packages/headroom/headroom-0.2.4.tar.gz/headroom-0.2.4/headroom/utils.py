# Helper Functions

import json
import shutil
from datetime import datetime, timedelta, timezone
import os
import platform
import yaml
import requests
import subprocess # Added for system checks
from dotenv import load_dotenv
import re
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir

def get_user_config_dir() -> Path:
    """Returns the path to the user-specific config directory."""
    return Path(user_config_dir("headroom", "headroom"))

def get_user_data_dir() -> Path:
    """Returns the path to the user-specific data directory."""
    return Path(user_data_dir("headroom", "headroom"))

def load_config() -> dict | None:
    # Load environment variables from .env file
    config_dir = get_user_config_dir()
    env_file = config_dir / ".env"
    load_dotenv(dotenv_path=env_file)
 
    config_file = config_dir / "config.yaml"
 
    # If the user config file doesn't exist, create it from the packaged default.
    if not config_file.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            default_config_path = Path(__file__).parent / "config.yaml"
            shutil.copy(default_config_path, config_file)
            print(f"Created default configuration at: {config_file}")
        except Exception as e:
            print(f"Error creating default config: {e}")
            return None
 
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
 
        # Set defaults for conversation settings if not specified
        conversation_settings = {
            'max_entries': 10,
            'max_age_hours': 24
        }
        config['conversation'] = {**conversation_settings, **(config.get('conversation', {}))}

        # Load LLM provider from environment variable
        provider = os.getenv("LLM_PROVIDER")
        if not provider:
            print("Error: LLM_PROVIDER environment variable not set. Please run setup again.")
            return None

        config['llm'] = {'provider': provider}

        # --- Validate and load provider-specific settings ---
        if provider == 'ollama':
            model = os.getenv("OLLAMA_MODEL")
            api_base = os.getenv("OLLAMA_ENDPOINT")
            if not model or not api_base:
                print("Error: For the 'ollama' provider, both OLLAMA_MODEL and OLLAMA_ENDPOINT must be set in your .env file.")
                return None
            config['llm']['model'] = model
            config['llm']['api_base'] = api_base

        elif provider == 'openai':
            if not os.getenv("OPENAI_API_KEY"):
                print("Error: OPENAI_API_KEY is not set in your .env file.")
                return None
            config['llm']['model'] = "gpt-4-turbo"
            config['llm']['api_base'] = "https://api.openai.com/v1"

        elif provider == 'anthropic':
            if not os.getenv("ANTHROPIC_API_KEY"):
                print("Error: ANTHROPIC_API_KEY is not set in your .env file.")
                return None
            config['llm']['model'] = "claude-3-opus-20240229"
            config['llm']['api_base'] = "https://api.anthropic.com/v1"

        elif provider == 'google':
            if not os.getenv("GOOGLE_API_KEY"):
                print("Error: GOOGLE_API_KEY is not set in your .env file.")
                return None
            config['llm']['model'] = "gemini-1.5-pro-latest"
            config['llm']['api_base'] = "https://generativelanguage.googleapis.com/v1beta"

        elif provider == 'local_gguf':
            model_path = os.getenv("LOCAL_GGUF_MODEL_PATH")
            if not model_path:
                print("Error: For the 'local_gguf' provider, LOCAL_GGUF_MODEL_PATH must be set in your .env file.")
                return None
            config['llm']['model'] = model_path

        else:
            print(f"Error: Unknown LLM provider '{provider}' configured.")
            return None

        return config

    except yaml.YAMLError as e:
        print(f"Error loading configuration from config.yaml: {e}")
        return None

def load_conversation_history(config: dict) -> list:
    data_dir = get_user_data_dir()
    history_file = data_dir / "conversation_history.json"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(history_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_conversation_history(history: list, config: dict) -> None:
    data_dir = get_user_data_dir()
    history_file = data_dir / "conversation_history.json"

    # Create backup before saving
    if history_file.exists():
        shutil.copy2(history_file, f"{history_file}.backup")

    data_dir.mkdir(parents=True, exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(history, f)

def truncate_history(history: list, max_entries: int = 10) -> list:
    return history[-max_entries:] if len(history) > max_entries else history

def prune_old_entries(history: list, max_age_hours: int = 24) -> list:
    now = datetime.now(timezone.utc)
    pruned = []
    for entry in history:
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = now - dt.astimezone(timezone.utc)
            if age <= timedelta(hours=max_age_hours):
                pruned.append(entry)
        except Exception:
            continue
    return pruned


def get_system_context_str() -> str:
    import platform, getpass, socket
    context = []
    os_name = platform.system()
    if os_name == 'Linux':
        try:
            release_info = platform.freedesktop_os_release()
            os_pretty = release_info.get('PRETTY_NAME', 'Linux')
        except Exception:
            os_pretty = f"Linux ({platform.release()})"
    else:
        os_pretty = f"{os_name} {platform.release()}"
    context.append(f"OS: {os_pretty}")
    context.append(f"Architecture: {platform.machine()}")
    context.append(f"Python version: {platform.python_version()}")
    context.append(f"Current directory: {os.getcwd()}")
    context.append(f"User: {getpass.getuser()}")
    # Add tool presence
    from headroom.system_tools import check_command_exists
    tools = ["node", "npm", "yarn", "docker", "git", "python3", "pip", "systemctl", "apt", "snap", "flatpak"]
    tool_status = ", ".join(f"{tool}: {'yes' if check_command_exists(tool)['exists'] else 'no'}" for tool in tools)
    context.append(f"Tools available: {tool_status}")
    return "\n".join(context)

def interpret_user_intent(prompt: str) -> dict | None:
    """
    Interprets simple user prompts to directly map to commands or tools.
    Returns a structured intent dictionary or None if no direct match.
    """
    prompt_lower = prompt.lower().strip()

    # Simple command mappings
    
    if prompt_lower.startswith("show me the contents of"):
        # NOTE: This assumes files are relative to the current working directory.
        # This is more portable than a hardcoded path.
        file_path = prompt_lower.replace("show me the contents of", "").strip().rstrip('.')
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return {"intent": "tool_use", "tool_name": "read_yaml_file", "arguments": {"file_path": file_path}}
        elif file_path.endswith(".json"):
            return {"intent": "tool_use", "tool_name": "read_json_file", "arguments": {"file_path": file_path}}
        elif file_path.endswith(".env"):
            return {"intent": "tool_use", "tool_name": "read_env_file", "arguments": {"file_path": file_path}}
        else:
            # For other file types, just cat it
            return {"intent": "command", "command": "raw_shell_command", "arguments": {"command_string": f"cat {file_path}"}}
    
    if prompt_lower == "what is the current cpu utilization and memory usage of this machine?":
        return {
            "intent": "plan",
            "plan_description": "Retrieve and display current CPU and memory usage.",
            "steps": [
                {
                    "description": "Get CPU utilization",
                    "tool_name": "parse_cpu_usage",
                    "arguments": {}
                },
                {
                    "description": "Get memory usage",
                    "tool_name": "parse_memory_usage",
                    "arguments": {}
                }
            ]
        }
    
    # Pattern for changing max_entries in config.yaml
    if prompt_lower.startswith("change the max_entries to"):
        try:
            value = int(prompt_lower.split("to")[-1].strip())
            return {
                "intent": "tool_use",
                "tool_name": "update_yaml_file",
                "arguments": {
                    "file_path": str(get_user_config_dir() / "config.yaml"),
                    "key_path": "conversation.max_entries",
                    "value": value
                }
            }
        except ValueError:
            pass # Fall through to LLM if parsing fails

    # Patterns for general package management
    # Install package
    match_install = re.search(r"install\s+(?:the\s+)?(?:package\s+)?(\S+)(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_install:
        package_name = match_install.group(1).strip()
        package_manager = match_install.group(2) # This will be None if not specified
        return {"intent": "tool_use", "tool_name": "install_package", "arguments": {"package_name": package_name, "package_manager": package_manager}}

    # Remove package
    match_remove = re.search(r"(?:remove|uninstall)\s+(?:the\s+)?(?:package\s+)?(\S+)(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_remove:
        package_name = match_remove.group(1).strip()
        package_manager = match_remove.group(2)
        return {"intent": "tool_use", "tool_name": "remove_package", "arguments": {"package_name": package_name, "package_manager": package_manager}}

    # List packages
    match_list = re.search(r"(?:list|show me)\s+(?:all\s+)?(?:installed\s+)?packages(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_list:
        package_manager = match_list.group(1)
        return {"intent": "tool_use", "tool_name": "list_packages", "arguments": {"package_manager": package_manager}}

    # Search package
    match_search = re.search(r"search\s+for\s+(?:package\s+)?(\S+)(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_search:
        package_name = match_search.group(1).strip()
        package_manager = match_search.group(2)
        return {"intent": "tool_use", "tool_name": "search_package", "arguments": {"package_name": package_name, "package_manager": package_manager}}

    # Original specific apt install rule (can be removed or kept for specificity)
    # if prompt_lower.startswith("install a package named"):
    #     package_name = prompt_lower.replace("install a package named", "").strip().replace(".", "")
    #     return {"intent": "tool_use", "tool_name": "install_package", "arguments": {"package_name": package_name, "package_manager": "apt"}} # Explicitly use apt here if rule is kept

    # New patterns for file system operations
    # Copy file/directory
    match_copy = re.search(r"copy\s+(.+?)\s+to\s+(.+?)(?:\s+recursively)?", prompt_lower)
    if match_copy:
        src = match_copy.group(1).strip()
        dst = match_copy.group(2).strip()
        recursive = "recursively" in prompt_lower
        # Assuming absolute paths will be provided by the user or handled by the LLM
        return {"intent": "tool_use", "tool_name": "copy_file", "arguments": {"src": src, "dst": dst, "recursive": recursive}}

    # Move file/directory
    match_move = re.search(r"move\s+(.+?)\s+to\s+(.+)", prompt_lower)
    if match_move:
        src = match_move.group(1).strip()
        dst = match_move.group(2).strip()
        # Assuming absolute paths will be provided by the user or handled by the LLM
        return {"intent": "tool_use", "tool_name": "move_file", "arguments": {"src": src, "dst": dst}}

    # Delete file/directory
    match_delete = re.search(r"delete\s+(.+?)(?:\s+and\s+its\s+contents|\s+recursively)?$", prompt_lower)
    if match_delete:
        # Assuming absolute paths will be provided by the user or handled by the LLM
        path = match_delete.group(1).strip().replace('`', '') # Remove backticks if present
        recursive = "and its contents" in prompt_lower or "recursively" in prompt_lower
        
        # Determine if it's likely a directory or file based on recursive flag
        if recursive:
             return {"intent": "tool_use", "tool_name": "remove_directory", "arguments": {"path": path, "recursive": True}}
        else:
            return {"intent": "tool_use", "tool_name": "delete_file", "arguments": {"path": path}}

def load_prompt_template() -> str:
    try:
        # Load from the package directory
        template_path = Path(__file__).parent / "prompt_template.txt"
        with open(template_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are Max, an AI assistant. Use the following conversation history and user prompt to determine intent.\n"
            "Conversation history:\n{history}\nUser prompt:\n{prompt}\n"
        )

def format_command_generation_prompt(prompt: str, history: list, config: dict) -> str:
    template = load_prompt_template()
    available_commands = get_available_tools_summary(config)
    system_context = get_system_context_str()
    history_str = "\n".join([f"User: {h['prompt']}\nMax: {h['response']}" for h in history])
    try:
        return template.format(
            available_commands=available_commands,
            history=history_str,
            prompt=prompt,
            system_context=system_context
        )
    except KeyError as e:
        # Log the error for developers, but do not print to user
        import logging
        logging.error(f"Missing key in prompt template: {e}")
        # Fallback: just use the user prompt
        return prompt

def query_llm(prompt: str, config: dict) -> str:
    """
    Queries the configured LLM provider with the given prompt and returns the response.
    """
    history = load_conversation_history(config)
    history = prune_old_entries(history, config['conversation']['max_age_hours'])
    history = truncate_history(history, config['conversation']['max_entries'])
    
    full_prompt = format_command_generation_prompt(prompt, history, config)
    
    provider = config["llm"]["provider"]
    model = config["llm"]["model"]
    api_base = config["llm"].get("api_base") # .get() is safer
    response = None

    headers = {}
    payload = {}
    
    try:
        # --- Provider-specific logic ---
        if provider == "ollama":
            url = f"{api_base}/api/generate"
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
            }
        elif provider == "openai":
            url = f"{api_base or 'https://api.openai.com/v1'}/chat/completions"
            headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": full_prompt}
                ],
                "stream": False,
            }
        elif provider == "anthropic":
            url = f"{api_base or 'https://api.anthropic.com/v1'}/messages"
            headers = {
                "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
                "anthropic-version": "2023-06-01"
            }
            payload = {
                "model": model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": full_prompt}],
            }
        elif provider == "google":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={os.getenv('GOOGLE_API_KEY')}"
            payload = {
                "contents": [{"parts":[{"text": full_prompt}]}]
            }
        else:
             return json.dumps({"intent": "chat", "response": f"Error: LLM provider '{provider}' is not supported for querying."})

        # --- Make the request ---
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status() # Raise an exception for bad status codes
        
        raw_response_data = response.json()
        
        # --- Extract the response text ---
        if provider == "ollama":
            result = raw_response_data.get("response", "").strip()
        elif provider == "openai":
            result = raw_response_data['choices'][0]['message']['content'].strip()
        elif provider == "anthropic":
            result = raw_response_data['content'][0]['text'].strip()
        elif provider == "google":
            result = raw_response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            result = ""

        # --- Process and save history ---
        # Try to extract a JSON code block from the result
        code_block_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", result)
        if code_block_match:
            json_str = code_block_match.group(1).strip()
        else:
            json_str = result

        try:
            # If the result is valid JSON, return it as is
            parsed_json = json.loads(json_str)
            response_to_save = json.dumps(parsed_json)
            response_to_return = json_str
        except json.JSONDecodeError:
            # If not, wrap it in a chat intent
            chat_response = {"intent": "chat", "response": result}
            response_to_save = json.dumps(chat_response)
            response_to_return = response_to_save

        history.append({
            "prompt": prompt,
            "response": response_to_save,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        save_conversation_history(history, config)
        
        return response_to_return

    except requests.exceptions.RequestException as e:
        return json.dumps({"intent": "chat", "response": f"API request failed: {e}"})
    except (KeyError, IndexError) as e:
        raw_response_text = response.text if response else "Not available"
        return json.dumps({"intent": "chat", "response": f"Failed to parse LLM response: {e}. Raw response: {raw_response_text}"})
    except Exception as e:
        return json.dumps({"intent": "chat", "response": f"An unexpected error occurred: {e}"})

def get_available_tools_summary(config):
    commands = config.get("commands", {})
    return "\n".join(f"- {name}: {details.get('description', '')}" for name, details in commands.items())
