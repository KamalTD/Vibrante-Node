# Vibrante-Node v1.6.0 — Release Notes

**Release Date:** 2026-04-18
**Branch:** `feature/python-script-while-loop-nodes`

---

## Overview

v1.6.0 is a major feature release that introduces full **Prism Pipeline integration**, a **Python Script node** with an in-UI editor, a **While Loop** node, a library of **utility nodes** for lists, dicts, and strings, and several engine and Qt compatibility fixes.

---

## New Features

### 🎬 Prism Pipeline Integration

Full integration with the [Prism Pipeline](https://prism-pipeline.com/) studio management system.

**40+ new nodes** in the `Prism` category:

| Group | Nodes |
|---|---|
| Core | `prism_core_init`, `prism_core_info` |
| Entities | `prism_get_assets`, `prism_get_shots`, `prism_build_entity`, `prism_create_entity` |
| Products | `prism_get_products`, `prism_get_product_versions`, `prism_create_product_version`, `prism_get_latest_product_path`, `prism_import_product` |
| Media | `prism_get_media`, `prism_get_media_versions`, `prism_create_playblast` |
| Scenes | `prism_get_current_scene`, `prism_get_scene_files`, `prism_get_preset_scenes`, `prism_open_scene`, `prism_save_scene_version`, `prism_create_scene_from_preset` |
| Config | `prism_get_config`, `prism_set_config`, `prism_get_project_config_path` |
| Projects | `prism_list_projects`, `prism_create_project`, `prism_change_project` |
| Departments/Tasks | `prism_get_departments`, `prism_get_tasks`, `prism_create_category` |
| Plugins | `prism_list_plugins`, `prism_get_plugin`, `prism_add_integration` |
| USD | `prism_usd_entity_path`, `prism_usd_department_layer_path`, `prism_usd_sublayer_path`, `prism_usd_update_department_layer`, `prism_usd_update_sublayer` |
| Advanced | `prism_eval`, `prism_monkey_patch`, `prism_register_callback`, `prism_trigger_callback`, `prism_popup`, `prism_send_cmd`, `prism_login_token`, `prism_studio_assign_project` |

**Auto-bootstrap**: Place a `prism_core_init` node in any graph. Before execution begins, the engine detects it and initializes PrismCore on the Qt main thread without any manual wiring or code.

**Zero-wiring core access**: All `prism_*` nodes automatically resolve the shared `PrismCore` instance from a global cache (`src/utils/prism_core.py`) — the `core` output of `prism_core_init` does not need to be wired to every subsequent node.

**Example workflow**: `workflows/example_workflow_prism_demo.json` demonstrates a complete Prism session using several of the new nodes.

---

### 🐍 Python Script Node

- New `python_script` node with an **Edit Script** button that launches a full-featured in-UI code editor.
- The authored script is stored in the `python_code` parameter and persisted inside the workflow JSON.
- The engine injects `python_code` before execution so reloaded workflows always run the correct script.
- Scripts expose a `result` variable that maps to the node's `result` output port.

---

### 🔁 While Loop Node

- New `while_loop` builtin node: iterates an execution chain while a boolean `condition` input remains `True`.
- The engine's lock-free re-entrant execution (introduced in v1.0.5) makes while loops safe without deadlocks.

---

### 🧩 Utility Node Library

New general-purpose data-transformation nodes (all `use_exec: false`, reactive):

| Category | Node IDs |
|---|---|
| List | `create_list`, `get_list_item`, `list_length` |
| Dictionary | `create_dictionary`, `get_dict_value`, `set_dict_value` |
| String | `concat`, `split`, `replace`, `lowercase`, `uppercase`, `string_length` |

---

## Bug Fixes & Improvements

### Engine

- **Prism bootstrap phase**: The engine now scans for `prism_core_init` nodes before the main execution pass and calls `_bootstrap_prism_on_main_thread()` via Qt signal. This guarantees PrismCore is ready before any `prism_*` node runs.
- **Workflow parameter injection** (carried forward from branch): Node instances now receive workflow-saved parameters before execution, fixing saved `python_script` workflows that previously ran with an empty script.

### Registry

- **`_prepare_definition()` normalization**: Before compiling a JSON node definition, the registry automatically injects `from src.utils.prism_core import resolve_prism_core` and rewrites `core = inputs.get('core')` → `core = resolve_prism_core(inputs)` for all `prism_*` nodes. This is transparent to node authors.

### Qt Compatibility (`src/utils/qt_compat.py`)

- **`ensure_qcolor_from_string()`**: Adds `QColor.fromString` as a classmethod for Qt5 bindings that lack it. Called automatically at module import time.
- **`ensure_shiboken_stub()`**: Creates stub `shiboken2` / `shiboken6` modules to prevent Prism from loading incompatible binary wheels. Called automatically at module import time.

### UI (`src/ui/window.py`)

- **`_bootstrap_prism_on_main_thread()`**: New method called via Qt signal during execution startup. Extracts parameters from the `prism_core_init` node, calls `bootstrap_prism_core()`, and logs success or failure to the Event Log. Gracefully skips if PrismCore is already initialized.

### Removed Nodes

- `nodes/Get_Project.json` — superseded by `prism_list_projects` and `prism_change_project`.
- `nodes/Parse_Path.json` — superseded by the Prism path-resolution nodes.

---

## New Files

| File | Purpose |
|---|---|
| `src/utils/prism_core.py` | `store_prism_core`, `resolve_prism_core`, `bootstrap_prism_core` |
| `icons/prism_icon.png` | Icon for all Prism category nodes |
| `nodes/prism_*.json` | 40+ Prism node definitions |
| `workflows/example_workflow_prism_demo.json` | Example Prism Pipeline workflow |
| `RELEASE_v1.6.0.md` | This file |

---

## Upgrading from v1.5.0

No breaking changes. All v1.5.0 workflows load and run without modification.

To use Prism nodes:
1. Ensure Prism Pipeline is installed and configured on your machine.
2. Add a `prism_core_init` node to your graph and set the `prism_root` path.
3. All other `prism_*` nodes will automatically pick up the initialized core.

---

## Version

`src/main.py` — `VERSION = "v1.6.0"`
