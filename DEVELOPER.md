# Vibrante-Node Developer Documentation

This guide is intended for developers who wish to understand the internal architecture of Vibrante-Node or extend its functionality.

## 🏗️ Architecture Overview

Vibrante-Node follows a modular architecture separated into three main layers:

1.  **Core Layer (`src/core/`)**: Handles the "brain" of the application.
    -   `engine.py`: Manages the asynchronous execution of the node network.
    -   `graph.py`: Logic for topological sorting and dependency resolution.
    -   `registry.py`: The central hub where all node types (built-in and dynamic) are registered.
    -   `models.py`: Pydantic data models for serialization and validation.

2.  **UI Layer (`src/ui/`)**: Handles the visual representation.
    -   `canvas/`: Custom `QGraphicsScene` and `QGraphicsView` for the node workspace.
    -   `node_widget.py`: The visual representation of a node on the canvas.
    -   `code_editor.py`: The professional source code editor used in the Node Builder and Export dialog.
    -   `export_python_dialog.py`: IDE-style dialog for viewing, editing, running, and AI-fixing exported Python code.

3.  **Nodes Layer (`src/nodes/`)**: Defines the node logic.
    -   `base.py`: The abstract base class `BaseNode` that all nodes must inherit from.
    -   `builtins/`: Python-native nodes bundled with the app.

## 📊 Data Flow

1.  **Serialization**: The canvas is serialized into a `WorkflowModel` (JSON).
2.  **Hybrid Execution Model (v1.0.5)**:
    -   **Flow Mode**: If execution pins (`exec`) are connected, the engine follows them sequentially.
    -   **Data Mode**: If no `exec` pins are present, `GraphManager` determines a topological sort.
3.  **Recursive Data Pulling**: Before any node executes, `NetworkExecutor` recursively calls `_run_single_node_impl` on upstream data-only nodes to ensure all inputs are fresh.
4.  **Re-entrant execution**: The `_exec_lock` was removed to allow nodes to trigger downstream flows (like loops) without deadlocking.
5.  **Propagation**: Output dictionaries from one node are mapped to the input dictionaries of the next based on wire connections.

## 🛠️ How to Add a Built-in Node

To add a new node directly in the source code:
1.  Create a class in `src/nodes/builtins/nodes.py` inheriting from `BaseNode`.
2.  Define `name`, `category`, and `icon_path`.
3.  In `__init__`, use `self.add_input()` and `self.add_output()`.
4.  Implement the `async def execute(self, inputs)` method.
5.  Register it in the `register_builtins()` function at the bottom of the file.

## 📝 Custom Node Schema (JSON)

Dynamic nodes created via the Node Builder are saved as JSON files in the `nodes/` directory. They contain:
-   Metadata (id, name, category, icon)
-   Port definitions (including widget types and options)
-   The full Python logic as a string inside `python_code`.

## 🎨 Theming System

Themes are applied globally using `QApplication.instance().setStyleSheet()`. Custom widgets (like `NodeWidget`) manually check the palette brightness to adjust internal colors (like labels and lines) to remain readable.

---

## 🆕 Developer Notes — Dynamic Nodes, Engine Fix, Gemini

- **Dynamic Node Loading**: JSON node definitions stored in `nodes/` contain a `python_code` field. During startup `NodeRegistry.load_all()` compiles these definitions and generates dynamic `BaseNode` subclasses so custom nodes can be registered at runtime.

- **Engine Parameter Application**: The `NetworkExecutor` now copies workflow-saved parameters into instantiated node objects before execution. This ensures node-specific runtime-only parameters (for example `python_code` on a `python_script` node) are available when the engine runs.

- **Gemini Integration Hook**: The Node Builder exposes hooks to Gemini for code assistance and snippet generation. See `src/ui/gemini_chat.py` for how the UI interacts with Gemini and how to configure API keys or local endpoints. Treat generated code as untrusted until reviewed — Gemini is intended to accelerate authoring rather than replace code review.

## 🆕 v1.1.0 — Engine Optimizations & New Features

