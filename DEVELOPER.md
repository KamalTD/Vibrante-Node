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
2.  **Topological Sort**: `GraphManager` determines the order of execution so that a node only runs after its dependencies.
3.  **Execution**: `NetworkExecutor` runs each node in an `asyncio` loop.
4.  **Propagation**: Output dictionaries from one node are mapped to the input dictionaries of the next based on wire connections.

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
