# Implementation Plan: Python Node-Based Desktop Application

**Branch**: `002-node-desktop-app` | **Date**: 2026-03-09 | **Spec**: [specs/002-node-desktop-app/spec.md](spec.md)
**Input**: Feature specification from `/specs/002-node-desktop-app/spec.md`

## Summary
Build a desktop application using Python and PyQt5 featuring a visual node editor. The application uses a `QGraphicsScene`-based canvas for constructing workflows, a dynamic plugin system for loading nodes from scripts, a multi-threaded execution engine for DAG evaluation, and a **Node Builder** for creating custom nodes via a built-in Python editor.

## Technical Context
**Language/Version**: Python 3.10+
**Primary Dependencies**: `PyQt5`, `pydantic`, `toposort`
**Storage**: JSON-based workflow files
**Testing**: `pytest`, `pytest-qt`
**Target Platform**: Desktop (Windows, macOS, Linux)
**Project Type**: GUI Application
**Performance Goals**: Responsive UI with 60 FPS, efficient multi-threaded DAG execution.
**Constraints**: Must strictly separate UI from execution logic; nodes must be sandboxed to prevent app crashes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Modular Python Architecture: Strict separation of UI, node logic, and engine.
- [x] Scriptable Extensibility: Dynamic loading via `importlib` from a "nodes" folder.
- [x] Stability & Sandboxed Execution: Safe runtime wrapper for node execution.
- [x] Workflow Serialization & Integrity: JSON storage for nodes, parameters, and connections.
- [x] Performance & Async Execution: Multi-threaded DAG evaluation and topological sorting.
- [x] User Experience Consistency: Consistent UI patterns for ports and parameters.

## Project Structure

### Documentation (this feature)

```text
specs/002-node-desktop-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── main.py              # Application entry point
├── core/
│   ├── engine.py        # DAG execution & topological sorting
│   ├── graph.py         # Graph manager (nodes, edges, connections)
│   ├── loader.py        # Plugin system (importlib script loading)
│   └── models.py        # Pydantic models for persistence
├── ui/
│   ├── window.py        # Main Window
│   ├── canvas/          # QGraphicsScene & QGraphicsView
│   ├── node_widget.py   # Custom node graphics items
│   ├── port_widget.py   # Input/Output port items
│   └── node_builder.py  # Node Builder dialog & code editor
├── nodes/               # Plugin folder for custom node scripts
│   ├── base.py          # Abstract Node base class
│   └── builtins/        # Default node types
└── utils/
    ├── runtime.py       # Error handling & sandboxing utilities
    └── highlighter.py   # Python syntax highlighter for editor
```

**Structure Decision**: Modular Python application with a clear separation between the Qt-based UI and the core execution engine.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
