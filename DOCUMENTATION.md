# Vibrante-Node - Technical API Documentation

This document provides a comprehensive reference for the Vibrante-Node Scripting API and Workflow Automation system.

---

## 🏗️ Part 1: Node Scripting API (`BaseNode`)

All custom nodes must inherit from `BaseNode`. This class provides the fundamental interface for ports, parameters, logging, and lifecycle events.

### 🔹 Attributes (Class Level)
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | The display name of the node. |
| `category` | `str` | The library category (e.g., "Math", "IO"). |
| `description` | `str` | Tooltip/help text for the node. |
| `icon_path` | `str` | Relative path to an SVG/PNG icon. |

### 🛠️ Configuration Methods (Usually in `__init__`)

#### `self.add_input(name, data_type="any", widget_type=None, options=None)`
Adds an input port.
- **`widget_type`**: `"text"`, `"text_area"`, `"int"`, `"float"`, `"bool"`, `"dropdown"`, `"slider"`, `"file"`.

#### `self.add_output(name, data_type="any")`
Adds an output port.

### 🔄 Lifecycle Hooks

- `on_plug_sync(port_name, is_input, other_node, other_port_name)`: **Immediate reaction** on connection.
- `on_unplug_sync(port_name, is_input)`: Cleanup on disconnection.
- `on_parameter_changed(name, value)`: Triggered when a UI widget value is changed.
- `async def execute(self, inputs)`: The main logic run during workflow execution.

---

## 🤖 Part 2: Workflow Automation API

Vibrante-Node features a built-in **Scripting Console** (Window -> Show/Hide Scripting Console) that allows you to automate the editor, build networks programmatically, and perform batch operations.

### 🔹 Available Globals
| Global | Type | Description |
| :--- | :--- | :--- |
| `app` | `MainWindow` | The main application window. |
| `scene` | `NodeScene` | The active canvas/tab. |
| `registry` | `NodeRegistry` | Access all available node types. |
| `print()` | `Function` | Logs to the Scripting Console and Event Log. |

---

### 🛠️ Automation Methods

#### `scene.add_node_by_name(node_id, pos)`
Adds a node to the canvas.
- **`node_id`**: The slug/name of the node in the library.
- **`pos`**: Tuple `(x, y)` or `QPointF`.
- **Returns**: `NodeWidget` instance.

#### `scene.connect_nodes(node_a, port_a, node_b, port_b)`
Creates a wire between two ports.
- **`node_a`/`node_b`**: `NodeWidget` instances or node name strings.

#### `node.set_parameter(name, value)`
Programmatically updates a widget's value and propagates data downstream.

#### `app.add_new_workflow(name)`
Creates a new empty tab.

#### `app.execute_pipeline()`
Triggers the execution of the active workflow.

---

## 📖 Automation Use Cases & Examples

### 🔹 Example 1: Build a Math Pipeline Automatically
This script clears the scene and builds a multiplier network.

```python
# 1. Clear current scene
scene.clear()

# 2. Add nodes
n1 = scene.add_node_by_name("math_add", (100, 100))
n2 = scene.add_node_by_name("console_print", (400, 100))

if n1 and n2:
    # 3. Setup initial values
    n1.set_parameter("a", 50)
    n1.set_parameter("b", 25)
    
    # 4. Connect them
    scene.connect_nodes(n1, "sum", n2, "data")
    
    print("Pipeline built successfully!")
```

### 🔹 Example 2: Stress Test / Grid Generation
Create a grid of 25 Message Nodes connected in a chain.

```python
prev_node = None
for i in range(5):
    for j in range(5):
        curr = scene.add_node_by_name("message_node", (j*300, i*200))
        curr.set_parameter("msg", f"Node {i},{j}")
        
        if prev_node:
            scene.connect_nodes(prev_node, "out", curr, "msg")
        prev_node = curr
```

### 🔹 Example 3: Batch Execution
Automate running the workflow after setting a parameter.

```python
# Find a specific node by its library name
node = scene.find_node_by_name("Message Node")
if node:
    node.set_parameter("msg", "Automated Trigger")
    # Run the whole pipeline
    app.execute_pipeline()
```

---

## 🛠️ Advanced: Node Internal Access
You can access the underlying Python logic of any node on the canvas via `node.node_definition`.

```python
# Access the actual BaseNode instance
logic = node.node_definition
print(f"Node Class: {type(logic).__name__}")
print(f"Current parameters: {logic.parameters}")
```
