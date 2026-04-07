# Vibrante-Node - Technical API & Architecture Documentation

This document provides an exhaustive reference for the Vibrante-Node platform, covering core architecture, the custom node Scripting API, the Workflow Automation system, and the SideFX Houdini integration.

---

## 🚀 1. Core Application Architecture

### 🔹 Professional Python Code Editor
The Node Builder and Export Python dialog feature a fully-integrated, professional-grade source code editor:
- **Intelligent Syntax Highlighting**: Dracula-inspired theme for keywords, builtins, and multi-line strings.
- **Auto-Indentation & Linting**: Automatic 4-space indent after colons (`:`) and instant syntax error detection with gutter highlighting.
- **IntelliSense**: Rich completion suggestions for Python keywords and common node methods.
- **Bracket Matching & Auto-Closing**: Instant feedback for `()`, `[]`, and `{}`.

### 🔹 IDE-Style Export Dialog (v1.1.0)
The "Export Workflow as Python" dialog provides a full development environment:
- **Editable code** with the same CodeEditor used in the Node Builder.
- **Code execution** via `QProcess` with real-time stdout/stderr streaming.
- **AI-powered error fixing** using Google Gemini with accept/reject workflow.
- **Dracula-themed** toolbar, editor, output panel, and status bar.
- **Status bar** with cursor position (Ln/Col) and execution status.

### 🔹 High-Performance Execution Engine
- **Asynchronous Execution**: Uses a background `asyncio` loop to keep the UI responsive.
- **Topological Sorting**: Automatically determines execution order for data-only graphs.
- **Hybrid Flow + Data Model (v1.0.5)**:
    - **Flow-Based Routing**: Execution follows `exec` pins sequentially.
    - **Recursive Data Pulling**: Before any node executes, it recursively triggers upstream data-only nodes to ensure all inputs are current.
    - **Re-entrant Execution**: Fixed deadlocks in `NetworkExecutor` to allow nested flow calls (essential for Loops).
- **Recursive Data Propagation**: A live system that pushes parameter changes through the entire node chain instantly as the user interacts with the UI.
- **Zero-Delay Loop Execution (v1.1.0)**: All artificial `asyncio.sleep()` delays removed from ForEach, WhileLoop, and Sequence nodes.
- **Indexed Connection Lookups (v1.1.0)**: O(1) pre-calculated dict lookups replace O(N) connection scans in the output handler.
- **Cached Widget Resolution (v1.1.0)**: Node widget lookups use a dict cache during execution instead of linear scans.

### 🔹 Event Log System
- **Filtered Logging**: Filter by node name, level (Errors, Warnings, Info, Execution, Outputs).
- **Silent Mode (v1.1.0)**: Toggle to suppress all non-error messages with zero processing overhead for maximum execution speed.
- **Auto-Restore (v1.2.0)**: Disabling Silent Mode automatically re-enables previously filtered message categories (Info, Exec, Output).

### 🔹 Advanced Connection System
- **Bidirectional Dragging**: Start wires from either input or output ports.
- **Single-Input Enforcement**: Automatically replaces old wires when a new one is connected to an input port.
- **Redrag-to-Disconnect**: Seamlessly move existing wires by dragging them away from ports.
- **Animated Snapping (v1.2.0)**: Ports feature smooth scaling animations on hover and a "magnetic" snap effect when wires are dragged within 35 pixels.

### 🔹 Keyboard Shortcuts (v1.2.0)
| Shortcut | Action |
| :--- | :--- |
| `F5` | Run active workflow |
| `Shift + F5` | Stop workflow execution |
| `F` | Focus on selection |
| `Tab` | Open Quick Search popup |
| `Ctrl + C` / `Ctrl + V` | Copy / Paste nodes |
| `Ctrl + G` | Wrap selected nodes in a Network Box (Backdrop) |
| `Ctrl + B` | Toggle Bypass on selected nodes |
| `Delete` | Remove selected items |
| `Space + Drag` | Pan the canvas (Left Mouse) |

---

## 🏗️ 2. Part 1: Node Scripting API (`BaseNode`)

All custom nodes must inherit from the `BaseNode` class.

### 🔹 Class Attributes
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | The display name of the node in the library and canvas. |
| `category` | `str` | Logical grouping (e.g., "Math", "IO", "Logic"). |
| `description` | `str` | Tooltip/help text for the user. |
| `icon_path` | `str` | Path to an SVG/PNG icon. |

