# Research: Python Node-Based Desktop Application (PyQt5)

## Decision: PyQt5 (Qt for Python)
- **Rationale**: Robust, industry-standard framework for desktop GUIs. The `QGraphicsScene` and `QGraphicsView` frameworks are highly efficient for managing complex interactive graphics like node graphs.
- **Alternatives considered**: PySide6 (similar but the user specifically requested PyQt5 for this architecture), Tkinter (too primitive), Kivy (better for mobile, but not as strong on standard desktop patterns).

## Decision: `toposort` for DAG Evaluation
- **Rationale**: Simple and efficient library for performing topological sorting. It helps determine the correct execution order for nodes in the Directed Acyclic Graph.
- **Alternatives considered**: Custom Depth-First Search (DFS) implementation (more prone to edge-case errors).

## Decision: `importlib` for Plugin Discovery
- **Rationale**: Standard library module for programmatically importing modules. It allows us to dynamically load custom node definitions from a dedicated "nodes" folder at runtime.
- **Alternatives considered**: `exec()` (higher security risks and harder to manage module scope).

## Decision: Pydantic for Serialization
- **Rationale**: Seamlessly bridges the gap between Python classes and JSON. Provides high-quality validation for saved workflows.
- **Alternatives considered**: `marshmallow` (slightly more verbose).

## Decision: Multi-threading with `QThreadPool`
- **Rationale**: Offloads node execution from the main GUI thread to keep the application responsive. `QRunnable` and `QThreadPool` integrate well with the PyQt5 event loop.
- **Alternatives considered**: `asyncio` (while powerful, threading with QThreads/QRunnable is more native to the Qt ecosystem for standard CPU-bound tasks).
