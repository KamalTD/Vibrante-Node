import os
import json

class ConfigManager:
    _instance = None
    _config_path = os.path.expanduser("~/.vibrante_node_config.json")
    _data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    self._data = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self._data = {}
        else:
            self._data = {}

    def _save(self):
        try:
            with open(self._config_path, "w") as f:
                json.dump(self._data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    # --- Generic key/value helpers ---

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self._save()

    # --- Specific helpers ---

    def get_recent_files(self) -> list:
        return self._data.get("recent_files", [])

    def add_recent_file(self, path: str):
        recent = [p for p in self._data.get("recent_files", []) if p != path]
        recent.insert(0, path)
        self._data["recent_files"] = recent[:10]
        self._save()

    def clear_recent_files(self):
        self._data["recent_files"] = []
        self._save()

    def get_gemini_api_key(self) -> str:
        return self._data.get("gemini_api_key", "")

    def set_gemini_api_key(self, api_key: str):
        self._data["gemini_api_key"] = api_key
        self._save()

# Global singleton instance
config = ConfigManager()
