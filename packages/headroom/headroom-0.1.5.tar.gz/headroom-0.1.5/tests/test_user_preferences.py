from headroom.user_preferences import save_user_preferences, load_user_preferences, get_preferences_file_path
import os
from unittest.mock import patch

def test_save_and_load_user_preferences(tmp_path):
    test_file = tmp_path / "prefs.json"
    prefs = {"always_allowed_commands": ["ls", "echo"]}

    # Patch get_preferences_file_path to return our temporary file path
    with patch('headroom.user_preferences.get_preferences_file_path', return_value=test_file):
        save_user_preferences(prefs)
        loaded = load_user_preferences()
        assert loaded == prefs

        # Test loading when file doesn't exist (after deleting it)
        os.remove(test_file)
        loaded_again = load_user_preferences()
        assert loaded_again == {} # Should return empty dict

        # Test saving again
        prefs2 = {"another_key": "another_value"}
        save_user_preferences(prefs2)
        loaded_final = load_user_preferences()
        assert loaded_final == prefs2