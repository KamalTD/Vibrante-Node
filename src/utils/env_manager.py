import os
import sys
import threading
from typing import Dict, List, Optional

from src.utils.config_manager import config


class EnvManager:
    """Centralized environment variable and Python path manager.

    Loads persisted settings from config and applies them to the current
    process at startup. Also provides helpers for subprocess propagation.

    Config keys:
      env.vibrante_pythonpath  — List[str] of extra sys.path entries
      env.v_nodes_dir          — List[str] of extra node directories
      env.v_scripts_path       — List[str] of extra script directories
      env.custom_variables     — Dict[str, str] of user-defined env vars
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize(self):
        """Apply all persisted environment settings to the current process.

        Safe to call multiple times (idempotent for already-applied paths).
        """
        with self._lock:
            self._apply_vibrante_pythonpath()
            self._apply_general_path_vars()
            self._apply_custom_variables()
            self._initialized = True

    def reinitialize(self):
        """Re-apply settings after they have been changed at runtime."""
        with self._lock:
            self._apply_vibrante_pythonpath()
            self._apply_general_path_vars()
            self._apply_custom_variables()

    # ------------------------------------------------------------------
    # Internal apply helpers
    # ------------------------------------------------------------------

    def _apply_vibrante_pythonpath(self):
        paths = self.get_vibrante_pythonpath()
        for p in paths:
            if not p:
                continue
            if not os.path.isdir(p):
                print(f"[EnvManager] Warning: VIBRANTE_PYTHONPATH path not found: {p}")
                continue
            if p not in sys.path:
                sys.path.insert(0, p)
                print(f"[EnvManager] VIBRANTE_PYTHONPATH: added {p}")

    def _apply_general_path_vars(self):
        self._merge_env_path_list("v_nodes_dir", self.get_v_nodes_dir())
        self._merge_env_path_list("v_scripts_path", self.get_v_scripts_path())

    def _merge_env_path_list(self, env_key: str, config_paths: List[str]):
        """Merge config_paths into os.environ[env_key], preserving existing entries."""
        existing = [
            p.strip()
            for p in os.environ.get(env_key, "").split(os.pathsep)
            if p.strip()
        ]
        additions = [p for p in config_paths if p and p not in existing]
        merged = existing + additions
        if merged:
            os.environ[env_key] = os.pathsep.join(merged)
            for p in additions:
                print(f"[EnvManager] {env_key}: added {p}")
        elif env_key in os.environ:
            # existing was set but config_paths is empty — leave it alone
            pass

    def _apply_custom_variables(self):
        custom = config.get("env.custom_variables", {})
        if not isinstance(custom, dict):
            return
        for name, value in custom.items():
            if name and isinstance(name, str):
                os.environ[name] = str(value)
                print(f"[EnvManager] Custom variable set: {name}")

    # ------------------------------------------------------------------
    # VIBRANTE_PYTHONPATH accessors
    # ------------------------------------------------------------------

    def get_vibrante_pythonpath(self) -> List[str]:
        """Return the list of extra Python paths as stored in config."""
        return self._path_list_from_config("env.vibrante_pythonpath")

    def set_vibrante_pythonpath(self, paths: List[str]):
        """Persist the list of extra Python paths."""
        config.set("env.vibrante_pythonpath", [str(p).strip() for p in paths if str(p).strip()])

    # ------------------------------------------------------------------
    # v_nodes_dir accessors
    # ------------------------------------------------------------------

    def get_v_nodes_dir(self) -> List[str]:
        """Return the list of extra node directories as stored in config."""
        return self._path_list_from_config("env.v_nodes_dir")

    def set_v_nodes_dir(self, paths: List[str]):
        """Persist the list of extra node directories."""
        config.set("env.v_nodes_dir", [str(p).strip() for p in paths if str(p).strip()])

    # ------------------------------------------------------------------
    # v_scripts_path accessors
    # ------------------------------------------------------------------

    def get_v_scripts_path(self) -> List[str]:
        """Return the list of extra script directories as stored in config."""
        return self._path_list_from_config("env.v_scripts_path")

    def set_v_scripts_path(self, paths: List[str]):
        """Persist the list of extra script directories."""
        config.set("env.v_scripts_path", [str(p).strip() for p in paths if str(p).strip()])

    def _path_list_from_config(self, key: str) -> List[str]:
        raw = config.get(key, [])
        if isinstance(raw, str):
            return [p.strip() for p in raw.split(os.pathsep) if p.strip()]
        if isinstance(raw, list):
            return [str(p).strip() for p in raw if str(p).strip()]
        return []

    # ------------------------------------------------------------------
    # Custom variable accessors
    # ------------------------------------------------------------------

    def get_custom_variables(self) -> Dict[str, str]:
        """Return all user-defined custom environment variables."""
        val = config.get("env.custom_variables", {})
        return dict(val) if isinstance(val, dict) else {}

    def set_custom_variables(self, variables: Dict[str, str]):
        """Persist all user-defined custom environment variables."""
        config.set("env.custom_variables", {str(k): str(v) for k, v in variables.items()})

    def get_custom_variable(self, name: str) -> Optional[str]:
        return self.get_custom_variables().get(name)

    def set_custom_variable(self, name: str, value: str):
        variables = self.get_custom_variables()
        variables[name] = value
        self.set_custom_variables(variables)

    def remove_custom_variable(self, name: str):
        variables = self.get_custom_variables()
        variables.pop(name, None)
        self.set_custom_variables(variables)

    # ------------------------------------------------------------------
    # Settings file import / export
    # ------------------------------------------------------------------

    def export_settings(self) -> dict:
        """Return all managed settings as a plain dict suitable for JSON serialization."""
        return {
            "vibrante_pythonpath": self.get_vibrante_pythonpath(),
            "v_nodes_dir": self.get_v_nodes_dir(),
            "v_scripts_path": self.get_v_scripts_path(),
            "custom_variables": self.get_custom_variables(),
        }

    def import_settings(self, data: dict):
        """Apply settings from a previously exported dict and persist to config.

        Unknown keys are silently ignored for forward-compatibility.
        """
        if "vibrante_pythonpath" in data:
            val = data["vibrante_pythonpath"]
            if isinstance(val, list):
                self.set_vibrante_pythonpath(val)
        if "v_nodes_dir" in data:
            val = data["v_nodes_dir"]
            if isinstance(val, list):
                self.set_v_nodes_dir(val)
        if "v_scripts_path" in data:
            val = data["v_scripts_path"]
            if isinstance(val, list):
                self.set_v_scripts_path(val)
        if "custom_variables" in data:
            val = data["custom_variables"]
            if isinstance(val, dict):
                self.set_custom_variables(val)

    # ------------------------------------------------------------------
    # Subprocess helper
    # ------------------------------------------------------------------

    def apply_to_subprocess_env(self, base_env: Optional[Dict] = None) -> Dict[str, str]:
        """Return a subprocess-safe env dict with all managed variables applied.

        Does not mutate os.environ — returns a new dict.
        """
        env = dict(base_env if base_env is not None else os.environ)
        env.update(self.get_custom_variables())
        paths = self.get_vibrante_pythonpath()
        if paths:
            env["VIBRANTE_PYTHONPATH"] = os.pathsep.join(paths)
        self._merge_path_list_into_dict(env, "v_nodes_dir", self.get_v_nodes_dir())
        self._merge_path_list_into_dict(env, "v_scripts_path", self.get_v_scripts_path())
        return env

    def _merge_path_list_into_dict(self, env: Dict, key: str, config_paths: List[str]):
        """Merge config_paths into env[key] without mutating os.environ."""
        existing = [p.strip() for p in env.get(key, "").split(os.pathsep) if p.strip()]
        additions = [p for p in config_paths if p and p not in existing]
        merged = existing + additions
        if merged:
            env[key] = os.pathsep.join(merged)


# Global singleton instance — mirrors the config singleton pattern
env_manager = EnvManager()