### Execution Performance
- **Zero-delay loop execution**: All `asyncio.sleep()` calls with non-zero delays in `ForEachNode`, `WhileLoopNode`, `SequenceNode`, and the engine poll loop have been replaced with `asyncio.sleep(0)`. This yields control to the event loop without introducing artificial latency.
- **Indexed outgoing connections**: `NetworkExecutor` now pre-calculates `_outgoing_data_conns` and `_outgoing_exec_conns` dictionaries at execution start, keyed by `(node_id, port_name)`. The `set_output` handler uses O(1) dict lookups instead of O(N) scans over all connections.
- **Widget cache**: `_find_node_widget` in `window.py` builds a dict cache at execution start and invalidates it when execution finishes, replacing O(N) linear scans per signal handler call.
- **Signal handler short-circuits**: `_on_node_started`, `_on_node_output`, and `_on_node_log` skip string formatting and log emission when the Event Log's silent mode is active.

### Export Python Dialog
- `export_python_dialog.py` was rewritten from a 74-line read-only preview to a ~300-line IDE dialog using `CodeEditor`, `PythonHighlighter`, `QProcess` for code execution, and `GeminiFixWorker` (background thread) for AI-powered error fixing. The dialog has its own hardcoded Dracula stylesheet independent of the global theme.

### Event Log
- Added `Silent Mode` checkbox to `LogPanel`. When active, the `_handle_log` fast-path returns immediately for non-error/warning messages, skipping regex extraction, entry creation, and UI updates.

## 🆕 v1.2.0 — Houdini Dynamic API & App Icon

### SideFX Houdini Integration

A full DCC integration with SideFX Houdini FX was added using a **Live Command Bridge** architecture:

#### Architecture
- **Command Server** (`plugins/houdini/houdini/scripts/python/vibrante_hou_server.py`): A JSON-RPC server that runs inside Houdini's Python process on `127.0.0.1:18811`. All scene-modifying commands are dispatched to Houdini's main thread via `hdefereval.executeDeferred()` to ensure thread safety. The server implements 22 commands (see DOCUMENTATION.md for the full table).
- **Bridge Client** (`src/utils/hou_bridge.py`): `HouBridge` class provides a high-level Python API for communicating with the command server. Accessed via the `get_bridge()` singleton. `is_available()` performs a ping health check.
- **All launch modes use subprocess**: In-process mode was removed entirely to avoid Houdini Signal 11 segfaults caused by Qt binding conflicts. `launch_inprocess()` now delegates to `launch()` (subprocess).

#### Houdini Node Definitions
19 JSON-defined nodes in `plugins/houdini/v_nodes_houdini/`, all validated against the pydantic `NodeDefinitionJSON` model. Each node's `python_code` calls the appropriate `bridge.*` method from `src/utils/hou_bridge.py`.

Nodes: `hou_create_node`, `hou_create_geo`, `hou_delete_node`, `hou_set_parm`, `hou_get_parm`, `hou_set_parms`, `hou_connect_nodes`, `hou_cook`, `hou_run_code`, `hou_scene_info`, `hou_node_info`, `hou_list_children`, `hou_node_exists`, `hou_set_display_flag`, `hou_set_expression`, `hou_set_keyframe`, `hou_set_frame`, `hou_save_hip`, `hou_layout_children`.

#### Plugin Structure
```
plugins/houdini/
├── houdini/                        # Copied to Houdini user prefs
│   ├── toolbar/vibrante.shelf      # Shelf tool definition
│   ├── mainmenu/vibrante.xml       # Menu bar integration
│   └── scripts/python/
│       ├── vibrante_node_houdini.py  # Main entry (launch, setup_env)
│       ├── vibrante_hou_server.py    # JSON-RPC command server
│       └── env/                      # Bundled venv (pydantic, etc.)
├── v_nodes_houdini/                # 19 Houdini node JSON definitions
└── v_scripts_houdini/              # Example scripts
```

#### Qt Compatibility
- `src/utils/qt_compat.py` provides a unified import layer for `QPolygonF`, `QPointF`, and other types across PyQt5 and PySide2.
- PySide6 support was removed. PySide2 is still used only for type references — all actual UI runs under PyQt5 in subprocess mode.

### Application Icon
- Custom icon (`icons/vibrante-node-icon.png`) set via `app.setWindowIcon()` in `src/main.py`. Visible in taskbar, title bar, and window switcher.

## 🆕 v1.2.0 — Dynamic API, UI Polish & Bypassing

