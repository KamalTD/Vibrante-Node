# Vibrante-Node User Guide

Welcome to Vibrante-Node! This guide will help you get started with building and executing visual workflows.

## 🕹️ Interface Basics

-   **Node Library (Left)**: Browse and search for nodes. Drag-and-drop or double-click to add them to the canvas.
-   **Main Canvas (Center)**: Your workspace.
    -   **Pan**: Middle-mouse button drag.
    -   **Zoom**: Mouse wheel.
    -   **Focus**: Press `F` to focus on selected nodes or the center of the graph.
    -   **Copy/Paste**: Press `Ctrl+C` to copy selected nodes and `Ctrl+V` to paste them at the cursor position.
    -   **Delete**: Select an item and press the `Delete` key.
-   **Event Log (Bottom)**: Real-time feedback on execution, outputs, and connection events.

## 🔗 Building a Workflow

1.  **Add Nodes**: Use the library or right-click on the canvas to add nodes.
2.  **Connect Ports**: Click and drag from an **Output Port** (right side) to an **Input Port** (left side).
    -   *Live Sync*: When you connect two nodes, the data from the source is instantly pushed to the destination.
3.  **Configure Data**: Interact with widgets (text boxes, sliders, etc.) directly on the node.
    -   *Reactive Flow*: Destination widgets are disabled when connected but will **update live** as you change the source node's values.
4.  **Run**: Click the **Play** icon in the toolbar or press `F5`.

## ⚙️ Advanced Execution Flow (v1.0.5+)

Vibrante-Node uses a hybrid **Flow + Data** execution model:

-   **Flow Pins (Exec)**: Use `exec_in` and `exec_out` (white ports) to define the order of operations. Execution follows these wires sequentially.
-   **Data Pulling**: Before a node executes, it automatically "pulls" the most recent values from all connected data nodes (e.g., Variable or Math nodes), even if they don't have execution pins.
-   **Data-Only Nodes**: You can create nodes without `exec` pins (using the `use_exec: false` property in the Node Builder). These nodes are reactive — they update their outputs immediately when their inputs change and are "pulled" by downstream flow nodes.

### 🧠 Topological Execution Engine
For workflows without explicit execution wires (Data-Flow only), the engine uses **Topological Sorting** to determine the correct order of operations. This ensures that every node has its required data before it begins processing, effectively resolving dependencies layer by layer.

## 🔄 Working with Loops

To iterate over data or repeat operations, use the **Loop** nodes:

1.  **For Loop**: Generates a range of indices (e.g., 0 to 10).
    -   Connect its `indices` output to a `Loop Body`.
    -   Connect its `exec_out` to start the iteration.
2.  **Loop Body**: Executes its downstream chain for every item in the provided list.
    -   `current_index`: Provides the current value for the iteration.
    -   `exec_out`: Triggers once for every item.
    -   `exec_on_finished`: Triggers once the entire loop is complete.
3.  **Break Condition**: You can connect a boolean value to the `break_condition` input of the `Loop Body` to stop the loop early.
4.  **While Loop** (v1.6.0): The `while_loop` node repeats its `exec_out` chain while its `condition` input is `True`. Connect a boolean-producing node to `condition` to control when the loop stops.

## 🐍 Python Script Node (v1.6.0)

Place a `python_script` node on the canvas and click the **Edit Script** button to author custom Python code directly in the app.

- Your script receives an `inputs` dict containing the current values of all connected input ports.
- Assign your primary output to a variable named `result` — it will be published to the `result` output port.
- Scripts are saved into the workflow JSON and restored automatically when you reopen the file.

**Example script:**
```python
val = inputs.get('data')
result = val.upper() if isinstance(val, str) else val
```

## 🧩 Utility Nodes (v1.6.0)

New helper nodes are available in the node library for common data operations:

| Category | Available Nodes |
|---|---|
| **List** | `create_list`, `get_list_item`, `list_length` |
| **Dictionary** | `create_dictionary`, `get_dict_value`, `set_dict_value` |
| **String** | `concat`, `split`, `replace`, `lowercase`, `uppercase`, `string_length` |

These nodes are data-only (no exec pins) and update reactively as their inputs change.

## 🎬 Prism Pipeline Integration (v1.6.0)

Vibrante-Node v1.6.0 includes full integration with [Prism Pipeline](https://prism-pipeline.com/).

### Getting started with Prism nodes

1.  **Add `prism_core_init`**: Drag a `prism_core_init` node onto the canvas. Set the `prism_root` path to your Prism installation directory.
2.  **Run**: When you execute the graph, the engine automatically initializes PrismCore before any other node runs. No wiring between the init node and other Prism nodes is required.
3.  **Add Prism nodes**: Browse the `Prism` category in the node library. All `prism_*` nodes share the same initialized core automatically.

### Available Prism node groups

| Group | What it does |
|---|---|
| Core | Initialize and inspect PrismCore |
| Entities | Retrieve assets, shots, build or create entities |
| Products | Manage product versions, import products |
| Media | Access media and media versions, create playblasts |
| Scenes | Open, save, and manage scene files |
| Config | Read and write Prism configuration values |
| Projects | List, create, and switch projects |
| Departments/Tasks | Browse departments, tasks, and categories |
| Plugins | List and retrieve loaded Prism plugins |
| USD | Resolve USD layer and entity paths |
| Advanced | Eval, monkey-patch, callbacks, popups, token auth |

## 🛠️ Using the Node Builder

Vibrante-Node allows you to create your own nodes with custom Python logic:

1.  **Open Builder**: Click the "New Node" icon in the toolbar.
2.  **Configure UI**:
    -   Add **Inputs** and **Outputs** using the tables.
    -   Select **Type** and **Widget** using the interactive dropdowns.
3.  **Write Logic**:
    -   `on_plug_sync`: Use this to react immediately to connections (e.g., `other_node.get_parameter(other_port_name)`).
    -   `on_parameter_changed`: Use this to update outputs reactively as the user types.
    -   `execute`: The main logic run when the workflow executes.
4.  **Save**: Click "Save & Register". Your node is now ready to use.

**Gemini Assistance**: When creating node logic in the Node Builder you can enable Gemini assistance to generate starter code, prompt templates, or example snippets. It is optional and configurable; always validate generated code before running.

## 🌓 Themes

You can switch between **Dark** and **Light** modes at any time using the **Themes** menu. Themes apply globally.

## 🪵 Troubleshooting

-   **Node is Red**: The node failed during execution. Check the **Event Log** for the error.
-   **Widgets are Disabled**: This is normal! Widgets are disabled when they are receiving data from another node via a wire.
-   **Prism nodes show "PrismCore not initialized"**: Make sure a `prism_core_init` node is present in the graph and that `prism_root` points to a valid Prism installation.
-   **Crashes**: If the app closes, check `crash.log` in the project folder for details.
