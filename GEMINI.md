# node_based_app Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-14

## Active Technologies
- Python 3.10+ + `PyQt5`, `pydantic`, `toposort`, `ast`
- JSON files in `nodes/` and `workflows/` directories
- Autodesk Maya, SideFX Houdini, Blender (Headless Subprocess & Live Bridge)
- Thinkbox Deadline (via `deadlinecommand`)

## Project Structure

```text
src/
├── core/       # Engine, Registry, Models, Graph Logic
├── ui/         # PyQt5 Canvas, Node Widgets, Panels, Dialogs
└── utils/      # Theming, Runtime, Qt Compat, DCC Bridges
nodes/          # JSON Node Definitions
plugins/        # DCC Integrations (Houdini package, scripts)
tests/          # Unit and Integration tests
```

## Recent Changes
- v1.5.0: Added Maya, Houdini, and Blender Headless executors with 55+ action nodes. Added Deadline render farm submitters.
- v1.4.0: Node Builder "Save & Register" fix. Category rename to VFX_Pipeline.
- v1.3.0: Houdini Geometry Nodes (Color Curves, Edges to Curves, ABC Convert).
- v1.2.0: Houdini Live Bridge (22 commands), Node Bypassing, UI Polish (Snapping, Drag & Drop).
- v1.1.0: Professional Code Editor for Python Export, Execution Optimizations, Event Log Silent Mode.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
