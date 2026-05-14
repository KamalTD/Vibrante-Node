<p align="center">
  <img src="logo.png" width="400" alt="Vibrante-Node Logo">
</p>

# Vibrante-Node

**Vibrante-Node** is a Python-node-based visual framework for building modular systems through connected nodes and data flows. It provides an intuitive graph interface where complex logic can be constructed visually by linking nodes together.

The project focuses on flexibility, extensibility, and developer productivity, making it suitable for building tools such as visual pipelines, automation workflows, and data-processing graphs. Node-based systems allow complex operations to be organized as interconnected components rather than traditional linear code structures, improving clarity and scalability in large workflows.

---

## 📸 Screenshots

![Vibrante-Node UI 1](shots/04.PNG)
![Vibrante-Node UI 2](shots/05.PNG)
![Vibrante-Node UI 3](shots/06.PNG)
![Vibrante-Node UI 4](shots/07.PNG)
![Vibrante-Node UI 5](shots/08.PNG)

---

## 🌟 Latest Enhancements

### 🔔 Unsaved Changes Detection — Tab `*` Marker (v2.1.0)
Every workflow tab now tracks unsaved edits. A `*` prefix appears on the tab label the moment a change is made (e.g. `my_graph.json` → `* my_graph.json`). Closing a dirty tab or the whole application shows a **Save / Discard / Cancel** dialog per tab so no work is lost.

### ⚠️ Port Type Mismatch Warning (v2.1.0)
Connecting ports of incompatible types (e.g. `string` → `int`) logs a warning to the log panel immediately. The connection is still allowed — the warning is informational. `any`-typed ports (including all exec flow pins) are always compatible.

### 🗂️ Subgraph / Group Node — Ctrl+Shift+G (v2.0.0)
Collapse any selection of connected nodes into a single **GroupNode** that stores the full subgraph internally:
- **Double-click** to open the subgraph in a new, fully editable tab. Changes sync back to the parent workflow in real time (undo/redo included).
- `exec_out` fires on success; `exec_fail` fires only on unhandled exceptions inside the subgraph.
- Inner node logs are forwarded to the main log panel.

### 🔭 Live Wire Value Inspector (v2.0.0)
Hover over any connected wire after execution to see the last value that flowed through it as a tooltip. Values persist until the next run.

### 💾 Autosave & Crash Recovery (v2.0.0)
Every 2 minutes the app writes all open tabs to `~/.vibrante_node_autosave.json`. If the app crashes, a restore dialog is shown on the next launch. On a clean exit the autosave file is deleted automatically.

### 🕐 Recent Files — File → Open Recent (v2.0.0)
The File menu lists the last 10 saved or loaded workflows. Missing files are shown grayed-out. One click to reopen.

### 🔍 Canvas Search Bar — Ctrl+F (v2.0.0)
A floating search bar filters all nodes by name or ID. Enter / Shift+Enter cycles through matches; Escape closes.

### 🗺️ Mini-map — Ctrl+M (v2.0.0)
A 200×150 px thumbnail of the full canvas with a viewport indicator. Click or drag to pan. Toggle with Ctrl+M.

### ⏱️ Node Execution Timing (v2.0.0)
The log panel shows how long each node took — e.g. `Node 'Get Asset' finished in 0.34s`.

### 🛠️ Node Reload & Dev Workflow (v1.8.x)
- **In-Place Node Reload**: Edit a node's JSON definition, then press `Ctrl+R` to reload all live instances on the canvas — ports are rebuilt, saved parameter values are re-applied, and valid connections are preserved.
- **Registry Source Tracking**: `NodeRegistry` now tracks the on-disk path of every loaded definition via `_source_paths`, and exposes `get_source_path(node_id)` / `reload_node_definition(node_id)` for programmatic reloads.
- **Right-Click Shortcuts**: The canvas context menu now includes "Edit Node" (opens Node Builder for that definition) and "Reload Node" (reloads from disk without reopening the builder).
- **Toolbar Buttons**: New buttons for Add Node, Add Sticky Note, Add Network Box, Edit Selected Node, and Reload Selected Node.
- **Keyboard Shortcuts**: `Tab` adds a node, `Ctrl+E` edits the selected node, `Ctrl+R` reloads it from disk, `Ctrl+Shift+R` reloads all nodes.

### 🚦 Init-First Scene Ordering (v1.8.x)
Nodes marked as **Init First** (`init_priority > 0`) are created and connected before all other nodes during workflow load. This guarantees that authentication or server-connect nodes are fully wired before downstream consumers are instantiated.

### 🎨 Wire Type Coloring & Settings Persistence (v1.8.x)
- Wires are now colored by the **output port's data type** rather than a fixed color; the light theme uses black wires for readability.
- Theme, window geometry, and dock layout are now **persisted between sessions**.

