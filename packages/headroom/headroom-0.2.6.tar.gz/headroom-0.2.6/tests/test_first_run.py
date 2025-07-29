import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from headroom.first_run import first_run_setup

# Use a dictionary to simulate a sequence of user inputs for the prompt mock
@pytest.mark.parametrize("provider_choice, provider_name, settings_prompts, expected_settings", [
    # Test Case 1: Ollama
    (
        "1", "ollama", ["llama3", "http://localhost:11434"],
        "LLM_PROVIDER=ollama\nOLLAMA_MODEL=llama3\nOLLAMA_ENDPOINT=http://localhost:11434\n"
    ),
    # Test Case 2: OpenAI
    (
        "2", "openai", ["sk-test-key"],
        "LLM_PROVIDER=openai\nOPENAI_API_KEY=sk-test-key\n"
    ),
    # Test Case 3: Anthropic
    (
        "3", "anthropic", ["anth-test-key"],
        "LLM_PROVIDER=anthropic\nANTHROPIC_API_KEY=anth-test-key\n"
    ),
    # Test Case 4: Google
    (
        "4", "google", ["goog-test-key"],
        "LLM_PROVIDER=google\nGOOGLE_API_KEY=goog-test-key\n"
    ),
    # Test Case 5: Local GGUF
    (
        "5", "local_gguf", ["/path/to/model.gguf"],
        "LLM_PROVIDER=local_gguf\nLOCAL_GGUF_MODEL_PATH=/path/to/model.gguf\n"
    ),
])
def test_first_run_setup(provider_choice, provider_name, settings_prompts, expected_settings, tmp_path):
    """Tests the complete first_run_setup flow for each provider."""
    # The first call to prompt selects the provider, the rest provide settings.
    prompt_inputs = [provider_choice] + settings_prompts

    # Mock the user's config directory to use the temporary path
    mock_config_dir = tmp_path / ".config" / "headroom"

    # Patch the prompt function to return our simulated inputs
    # Patch get_user_config_dir to return our temp directory
    # Patch open to capture what's being written to the .env file
    with patch('headroom.first_run.prompt', side_effect=prompt_inputs),         patch('headroom.first_run.get_user_config_dir', return_value=mock_config_dir),         patch('builtins.open', mock_open()) as mocked_file,         patch('headroom.first_run.print_formatted_text'):

        first_run_setup()

        # Assert that the .env file was created in the correct directory
        expected_env_path = mock_config_dir / ".env"
        mocked_file.assert_called_once_with(expected_env_path, "w")

        # Assert that the correct content was written to the .env file
        handle = mocked_file()
        handle.write.assert_called_once_with(expected_settings)