### SideFX Houdini Dynamic API
The Houdini integration was expanded to support arbitrary API calls:
- **Dynamic Call Dispatcher**: A new `call` command was added to `vibrante_hou_server.py`. It uses recursion to traverse the `hou` module and execute any method with provided `*args` and `**kwargs`.
- **IntelliSense Server**: The `get_completions` command provides a list of available members for any `hou` object, enabling real-time auto-complete in the Node Builder.
- **Enhanced Tracebacks**: The server now captures full Python tracebacks from Houdini and returns them to Vibrante-Node for easier debugging of DCC-side scripts.

### Node Bypassing Implementation
- **Data Model**: `NodeInstanceModel` now includes a `bypassed: bool` field.
- **Engine Logic**: In `NetworkExecutor._run_single_node_impl`, bypassed nodes skip `execute()`. Instead, they identify the first non-exec input and map its value to all non-exec outputs. All `exec` output pins are triggered to maintain flow.
- **UI Component**: `NodeWidget` features a new `bypass_rect` in the header. `mousePressEvent` toggles the state, and `paint()` applies a 0.4 opacity effect to the entire item when bypassed.

### UI & UX Refinement
- **Drag and Drop**: Implemented `DraggableTreeWidget` (subclass of `QTreeWidget`) in `library_panel.py` to initiate `QDrag` operations. `NodeView` implements `dropEvent` to spawn nodes at scene coordinates.
- **Port Animations**: `PortWidget` uses `QVariantAnimation` to smoothly transition `scale_factor` between 1.0 and 1.5 during hover events.
- **Connection Snapping**: `NodeScene.mouseMoveEvent` performs a proximity search for `PortWidget` items. If a compatible port is within 35 pixels, the `active_edge` endpoint is snapped to the port center and a hover animation is triggered on the target.

### Python Export Engine (v2)
`WorkflowToPythonConverter` was refactored for better logical mapping:
- **Bypass Support**: Bypassed nodes are emitted as pass-through comments, mapping outputs to the first input variable.
- **Generic Exec Branching**: The recursion logic now automatically follows ALL execution pins (e.g., `exec_false`, `then`, `on_finished`) if they are not explicitly handled by specialized control-flow emitters.
- **Loop Logic Refactor**: `for_loop` is now treated as a data-provider node (generating a range list) while `loop_body` handles the actual Python `for` loop, eliminating redundant nesting.

## 🆕 v1.3.0 — Houdini Geometry Nodes, AI Context Fix & CLAUDE.md

### New Houdini Geometry Nodes
Three new bridge-based nodes were added for geometry pipeline work:
- **Color Curves**: Assigns a ramp-driven color attribute along curve primitives.
- **Edges to Curves**: Extracts polygon edges and converts them to curves for hair/grooming workflows.
- **ABC Convert**: Imports an Alembic and converts the result to polygons.

### AI Context Fix
Gemini node-building requests now receive the correct node-builder context (previous versions leaked irrelevant workflow state into the prompt).

### CLAUDE.md Developer Guide
A new `CLAUDE.md` in the repo root teaches AI assistants how to author Houdini bridge nodes — the JSON file format, the `BaseNode` skeleton, the full `hou_bridge` API with return-value contracts, and common patterns (geo container construction, Object vs SOP resolution, VEX wrangles). See `CLAUDE.md` for the full guide.

### YouTube Channel
A `@Vibrante-Node` YouTube channel was launched with walkthroughs and tutorials. Links added to README.

## 🆕 v1.4.0 — Node Builder Save & Register Fix, BaseNode Hardening, VFX Nodes

### Node Builder "Save & Register" No Longer Erases Manual Code Edits
**Bug:** `save_node()` previously called `_sync_ui_to_code()` as its first step, which regenerated the code from the UI tables. If the 1-second debounce timer in the editor hadn't fired yet, any hand-written logic inside `execute()` was overwritten before being saved.

**Fix:** `save_node()` now stops the pending timer and calls `_sync_code_to_ui()` instead — parsing the latest *code* to update the tables. The code editor is the source of truth.

### `BaseNode.set_parameter()` Added
`BaseNode.set_parameter(name, value)` is now a public method. It handles the dropdown-port edge case: if `value` is a list, it updates the port's `options` list and selects the first item. This resolved an `AttributeError` crash on nodes (e.g. `Get_Project`) that called `set_parameter()` in their `__init__`.

