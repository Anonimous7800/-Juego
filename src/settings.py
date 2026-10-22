import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "music_volume": 0.70,
    "sfx_volume": 0.85,
    "fullscreen": False,
    "difficulty": "Normal",
    "show_particles": True,
    "fast_ai": False
}

class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance.data = dict(DEFAULT_SETTINGS)
            cls._instance.load()
        return cls._instance

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
