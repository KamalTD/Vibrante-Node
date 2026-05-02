# Release v1.1.5: SideFX Houdini Live Integration, Command Bridge & App Icon

## Overview

Version 1.1.5 introduces a deep integration with **SideFX Houdini FX** via a Live Command Bridge architecture, 19 new Houdini-specific nodes, a Qt compatibility layer, and a custom application icon. This release transforms Vibrante-Node into a DCC-connected pipeline tool capable of controlling live Houdini sessions.

---

## New Features

### SideFX Houdini Live Integration
A complete plugin system for SideFX Houdini FX (tested with 20.5.278):

- **JSON-RPC Command Server** (`vibrante_hou_server.py`): Runs inside Houdini's Python process on `127.0.0.1:18811`. Supports 22 commands for scene manipulation, parameter control, animation, and code execution. All scene-modifying commands are dispatched to Houdini's main thread via `hdefereval.executeDeferred()` for thread safety.
- **Bridge Client** (`src/utils/hou_bridge.py`): `HouBridge` class provides a high-level API for communicating with the Houdini server. Accessed via `get_bridge()` singleton with `is_available()` health check.
- **Houdini Shelf & Menu**: Custom shelf tool and menu bar entry for launching Vibrante-Node directly from Houdini.
- **Auto-Configuration**: `setup_env()` configures Python paths and bundled virtual environment automatically on launch.
- **Bundled Virtual Environment**: Dependencies (pydantic, etc.) are packaged in `plugins/houdini/houdini/scripts/python/env/` to avoid modifying Houdini's Python installation.

### 19 Houdini Node Definitions
All nodes are JSON-defined, validated against the pydantic `NodeDefinitionJSON` model, and categorized under "Houdini" in the Node Library:

| Node | Description |
| :--- | :--- |
| `hou_create_node` | Create a node in the Houdini scene |
| `hou_create_geo` | Create a Geometry container at /obj |
| `hou_delete_node` | Delete a node by path |
| `hou_set_parm` | Set a single parameter |
| `hou_get_parm` | Read a parameter value |
| `hou_set_parms` | Set multiple parameters (JSON dict) |
| `hou_connect_nodes` | Wire two nodes together |
| `hou_cook` | Force-cook a node |
| `hou_run_code` | Execute Python code in Houdini |
| `hou_scene_info` | Query scene metadata (filename, frame, FPS) |
| `hou_node_info` | Get detailed info about a specific node |
| `hou_list_children` | List child nodes of a path |
| `hou_node_exists` | Check if a node path exists |
| `hou_set_display_flag` | Toggle display flag |
| `hou_set_expression` | Set a channel expression |
| `hou_set_keyframe` | Set a keyframe value |
| `hou_set_frame` | Jump to a timeline frame |
| `hou_save_hip` | Save the .hip file |
| `hou_layout_children` | Auto-layout network children |

### Houdini Example Scripts
Three example scripts in `plugins/houdini/v_scripts_houdini/`:
- `hou_scene_info.py` — Query scene metadata via the bridge.
- `hou_create_box_demo.py` — Create a Geometry container with a Box SOP.
- `hou_list_scene_nodes.py` — List all children under `/obj`.

### Application Icon
- Custom application icon (`icons/vibrante-node-icon.png`) displayed in the taskbar, title bar, splash screen, and window switcher via `app.setWindowIcon()`.

### Qt Compatibility Layer
- New `src/utils/qt_compat.py` module for unified imports across PyQt5 and PySide2.
- Handles `QPolygonF`, `QPointF`, and other types that differ between Qt bindings.

---

## Architecture Changes

### Subprocess-Only Launch Mode
- **In-process mode removed**: `launch_inprocess()` now delegates to `launch()` (subprocess mode) to prevent Houdini Signal 11 segfaults caused by competing Qt event loops (PyQt5 vs PySide2).
- All launch modes (shelf button, menu, scripts) use subprocess execution exclusively.

### Plugin Directory Structure
```
plugins/houdini/
├── houdini/                          # Installed to Houdini user prefs
│   ├── toolbar/vibrante.shelf        # Shelf tool definition
│   ├── mainmenu/vibrante.xml         # Menu bar integration
│   └── scripts/python/
│       ├── vibrante_node_houdini.py  # Entry point (launch, setup_env)
│       ├── vibrante_hou_server.py    # JSON-RPC command server (22 cmds)
│       └── env/                      # Bundled venv (pydantic, etc.)
├── v_nodes_houdini/                  # 19 Houdini node definitions
└── v_scripts_houdini/                # Example scripts
```

---

## Command Server Protocol

The command server uses a simple JSON-RPC protocol over TCP:

```json
{"command": "create_node", "args": {"parent": "/obj", "type": "geo", "name": "my_geo"}}
```

Response:
```json
{"status": "ok", "result": "/obj/my_geo"}
```

Error:
```json
{"status": "error", "error": "Node not found: /obj/missing"}
```

---

## Files Added
- `plugins/houdini/houdini/scripts/python/vibrante_hou_server.py` — JSON-RPC command server
- `src/utils/hou_bridge.py` — Bridge client for Houdini communication
- `src/utils/qt_compat.py` — Qt compatibility layer
- `plugins/houdini/v_nodes_houdini/*.json` — 19 Houdini node definitions
- `plugins/houdini/v_scripts_houdini/*.py` — 3 example Houdini scripts
- `icons/vibrante-node-icon.png` — Application icon

## Files Changed
- `src/main.py` — Version bump to v1.1.5, application icon setup
- `src/ui/window.py` — About dialog updated to v1.1.5
- `plugins/houdini/houdini/scripts/python/vibrante_node_houdini.py` — Added `_ensure_command_server()`, subprocess-only mode
- `README.md` — Houdini integration section, updated project structure
- `DOCUMENTATION.md` — Added Houdini technical reference (Section 4)
- `USER_GUIDE.md` — Added Houdini setup and usage guide
- `DEVELOPER.md` — Added Houdini architecture documentation

---

**Branch:** `feature/topological-engine-and-foreach-improvements`