### 🔹 Configuration Methods
- **`self.add_input(name, data_type, widget_type, options)`**: Adds an input port. 
  - Supported widgets: `"text"`, `"text_area"`, `"int"`, `"float"`, `"bool"`, `"dropdown"`, `"slider"`, `"file"`, `"file_save"` (Save File dialog — new in v1.5.0), `"checkbox"`.
- **`self.add_output(name, data_type)`**: Adds an output port.
- **`self.add_parameter(name, type, default)`**: Defines internal data not linked to a port.

### 🔹 Data Access & Logging
- **`self.get_parameter(name)`** or **`self[name]`**: Safely retrieve current port/widget values.
- **`self.set_parameter(name, value)`**: Programmatically update a widget and trigger downstream sync.
- **`self.log_info(msg)`** / **`log_success`** / **`log_error`**: Thread-safe logging to the Event Log panel.

### 🔄 Lifecycle Hooks
- **`on_plug_sync(port_name, is_input, other_node, other_port_name)`**: (Sync) Called instantly on the GUI thread. Best for immediate data copying or UI updates.
- **`on_unplug_sync(port_name, is_input)`**: (Sync) Cleanup logic when a wire is removed.
- **`on_parameter_changed(name, value)`**: Triggered live as the user interacts with node widgets.
- **`async on_plug(...)` / `on_unplug(...)`**: (Async) Background triggers for heavy IO or network tasks.
- **`async def execute(self, inputs)`**: The main logic executed during a workflow run.

### 📖 Node Scripting Scenarios

#### Scenario A: Reactive Multi-Port Sync
```python
def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
    if is_input:
        data = other_node.get_parameter(other_port_name)
        self.set_parameter(port_name, data) # Sync UI immediately
        self.log_info(f"Connected to {other_node.name}")
```

#### Scenario B: Async Background Worker
```python
async def execute(self, inputs):
    self.log_info("Starting heavy calculation...")
    await asyncio.sleep(2.0) # Non-blocking sleep
    return {"result": inputs.get("val") * 10}
```

---

## 🤖 3. Part 2: Workflow Automation API

The built-in **Scripting Console** allows for full application automation using Python.

### 🔹 Available Globals
| Global | Type | Description |
| :--- | :--- | :--- |
| `app` | `MainWindow` | The main application instance. |
| `scene` | `NodeScene` | The active canvas/tab for node manipulation. |
| `registry` | `NodeRegistry` | Global registry of all available node types. |
| `git` | `GitWrapper` | Integrated source control management. |

### 🔹 Automation Methods
- **`scene.add_node_by_name(node_id, (x, y))`**: Spawn a node programmatically.
- **`scene.connect_nodes(node_a, port_a, node_b, port_b)`**: Create wires between ports.
- **`scene.clear()`**: Wipe the current workspace.
- **`app.add_new_workflow(name)`**: Create a new tab.
- **`app.execute_pipeline()`**: Trigger the workflow execution engine.

### 📖 Automation Scenarios

#### Scenario C: Pipeline Grid Generation
```python
# Create a grid of connected nodes
prev = None
for i in range(3):
    for j in range(3):
        curr = scene.add_node_by_name("message_node", (j*300, i*200))
        curr.set_parameter("msg", f"Auto-Node {i}-{j}")
        if prev: scene.connect_nodes(prev, "out", curr, "msg")
        prev = curr
```

#### Scenario D: Automated Batch Execution
```python
# Update input and run workflow programmatically
node = scene.find_node_by_name("Message Node")
if node:
    for val in ["Test A", "Test B", "Test C"]:
        node.set_parameter("msg", val)
        app.execute_pipeline()
```

---

## 🎬 4. Headless DCC Execution (v1.5.0)

Vibrante-Node ships two headless executor nodes that launch Maya (`mayapy.exe`) and Houdini (`hython.exe`) as subprocesses, run a list of structured "actions" against the DCC, and return the results. This is distinct from the live `hou_bridge` integration (Section 5) — it's designed for **batch processing**, **CI/render-farm use**, and **repeatable pipelines** where spinning up a short-lived DCC per run is the right model.

### 🔹 Architecture

