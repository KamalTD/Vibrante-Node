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

## 🖥️ Python Code Editor (Export)

Export your workflow as Python and edit, run, and debug it in a professional IDE-style editor:

1.  **Export**: Go to **File > Export Workflow as Python** (or `Ctrl+Shift+E`).
2.  **Edit**: The generated code is fully editable with syntax highlighting, auto-completion, bracket matching, and live syntax linting.
3.  **Run**: Press **F5** or click the **Run** button. See stdout/stderr output in real-time in the **Output** panel.
4.  **Stop**: Click **Stop** to kill a running script.
5.  **Fix with AI**: If your code has errors, click **Fix with AI** to send the code and error to Google Gemini. Review the suggested fix and accept or reject it.
6.  **Save**: Press `Ctrl+S` to save the script to a `.py` file.

## 🔇 Event Log Silent Mode

The Event Log supports a **Silent Mode** toggle in the filter bar:
-   When enabled, only **Errors** and **Warnings** are shown. Info, Execution, and Output messages are suppressed.
-   Silent mode also skips all internal log processing for filtered messages, reducing overhead during execution.
-   Toggle it on for faster execution when you only need to see errors.

## 🪵 Troubleshooting

- **Python Script Node (`python_script`)**: Place the node on the canvas and click the `Edit Script` button to author Python code. The script executes with access to a local `inputs` dictionary containing current input values and `params` for node parameters. Assign your output to `result` to publish it to the node's `result` output port.

- **Example script**:
```python
# Example: upper-case input
val = inputs.get('data')
if isinstance(val, str):
    result = val.upper()
else:
    result = val
```

- **Saved Workflows**: The editor writes the script into the node's saved `python_code` parameter. The engine applies saved parameters at run-time so scripts persist across sessions.

- **Gemini Assistance in Node Builder**: When creating node logic in the Node Builder you can enable Gemini assistance to generate starter code, prompt templates, or example snippets. Gemini integration is optional and configurable in the app settings; it is intended to speed up authoring but always validate generated code before running.

## 🪵 Troubleshooting
-   **Node is Red**: The node failed during execution. Check the **Event Log** for the error.
-   **Widgets are Disabled**: This is normal! Widgets are disabled when they are receiving data from another node via a wire.
-   **Crashes**: If the app closes, check `crash.log` in the project folder for details.
