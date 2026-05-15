"""Tests for src/utils/env_manager.py.

All tests isolate state by:
  - patching config._data directly (avoids disk writes during test runs)
  - restoring sys.path and os.environ after each test
  - resetting the EnvManager singleton's _initialized flag
"""
import os
import sys
import pytest

from src.utils.config_manager import config
from src.utils.env_manager import env_manager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Snapshot and restore config._data, sys.path, os.environ around each test."""
    original_data = dict(config._data)
    original_path = list(sys.path)
    original_env = dict(os.environ)
    original_initialized = env_manager._initialized

    # Clear env keys so tests start clean
    config._data.pop("env.vibrante_pythonpath", None)
    config._data.pop("env.custom_variables", None)
    config._data.pop("env.v_nodes_dir", None)
    config._data.pop("env.v_scripts_path", None)
    # Also clear any env vars that might have been injected by previous tests
    os.environ.pop("v_nodes_dir", None)
    os.environ.pop("v_scripts_path", None)
    env_manager._initialized = False

    yield

    # Restore everything
    config._data.clear()
    config._data.update(original_data)
    sys.path[:] = original_path
    # Restore os.environ
    for k in list(os.environ):
        if k not in original_env:
            del os.environ[k]
    for k, v in original_env.items():
        os.environ[k] = v
    env_manager._initialized = original_initialized


# ---------------------------------------------------------------------------
# VIBRANTE_PYTHONPATH config accessors
# ---------------------------------------------------------------------------

def test_get_vibrante_pythonpath_empty():
    assert env_manager.get_vibrante_pythonpath() == []


def test_set_and_get_vibrante_pythonpath(tmp_path):
    d1 = str(tmp_path / "lib1")
    d2 = str(tmp_path / "lib2")
    os.makedirs(d1)
    os.makedirs(d2)

    env_manager.set_vibrante_pythonpath([d1, d2])
    result = env_manager.get_vibrante_pythonpath()
    assert result == [d1, d2]


def test_set_vibrante_pythonpath_strips_blanks(tmp_path):
    d = str(tmp_path / "lib")
    os.makedirs(d)
    env_manager.set_vibrante_pythonpath([d, "  ", ""])
    assert env_manager.get_vibrante_pythonpath() == [d]


def test_vibrante_pythonpath_legacy_string_format(tmp_path):
    """Legacy configs stored paths as an os.pathsep-joined string."""
    d1 = str(tmp_path / "a")
    d2 = str(tmp_path / "b")
    os.makedirs(d1)
    os.makedirs(d2)
    config._data["env.vibrante_pythonpath"] = os.pathsep.join([d1, d2])
    result = env_manager.get_vibrante_pythonpath()
    assert d1 in result
    assert d2 in result


# ---------------------------------------------------------------------------
# VIBRANTE_PYTHONPATH sys.path injection
# ---------------------------------------------------------------------------

def test_initialize_injects_valid_paths_into_sys_path(tmp_path):
    d = str(tmp_path / "mylib")
    os.makedirs(d)
    env_manager.set_vibrante_pythonpath([d])
    assert d not in sys.path  # not yet applied

    env_manager.initialize()
    assert d in sys.path


def test_initialize_skips_nonexistent_paths(tmp_path, capsys):
    missing = str(tmp_path / "does_not_exist")
    env_manager.set_vibrante_pythonpath([missing])
    env_manager.initialize()

    assert missing not in sys.path
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_initialize_does_not_duplicate_path(tmp_path):
    d = str(tmp_path / "dup")
    os.makedirs(d)
    sys.path.insert(0, d)  # already present
    env_manager.set_vibrante_pythonpath([d])
    env_manager.initialize()

    assert sys.path.count(d) == 1


def test_reinitialize_applies_newly_added_path(tmp_path):
    d = str(tmp_path / "newlib")
    os.makedirs(d)
    env_manager.initialize()  # no paths yet
    assert d not in sys.path

    env_manager.set_vibrante_pythonpath([d])
    env_manager.reinitialize()
    assert d in sys.path


# ---------------------------------------------------------------------------
# Custom variables accessors
# ---------------------------------------------------------------------------

def test_get_custom_variables_empty():
    assert env_manager.get_custom_variables() == {}


def test_set_and_get_custom_variables():
    env_manager.set_custom_variables({"STUDIO_ROOT": "/studio", "SHOW": "myshow"})
    result = env_manager.get_custom_variables()
    assert result == {"STUDIO_ROOT": "/studio", "SHOW": "myshow"}


def test_set_custom_variable_single():
    env_manager.set_custom_variable("MY_VAR", "hello")
    assert env_manager.get_custom_variable("MY_VAR") == "hello"


def test_remove_custom_variable():
    env_manager.set_custom_variables({"A": "1", "B": "2"})
    env_manager.remove_custom_variable("A")
    assert "A" not in env_manager.get_custom_variables()
    assert env_manager.get_custom_variables()["B"] == "2"


def test_remove_nonexistent_variable_is_noop():
    env_manager.set_custom_variables({"X": "1"})
    env_manager.remove_custom_variable("DOES_NOT_EXIST")  # must not raise
    assert env_manager.get_custom_variables() == {"X": "1"}


def test_get_custom_variable_missing_returns_none():
    assert env_manager.get_custom_variable("MISSING") is None


# ---------------------------------------------------------------------------
# Custom variables os.environ injection
# ---------------------------------------------------------------------------

def test_initialize_injects_custom_variables():
    env_manager.set_custom_variables({"VIBRANTE_TEST_VAR": "test_value_xyz"})
    env_manager.initialize()
    assert os.environ.get("VIBRANTE_TEST_VAR") == "test_value_xyz"


def test_reinitialize_injects_updated_variable():
    env_manager.initialize()
    env_manager.set_custom_variable("VIBRANTE_DYNAMIC_VAR", "v1")
    env_manager.reinitialize()
    assert os.environ.get("VIBRANTE_DYNAMIC_VAR") == "v1"

    env_manager.set_custom_variable("VIBRANTE_DYNAMIC_VAR", "v2")
    env_manager.reinitialize()
    assert os.environ.get("VIBRANTE_DYNAMIC_VAR") == "v2"


# ---------------------------------------------------------------------------
# Subprocess env helper
# ---------------------------------------------------------------------------

def test_apply_to_subprocess_env_includes_custom_vars():
    env_manager.set_custom_variables({"PROJ_ROOT": "/projects/foo"})
    result = env_manager.apply_to_subprocess_env({})
    assert result["PROJ_ROOT"] == "/projects/foo"


def test_apply_to_subprocess_env_includes_vibrante_pythonpath(tmp_path):
    d = str(tmp_path / "sublib")
    os.makedirs(d)
    env_manager.set_vibrante_pythonpath([d])
    result = env_manager.apply_to_subprocess_env({})
    assert "VIBRANTE_PYTHONPATH" in result
    assert d in result["VIBRANTE_PYTHONPATH"]


def test_apply_to_subprocess_env_does_not_mutate_os_environ():
    env_manager.set_custom_variables({"SUBPROCESS_TEST_VAR": "should_not_leak"})
    snapshot_before = dict(os.environ)
    env_manager.apply_to_subprocess_env()
    # os.environ must not have been mutated by the call itself
    assert os.environ == snapshot_before


def test_apply_to_subprocess_env_uses_base_env():
    base = {"BASE_VAR": "base_value"}
    env_manager.set_custom_variables({"EXTRA": "extra_value"})
    result = env_manager.apply_to_subprocess_env(base)
    assert result["BASE_VAR"] == "base_value"
    assert result["EXTRA"] == "extra_value"


def test_apply_to_subprocess_env_no_pythonpath_when_empty():
    env_manager.set_vibrante_pythonpath([])
    result = env_manager.apply_to_subprocess_env({})
    assert "VIBRANTE_PYTHONPATH" not in result


# ---------------------------------------------------------------------------
# v_nodes_dir accessors
# ---------------------------------------------------------------------------

def test_get_v_nodes_dir_empty():
    assert env_manager.get_v_nodes_dir() == []


def test_set_and_get_v_nodes_dir(tmp_path):
    d1 = str(tmp_path / "nodes1")
    d2 = str(tmp_path / "nodes2")
    os.makedirs(d1)
    os.makedirs(d2)
    env_manager.set_v_nodes_dir([d1, d2])
    assert env_manager.get_v_nodes_dir() == [d1, d2]


def test_set_v_nodes_dir_strips_blanks(tmp_path):
    d = str(tmp_path / "nodes")
    os.makedirs(d)
    env_manager.set_v_nodes_dir([d, "  ", ""])
    assert env_manager.get_v_nodes_dir() == [d]


def test_initialize_sets_v_nodes_dir_in_environ(tmp_path):
    d = str(tmp_path / "nodes")
    os.makedirs(d)
    env_manager.set_v_nodes_dir([d])
    env_manager.initialize()
    assert d in os.environ.get("v_nodes_dir", "")


def test_initialize_merges_v_nodes_dir_with_existing(tmp_path, monkeypatch):
    existing = str(tmp_path / "houdini_nodes")
    config_dir = str(tmp_path / "my_nodes")
    os.makedirs(existing)
    os.makedirs(config_dir)
    monkeypatch.setenv("v_nodes_dir", existing)
    env_manager.set_v_nodes_dir([config_dir])
    env_manager.initialize()
    result = os.environ.get("v_nodes_dir", "")
    assert existing in result
    assert config_dir in result


def test_initialize_does_not_duplicate_v_nodes_dir(tmp_path, monkeypatch):
    d = str(tmp_path / "nodes")
    os.makedirs(d)
    monkeypatch.setenv("v_nodes_dir", d)
    env_manager.set_v_nodes_dir([d])
    env_manager.initialize()
    result = os.environ.get("v_nodes_dir", "").split(os.pathsep)
    assert result.count(d) == 1


def test_v_nodes_dir_not_set_in_environ_when_empty():
    env_manager.set_v_nodes_dir([])
    env_manager.initialize()
    # Should not inject an empty string
    assert os.environ.get("v_nodes_dir", "") == ""


# ---------------------------------------------------------------------------
# v_scripts_path accessors
# ---------------------------------------------------------------------------

def test_get_v_scripts_path_empty():
    assert env_manager.get_v_scripts_path() == []


def test_set_and_get_v_scripts_path(tmp_path):
    d1 = str(tmp_path / "scripts1")
    d2 = str(tmp_path / "scripts2")
    os.makedirs(d1)
    os.makedirs(d2)
    env_manager.set_v_scripts_path([d1, d2])
    assert env_manager.get_v_scripts_path() == [d1, d2]


def test_set_v_scripts_path_strips_blanks(tmp_path):
    d = str(tmp_path / "scripts")
    os.makedirs(d)
    env_manager.set_v_scripts_path([d, "  ", ""])
    assert env_manager.get_v_scripts_path() == [d]


def test_initialize_sets_v_scripts_path_in_environ(tmp_path):
    d = str(tmp_path / "scripts")
    os.makedirs(d)
    env_manager.set_v_scripts_path([d])
    env_manager.initialize()
    assert d in os.environ.get("v_scripts_path", "")


def test_initialize_merges_v_scripts_path_with_existing(tmp_path, monkeypatch):
    existing = str(tmp_path / "houdini_scripts")
    config_dir = str(tmp_path / "my_scripts")
    os.makedirs(existing)
    os.makedirs(config_dir)
    monkeypatch.setenv("v_scripts_path", existing)
    env_manager.set_v_scripts_path([config_dir])
    env_manager.initialize()
    result = os.environ.get("v_scripts_path", "")
    assert existing in result
    assert config_dir in result


def test_initialize_does_not_duplicate_v_scripts_path(tmp_path, monkeypatch):
    d = str(tmp_path / "scripts")
    os.makedirs(d)
    monkeypatch.setenv("v_scripts_path", d)
    env_manager.set_v_scripts_path([d])
    env_manager.initialize()
    result = os.environ.get("v_scripts_path", "").split(os.pathsep)
    assert result.count(d) == 1


def test_v_scripts_path_not_set_in_environ_when_empty():
    env_manager.set_v_scripts_path([])
    env_manager.initialize()
    assert os.environ.get("v_scripts_path", "") == ""


# ---------------------------------------------------------------------------
# Subprocess env — v_nodes_dir and v_scripts_path
# ---------------------------------------------------------------------------

def test_apply_to_subprocess_env_includes_v_nodes_dir(tmp_path):
    d = str(tmp_path / "nodes")
    os.makedirs(d)
    env_manager.set_v_nodes_dir([d])
    result = env_manager.apply_to_subprocess_env({})
    assert "v_nodes_dir" in result
    assert d in result["v_nodes_dir"]


def test_apply_to_subprocess_env_includes_v_scripts_path(tmp_path):
    d = str(tmp_path / "scripts")
    os.makedirs(d)
    env_manager.set_v_scripts_path([d])
    result = env_manager.apply_to_subprocess_env({})
    assert "v_scripts_path" in result
    assert d in result["v_scripts_path"]


def test_apply_to_subprocess_env_no_v_nodes_dir_when_empty():
    env_manager.set_v_nodes_dir([])
    result = env_manager.apply_to_subprocess_env({})
    assert result.get("v_nodes_dir", "") == ""


def test_apply_to_subprocess_env_no_v_scripts_path_when_empty():
    env_manager.set_v_scripts_path([])
    result = env_manager.apply_to_subprocess_env({})
    assert result.get("v_scripts_path", "") == ""
