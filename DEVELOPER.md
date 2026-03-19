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
