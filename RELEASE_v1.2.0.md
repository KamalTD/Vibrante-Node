# Release v1.2.0: Dynamic Houdini API, Node Bypassing & UI/UX Polish

Version 1.2.0 is a major update that expands the **SideFX Houdini** integration with a dynamic API bridge, introduces **Node Bypassing** for better workflow control, and delivers a suite of **UI/UX enhancements** including Drag & Drop, port animations, and connection snapping.

---

## 🚀 Key Features

### 🔥 SideFX Houdini Dynamic API
The Houdini plugin is no longer limited to a fixed set of commands.
- **Full API Access**: Call ANY method from the `hou` module dynamically through the command bridge.
- **Houdini IntelliSense**: Real-time auto-completion for Houdini module members in the Node Builder and node parameter widgets.
- **Improved Debugging**: Full Python tracebacks from Houdini are now captured and displayed directly in the Vibrante-Node console.
- **Updated Nodes**: Enhanced "Hou Run Python" node with auto-complete support.

### 🖱️ UI/UX & Workflow Enhancements
- **Drag & Drop**: Spawning nodes is now faster — simply drag any node from the Library panel directly onto the canvas.
- **Enhanced Network Boxes (Backdrops)**:
    - **Fit to Selection**: Right-click a backdrop to automatically resize it to perfectly wrap all contained nodes.
    - **Body Interaction**: Restructured interaction model — move boxes via the header, while dragging the body allows for rubber-band selection of nodes inside.
- **Animated Ports**: Ports now scale up smoothly when hovered and feature a "magnetic" snap effect that pulls wires to compatible pins.
- **Power-User Shortcuts**:
    - `F5` / `Shift+F5`: Run/Stop the active workflow.
    - `Ctrl+G`: Wrap selected nodes in a new Network Box.
    - `Ctrl+B`: Toggle Bypass state for selected nodes.
    - `Space + Drag`: Pan the canvas using the left mouse button.

### 🚫 Node Bypassing
Disable logic without breaking your connections.
- **Visual Toggle**: Click the "B" button in the node header to bypass.
- **Logic Passthrough**: Bypassed nodes turn semi-transparent, skip execution, and automatically pass the data from their first input to all outputs.
- **Persistence**: Bypass states are fully saved and restored in workflow files.

### 🐍 Refined Python Export (Engine v2)
The Python export engine has been refactored for professional-grade script generation:
- **Branching Support**: Full support for all execution outputs (e.g., `exec_false` in If Condition).
- **Loop Optimization**: Resolved nested loop issues in `For Loop` / `Loop Body` patterns.
- **Bypass Awareness**: Bypassed nodes are exported as pass-through comments, maintaining workflow logic in standalone scripts.

---

## 🐞 Bug Fixes & Refinements
- **Log Panel**: Disabling "Silent Mode" now automatically restores previously checked filters (Info, Exec, Output).
- **Export Dialog**: Fixed `TypeError` related to `QProcess` slot signatures in some PyQt5 environments.
- **UI Consistency**: Fixed typos in connection handling logic (`to_p` vs `to_port`).
- **If Condition**: Updated `exec_false` output to be a proper execution type pin.

---

## 📂 Changed Files
- `src/main.py` — Version bump to v1.2.0, splash screen update
- `src/ui/window.py` — New shortcuts, about dialog updated
- `src/ui/canvas/scene.py` — Snapping logic, backdrop enhancements
- `src/ui/canvas/view.py` — Drag & Drop handling, new shortcuts
- `src/ui/node_widget.py` — Bypass button UI and logic
- `src/core/engine.py` — Bypass support in execution engine
- `src/core/workflow_to_python.py` — Refactored export engine
- `plugins/houdini/...` — Dynamic API and completion support
- `README.md`, `USER_GUIDE.md`, `DEVELOPER.md`, `DOCUMENTATION.md` — All docs updated

---

## 📜 License
Permission is granted to use, modify, and test this software for personal and non-commercial purposes.
Commercial use requires written permission from the author.
