from pathlib import Path
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import prompt
from .utils import get_user_config_dir
 
def prompt_for_llm_provider():
    """Prompts the user to select their LLM provider."""
    print_formatted_text(HTML("<ansigreen>Welcome to Max! Let's set up your LLM provider.</ansigreen>"))
    print_formatted_text(HTML("<ansiyellow>Please select your LLM provider:</ansiyellow>"))
    print_formatted_text(HTML("  1. Ollama"))
    print_formatted_text(HTML("  2. OpenAI"))
    print_formatted_text(HTML("  3. Anthropic"))
    print_formatted_text(HTML("  4. Google"))
    print_formatted_text(HTML("  5. Local GGUF"))
    while True:
        choice = prompt("Enter the number of your choice: ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return {
                "1": "ollama",
                "2": "openai",
                "3": "anthropic",
                "4": "google",
                "5": "local_gguf",
            }[choice]
        else:
            print_formatted_text(HTML("<ansired>Invalid choice. Please enter a number from 1 to 5.</ansired>"))
 
def prompt_for_ollama_settings():
    """Prompts the user for their Ollama settings."""
    model = prompt("Enter the Ollama model you want to use (e.g., 'llama3'): ").strip()
    api_base = prompt("Enter the Ollama API base URL (e.g., 'http://localhost:11434'): ").strip()
    return {"OLLAMA_MODEL": model, "OLLAMA_ENDPOINT": api_base}

def prompt_for_openai_settings():
    """Prompts the user for their OpenAI API key."""
    api_key = prompt("Enter your OpenAI API key: ").strip()
    return {"OPENAI_API_KEY": api_key}

def prompt_for_anthropic_settings():
    """Prompts the user for their Anthropic API key."""
    api_key = prompt("Enter your Anthropic API key: ").strip()
    return {"ANTHROPIC_API_KEY": api_key}

def prompt_for_google_settings():
    """Prompts the user for their Google API key."""
    api_key = prompt("Enter your Google API key: ").strip()
    return {"GOOGLE_API_KEY": api_key}

def prompt_for_local_gguf_settings():
    """Prompts the user for the path to their local GGUF model file."""
    model_path = prompt("Enter the absolute path to your .gguf model file: ").strip()
    return {"LOCAL_GGUF_MODEL_PATH": model_path}

def create_env_file(settings):
    """Creates a .env file in the user's configuration directory."""
    config_dir = get_user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    env_file = config_dir / ".env"
    with open(env_file, "w") as f:
       f.write("".join([f"{key}={value}\n" for key, value in settings.items()]))
    print_formatted_text(HTML(f"<ansigreen>Successfully created .env file at: {env_file}</ansigreen>"))
 
def first_run_setup():
    """Orchestrates the first-run setup process."""
    provider = prompt_for_llm_provider()
    settings = {"LLM_PROVIDER": provider}
    if provider == "ollama":
        settings.update(prompt_for_ollama_settings())
    elif provider == "openai":
        settings.update(prompt_for_openai_settings())
    elif provider == "anthropic":
        settings.update(prompt_for_anthropic_settings())
    elif provider == "google":
        settings.update(prompt_for_google_settings())
    elif provider == "local_gguf":
        settings.update(prompt_for_local_gguf_settings())
    create_env_file(settings)
    print_formatted_text(HTML(f"<ansigreen>Your LLM settings have been saved to {get_user_config_dir() / '.env'}.</ansigreen>"))
    print_formatted_text(HTML("<ansigreen>You can change these settings at any time by typing 'config' in the Max CLI.</ansigreen>"))