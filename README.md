# Vibrante-Node

**Vibrante-Node** is a dynamic, Python-based desktop application for creating and executing visual workflows. Built with PyQt5 and Asyncio, it allows users to design complex processing pipelines through an intuitive node-based interface, with real-time feedback and extensible custom node definitions.

---

## 🚀 Key Features

### 🎨 Intuitive Visual Canvas
- **Bidirectional Connections:** Drag wires from outputs to inputs or vice versa.
- **Single-Input Enforcement:** Automatically manages logical data flow by allowing only one connection per input port.
- **Redrag to Disconnect:** Intuitive "pull-away" gesture to break existing connections.
- **Canvas Navigation:** Smooth Panning (Middle Mouse) and Zooming (Mouse Wheel).

### 🛠️ Interactive Node Widgets
Nodes aren't just static boxes; they support live UI components for direct data entry:
- **String Inputs:** Standard Text Boxes and Multiline Text Areas.
- **Numerical Controls:** Integer and Float Spin Boxes, plus Sliders.
- **Logic & Selection:** Checkboxes for booleans and Dropdowns (QComboBox) for predefined options.

### ⚡ Powerful Execution Engine
- **Asynchronous Processing:** Non-blocking background execution ensures the UI remains responsive during long-running tasks.
- **Topological Sorting:** Smart dependency resolution ensures nodes execute in the correct order.
- **Data Propagation:** Real-time flow of data from widgets and connected nodes throughout the network.
- **Visual Status:** Nodes provide immediate visual cues (`Running`, `Success`, `Failed`).

### 📝 Integrated Node Builder
Create your own nodes using a built-in editor that supports:
- **Live Port Management:** Add/Remove inputs and outputs via a simple table.
- **Python Scripting:** Define node logic using standard Python strings.
- **Widget Configuration:** Configure interactive widgets and dropdown options (CSV) directly.

### 🪵 Fancy Event Log
A color-coded, dockable log window provides detailed feedback:
- `[EXEC]` Cyan: Execution status.
- `[OK]` Green: Data output and success messages.
- `[ERROR]` Red: Errors and stack traces.

---

## 📥 Installation

### Prerequisites
- Python 3.10 or higher
- `pip` (Python package manager)

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

---

## 🏃 How to Run

Launch the application using the main entry point:
```bash
python ./src/main.py
```

---

## 📖 Quick Start & Usage

1. **Add Nodes:** Right-click on the canvas or use the **Library Panel** on the left to add nodes like `Math Add`, `String Concat`, or `Console Print`.
2. **Configure Data:** Use the widgets embedded directly on the nodes (e.g., type text into a `Message Node` or adjust a slider).
3. **Connect Nodes:** Click and drag from an output port (right side) to an input port (left side).
4. **Run Workflow:** Press **F5** or click the **"Run Workflow"** button in the toolbar.
5. **View Results:** Watch the **Event Log** at the bottom for real-time output and execution steps.

---

## 📂 Project Structure

```text
├── nodes/              # JSON definitions for custom nodes
├── src/
│   ├── core/           # Engine, Registry, and Graph logic
│   ├── ui/             # PyQt components (Canvas, Widgets, Panels)
│   ├── utils/          # Runtime wrappers and syntax highlighters
│   └── main.py         # Application entry point
├── workflows/          # Saved pipeline files (.json)
└── DOCUMENTATION.md    # Detailed technical feature list
```

---

## 🤝 Example Nodes Included
- **Math Add:** Real-time numerical addition.
- **String Concat:** Join strings with configurable separators.
- **Fruit Selector:** Demonstrates dropdown widget usage.
- **Async Delay:** Showcases non-blocking asynchronous execution.
- **Console Print:** Logs network data to the system console.

---

## 📜 License
This project is provided for educational and developmental purposes. Feel free to fork and extend!
