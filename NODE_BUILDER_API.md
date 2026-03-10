# Vibrante-Node: Node Builder Scripting API

This guide provides a full reference for creating custom nodes using the **Node Builder**. It covers the `BaseNode` class, port configuration, lifecycle events, and common use cases.

---

## 🏗️ The `BaseNode` Class

Every custom node must be a class inheriting from `BaseNode`.

### 🔹 Core Attributes
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | Display name. |
| `category` | `str` | Library folder name. |
| `description`| `str` | Hover tooltip text. |
| `icon_path` | `str` | Local path to SVG/PNG icon. |

---

## 🛠️ Configuration Methods

These are typically called in the `__init__` method of your node.

### `self.add_input(name, data_type="any", widget_type=None, options=None)`
- **`widget_type`**: Options are `"text"`, `"text_area"`, `"int"`, `"float"`, `"bool"`, `"dropdown"`, `"slider"`, `"file"`.
- **`options`**: A list of strings used only for the `"dropdown"` widget.

### `self.add_output(name, data_type="any")`
- Adds an outgoing port for data flow.

### `self.add_parameter(name, type, default=None)`
- Defines internal state variables not necessarily linked to a port.

---

## 🔄 Lifecycle Hooks (Events)

### `on_plug_sync(self, port_name, is_input, other_node, other_port_name)`
- **Thread**: Main GUI (Synchronous).
- **Use Case**: Immediate UI updates or data copying when a wire is connected.
- **Example**: `val = other_node.get_parameter(other_port_name)`

### `on_unplug_sync(self, port_name, is_input)`
- **Thread**: Main GUI (Synchronous).
- **Use Case**: Resetting a widget or clearing data when a wire is removed.

### `on_parameter_changed(self, name, value)`
- **Trigger**: When a user types in a text box, moves a slider, etc.
- **Use Case**: Real-time mirroring of inputs to outputs or updating internal calculations.

### `async def execute(self, inputs)`
- **Trigger**: When the user clicks "Run Workflow".
- **Inputs**: A dictionary `{port_name: value}`.
- **Returns**: A dictionary `{output_port_name: value}`.

---

## 📖 Practical Node Scenarios

### 1. The Real-Time Mirror (Pass-through)
A node that instantly reflects its input to its output as you type.

```python
def on_parameter_changed(self, name, value):
    if name == "input_msg":
        self.parameters["out"] = value # Mirror to output instantly
```

### 2. Reactive Data Fetcher
A node that queries its connected neighbor for configuration.

```python
def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
    if is_input:
        # Get data from the node we just connected to
        neighbor_data = other_node.get_parameter(other_port_name)
        # Update our own widget with that data
        self.set_parameter("config_text", neighbor_data)
```

### 3. Asynchronous Timer (Non-blocking)
Wait for a duration without freezing the UI.

```python
async def execute(self, inputs):
    delay = inputs.get("seconds", 1.0)
    await asyncio.sleep(delay) # Use await, NEVER time.sleep
    return {"done": True}
```

---

## 💡 Best Practices & Tips
- **Safely Access Data**: Use `self.get_parameter(name)` or `self[name]` to avoid KeyErrors.
- **Logging**: Use `self.log_info("message")`, `log_success`, or `log_error` to communicate with the user via the Event Log.
- **Widget Control**: Use `self.set_parameter(name, value)` to programmatically update UI widgets from within your code.
