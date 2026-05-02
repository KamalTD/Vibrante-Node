# Release Notes — Vibrante-Node v1.7.0

**Release date:** 2026-04-19
**Build:** Python 3.10 / PyInstaller 6.19

---

## Overview

v1.7.0 is a major Prism Pipeline integration overhaul. All Prism getter nodes have been audited and standardised, department/task/path resolution is now fully dynamic (read from the project's `pipeline.json`), and two new path-resolution nodes have been added.

---

## New Features

### `prism_get_scene_path`
Resolves the filesystem path for a scene file from entity + department + task + application + version inputs.
- Scans `Scenefiles/<dept>/<task>/` using the project's configured folder structure
- Filters by application extension (Blender → `.blend`, Houdini → `.hip`/`.hiplc`/`.hipnc`, Maya → `.ma`/`.mb`, Nuke → `.nk`, etc.)
- `version=latest` picks the highest `_v####` file; explicit version resolves exact match
- If no file exists, constructs the expected filename from Prism's template (`<seq>-<shot>_<task>_<version><ext>`)
- Outputs: `scene_path`, `task_path`, `version`, `exists`

### `prism_get_export_path`
Resolves output paths for exports, renders, and playblasts.
- `output_type`: `export` → `Export/`, `3drender` → `Renders/3dRender/`, `2drender` → `Renders/2dRender/`, `playblast` → `Playblasts/`
- Scans identifier folder for existing version directories; `version=latest` returns highest
- Outputs: `identifier_path`, `version_path`, `version`, `file_pattern`, `exists`
- `file_pattern` uses Prism naming: `<seq>-<shot>_<identifier>_<version>.####.exr`

### `src/utils/prism_config.py` — Dynamic Project Config Reader
New shared utility replacing all hardcoded department abbreviation dictionaries.
- Reads `globals.departments_shot` / `globals.departments_asset` from `pipeline.json`
- Config discovery: entity `path` walk-up → `project['configPath']` → core's current project → user Prism2 dir
- Respects `PRISM_LAUNCHER_CONFIG` environment variable for non-standard installs
- API: `get_departments()`, `resolve_dept_folder()`, `resolve_dept_name()`, `get_entity_scenefiles_root()`, `build_abbrev_map()`
- `versionPadding` read from project globals for correct `v0001`/`v0004` formatting

### `prism_get_departments` — New Outputs
- Added `default_tasks` output: list of default task names per department (from `pipeline.json`)
- Added `abbreviations` output: raw folder names (`anm`, `cfx`, …) alongside full names

---

## Bug Fixes

### Entity dict enrichment — `path`/`location`/`paths` fields
`prism_get_shot_by_sequence` and `prism_get_shot_by_name` previously emitted a minimal entity dict `{type, sequence, shot}`. Prism's `getScenefiles()` silently returns empty without the `path` field. All shot-outputting nodes now emit the full dict:
```json
{"type": "shot", "sequence": "seq_0001", "shot": "shot_001",
 "path": "G:/Prism/.../shot_001", "location": "global", "paths": [...]}
```

### `prism_get_scene_files` — Disk fallback
`getScenefiles()` returns empty even with a correctly enriched entity. Added disk scanner that reads `Scenefiles/<dept>/<task>/` directly, filters out `*versioninfo.json` and `*preview.jpg`, sorts by version, and returns file dicts with `path`, `version`, `task`, `department`.

### `prism_get_departments` — Wrong data source
Was calling `getCategories()` which returns Prism UI tabs (Scenefiles/Renders/Exports) not departments. Fixed to read from `pipeline.json` globals first, then scan `Scenefiles/` as fallback.

### `prism_get_tasks` — Crash on `getTaskNames`
Prism's decorator re-raises exceptions as `BaseException`, bypassing `except Exception`. Removed the broken `getTaskNames` fallback. Tasks are now resolved via disk scan of `Scenefiles/<dept>/` with config-driven abbreviation mapping.

### Department resolution — All nodes
Removed hardcoded `DEPT_ABBREVS` dictionaries from `prism_get_tasks`, `prism_get_entity_path`, `prism_get_scene_files`. All nodes now use `prism_config.resolve_dept_folder()` which reads the actual project's department list.

### `prism_get_entity_info` — Missing `path` output
Added `path` output port that passes through `entity['path']` for downstream nodes.

### `prism_get_shot_info` — Broken `getEntityPath` call
Removed calls to non-existent `getEntityPath`/`getShotPath` API methods. `entity_path` now reads directly from `entity.get('path')`.

### `prism_get_sequences_by_project` — Inconsistent output type
Was outputting a list of strings. Now outputs a list of dicts `{name, project_path, project_name}` matching the shape expected by `prism_get_shot_by_sequence`.

### Audit: None defaults
12 nodes (`prism_get_media_versions`, `prism_get_product_versions`, `prism_get_plugin`, `prism_import_product`, `prism_send_cmd`, `prism_trigger_callback`, `prism_eval`, `prism_register_callback`, and others) returned `None` for output ports on error. Changed to safe empty defaults (`{}` or `""`).

### `prism_core_info` — Runtime crash
Removed stray `exec_out` emission on a `use_exec=False` node.

### `prism_build_entity` / `prism_create_entity` — Incomplete entity dicts
Shot entities now include `path`, `location`, `paths`; asset entities include `path`.

### `prism_get_shots` — `getShots()` unpack crash
`sequences, shots = core.entities.getShots()` crashes when Prism returns a single list after `changeProject()`. Fixed with try/except unpack pattern across all affected nodes.

---

## Nodes Changed

| Node | Change |
|---|---|
| `prism_get_shot_by_sequence` | Entity enrichment: path/location/paths |
| `prism_get_shot_by_name` | Entity enrichment: path/location/paths |
| `prism_get_departments` | Config-driven, added abbreviations + default_tasks outputs |
| `prism_get_tasks` | Config-driven, disk fallback, removed crashing getTaskNames |
| `prism_get_scene_files` | Disk fallback scanner |
| `prism_get_entity_path` | Config-driven dept resolution |
| `prism_get_entity_info` | Added path output |
| `prism_get_shot_info` | Uses entity.path directly |
| `prism_get_sequences_by_project` | Outputs sequence dicts not strings |
| `prism_get_shots` | getShots unpack fix |
| `prism_get_shots_by_sequence` | getShots unpack fix |
| `prism_get_asset_by_name` | Asset entity includes path |
| `prism_get_scene_files` | DEPT_ABBREVS → prism_config |
| `prism_core_info` | Remove stray exec_out |
| `prism_build_entity` | Full entity dict fields |
| `prism_create_entity` | Full entity dict fields |
| `prism_get_current_scene` | Full entity dict reconstruction |
| 12× misc nodes | None → safe empty defaults |
