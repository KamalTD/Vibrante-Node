# Release Notes — Vibrante-Node v1.8.0

**Release date:** 2026-04-23
**Build:** Python 3.10 / PyInstaller

---

## Overview

v1.8.0 is a stability and bugfix release focused on the VFX pipeline workflows. All known execution errors across the Maya, Houdini, Blender, Prism, and Deadline nodes have been resolved, and the engine has been hardened against edge-case crashes.

---

## Bug Fixes

### Engine
- **`result or {}` guard** — `NetworkExecutor` now protects `node_results.update(result)` against nodes that return `None` from `execute()`, preventing `TypeError: 'NoneType' object is not iterable` crashes.

### Flow Control
- **`for_loop`** — Was firing `exec_out` only once (last index). Now iterates correctly in a Python loop, calling `set_output('current_index', i)` then `set_output('exec_out', True)` per index.
- **`_executed_nodes` cache invalidation** — Pure data nodes are now discarded from the cache when their inputs change reactively, forcing them to recompute each loop iteration instead of serving stale results.
- **Bypass flag** — Bypassed nodes now correctly skip `execute()` and pass exec flow through to downstream nodes.

### Prism Nodes
- **`prism_get_export_path`**
  - Added `"3d"` and `"2d"` as valid `output_type` aliases (previously only `"3drender"` / `"2drender"` were recognised).
  - `version_path` output now returns the **full file path** of the first matching file inside the version directory, not the directory itself. Falls back to the directory path when no file exists yet.
  - Added new `version_dir` output for the directory path.
- **`prism_create_product_version`** — Data outputs (`version_path`, `success`) are now emitted via `set_output()` before `exec_out` fires, so downstream nodes receive values before continuing.
- **Prism shot/sequence getter nodes** — All six nodes (`prism_get_shots`, `prism_get_shots_by_sequence`, `prism_get_sequence_by_project`, `prism_get_sequences_by_project`, `prism_get_sequence_by_project`, `prism_get_shot_by_sequence`) updated to use Prism v2.1.0 flat-list `getShots()` API.

### Deadline Nodes
- **`deadline_job_status`** — Two bare `return` statements inside `execute()` replaced with `return {}` to prevent `NoneType` crashes in the engine.

### Houdini Nodes
- **`houdini_headless`**
  - Added upfront `os.path.isfile(hython)` check with a clear error message instead of the cryptic `[WinError 2]` when the executable path is wrong.
  - `import_alembic` context logic inverted: now defaults to `/obj` for any value except the explicit string `"/stage"`, preventing accidental LOP imports.
  - `import_obj` and `import_fbx` context checks hardened with the same inversion.
- **`houdini_action_import_alembic`** — Context value normalised with `(value or "/obj").strip()` to prevent `None` falling through to the `/stage` branch.

### Blender Nodes
- **`blender_headless`**
  - Fixed `SyntaxError: unterminated string literal` in the runner script: `'\n'` inside a triple-quoted Python string was being written as a real newline to the temp `.py` file. Replaced with `chr(10)`.
  - `bpy.ops.wm.alembic_export`: Blender 4+ renamed `frame_start`/`frame_end` to `start`/`end`. Runner now tries `start`/`end` first and falls back to the old names.
  - Added `os.makedirs(..., exist_ok=True)` before FBX, Alembic, and USD exports so missing output directories don't silently fail.

### UI
- **Delete / F key conflicts** — `keyPressEvent` in both `scene.py` and `view.py` now checks `QApplication.focusWidget()` and bails early if focus is on a text widget, preventing accidental node deletion or focus-fitting while typing in parameters, sticky notes, or backdrop titles.

---

## VFX Workflow Files

Six production VFX workflow templates added/updated under `vfx_workflows/`:

| File | Description |
|---|---|
| `01_prism_project_overview.json` | Project/shot/asset browser |
| `02_maya_asset_publish.json` | Maya headless asset publish to Prism |
| `03_multi_shot_alembic_export.json` | Multi-shot alembic export loop via Maya |
| `04_deadline_render_pipeline.json` | Deadline Maya render submission + job status polling |
| `05_houdini_fx_pipeline.json` | Houdini FX sim + Prism cache registration |
| `06_blender_multi_format_export.json` | Blender FBX / Alembic / USD multi-format export |
