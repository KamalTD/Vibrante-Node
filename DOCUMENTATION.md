# Vibrante-Node - Technical API & Architecture Documentation

This document provides an exhaustive reference for the Vibrante-Node platform, covering core architecture, the custom node Scripting API, and the Workflow Automation system.

---

## 🚀 1. Core Application Architecture

### 🔹 Professional Python Code Editor
The Node Builder features a fully-integrated, professional-grade source code editor:
- **Intelligent Syntax Highlighting**: Dracula-inspired theme for keywords, builtins, and multi-line strings.
- **Auto-Indentation & Linting**: Automatic 4-space indent after colons (`:`) and instant syntax error detection with gutter highlighting.
- **IntelliSense**: Rich completion suggestions for Python keywords and common node methods.
- **Bracket Matching & Auto-Closing**: Instant feedback for `()`, `[]`, and `{}`.

### 🔹 High-Performance Execution Engine
- **Asynchronous Execution**: Uses a background `asyncio` loop to keep the UI responsive.
- **Topological Sorting**: Automatically determines execution order for data-only graphs.
- **Hybrid Flow + Data Model (v1.0.5)**:
    - **Flow-Based Routing**: Execution follows `exec` pins sequentially.
    - **Recursive Data Pulling**: Before any node executes, it recursively triggers upstream data-only nodes to ensure all inputs are current.
    - **Re-entrant Execution**: Fixed deadlocks in `NetworkExecutor` to allow nested flow calls (essential for Loops).
- **Prism Bootstrap Phase (v1.6.0)**: Before main execution, the engine detects `prism_core_init` nodes and bootstraps PrismCore on the Qt main thread.
- **Recursive Data Propagation**: A live system that pushes parameter changes through the entire node chain instantly as the user interacts with the UI.

### 🔹 Advanced Connection System
- **Bidirectional Dragging**: Start wires from either input or output ports.
- **Single-Input Enforcement**: Automatically replaces old wires when a new one is connected to an input port.
- **Redrag-to-Disconnect**: Seamlessly move existing wires by dragging them away from ports.

---

## 🏗️ 2. Part 1: Node Scripting API (`BaseNode`)

All custom nodes must inherit from the `BaseNode` class.

### 🔹 Class Attributes
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | The display name of the node in the library and canvas. |
| `category` | `str` | Logical grouping (e.g., "Math", "IO", "Logic", "Prism"). |
| `description` | `str` | Tooltip/help text for the user. |
| `icon_path` | `str` | Path to an SVG/PNG icon. |

### 🔹 Configuration Methods
- **`self.add_input(name, data_type, widget_type, options)`**: Adds an input port.
  - Supported widgets: `"text"`, `"text_area"`, `"int"`, `"float"`, `"bool"`, `"dropdown"`, `"slider"`, `"file"`, `"file_save"`.
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
        self.set_parameter(port_name, data)
        self.log_info(f"Connected to {other_node.name}")
```

#### Scenario B: Async Background Worker
```python
async def execute(self, inputs):
    self.log_info("Starting heavy calculation...")
    await asyncio.sleep(2.0)
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
node = scene.find_node_by_name("Message Node")
if node:
    for val in ["Test A", "Test B", "Test C"]:
        node.set_parameter("msg", val)
        app.execute_pipeline()
```

---

## 🎨 4. UI Architecture & Features

- **Dynamic Node Scaling**: Nodes automatically resize their bounding box based on port count and child widget dimensions.
- **Vertical Parameter Centering**: Parameter widgets (Label + Input) are distributed and centered within the node body.
- **Clip-Path Header Rendering**: Clean, solid title bars that perfectly respect the node's rounded corners without overlapping lines.
- **Global Theme System**: Integrated Dracula-based **Dark Mode** and standard **Light Mode** available via the Themes menu.
- **SVG Vector Support**: Native rendering for all icons in the library, toolbar, and node headers.

---

## 🛠️ 5. Technical Safety & Reliability

- **Thread-Safe UI Updates**: Signal-based communication ensures that background threads can safely update the Event Log and widgets.
- **Crash Protection**: A global exception hook captures unhandled errors and generates a `crash.log` file for instant debugging.
- **Robust Persistence**: Full workflow states (positions, parameters, and connections) are serialized as clean, portable JSON.
- **Name Sanitization**: Automated slug generation for custom nodes to ensure filesystem and class compatibility.

---

## 🆕 6. v1.6.0 — Prism Integration, Python Script, While Loop, Utilities

### Prism Pipeline Integration

40+ new nodes in the `Prism` category enable full Prism Pipeline studio-management workflows:

| Node Group | Nodes |
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

Key behaviours:
- **Auto-bootstrap**: `prism_core_init` is detected before execution and PrismCore is initialized on the Qt main thread.
- **Zero-wiring**: All `prism_*` nodes resolve the shared `PrismCore` via `resolve_prism_core()` — no `core` wire needed.
- **Qt compat**: `qt_compat.py` auto-stubs `shiboken` and backfills `QColor.fromString` so Prism loads without binary-wheel conflicts.

### Python Script Node

- `python_script` node ships with an **Edit Script** button that opens a full code editor dialog.
- Scripts are persisted in the workflow JSON under the `python_code` parameter.
- The engine injects `python_code` into node instances before execution, so saved scripts always run correctly.
- User scripts should assign their primary output to a variable named `result`, which is published to the `result` output port.

### While Loop Node

- `while_loop` builtin: iterates while a boolean `condition` input is `True`.
- Safe re-entrant execution — the engine's lock-free design prevents deadlocks in nested loop scenarios.

### Utility Nodes

| Category | Nodes |
|---|---|
| List | `create_list`, `get_list_item`, `list_length` |
| Dictionary | `create_dictionary`, `get_dict_value`, `set_dict_value` |
| String | `concat`, `split`, `replace`, `lowercase`, `uppercase`, `string_length` |

### `file_save` Widget Type

A new `"file_save"` widget type is available for output file path inputs. It opens a save-file dialog rather than an open-file dialog, making it suitable for export nodes.

### Engine Runtime Fix

Workflow-saved parameters (including `python_code`) are now applied to node instances at startup so authored scripts embedded in saved workflows execute as intended.

### Gemini Support in Node Builder

The Node Builder includes integration hooks for Gemini-based assistance to scaffold example scripts, generate prompt templates, and provide sample code snippets. See `src/ui/gemini_chat.py` for configuration and usage notes.
