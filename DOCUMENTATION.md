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

### 🔹 Advanced Connection System
- **Bidirectional Dragging**: Start wires from either input or output ports.
- **Single-Input Enforcement**: Automatically replaces old wires when a new one is connected to an input port.
- **Redrag-to-Disconnect**: Seamlessly move existing wires by dragging them away from ports.

### 🔹 Application Icon (v1.1.5)
- Custom application icon (`icons/vibrante-node-icon.png`) displayed in the taskbar, title bar, and splash screen.

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
  - Supported widgets: `"text"`, `"text_area"`, `"int"`, `"float"`, `"bool"`, `"dropdown"`, `"slider"`, `"file"`.
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

## 🔥 4. SideFX Houdini Integration (v1.1.5)

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

## 🎨 5. UI Architecture & Features

- **Dynamic Node Scaling**: Nodes automatically resize their bounding box based on port count and child widget dimensions.
- **Vertical Parameter Centering**: Parameter widgets (Label + Input) are distributed and centered within the node body.
- **Clip-Path Header Rendering**: Clean, solid title bars that perfectly respect the node's rounded corners without overlapping lines.
- **Global Theme System**: Integrated Dracula-based **Dark Mode** and standard **Light Mode** available via the Themes menu.
- **SVG Vector Support**: Native rendering for all icons in the library, toolbar, and node headers.

---

## 🛠️ 6. Technical Safety & Reliability

- **Thread-Safe UI Updates**: Signal-based communication ensures that background threads can safely update the Event Log and widgets.
- **Crash Protection**: A global exception hook captures unhandled errors and generates a `crash.log` file for instant debugging.
- **Robust Persistence**: Full workflow states (positions, parameters, and connections) are serialized as clean, portable JSON.
- **Name Sanitization**: Automated slug generation for custom nodes to ensure filesystem and class compatibility.
- **Qt Compatibility Layer** (v1.1.5): A unified `src/utils/qt_compat.py` module handles differences between PyQt5 and PySide2 for cross-environment support.

---

## 🆕 7. Branch Notes — Scripting & Looping Enhancements

- **Python Script Node**: A dynamic `python_script` node and in-UI `ScriptEditorDialog` were added. The node stores user code in the `python_code` parameter and executes it during workflow runs. User scripts should assign their primary output to a variable named `result` which is published to the `result` output port.
- **While Loop Support**: A builtin `WhileLoopNode` and example workflows (`workflows/while_loop_example.json`, `workflows/while_loop_retry_example.json`) provide flow-driven loop control patterns. The engine supports nested and re-entrant execution for safe loop operation.
- **Utility Nodes**: New helper nodes for lists, dictionaries, and string operations were added in the `nodes/` folder to accelerate common tasks.
- **Engine Runtime Fix**: Workflow-saved parameters (including `python_code`) are now applied to node instances at startup so authored scripts embedded in saved workflows execute as intended.
- **Gemini Support in Node Builder**: The Node Builder includes integration hooks for Gemini-based assistance to scaffold example scripts, generate prompt templates, and provide sample code snippets. See `src/ui/gemini_chat.py` for configuration and usage notes.
