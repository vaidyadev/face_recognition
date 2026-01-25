import json
import os

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file. Returns default if file doesn't exist."""
        if not os.path.exists(self.settings_file):
            return self.get_defaults()
        
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.get_defaults()

    def get_defaults(self):
        """Returns default settings."""
        return {
            "language": "en",
            "model": "tngtech/deepseek-r1t2-chimera:free"
        }

    def save_settings(self, new_settings=None):
        """Saves current settings to the JSON file."""
        if new_settings:
            self.settings.update(new_settings)
            
        # Ensure directory exists if path has one
        directory = os.path.dirname(self.settings_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Retrieves a setting value."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Sets a setting value and saves immediately."""
        self.settings[key] = value
        self.save_settings()