1. **Action Nodes** — small chainable nodes, each describing one DCC operation (e.g. `Import OBJ`, `Export Alembic`). They expose `actions_in` / `actions_out` list ports and append a typed action dict to the list.
2. **Headless Executor Node** — `Maya Headless` or `Houdini Headless`. Validates the action list, serializes it to a temp JSON file, writes an embedded runner script to a second temp file, launches the DCC subprocess with both as arguments, reads the results JSON back, and maps success/failure per action.
3. **Runner Script** — a self-contained Python script that runs inside `mayapy`/`hython`, iterates the action list, dispatches each to a typed handler, and writes a per-action `{index, type, ok, error, info?}` dict into the results file.
4. **Get Action Result helper** — extracts a single action from `executed_actions` by type (first match) or index, exposing `action`, `info`, and a best-guess `path` field so downstream nodes don't have to filter the list manually.

### 🔹 Why Subprocess + Structured Payload?

- **No f-string injection** — action values are JSON-encoded, not interpolated into code.
- **Per-action isolation** — each action runs in its own try/except inside the runner; one failing action doesn't blank out the rest.
- **Success contract** — the executor only reports success when process returncode is 0 **and** no action-level errors were reported. DCC stderr warnings (which Maya emits even on successful runs) are informational.
- **Version-pinned** — each executor has a version dropdown that auto-fills the binary path (Maya: 2022/2024/2025/2026, Houdini: 20.5.445/20.5.278/20.0.547/19.5.493). Paths remain editable.
- **Custom env vars** — both executors accept a `.bat` file (parses `SET key=val` lines) and a `Maya.env` / `houdini.env` file, merged into the subprocess environment. `%VAR%` references are expanded against the current environment.

### 🔹 Maya Headless Node

**Inputs:** `maya_version` (dropdown), `mayapy.exe`, `bat_file`, `maya_env_file`, `scene_file`, `actions`
**Outputs:** `success`, `stdout`, `stderr`, `exit_code`, `executed_actions`, `skipped_actions`

**Supported action types:** `open_scene`, `new_scene`, `save_scene`, `scene_info`, `set_frame_range`, `import_obj`, `import_fbx`, `import_alembic`, `export_fbx`, `export_alembic`, `export_camera_alembic`, `import_camera`, `reference_scene`, `reference_alembic`, `list_references`, `playblast`, `bake_animation`, `set_render_settings`, `set_aovs`, `create_render_layer`, `assign_material`, `custom_python`.

**Renderer-specific support:**
- **AOVs**: Arnold (via `mtoa.core.createOptions()` + `mtoa.aovs.AOVInterface`) and Redshift (via `rsCreateAov`).
- **Render Layers**: Maya's `renderSetup` API.
- **Render Settings**: Resolution, frame range, image format (per-renderer mapping), file prefix.

### 🔹 Houdini Headless Node

**Inputs:** `houdini_version` (dropdown), `hython.exe`, `bat_file`, `houdini_env_file`, `hip_file`, `actions`
**Outputs:** `success`, `stdout`, `stderr`, `exit_code`, `executed_actions`, `skipped_actions`

**Supported action types:** `open_hip`, `save_hip`, `new_hip`, `scene_info`, `set_frame_range`, `import_obj`, `import_fbx`, `import_alembic`, `import_camera`, `export_fbx`, `export_alembic`, `export_camera_alembic`, `bake_animation`, `custom_python`.

**Import context:** Every import action takes an optional `context` parameter — `/obj` for the classic Object/SOP workflow, or `/stage` for Solaris/LOPs (creates SOP Import LOP, FBX Character Import LOP, Sublayer LOP, etc.).

### 🔹 Action Nodes at a Glance

| Category | Maya | Houdini |
|---|---|---|
| Scene IO | Open/Save/New Scene, Scene Info | Open/Save/New HIP, Scene Info |
| Frame | Set Frame Range | Set Frame Range |
| Geometry In | Import OBJ, Import FBX, Import Alembic | Import OBJ, Import FBX, Import Alembic |
| Geometry Out | Export FBX, Export Alembic | Export FBX, Export Alembic |
| References | Reference Scene, Reference Alembic, List References | — |
| Camera | Import Camera, Export Camera Alembic | Import Camera, Export Camera Alembic |
| Animation | Bake Animation | Bake Animation |
| Rendering | Playblast, Set Render Settings, Set AOVs, Create Render Layer, Assign Material | — |
| Extensibility | Custom Python (editable) | Custom Python (editable) |

### 🔹 New `file_save` Widget Type

