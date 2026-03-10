# Vibrante-Node - Technical API Documentation

This document provides a comprehensive reference for the Vibrante-Node Scripting API. Use this guide to build custom nodes with the integrated Python editor.

---

## 🏗️ Core Class: `BaseNode`

All custom nodes must inherit from `BaseNode`. This class provides the fundamental interface for ports, parameters, logging, and lifecycle events.

### 🔹 Attributes (Class Level)
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | The display name of the node. |
| `category` | `str` | The library category (e.g., "Math", "IO"). |
| `description` | `str` | Tooltip/help text for the node. |
| `icon_path` | `str` | Relative path to an SVG/PNG icon. |

---

## 🛠️ API Methods

### 🔹 Configuration (Usually in `__init__`)

#### `self.add_input(name, data_type="any", widget_type=None, options=None)`
Adds an input port to the node.
- **`name`**: Unique identifier for the port.
- **`data_type`**: Type constraint (e.g., "int", "string").
- **`widget_type`**: Optional UI widget: `"text"`, `"text_area"`, `"int"`, `"float"`, `"bool"`, `"dropdown"`, `"slider"`, `"file"`.
- **`options`**: List of strings for `"dropdown"`.

#### `self.add_output(name, data_type="any")`
Adds an output port to the node.

#### `self.add_parameter(name, param_type, default=None)`
Defines a custom internal parameter not necessarily linked to a port.

---

### 🔹 Data Access

#### `self.get_parameter(name, default=None)`
Retrieves the current value of an input or parameter.
- **Note**: Can be used to read data from `other_node` during plug events.

#### `self[name]` (Shortcut)
Access parameters using dictionary syntax: `value = self["my_port"]`.

---

### 🔹 Logging
Messages are sent to the **Event Log** panel.
- `self.log_info(msg)`: Purple text.
- `self.log_success(msg)`: Green text.
- `self.log_error(msg)`: Red text (use for critical failures).

---

## 🔄 Lifecycle Hooks

### 🔹 `on_plug_sync(port_name, is_input, other_node, other_port_name)`
**Sync (GUI Thread)**. Called immediately when a wire is connected.
- Use this for instant UI reactions or to copy data from `other_node`.
- **`other_node`**: The node on the other end of the wire.
- **`other_port_name`**: The specific port name on the other node.

### 🔹 `on_unplug_sync(port_name, is_input)`
**Sync (GUI Thread)**. Called when a wire is removed.
- Use this to reset values or clear internal states.

### 🔹 `on_parameter_changed(name, value)`
Called whenever a user interacts with a widget on the node.
- Use this to dynamically update output values or other parameters.

### 🔹 `async on_plug(...)` / `async on_unplug(...)`
**Async (Background Thread)**. Same as sync versions but for heavy operations (IO, Network) that shouldn't freeze the UI.

---

## ⚡ Execution Logic

### `async def execute(self, inputs)`
The primary logic executed when the workflow runs.
- **`inputs`**: A dictionary containing data from all connected input ports.
- **Return**: A dictionary where keys match your **Output Port** names.

```python
async def execute(self, inputs):
    val = inputs.get("data_in", 0)
    result = val * 2
    return {"data_out": result}
```

---

## 📖 Complete Scripting Example

A reactive node that displays data from its neighbor instantly upon connection:

```python
from src.nodes.base import BaseNode

class ReactiveNode(BaseNode):
    name = "Reactive Example"
    
    def __init__(self):
        super().__init__()
        # 1. Setup Ports
        self.add_input("in_port", "any", widget_type="text")
        self.add_output("out_port", "any")
        
    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        # 2. React to connection
        if is_input:
            # Read data from the other node's output port
            data = other_node.get_parameter(other_port_name)
            self.log_info(f"Incoming data detected: {data}")
            # Automatically update our own widget
            self.set_parameter("in_port", data)

    def on_parameter_changed(self, name, value):
        # 3. Handle live user typing
        if name == "in_port":
            self.log_info(f"User is typing: {value}")
            # Update output port so next node sees it
            self.parameters["out_port"] = value

    async def execute(self, inputs):
        # 4. Standard execution
        return {"out_port": inputs.get("in_port")}

def register_node():
    return ReactiveNode
```

---

## 🛠️ UI Helpers (Inside Scripts)

When working with `other_node` in plug events, you can use these methods:
- `node.name`: Access the node's display name.
- `node.set_parameter(name, value)`: Update a widget value on that node.
- `node.log_info(msg)`: Trigger a log message from that node's context.
