"""
Dynamic Prism project configuration reader.

Reads department definitions, folder structure, and task presets directly
from the project's pipeline.json — no hardcoded abbreviations.

Config discovery order:
  1. Explicit cfg_path argument
  2. Walk up from entity['path'] to find 00_Pipeline/pipeline.json
  3. project['configPath']
  4. core's currently loaded project
  5. User config at %USERPROFILE%/Documents/Prism2 (Windows) or ~/Documents/Prism2
"""

import os
import json


# ---------------------------------------------------------------------------
# Config file discovery
# ---------------------------------------------------------------------------

def get_prism_user_dir():
    launcher = os.environ.get("PRISM_LAUNCHER_CONFIG", "")
    if launcher and os.path.exists(launcher):
        return os.path.dirname(launcher)
    return os.path.join(os.path.expanduser("~"), "Documents", "Prism2")


def find_pipeline_cfg(start_path):
    """Walk up from start_path until 00_Pipeline/pipeline.json is found."""
    if not start_path:
        return None
    current = os.path.abspath(start_path)
    for _ in range(12):
        cfg = os.path.join(current, "00_Pipeline", "pipeline.json")
        if os.path.exists(cfg):
            return cfg
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def cfg_from_entity(entity):
    return find_pipeline_cfg(entity.get("path", "")) if isinstance(entity, dict) else None


def cfg_from_project(project):
    return project.get("configPath", "") if isinstance(project, dict) else ""


def cfg_from_core(core):
    """Try to get the current project's pipeline.json from a live PrismCore."""
    try:
        path = core.projects.getRecentPrjPath() or ""
        if path:
            cfg = find_pipeline_cfg(path)
            if cfg:
                return cfg
    except Exception:
        pass
    try:
        cfg = core.getConfig("globals", "config_path") or ""
        if cfg and os.path.exists(cfg):
            return cfg
    except Exception:
        pass
    return None


def resolve_cfg(core=None, entity=None, project=None, cfg_path=None):
    """Return the best available pipeline.json path, or None."""
    if cfg_path and os.path.exists(cfg_path):
        return cfg_path
    if entity:
        p = cfg_from_entity(entity)
        if p:
            return p
    if project:
        p = cfg_from_project(project)
        if p and os.path.exists(p):
            return p
    if core:
        p = cfg_from_core(core)
        if p:
            return p
    return None


# ---------------------------------------------------------------------------
# pipeline.json reader
# ---------------------------------------------------------------------------

def read_pipeline_json(cfg_path):
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _getconfig(core, category, key, cfg_path):
    """Thin wrapper around core.getConfig that swallows all errors."""
    try:
        return core.getConfig(category, key, configPath=cfg_path)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Department API
# ---------------------------------------------------------------------------

def get_departments(core, cfg_path, entity_type="shot"):
    """
    Return list of dicts: [{name, abbreviation, defaultTasks}, ...]
    entity_type: 'shot' | 'asset'
    """
    key = f"departments_{entity_type}"

    # 1. Direct JSON read (fastest, most reliable)
    if cfg_path and os.path.exists(cfg_path):
        data = read_pipeline_json(cfg_path)
        depts = data.get("globals", {}).get(key)
        if depts and isinstance(depts, list):
            return _normalise_dept_list(depts)

    # 2. core.getConfig
    if core and cfg_path:
        depts = _getconfig(core, "globals", key, cfg_path)
        if depts and isinstance(depts, list):
            return _normalise_dept_list(depts)

    return []


def _normalise_dept_list(raw):
    """Ensure each entry has name, abbreviation, defaultTasks."""
    result = []
    for item in raw:
        if isinstance(item, dict):
            result.append({
                "name": item.get("name", item.get("abbreviation", "")),
                "abbreviation": item.get("abbreviation", item.get("name", "")).lower(),
                "defaultTasks": item.get("defaultTasks", []),
            })
        elif isinstance(item, str):
            result.append({"name": item, "abbreviation": item.lower(), "defaultTasks": []})
    return result


def build_abbrev_map(depts):
    """
    Build {abbreviation_or_name_lower -> dept_dict} lookup from get_departments() output.
    Both the abbreviation and the full name resolve to the same dict.
    """
    mapping = {}
    for d in depts:
        mapping[d["abbreviation"]] = d
        mapping[d["name"].lower()] = d
    return mapping


def resolve_dept_folder(dept_input, depts):
    """
    Given user input (e.g. 'Animation' or 'anm') and a depts list,
    return the abbreviation (folder name) or None.
    """
    abbrev_map = build_abbrev_map(depts)
    entry = abbrev_map.get(dept_input.lower())
    return entry["abbreviation"] if entry else None


def resolve_dept_name(folder_name, depts):
    """Given a folder abbreviation (e.g. 'anm'), return the full name ('Animation')."""
    abbrev_map = build_abbrev_map(depts)
    entry = abbrev_map.get(folder_name.lower())
    return entry["name"] if entry else folder_name.title()


# ---------------------------------------------------------------------------
# Folder structure API
# ---------------------------------------------------------------------------

_SCENEFILES_KEYS = ("scenesFolder", "scenefilesFolder", "sceneFolder", "pipeline_folder")


def get_scenefiles_folder_name(core, cfg_path):
    """Returns the Scenefiles folder name configured for this project."""
    if cfg_path and os.path.exists(cfg_path):
        data = read_pipeline_json(cfg_path)
        g = data.get("globals", {})
        for key in _SCENEFILES_KEYS:
            val = g.get(key)
            if val:
                return val
        if core:
            for key in _SCENEFILES_KEYS:
                val = _getconfig(core, "globals", key, cfg_path)
                if val:
                    return val
    return "Scenefiles"


def get_entity_scenefiles_root(entity, core=None, cfg_path=None):
    """
    Returns the Scenefiles folder path for a given entity, or None.
    Combines entity['path'] + configured folder name.
    """
    entity_path = entity.get("path", "") if isinstance(entity, dict) else ""
    if not entity_path:
        return None
    if cfg_path is None:
        cfg_path = cfg_from_entity(entity)
    folder_name = get_scenefiles_folder_name(core, cfg_path)
    # Try exact name first, then case-insensitive scan
    exact = os.path.join(entity_path, folder_name)
    if os.path.isdir(exact):
        return exact
    try:
        for entry in os.scandir(entity_path):
            if entry.is_dir() and entry.name.lower() == folder_name.lower():
                return entry.path
    except OSError:
        pass
    return None