### Safer Engine Initialization
Node instantiation inside `NetworkExecutor` is now wrapped in try/except. If a node's `__init__` raises, the error is reported via the `node_error` signal rather than crashing the whole executor and tearing down the UI.

### New VFX Pipeline Nodes
- **`Get_Project`** (VFX_Pipeline) — retrieves project context/path.
- **`Parse_Path`** (VFX_Pipeline) — splits and parses file paths.
- **`Test`** (General) — utility test node.
- Category `Trend_Pipeline` → `VFX_Pipeline` across existing nodes.

### UI: Dark Theme Checkboxes
QCheckBox widgets in the Node Builder are now themed correctly: white label, dark background indicator, green highlight when checked.

### Miscellaneous
- `.gitignore` now ignores the `main/` directory.

## 🆕 v1.5.0 — Maya Headless, Houdini Headless & Chainable Action Nodes

### Architecture Overview

Two new DCC executor nodes ship in v1.5.0: `Maya Headless` and `Houdini Headless`. Both launch the DCC in batch mode as a subprocess (`mayapy.exe` / `hython.exe`), run a list of structured "action" dicts against the DCC, and return per-action success/failure plus captured stdout/stderr. This is distinct from the live `hou_bridge` command-server pattern (v1.2.0): the new executors are **short-lived**, **version-pinned**, and **designed for batch/CI use**.

The executors share one design:

