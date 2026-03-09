# Vibrante-Node User Guide

Welcome to Vibrante-Node! This guide will help you get started with building and executing visual workflows.

## 🕹️ Interface Basics

-   **Node Library (Left)**: Browse and search for nodes. Drag-and-drop or double-click to add them to the canvas.
-   **Main Canvas (Center)**: Your workspace.
    -   **Pan**: Middle-mouse button drag.
    -   **Zoom**: Mouse wheel.
    -   **Delete**: Select an item and press the `Delete` key or use the Trash icon in the toolbar.
-   **Event Log (Bottom)**: Real-time feedback on execution, outputs, and errors.

## 🔗 Building a Workflow

1.  **Add Nodes**: Use the library or right-click on the canvas to add nodes.
2.  **Connect Ports**: Click and drag from an **Output Port** (right side of a node) to an **Input Port** (left side of another node).
    -   *Note: Input ports only accept one wire. Connecting a new wire will replace the old one.*
3.  **Configure Data**: Many nodes have built-in widgets like sliders, text boxes, or dropdowns. You can type data directly into these on the canvas.
4.  **Run**: Click the **Play** icon in the toolbar or press `F5`.

## 🛠️ Using the Node Builder

Vibrante-Node allows you to create your own nodes with custom Python logic:

1.  **Open Builder**: Click the "New Node" icon in the toolbar.
2.  **Configure UI**:
    -   Add **Inputs** and **Outputs** in the tables.
    -   Choose a **Widget Type** (e.g., `slider`, `dropdown`) if you want a UI control on the node.
    -   For dropdowns, enter comma-separated values in the **Options** column.
3.  **Write Logic**: Use the built-in code editor on the right.
    -   The `execute` function receives an `inputs` dictionary.
    -   It must return a dictionary where keys match your **Output** names.
4.  **Save**: Click "Save & Register". Your node will appear in the library immediately.

## 🌓 Themes

You can switch between **Dark** and **Light** modes at any time using the **Themes** menu. Themes apply globally across all windows.

## 🪵 Troubleshooting

-   **Node is Red**: The node failed during execution. Check the **Event Log** at the bottom for the specific error message and line number.
-   **Python Errors**: If your custom node has a syntax error, the Node Builder code editor will highlight the line in red in the gutter.
