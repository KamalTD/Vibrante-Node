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
    -   `code_editor.py`: The professional source code editor used in the Node Builder.

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

---

## 🆕 Developer Notes — v1.7.0 (Prism Overhaul, Atomic Save)

### New Prism Getter Nodes

Six new nodes were added to the Prism category: `prism_get_scene_path`, `prism_get_export_path`, `prism_get_shot_by_sequence`, `prism_get_asset_type_by_name`, `prism_get_asset_types_by_project`, `prism_get_assets_by_type`. All follow the standardised Prism getter pattern (guard `if core is None`, safe defaults).

`prism_get_export_path` returns the actual file path, not its containing directory. It handles `output_type` values `'3d'` and `'2d'` and accepts an optional `version` argument.

### Prism Entity Dict Enrichment

The entity dict produced by `prism_build_entity` and related nodes is now enriched with `path`, `location`, and `paths` keys so downstream nodes can resolve scene file locations without an extra bridge call.

### Dynamic Config Reader

The Prism config reader no longer hardcodes department abbreviations. Abbreviations are now read at runtime from the active project's config via `core.getConfig()`, making the nodes compatible with any studio that customises department names.

### `get_tasks` Multi-Method Fallback

`prism_get_tasks` now tries multiple Prism API methods in sequence (`getTasks`, `getTasksForEntity`, `task_mgr.getTasks`) to stay compatible across Prism versions.

### Atomic Workflow Save + Safe Load

`NodeScene.save_workflow_model()` strips non-serializable runtime values (widget objects, Qt handles, live Python references) before writing JSON so saves never corrupt on object-rich graphs. `load_workflow_model()` uses a safe loader that catches `json.JSONDecodeError` on empty or corrupt files and prompts the user to start fresh rather than crashing.

### Prism v2.1.0 API Fixes

- `getShots()` in Prism v2.1.0 returns a flat list instead of a dict; `prism_get_shots` now handles both shapes.
- `createProduct` signature corrected for v2.1.0.
- Version directory is created on disk before `prism_save_scene_version` writes the file; improved error diagnostics.

---

## 🆕 Developer Notes — v1.8.0 (Stability & Bugfix)

### Engine: Bypass Flag

`NetworkExecutor._run_single_node_impl()` now checks `node.bypassed` before executing. Bypassed nodes propagate their primary input straight to their primary output (passthrough semantics) and fire `exec_out` normally so the downstream chain is not broken.

### `for_loop` Fix

The `for_loop` builtin was stopping iteration after the first shot because it re-entered `_run_from_node()` before the loop variable advanced. The fix iterates the full list inside a single `execute` call, building the complete index list and returning it; `exec_out` fires once. The `loop_body` node then drives per-item iteration.

### Hotkey Guard on Text Fields

The `KeyPressEvent` handler in `NodeCanvas` now checks `QApplication.focusWidget()` — if a `QLineEdit` or `QTextEdit` has focus, all hotkeys are suppressed. This prevents `Delete` and `F5` from triggering while the user is typing in a node widget.

### Houdini Headless Fixes

- `houdini_headless_executor` validates that the hython path exists before spawning a subprocess; raises `FileNotFoundError` with a clear message if not.
- `import_alembic` defaults its SOP context to `/obj` rather than `/stage`.

### Blender Runner Fix

Alembic frame arguments renamed to match Blender's current CLI (`--frame-start` / `--frame-end`). `makedirs(exist_ok=True)` added before writing output files.

### `deadline_job_status` Crash Fix

The node now guards against a `None` return from the Deadline REST endpoint and logs a clear error instead of raising an `AttributeError`.

### Prism `set_output` Ordering

In nodes that expose data ports alongside `exec_out`, `set_output` is now called on data ports before `exec_out` fires, ensuring downstream nodes receive data before their own `execute` is triggered.

---

## 🆕 Developer Notes — v1.8.x (Node Reload, Init-First, Wire Color, Settings)

### `on_parameter_changed` Timing (v1.8.1–v1.8.3)