1. **Validation pass** (host side, inside Python): walk the action list, skip actions with missing required fields, fail the node early if any were skipped.
2. **Serialization**: write a temp JSON payload (`{hip_file/scene_file, actions}`) and a temp Python runner script (embedded as a constant in the executor's `python_code`).
3. **Subprocess launch**: `subprocess.run([dcc_py, runner_script, payload_path, results_path], env=merged_env, timeout=600)`.
4. **Runner execution** (inside the DCC Python): the runner loads the payload, iterates actions, dispatches each to a typed branch inside try/except, and writes `{index, type, ok, error, info?}` per action into the results JSON.
5. **Results merge** (host side): the executor reads the results JSON and builds the `executed_actions` list by merging the planned action dict with any `info` field the runner produced.

#### Why structured payload + runner script?
- **No f-string injection** — action values are JSON-encoded, not interpolated into code strings.
- **Per-action isolation** — one failing action doesn't blank the rest.
- **Success contract** — `success = (returncode == 0) and (no_action_errors)`. DCC stderr is informational (Maya emits warnings to stderr even on success; treating stderr as a failure signal caused false failures in early revisions).

#### Version pinning and environment injection
Both executors have a version dropdown that auto-fills the binary path via an `on_parameter_changed` handler:
- **Maya**: 2022 / 2024 / 2025 / 2026 → `mayapy.exe`
- **Houdini**: 20.5.445 / 20.5.278 / 20.0.547 / 19.5.493 → `hython.exe`

Users can also override the path directly. Both executors accept:
- A `.bat` file — parsed for `SET key=val` lines (case-insensitive `set ` prefix).
- A `Maya.env` / `houdini.env` file — parsed as `key=value` lines, `#` comments.
Values are expanded for `%VAR%` references against the current environment, then merged into the subprocess env (`.bat` overrides `.env`, both override the inherited env).

### Action Node Pattern

An action node is a small JSON node that takes `actions_in: list` + action-specific parameters, appends a typed action dict to the list, and outputs `actions_out: list`. Users chain them left-to-right and plug the final list into the headless executor's `actions` input. This keeps the graph flat and makes individual actions easy to insert/remove.

### Action Types Supported

**Maya Headless:** `open_scene`, `new_scene`, `save_scene`, `scene_info`, `set_frame_range`, `import_obj`, `import_fbx`, `import_alembic`, `export_fbx`, `export_alembic`, `export_camera_alembic`, `import_camera`, `reference_scene`, `reference_alembic`, `list_references`, `playblast`, `bake_animation`, `set_render_settings`, `set_aovs` (Arnold/Redshift), `create_render_layer` (renderSetup), `assign_material`, `custom_python`.

**Houdini Headless:** `open_hip`, `save_hip`, `new_hip`, `scene_info`, `set_frame_range`, `import_obj`, `import_fbx`, `import_alembic`, `import_camera`, `export_fbx`, `export_alembic`, `export_camera_alembic`, `bake_animation`, `custom_python`.

All Houdini import actions take an optional `context` parameter (`/obj` or `/stage`) to pick between the classic Object/SOP workflow and Solaris/LOPs.

### Renderer-Specific Details (Maya)
- **`set_aovs` (Arnold)** calls `mtoa.core.createOptions()` to initialize `defaultArnoldRenderOptions` before invoking `AOVInterface`, with a fallback to creating the node directly via `cmds.createNode("aiOptions", ...)` if the import fails. Without this, `AOVInterface` raises `No object matches name: defaultArnoldRenderOptions.aovs` in a cold `mayapy` session.
- **`set_aovs` (Redshift)** uses `rsCreateAov(type=name)`.
- **`create_render_layer`** uses the `renderSetup` API (`maya.app.renderSetup.model.renderSetup`) with collection + selector pattern for members.
- **`assign_material`** auto-looks-up the shader's `shadingEngine` connection, and creates an SG if the material doesn't have one.
- **`set_render_settings`** maps image format strings (`exr`/`png`/`jpg`/...) to Maya's `defaultRenderGlobals.imageFormat` integer codes for non-Arnold renderers; for Arnold it sets `defaultArnoldDriver.aiTranslator`.

### Get Action Result Helper Nodes

`maya_get_action_result` and `houdini_get_action_result` take an `executed_actions` list and either:
- An `action_type` string — first-match lookup, or
- An `index` — 0-based position lookup (defaults to 0).

They output `found`, `action` (full dict), `info` (pointer to `action["info"]` for query actions), and `path` (best-guess from `fbx_path`/`abc_path`/`obj_path`/`scene_path`/`save_scene_path`/`camera_path`/`output_path`/`hip_path`). This replaces manual list filtering downstream and is an additive helper — existing workflows that read `executed_actions` directly keep working.

### New `file_save` Widget Type

A new `widget_type` value on string ports that opens `QFileDialog.getSaveFileName` instead of `getOpenFileName`. Implemented in `src/ui/node_widget.py`:

```python
elif p_model.widget_type in ('file', 'file_save'):
    ...
    is_save = p_model.widget_type == 'file_save'
    def select_file(_checked=None, save=is_save):
        if save:
            path, _ = QFileDialog.getSaveFileName(curr, "Save File")
        else:
            path, _ = QFileDialog.getOpenFileName(curr, "Select File")
```

**Gotcha fixed:** The inner function takes `_checked=None` as its first parameter because `QPushButton.clicked` emits a `bool` argument. Without the absorber, that bool overrode the default `save=is_save` and `file_save` silently fell back to `getOpenFileName`.

### Custom Action Script Editor
`maya_action_custom` and `houdini_action_custom` are editable action nodes. The Edit Script button in `node_widget.py` is wired for those node_ids:

```python
if getattr(self.node_definition, 'node_id', None) in ('python_script', 'maya_action_custom', 'houdini_action_custom') and '_script_btn' not in self.param_widgets:
```

The `_open_script_editor` callback reads/writes `python_code` via `get_parameter`/`set_parameter` (not via the raw parameters dict) so the dialog always reflects current code, and invokes `scene.push_history()` on accept.

### Safer Node Drop
`NodeScene` and `NodeView` now wrap the node-spawn path in try/except. A failing constructor logs an error via the parent's `log_panel` (if available) and returns `None`. The drop handler checks the return value and only calls `push_history()` / `acceptProposedAction()` on success.

Before this fix, a node with a broken `__init__` (e.g. during active development) would crash the canvas on drag-and-drop.

### File & Module Touchpoints
- `nodes/maya_headless.json`, `nodes/houdini_headless.json` — executors.
- `nodes/maya_action_*.json` (22 files), `nodes/houdini_action_*.json` (14 files) — action nodes.
- `nodes/maya_get_action_result.json`, `nodes/houdini_get_action_result.json` — helpers.
- `src/ui/node_widget.py` — `file_save` widget type, custom action script editor wiring.
- `src/ui/canvas/scene.py`, `src/ui/canvas/view.py` — safer node drop.
- `src/core/models.py` — `file_save` listed in `widget_type` comment.
