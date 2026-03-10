# Vibrante-Node

**Vibrante-Node** is a professional, Python-based desktop application designed for creating and executing complex visual workflows. Combining a powerful node-based canvas with an integrated professional code editor, it empowers users to build modular data pipelines with real-time feedback and high-performance execution.

---

## 📸 Screenshots

![Vibrante-Node UI 1](shots/01.PNG)
![Vibrante-Node UI 2](shots/02.PNG)
![Vibrante-Node UI 3](shots/03.PNG)

---

## 🌟 Latest Enhancements

### ⚡ Reactive Data Propagation
Workflow data now flows in **real-time** across the canvas:
- **Instant Sync:** Changing a value in one node immediately updates all connected downstream nodes.
- **Visual Monitoring:** Destination widgets update live even when disabled by a connection, acting as real-time monitors.
- **Predictive Flow:** Smart data mirroring ensures nodes possess output data even before the full workflow is executed.

### 🔄 Node Lifecycle Events
Nodes are now fully "aware" of their environment:
- **on_plug_sync:** React instantly when a wire is connected.
- **on_unplug_sync:** Cleanup or reset logic when disconnected.
- **on_parameter_changed:** Custom logic that triggers as you type or interact with widgets.

### 🏗️ Advanced Node Builder
The specialized creation tool is now more powerful:
- **Interactive Selectors:** Dropdown menus for selecting port **Types** and **Widget** styles.
- **Automatic Code Generation:** Generates full Python class structures with lifecycle stubs automatically.
- **Robust Sync:** Bi-directional synchronization between the UI tables and the Python source code.

### 🎨 Refined Node Layout
- **Dynamic Scaling:** Nodes automatically resize their width and height to fit any number of ports and widgets perfectly.
- **Vertical Centering:** All parameter widgets are automatically distributed and centered within the node body.
- **Clean UI:** Professional header rendering with no overlapping lines and clear, bold parameter labeling.

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

---

## 📂 Project Structure

```text
├── nodes/              # JSON definitions for custom nodes
├── src/
│   ├── core/           # Engine, Registry, and Graph logic
│   ├── ui/             # PyQt components (Canvas, Editor, Library)
│   ├── utils/          # Runtime and Threading helpers
│   └── main.py         # Application entry point
├── workflows/          # Saved pipeline files (.json)
└── DOCUMENTATION.md    # Full technical feature list
```

---

## 📜 License
This project is provided for educational and developmental purposes. Feel free to fork and extend!
