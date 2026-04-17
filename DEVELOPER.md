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