### 🔧 Stability & Bugfix Release (v1.8.x)
- **Bypass flag**: The engine now honours the node bypass flag — bypassed nodes are skipped during execution.
- **`on_parameter_changed` timing**: No longer called during pre-execute input sync or reactive output propagation, preventing cascading side effects (v1.8.1–v1.8.3).
- **Dropdown fix**: Dropdown parameters now return the selected item correctly during `execute`, and `set_parameter` no longer resets selection on options update (v1.8.2).
- **`for_loop` behavior**: `for_loop` fires `exec_out` once after building the full index list; use a `loop_body` node to iterate per item.

### 🎬 Prism Pipeline Overhaul (v1.7.0)
New Prism nodes and reliability improvements:
- **New nodes**: `prism_get_scene_path`, `prism_get_export_path`, `prism_get_shot_by_sequence`, `prism_get_asset_type_by_name`, `prism_get_asset_types_by_project`, `prism_get_assets_by_type`.
- **Export path resolution**: `prism_get_export_path` returns the actual file path (not directory) and handles `output_type` `'3d'`/`'2d'`.
- **Dynamic config reader**: Department abbreviations are read dynamically from the project config — no more hardcoded values.
- **Prism v2.1.0 API fixes**: `getShots()` flat-list handling, corrected `createProduct` signature, version directory creation before save.
- **Atomic workflow save + safe load**: Scene strips non-serializable runtime values before saving; corrupted or empty files are handled gracefully.
- **Full Prism + Maya headless tutorial workflow** included.

