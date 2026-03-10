# Vibrante-Node - Technical Documentation

This document provides a detailed breakdown of the features, architecture, and APIs of the Vibrante-Node Pipeline Editor.

---

## 🚀 1. Core Application Features

### 🔹 Interactive Node Widgets
Nodes support embedded UI components for direct data interaction:
- **Text Entry**: Single-line (`QLineEdit`) and Multiline (`QTextEdit`) with auto-scaling constraints.
- **Numerical**: Spin Boxes (`QSpinBox`, `QDoubleSpinBox`) and horizontal Sliders.
- **Selection**: Dropdowns (`QComboBox`) with CSV-defined options and Checkboxes.
- **System**: File Selectors with native OS dialog integration.

### 🔹 Advanced Connection System
- **Bidirectional Dragging**: Start connections from either input or output ports.
- **Single-Input Enforcement**: Automatically replaces existing wires when a new one is connected to an input port.
- **Redrag-to-Disconnect**: Disconnect and move existing wires by dragging them away from their ports.
- **Smart Disabling**: UI widgets automatically disable when a port is connected to show data is being received from a wire.

### 🔹 High-Performance Execution Engine
- **Asynchronous Execution**: Uses a background `asyncio` loop to keep the UI responsive during processing.
- **Topological Sorting**: Automatically calculates the correct execution order based on graph dependencies.
- **Real-Time Data Propagation**: Recursive system that pushes data through the entire chain instantly as parameters change.

---

## 🏗️ 2. Node Scripting API (`BaseNode`)

Use these methods within the **Node Builder** to define custom logic.

### 🔹 Key Methods
- `self.add_input(name, data_type, widget_type, options)`: Add an input port with optional UI.
- `self.add_output(name, data_type)`: Add an output port.
- `self.log_info(msg)` / `log_success` / `log_error`: Send messages to the Event Log.
- `self.get_parameter(name)`: Access current port/widget data.

### 🔹 Lifecycle Hooks
- `on_plug_sync(port_name, is_input, other_node, other_port_name)`: React immediately to connections.
- `on_parameter_changed(name, value)`: Handle live user interaction with widgets.
- `async def execute(self, inputs)`: Main workflow execution logic.

### 📖 Node Example: Reactive Buffer
```python
def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
    if is_input:
        data = other_node.get_parameter(other_port_name)
        self.set_parameter(port_name, data) # Sync UI immediately
```

---

## 🤖 3. Workflow Automation API

The **Scripting Console** allows for full application automation using Python.

### 🔹 Global Objects
- `app`: Access main window methods (e.g., `app.execute_pipeline()`).
- `scene`: Manipulate the canvas (e.g., `scene.add_node_by_name()`, `scene.connect_nodes()`).
- `registry`: Query available node types.
- `git`: Manage source control directly from the editor.

### 📖 Automation Example: Grid Generation
```python
# Create a chain of 25 nodes programmatically
prev = None
for i in range(5):
    for j in range(5):
        curr = scene.add_node_by_name("message_node", (j*300, i*200))
        if prev: scene.connect_nodes(prev, "out", curr, "msg")
        prev = curr
```

---

## 🎨 4. UI Architecture & Theming
- **Dynamic Scaling**: Nodes automatically resize width/height based on port and widget counts.
- **Clip-Path Headers**: Clean title bars that respect node roundness with zero overlapping lines.
- **Global Themes**: Dracula-based Dark Mode and standard Light Mode.
- **SVG Integration**: Native vector support for all node icons and library items.

---

## 🛠️ 5. Technical Improvements
- **Unified Port Model**: Consistent handling of builtin Python classes and dynamic JSON definitions.
- **Thread-Safe Logging**: Signal-based communication between background nodes and the UI.
- **Crash Protection**: Global exception hooks that generate `crash.log` for debugging.
- **Robust Serialization**: Full workflow state (positions, parameters, connections) saved as portable JSON.
