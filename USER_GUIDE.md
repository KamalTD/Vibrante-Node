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
-   **Data-Only Nodes**: You can create nodes without `exec` pins (using the `use_exec: false` property in the Node Builder). these nodes are reactive—they update their outputs immediately when their inputs change and are "pulled" by downstream flow nodes.

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

## 🌓 Themes

You can switch between **Dark** and **Light** modes at any time using the **Themes** menu. Themes apply globally.

## 🪵 Troubleshooting

-   **Node is Red**: The node failed during execution. Check the **Event Log** for the error.
-   **Widgets are Disabled**: This is normal! Widgets are disabled when they are receiving data from another node via a wire.
-   **Crashes**: If the app closes, check `crash.log` in the project folder for details.