### 🎬 Prism Pipeline Integration (v1.6.0)
Full integration with the [Prism Pipeline](https://prism-pipeline.com/) studio management system:
- **40+ Prism Nodes**: Complete node library covering entities, products, media, scenes, configs, USD workflows, and more.
- **Auto-Bootstrap**: Place a `prism_core_init` node in any graph — the engine automatically initializes PrismCore before execution without manual wiring.
- **Zero-Wiring Core Access**: All `prism_*` nodes resolve the shared `PrismCore` instance from a global cache automatically; no `core` wire required.
- **Qt Compatibility Layer**: New helpers in `qt_compat.py` backfill Qt6-style APIs and stub out incompatible shiboken wheels so Prism loads cleanly inside the app.
- **Main-Thread Bootstrap**: PrismCore is initialized on the Qt main thread (required by Prism) with a graceful fallback if initialization fails.

### 🐍 Python Script Node (v1.6.0)
- **In-UI Code Editor**: The `python_script` node ships with an **Edit Script** button that opens a full-featured code editor directly on the node.
- **Saved Scripts**: Scripts are persisted inside the workflow JSON — reopening a saved workflow reloads the exact code that was authored.
- **Runtime Parameter Injection**: The engine now injects workflow-saved parameters (such as `python_code`) into node instances before execution, so scripts run correctly after loading.

### 🔁 While Loop Node (v1.6.0)
- **`while_loop` builtin node**: Loop-based control flow driven by a boolean condition port.
- **Graph-level loop support**: The execution engine handles recursive re-entry safely, enabling while loops without deadlocking.

### 🧩 Utility Node Library (v1.6.0)
New general-purpose helper nodes:
- **List**: `create_list`, `get_list_item`, `list_length`
- **Dictionary**: `create_dictionary`, `get_dict_value`, `set_dict_value`
- **String**: `concat`, `split`, `replace`, `lowercase`, `uppercase`, `string_length`

### ⚡ Refined Flow Engine (v1.0.5)
The execution engine has been significantly upgraded for power and reliability:
- **Loop Execution Fixed:** Resolved a critical deadlock in `NetworkExecutor`, enabling smooth, nested flow processing for `For Loop` and `Loop Body` nodes.
- **Recursive Data Pulling:** Nodes now automatically "pull" the latest values from upstream data-only nodes immediately before execution, ensuring loop iterations always use fresh data.
- **Selective Reactive Updates:** Smart propagation logic in Flow Mode only triggers downstream nodes if they lack execution pins, preventing redundant processing while keeping the UI live.
- **`use_exec` Support:** Custom nodes can now be defined without execution pins for a cleaner, data-focused UI.

### 🎨 Visual Overhaul & Theming
*   **Dynamic Dark/Light Themes:** Fully integrated theme switching across the entire application, including the canvas and all dock panels.
*   **Category-Based Coloring:** Nodes are automatically color-coded based on their category (Math, Logic, Data, etc.) for instant visual identification.
*   **Refined Node Layout:** Nodes automatically scale to fit their content with perfectly centered widgets and clear headers.

### 🔌 Type-Coded Ports
*   **Visual Data Types:** Ports are color-coded by data type (e.g., Cyan for `int`, Purple for `string`), making connections intuitive and error-resistant.
*   **Interactive Tooltips:** Hover over any port to see its name and expected data type instantly.

### 🤖 Automation Suite
*   **Power-User Examples:** 11 new Python scripts demonstrating batch processing, scene management, and complex workflow automation.
*   **Scripting Console:** Full access to the internal API for programmatically manipulating the node graph.

### 📊 Interactive Status Bar
*   **Real-time Feedback:** Monitor execution status and get detailed descriptions of selected nodes directly in the status bar.

### 🏗️ Advanced Node Builder
The specialized creation tool is now more powerful:
- **Interactive Selectors:** Dropdown menus for selecting port **Types** and **Widget** styles.
- **Automatic Code Generation:** Generates full Python class structures with lifecycle stubs automatically.
- **Robust Sync:** Bi-directional synchronization between the UI tables and the Python source code.

### ⚡ Reactive Data Propagation
Workflow data now flows in **real-time** across the canvas:
- **Instant Sync:** Changing a value in one node immediately updates all connected downstream nodes.
- **Visual Monitoring:** Destination widgets update live even when disabled by a connection, acting as real-time monitors.
- **Predictive Flow:** Smart data mirroring ensures nodes possess output data even before the full workflow is executed.

---

## 🚀 Key Features

- **Interactive Node Widgets:** Embed Text Boxes, Sliders, Dropdowns, and File Selectors directly into your nodes.
- **Thread-Safe Logging:** Background nodes communicate with the UI via a robust signal-based logging system.
- **Asynchronous Engine:** Background execution via `asyncio` keeps the UI responsive during high-load processing.
- **Robust Persistence:** Workflows and custom nodes are saved as clean, portable JSON definitions.

---

## 📥 Installation & Setup

### Prerequisites
- Python 3.10+
- `pip`

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/KamalTD/Vibrante-Node.git
   cd Vibrante-Node
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App:**
   ```bash
   python ./src/main.py
   ```

---

## 📚 Documentation

Detailed documentation is available for both users and developers:
-   📖 **[User Guide](USER_GUIDE.md)**: How to use the interface and build workflows.
-   🛠️ **[Node Builder API](NODE_BUILDER_API.md)**: In-depth guide for creating custom nodes.
-   🤖 **[Automation API](AUTOMATION_API.md)**: Reference for Scripting Console automation.
-   🛠️ **[Developer Documentation](DEVELOPER.md)**: Technical architecture and internal data flow.
-   📄 **[Technical Feature List](DOCUMENTATION.md)**: Detailed breakdown of all platform features.
-   📋 **[Release Notes v2.1.0](RELEASE_v2.1.0.md)**: Full changelog for the current release.
-   📋 **[Release Notes v2.0.0](RELEASE_v2.0.0.md)**: Changelog for v2.0.0.

---

## 📂 Project Structure

```text
├── examples/           # Automation scripts and custom node examples
├── icons/              # UI icons (SVG/PNG format)
├── nodes/              # Primary JSON definitions for custom nodes
│   └── prism_*/        # 40+ Prism Pipeline integration nodes
├── node_examples/      # Pre-built node library for quick reference
├── src/                # Application source code
│   ├── core/           # Engine, Registry, and Graph management
│   ├── ui/             # PyQt5/PyQt6 components (Canvas, Panels, Node Widgets)
│   ├── utils/          # Theming, Runtime, Threading, and Bridge helpers
│   │   ├── prism_core.py   # Prism initialization and shared-memory cache
│   │   └── qt_compat.py    # Qt5/Qt6 compatibility layer
│   └── main.py         # Application entry point
├── specs/              # Feature and design specifications
├── tests/              # Unit and integration tests
├── workflows/          # Saved pipeline files (.json)
├── ai_memory/          # Persistent AI context and memory files
└── DOCUMENTATION.md    # Detailed technical documentation
```

---

## 📜 License

Vibrante-Node uses an **open-core** hybrid licensing model.

| Component | License |
|---|---|
| Core Runtime | [AGPLv3](LICENSE) |
| SDK / Public API | [MIT](LICENSE) |
| Documentation & Examples | [CC BY 4.0](LICENSE) |
| Official Plugins & Nodes | [Commercial](COMMERCIAL_LICENSE.md) |
| Enterprise Integrations | [Commercial](COMMERCIAL_LICENSE.md) |

**Free for** individuals, students, education, and open productions.  
**Commercial studio deployment** requires a [commercial license](COMMERCIAL_LICENSE.md).

### Read the Full License Agreement

- 📄 [LICENSE](LICENSE) — AGPLv3 runtime + MIT SDK + CC BY 4.0 docs
- 💼 [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) — Studio, SaaS, and enterprise terms
- ™️ [TRADEMARK_POLICY.md](TRADEMARK_POLICY.md) — Vibrante-Node branding guidelines
- 🤝 [CLA.md](CLA.md) — Contributor License Agreement

Licensing inquiries: **m.kamalvfx@gmail.com**
