# Vibrante-Node User Guide

Welcome to Vibrante-Node! This guide will help you get started with building and executing visual workflows.

## 🕹️ Interface Basics

-   **Node Library (Left)**: Browse and search for nodes. **Drag-and-drop** or double-click to add them to the canvas.
-   **Main Canvas (Center)**: Your workspace.
    -   **Pan**: Middle-mouse button drag or `Space + Left Drag`.
    -   **Zoom**: Mouse wheel.
    -   **Focus**: Press `F` to focus on selected nodes.
    -   **Copy/Paste**: Press `Ctrl+C` / `Ctrl+V`.
    -   **Bypass**: Press `Ctrl+B` to toggle bypass on selected nodes.
    -   **Group**: Press `Ctrl+G` to wrap selected nodes in a Network Box (Backdrop).
    -   **Delete**: Select an item and press the `Delete` key.
-   **Event Log (Bottom)**: Real-time feedback on execution, outputs, and connection events.

## 🔗 Building a Workflow

1.  **Add Nodes**: Drag from the library or right-click on the canvas.
2.  **Connect Ports**: Click and drag from an **Output Port** to an **Input Port**.
    -   **Snapping**: Wires will automatically snap to compatible ports when dragged nearby.
    -   **Animations**: Ports scale up on hover to show they are ready for connection.
3.  **Configure Data**: Interact with widgets directly on the node.
4.  **Run**: Click the **Play** icon, press **F5**, or use the scripting console.

## 🚫 Bypassing Nodes (v1.2.0)

You can temporarily disable nodes without removing them from your workflow:
-   **Toggle**: Click the **"B" button** in the top-right corner of any node, or press `Ctrl+B` with nodes selected.
-   **Behavior**: Bypassed nodes turn semi-transparent. They skip their internal logic and instead pass the data from their **first input** directly to all outputs. Execution flow (`exec`) continues through the node normally.

## 📦 Network Boxes (Backdrops)

Organize your graph using Network Boxes:
-   **Create**: Right-click > Add Network Box, or select nodes and press `Ctrl+G`.
-   **Interact**: Move the box by dragging its **Title Bar**. Dragging the body allows you to use rubber-band selection for nodes inside.
-   **Context Menu**: Right-click a box to:
    -   **Fit to Contained Nodes**: Automatically resize the box to wrap all overlapping nodes.
    -   **Select Contained Nodes**: Select everything inside the box.

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

## 🔥 SideFX Houdini Integration (v1.2.0)

Vibrante-Node can control a live SideFX Houdini session directly from your workflows.

### Setting Up the Houdini Plugin

1. Locate the `plugins/houdini/vibrante_node.json` file in the project folder.
2. Edit the JSON file and replace the placeholders:
    - Change `<VIBRANTE NODE DIR>` to the absolute path of your Vibrante-Node folder.
    - Change `<PYTHON EXE PATH>` to the absolute path of your Python executable (e.g., `C:\Python310\python.exe`).
3. Copy the modified `vibrante_node.json` file into your Houdini **packages** directory:
    - **Windows**: `C:\Users\<USER_NAME>\Documents\houdini20.5\packages\`
    - **Linux/Mac**: `~/houdini20.5/packages/`
    *(Note: If the `packages` folder doesn't exist, create it.)*
4. Restart Houdini. You will now see a **Vibrante_Node** menu in the main menu bar and a **Vibrante** shelf tab.
5. Click the **Launch Vibrante-Node** button on the shelf to start the app.

### Using Houdini Nodes

Once the command server is running inside Houdini, the **Houdini** category appears in the Node Library with 19 nodes:

- **Scene Operations**: Query scene info, save .hip files, set timeline frame/range.
- **Node Operations**: Create, delete, cook, layout, connect nodes. Set display/render flags.
- **Parameter Operations**: Get/set single or multiple parameters, set expressions/keyframes.
- **Code Execution**: Run arbitrary Python code inside Houdini's Python interpreter.

### Example Workflow: Create a Box in Houdini

1. Add a **Hou Create Geo** node — set the name to `my_box`.
2. Add a **Hou Create Node** — set parent to `/obj/my_box`, type to `box`, name to `box1`.
3. Add a **Hou Set Parm** node — set node to `/obj/my_box/box1`, parm to `sizex`, value to `3`.
4. Connect the exec flow pins and press **Play**.

### Houdini Example Scripts

Pre-built scripts in `plugins/houdini/v_scripts_houdini/`:
- **`hou_scene_info.py`** — Query the current Houdini scene.
- **`hou_create_box_demo.py`** — Create a Geometry container with a Box SOP.
- **`hou_list_scene_nodes.py`** — List all children under `/obj`.

---

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