Export action nodes use a new `"widget_type": "file_save"` on string ports, which opens a **Save File** dialog instead of an Open dialog. Implemented in `src/ui/node_widget.py` with the `QPushButton.clicked` bool-arg bug worked around via a defaulted `_checked=None` parameter.

### 🔹 Custom Python Action Nodes

`maya_action_custom` and `houdini_action_custom` are editable action nodes with a `python_code` text-area parameter and an **Edit Script** button wired into `node_widget.py`'s script-editor list. Duplicate one, click Edit Script, write your own code — the runner exposes `hou` / `cmds`, the action dict, and `os`/`json` to your code.

### 🔹 Get Action Result Helpers

`maya_get_action_result` and `houdini_get_action_result` take an `executed_actions` list and either an `action_type` string (first-match) or an `index`. They output:
- `found` (bool)
- `action` (dict) — the matched action
- `info` (dict) — convenience pointer to `action["info"]` for query actions (`scene_info`, `list_references`)
- `path` (string) — auto-picked from the first non-empty path-like field (`fbx_path`, `abc_path`, etc.)

---

## 🔥 5. SideFX Houdini Integration (v1.2.0)

Vibrante-Node provides a deep integration with SideFX Houdini FX via a **Live Command Bridge** architecture. This allows you to control a live Houdini session from within Vibrante-Node workflows.

### 🔹 Architecture Overview

The integration uses a client-server model:

1. **Command Server** (`vibrante_hou_server.py`): A JSON-RPC server that runs inside Houdini's Python process on `127.0.0.1:18811`. It dispatches commands to Houdini's main thread using `hdefereval` for thread-safe scene manipulation.
2. **Bridge Client** (`src/utils/hou_bridge.py`): A Python client (`HouBridge`) used by the Vibrante-Node engine to send commands to the Houdini server. It exposes a high-level API and is accessed via `get_bridge()` singleton.
3. **Houdini Node Definitions** (`plugins/houdini/v_nodes_houdini/`): 19 JSON-defined nodes that map directly to Houdini operations.

### 🔹 Command Server (22 Commands)

The server supports the following JSON-RPC commands:

| Command | Description |
| :--- | :--- |
| `ping` | Health check — returns `"pong"` |
| `create_node` | Create a Houdini node (parent, type, name) |
| `delete_node` | Delete a node by path |
| `set_parm` | Set a single parameter on a node |
| `get_parm` | Get a single parameter value |
| `set_parms` | Set multiple parameters at once |
| `get_parms` | Get multiple parameter values |
| `connect_nodes` | Connect two nodes (output → input) |
| `cook_node` | Force-cook a node |
| `run_code` | Execute arbitrary Python code in Houdini |
| `scene_info` | Get scene metadata (filename, frame, FPS, etc.) |
| `node_info` | Get detailed info about a specific node |
| `children` | List child nodes of a given path |
| `node_exists` | Check if a node path exists |
| `set_display_flag` | Set the display flag on a node |
| `set_render_flag` | Set the render flag on a node |
| `layout_children` | Auto-layout child nodes in the network editor |
| `save_hip` | Save the current .hip file |
| `set_expression` | Set a channel expression on a parameter |
| `set_keyframe` | Set a keyframe on a parameter |
| `set_frame` | Set the current timeline frame |
| `set_playback_range` | Set the timeline frame range |
| `call` | Execute ANY Houdini API method dynamically (`path`, `args`, `kwargs`) |
| `get_completions` | Fetch auto-complete suggestions for `hou` members |

### 🔹 Bridge Client API

```python
from src.utils.hou_bridge import get_bridge

bridge = get_bridge()
if bridge.is_available():
    result = bridge.create_node("/obj", "geo", "my_geo")
    bridge.set_parm("/obj/my_geo/tx", 5.0)
    info = bridge.scene_info()
```

### 🔹 Houdini Node Library (19 Nodes)

All nodes are JSON-defined and validated against the pydantic `NodeDefinitionJSON` model:

