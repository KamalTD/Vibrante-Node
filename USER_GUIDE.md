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

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Tab` | Open the "Add Node" search popup at the canvas centre |
| `F5` | Run the current workflow |
| `F` | Focus view on selected nodes (or graph centre) |
| `Ctrl+C` | Copy selected nodes |
| `Ctrl+V` | Paste nodes at cursor position |
| `Delete` | Delete selected nodes or wires |
| `Ctrl+E` | Open Node Builder for the selected node's definition |
| `Ctrl+R` | Reload the selected node from disk |
| `Ctrl+Shift+R` | Reload all nodes from disk |

> **Note**: Hotkeys are disabled when a text input field on the canvas has keyboard focus, so typing in widgets will not accidentally trigger shortcuts.

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

1.  **For Loop**: Generates a list of indices (e.g., 0 to N-1) and fires `exec_out` **once** after building the full list — it does not iterate itself.
    -   Connect its `indices` output to a `Loop Body`'s list input.
    -   Connect its `exec_out` to the `Loop Body`'s `exec_in` to start iteration.
2.  **Loop Body**: Receives the index list and iterates over it, executing its downstream chain once per item.
    -   `current_index`: Provides the current value for the iteration.
    -   `exec_out`: Triggers once for every item in the list.
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

1.  **Open Builder**: Click the "New Node" icon in the toolbar, or press `Ctrl+E` with a node selected to edit an existing definition.
2.  **Configure UI**:
    -   Set a **Display Name** (v1.8.x) — the text shown in the node's canvas header, independent of the node's internal ID.
    -   Add **Inputs** and **Outputs** using the tables.
    -   Select **Type** and **Widget** using the interactive dropdowns.
3.  **Write Logic**:
    -   `on_plug_sync`: Use this to react immediately to connections (e.g., `other_node.get_parameter(other_port_name)`).
    -   `on_parameter_changed`: Use this to update outputs reactively as the user types. Also called during execution when upstream data changes mid-run (reactive nodes). Not called during pre-execute input sync.
    -   `execute`: The main logic run when the workflow executes.
4.  **Save**: Click "Save & Register". Your node is now ready to use.

**Gemini Assistance**: When creating node logic in the Node Builder you can enable Gemini assistance to generate starter code, prompt templates, or example snippets. It is optional and configurable; always validate generated code before running.

## 🔄 Editing & Reloading Nodes (v1.8.x)

After a node definition has been saved you can iterate on it without closing and reopening the app:

1.  **Edit**: Select the node on canvas and press `Ctrl+E` (or right-click > "Edit Node"). The Node Builder opens with that node's current definition pre-loaded.
2.  **Save changes** in the Node Builder — this writes the updated JSON to disk.
3.  **Reload**: Press `Ctrl+R` (or right-click > "Reload Node"). The canvas widget is rebuilt in place — ports are updated, saved parameter values are re-applied, and connections that are still compatible are preserved.
4.  To reload every node type at once (e.g., after a bulk edit), press `Ctrl+Shift+R`.

## 🚦 Init First Nodes (v1.8.x)

Some nodes need to be fully initialized before any other node in the graph runs — for example, an authentication node or a server-connection node. You can mark any node as **Init First**:

-   Right-click the node on the canvas and select **"Init First"** to promote it. A badge appears on the node header.
-   Right-click again and select **"Remove Init First"** to demote it.

When a workflow is loaded, all Init First nodes (those with `init_priority > 0`) are created and wired up **before** all other nodes. This ensures that downstream nodes that depend on the init result receive it correctly on first execution.

## 🌓 Themes

You can switch between **Dark** and **Light** modes at any time using the **Themes** menu. Themes apply globally.

## 🪵 Troubleshooting

-   **Node is Red**: The node failed during execution. Check the **Event Log** for the error.
-   **Widgets are Disabled**: This is normal! Widgets are disabled when they are receiving data from another node via a wire.
-   **Prism nodes show "PrismCore not initialized"**: Make sure a `prism_core_init` node is present in the graph and that `prism_root` points to a valid Prism installation.
-   **Crashes**: If the app closes, check `crash.log` in the project folder for details.
-   **Stale ports after editing a node**: If a node's ports look outdated after you edited its JSON definition, select the node and press `Ctrl+R` to reload it from disk. All live instances of that node type on the canvas will be refreshed.
