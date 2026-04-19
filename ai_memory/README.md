# Vibrante-Node — AI Project Memory

**Last updated:** 2026-04-19
**Current version:** v1.7.0
**Repository:** https://github.com/KamalTD/Vibrante-Node.git

---

## What Is This Directory?

This directory is the persistent memory system for AI-assisted development on Vibrante-Node.
It stores full project context so any AI agent — in any session, on any machine — can pick up exactly where the last session left off.

**Start every session by reading `project_state.json`.**

---

## Project Summary

Vibrante-Node is a visual node-based pipeline automation tool for VFX studios.
It connects **Prism Pipeline 2.1.0**, **Blender**, **Houdini**, **Maya**, and **Deadline Render Farm** through a drag-and-drop Qt node graph.

Nodes are defined as `.json` files in `nodes/`. The Python logic for each node lives inside the `python_code` field of that JSON. The execution engine (`src/core/engine.py`) loads, instantiates, and runs them.

---

## Current State

### Version: 1.7.0 — Released 2026-04-19

**Build:** Python 3.10.11 / PyInstaller 6.19.0
**Artifact:** `dist/Vibrante-Node/Vibrante-Node.exe`

### What shipped in v1.7.0

| Area | Change |
|---|---|
| `src/utils/prism_config.py` | NEW — dynamic pipeline.json reader, replaces all hardcoded dept dicts |
| `prism_get_scene_path` | NEW — resolves scene file path from entity + dept + task + app + version |
| `prism_get_export_path` | NEW — resolves export/render/playblast output paths |
| Entity enrichment | All shot nodes now emit full `{type, sequence, shot, path, location, paths}` |
| `prism_get_departments` | Config-driven from pipeline.json, added `abbreviations` + `default_tasks` outputs |
| `prism_get_tasks` | Disk scan fallback, removed crashing `getTaskNames` call |
| `prism_get_scene_files` | Disk scanner for `Scenefiles/<dept>/<task>/` |
| `prism_get_sequences_by_project` | Now outputs `{name, project_path, project_name}` dicts, not strings |
| `prism_get_shots` + `_by_sequence` | Fixed `getShots()` unpack crash |
| 12 misc nodes | `None` outputs → safe `{}` or `""` defaults |
| `vibrante_node.spec` | Added `src.utils.prism_config` + `src.utils.prism_core` to hiddenimports |

---

## Architecture at a Glance

```
node_based_app/
├── src/
│   ├── main.py                  # Entry point
│   ├── core/
│   │   ├── engine.py            # Async graph executor
│   │   ├── graph.py             # Node graph model
│   │   └── registry.py          # Loads nodes from nodes/*.json
│   ├── nodes/
│   │   └── base.py              # BaseNode — all nodes inherit this
│   └── utils/
│       ├── prism_core.py        # resolve_prism_core() — global PrismCore cache
│       ├── prism_config.py      # Dynamic pipeline.json reader (NEW v1.7.0)
│       ├── hou_bridge.py        # TCP bridge to live Houdini session
│       └── qt_compat.py         # Qt5/Qt6 shim for Prism compatibility
├── nodes/                       # ~140 node JSON definitions
├── workflows/                   # Saved workflow examples
├── plugins/houdini/             # Houdini bridge plugin
├── icons/                       # UI icons including prism_icon.png
├── vibrante_node.spec           # PyInstaller build spec
├── build_py310.bat              # Build script (Python 3.10)
└── ai_memory/                   # ← You are here
    ├── README.md                # This file
    └── project_state.json       # Full structured memory
```

---

## Node Categories

| Category | Count | Notes |
|---|---|---|
| Prism | 61 | Full Prism 2.1.0 integration. See prism_integration section in project_state.json |
| Blender | ~17 | headless executor + action builder pattern |
| Houdini | ~13 | headless + live TCP bridge |
| Maya | ~20 | mayapy headless executor |
| Deadline | 4 | blender/houdini/maya submit + job_status |
| Logic | ~10 | if, for, while, compare, logical_gate |
| Data/Util | ~20 | dict, list, string, math, filesystem |

---

## Critical Rules (Learn These First)

### 1. Never hardcode department abbreviations
```python
# WRONG
DEPT_ABBREVS = {'animation': 'anm', 'lighting': 'lgt'}

# RIGHT
from src.utils.prism_config import get_departments, resolve_dept_folder
dept_defs = get_departments(core, cfg_path, entity_type)
abbrev = resolve_dept_folder(dept_input, dept_defs)
```

### 2. Entity dicts must be fully enriched
Shot entities need: `type, sequence, shot, path, location, paths`
Asset entities need: `type, asset_path, path`
The `path` field is required — its absence causes all downstream Prism API calls to silently return empty.

### 3. getScenefiles() always returns empty — use disk scan
```python
# getScenefiles() is unreliable in standalone Python context
# Always fall back to scanning Scenefiles/<dept>/<task>/ directly
scenes_root = get_entity_scenefiles_root(entity, core, cfg_path)
```

### 4. getShots() unpack — always use try/except
```python
result = core.entities.getShots()
try:
    sequences, shots = result
except (TypeError, ValueError):
    shots = list(result or [])
    sequences = []
```

### 5. exec_in / exec_out — never add manually
`super().__init__()` on `use_exec=True` nodes adds them automatically.
Adding them again creates duplicates in the UI.

### 6. Python 3.10 f-strings
No same-quote characters inside `{}` expressions:
```python
# WRONG (Python 3.10)
f"value: {d['key']}"

# RIGHT
val = d['key']
f"value: {val}"
# or use double-outer / single-inner
f"value: {d.get('key')}"
```

---

## Prism API Known Issues

| Call | Status | Fix |
|---|---|---|
| `core.entities.getDepartments()` | Does not exist | Read `pipeline.json globals.departments_shot/asset` |
| `core.entities.getTaskNames()` | Crashes via BaseException | Removed — disk scan Scenefiles/<dept>/ |
| `core.entities.getScenefiles(entity)` | Returns empty | Disk scan Scenefiles/<dept>/<task>/ |
| `getEntityPath()` / `getShotPath()` | Do not exist | Use `entity.get('path')` |
| `core.entities.getCategories()` | Returns UI tabs, not depts | Do not use for dept listing |
| `core.entities.getShots()` | May return tuple or list | Always try/except unpack |

---

## Task Status

### Done (v1.7.0)
- Full Prism integration overhaul (entity enrichment, config-driven dept resolution, disk fallbacks)
- `prism_get_scene_path` and `prism_get_export_path` new nodes
- `src/utils/prism_config.py` dynamic config reader
- v1.7.0 build (Python 3.10 / PyInstaller 6.19) — EXE shipped
- v1.7.0 committed and pushed to main

### Pending
- Record YouTube tutorial for `example_workflow_prism_demo_02` (script complete)
- Implement batch shot submission workflow (for_loop over shots → deadline submit)
- Implement version bump automation workflow
- Implement project onboarding automation workflow
- Plan migration from `google.generativeai` to `google.genai` (package deprecated)
- Consider Python 3.11+ upgrade (3.10 EOL: 2026-10-04)

---

## How to Continue in a New Session

1. Read this file (`ai_memory/README.md`) for orientation
2. Read `ai_memory/project_state.json` for full technical detail
3. Check `tasks.in_progress` — resume from there
4. Check `tasks.pending` — pick highest priority item
5. Before writing any code: grep the codebase, check established patterns in `project_state.json`
6. After every meaningful change: update `project_state.json` (last_updated, tasks, known_issues)