| Node | Category | Description |
| :--- | :--- | :--- |
| `hou_create_node` | Houdini | Create a node in the Houdini scene |
| `hou_create_geo` | Houdini | Create a Geometry container at /obj |
| `hou_delete_node` | Houdini | Delete a node by path |
| `hou_set_parm` | Houdini | Set a single parameter |
| `hou_get_parm` | Houdini | Read a parameter value |
| `hou_set_parms` | Houdini | Set multiple parameters (JSON) |
| `hou_connect_nodes` | Houdini | Wire two nodes together |
| `hou_cook` | Houdini | Force-cook a node |
| `hou_run_code` | Houdini | Execute Python code in Houdini |
| `hou_scene_info` | Houdini | Query scene metadata |
| `hou_node_info` | Houdini | Get detailed node information |
| `hou_list_children` | Houdini | List child nodes |
| `hou_node_exists` | Houdini | Check node existence |
| `hou_set_display_flag` | Houdini | Toggle display flag |
| `hou_set_expression` | Houdini | Set a channel expression |
| `hou_set_keyframe` | Houdini | Set a keyframe value |
| `hou_set_frame` | Houdini | Jump to a timeline frame |
| `hou_save_hip` | Houdini | Save the .hip file |
| `hou_layout_children` | Houdini | Auto-layout network children |

### 🔹 Plugin Installation

1. Copy `plugins/houdini/houdini/` to your Houdini user preferences directory (e.g., `$HOME/houdiniXX.X/`).
2. The plugin registers a **Vibrante** shelf and **Vibrante** menu in Houdini.
3. Launch Vibrante-Node from the shelf button — the command server starts automatically.
4. The bundled virtual environment (`plugins/houdini/houdini/scripts/python/env/`) provides dependencies (pydantic, etc.) without modifying Houdini's Python.

### 🔹 Example Houdini Scripts

Located in `plugins/houdini/v_scripts_houdini/`:
- **`hou_scene_info.py`** — Query the current Houdini scene via the bridge.
- **`hou_create_box_demo.py`** — Create a Geometry container with a Box SOP.
- **`hou_list_scene_nodes.py`** — List all children under `/obj`.

---

## 🎨 6. UI Architecture & Features

- **Dynamic Node Scaling**: Nodes automatically resize their bounding box based on port count and child widget dimensions.
- **Vertical Parameter Centering**: Parameter widgets (Label + Input) are distributed and centered within the node body.
- **Clip-Path Header Rendering**: Clean, solid title bars that perfectly respect the node's rounded corners without overlapping lines.
- **Global Theme System**: Integrated Dracula-based **Dark Mode** and standard **Light Mode** available via the Themes menu.
- **SVG Vector Support**: Native rendering for all icons in the library, toolbar, and node headers.

---

## 🛠️ 7. Technical Safety & Reliability

- **Thread-Safe UI Updates**: Signal-based communication ensures that background threads can safely update the Event Log and widgets.
- **Crash Protection**: A global exception hook captures unhandled errors and generates a `crash.log` file for instant debugging.
- **Safer Node Drop (v1.5.0)**: Node constructor failures during drag-and-drop are wrapped in try/except in `scene.py` and `view.py`. Failing nodes log a clean error and do not corrupt undo history.
- **Safer Engine Init (v1.4.0)**: `NetworkExecutor` wraps node instantiation in try/except and reports errors via the `node_error` signal instead of crashing the executor.
- **Robust Persistence**: Full workflow states (positions, parameters, and connections) are serialized as clean, portable JSON.
- **Name Sanitization**: Automated slug generation for custom nodes to ensure filesystem and class compatibility.
- **Qt Compatibility Layer** (v1.2.0): A unified `src/utils/qt_compat.py` module handles differences between PyQt5 and PySide2 for cross-environment support.

---

## 🆕 8. Branch Notes — Scripting & Looping Enhancements

- **Python Script Node**: A dynamic `python_script` node and in-UI `ScriptEditorDialog` were added. The node stores user code in the `python_code` parameter and executes it during workflow runs. User scripts should assign their primary output to a variable named `result` which is published to the `result` output port.
- **While Loop Support**: A builtin `WhileLoopNode` and example workflows (`workflows/while_loop_example.json`, `workflows/while_loop_retry_example.json`) provide flow-driven loop control patterns. The engine supports nested and re-entrant execution for safe loop operation.
- **Utility Nodes**: New helper nodes for lists, dictionaries, and string operations were added in the `nodes/` folder to accelerate common tasks.
- **Engine Runtime Fix**: Workflow-saved parameters (including `python_code`) are now applied to node instances at startup so authored scripts embedded in saved workflows execute as intended.
- **Gemini Support in Node Builder**: The Node Builder includes integration hooks for Gemini-based assistance to scaffold example scripts, generate prompt templates, and provide sample code snippets. See `src/ui/gemini_chat.py` for configuration and usage notes.
