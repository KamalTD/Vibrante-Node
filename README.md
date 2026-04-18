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
-   📋 **[Release Notes v1.6.1](RELEASE_v1.6.1.md)**: Full changelog for the current release.

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
├── tests/              # Unit and integration tests
├── workflows/          # Saved pipeline files (.json)
└── DOCUMENTATION.md    # Detailed technical documentation
```

---

## 📜 License

Permission is granted to use, modify, and test this software for personal and non-commercial purposes.

Commercial use, redistribution in commercial products, or use within commercial services requires written permission from the author.

Contributions are welcome via pull requests.