`on_parameter_changed` is called **reactively during execution** when the output handler propagates a result to a connected input port (i.e., after an upstream node finishes, the downstream node's parameter is updated and `on_parameter_changed` fires). This enables reactive nodes (e.g., `TwoWaySwitchNode`) to update their own outputs mid-run.

It is **not** called during:
- Pre-execute input sync (the sweep that copies wire values into node parameters before `execute` begins) — removed in v1.8.3.
- Reactive output propagation outside the execution path — removed in v1.8.3 to prevent double-propagation.

### Registry Source Paths

`NodeRegistry` maintains a `_source_paths: dict[str, str]` mapping `node_id → absolute JSON file path`. Two new public methods:
- `get_source_path(node_id) -> str | None` — returns the file path or `None` if the node is built-in / not found.
- `reload_node_definition(node_id) -> bool` — re-reads the JSON from `_source_paths[node_id]`, re-compiles the Python class, and replaces the registry entry. Returns `True` on success.

### `NodeWidget.reload_definition(new_definition)`

Accepts a new node definition dict and performs an in-place widget update:
1. Replaces the internal `definition`.
2. Removes existing port items from the scene.
3. Calls `_build_ports()` with the new definition.
4. Re-applies parameter values that are still valid (port still exists, type compatible).
5. Removes wire connections to ports that no longer exist.

### `NodeScene.reload_node_type(node_id)`

Calls `registry.reload_node_definition(node_id)` then iterates all `NodeWidget` instances in the scene whose `node_id` matches, calling `widget.reload_definition(new_definition)` on each. This is the entry point for `Ctrl+R`.

### Init-First Scene Ordering

`NodeScene.load_workflow_model()` now performs two passes:
1. **Pass 1**: Create and connect all nodes with `init_priority > 0` (Init First nodes).
2. **Pass 2**: Create and connect all remaining nodes.

This guarantees that authentication and server-connect nodes are fully instantiated and wired before any downstream node is built, which matters when `on_plug_sync` reads a value from an already-connected init node.

The `init_priority` is stored in the node's JSON definition and on `BaseNode` as an integer attribute (default `0`).

### Wire Coloring by Port Type

`WireItem.paint()` now resolves the color from the **output port's data type** by calling `PortItem.get_type_color(data_type)` rather than using a fixed color. In the light theme, all wires render in black regardless of type for legibility.

### User Settings Persistence

`MainWindow` now saves theme, window geometry (`saveGeometry()`) and dock layout (`saveState()`) to `QSettings` on close, and restores them on startup. The settings key group is `VibrateNode/session`.

---

## 🆕 Developer Notes — v1.6.0 (Prism, Python Script, While Loop)

### Prism Pipeline Integration

**`src/utils/prism_core.py`** — Three public functions form the Prism support layer:
- `store_prism_core(core)` — persists a `PrismCore` instance to a module-level global and optionally to shared memory.
- `resolve_prism_core(inputs)` — checks (in order): `inputs["core"]`, the global cache, shared memory, and the active DCC session. Returns `None` if none found.
- `bootstrap_prism_core(prism_root, dcc_path, args)` — synchronously initializes `PrismCore` on the calling thread. Must be called on the Qt main thread.

**`src/core/registry.py` — `_prepare_definition()`** — Before a JSON node definition is compiled into a Python class, the registry calls this method. For `prism_*` nodes it:
1. Injects `from src.utils.prism_core import resolve_prism_core` into `python_code`.
2. Replaces `core = inputs.get('core')` with `core = resolve_prism_core(inputs)`.

This means Prism nodes do not need to be written differently — the registry handles it transparently.

**`src/core/engine.py` — Prism bootstrap phase** — At the start of each execution run, the engine scans the graph for `prism_core_init` nodes. If found and PrismCore is not yet cached:
1. A `_bootstrap_prism_on_main_thread()` call is dispatched to the Qt event loop.
2. The engine waits (with a short timeout) for bootstrap to complete.
3. Regular execution then proceeds with PrismCore available to all nodes.

**`src/ui/window.py` — `_bootstrap_prism_on_main_thread()`** — Called by the engine via Qt signal. Extracts parameters from the `prism_core_init` node instance and calls `bootstrap_prism_core()`. Logs success or failure to the Event Log panel.

**`src/utils/qt_compat.py`** — Two new auto-called helpers:
- `ensure_qcolor_from_string()` — adds `QColor.fromString` as a classmethod if missing (Qt5 compatibility).
- `ensure_shiboken_stub()` — creates stub `shiboken2`/`shiboken6` modules to prevent Prism from loading incompatible binary wheels.

### Python Script Node

The `python_script` builtin node stores user code in a `python_code` parameter. The engine's parameter-application step (added in v1.0.5) injects this value before execution, so saved workflows always run the authored script. An **Edit Script** button on the node widget opens a full code editor dialog.

### While Loop Node

The `while_loop` builtin re-enters the engine's `_run_from_node()` path on each iteration. The removal of `_exec_lock` (done in v1.0.5 to fix `ForLoop` deadlocks) also makes while-loop re-entry safe.

### Utility Nodes

List, dictionary, and string utility nodes live in `src/nodes/builtins/nodes.py` and are registered by the `register_builtins()` call at module load time. They use `use_exec=False` so they behave as pure data nodes and participate in reactive propagation without explicit exec wires.
