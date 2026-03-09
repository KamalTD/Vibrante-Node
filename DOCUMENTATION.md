# Node-Based Pipeline Editor - Feature Documentation

This document summarizes the features and improvements implemented in the current version of the Python Node-Based Desktop Application.

## Core Features

### 1. Interactive Node Widgets
Nodes now support embedded UI components that allow users to input data directly on the canvas.
- **Text Box (`QLineEdit`):** For single-line string inputs.
- **Multiline Text Area (`QTextEdit`):** For large text blocks.
- **Spin Boxes (`QSpinBox`, `QDoubleSpinBox`):** For integer and floating-point numbers.
- **Checkbox (`QCheckBox`):** For boolean toggles.
- **Dropdown (`QComboBox`):** Supports a list of predefined options (configured via CSV in the Node Builder).
- **Slider (`QSlider`):** For intuitive numerical range selection.

### 2. Advanced Connection System
- **Bidirectional Initiation:** Start a wire from either an output or an input port.
- **Single Connection Rule:** Input ports are restricted to exactly one incoming wire to ensure logical data flow.
- **Redrag to Disconnect:** Pulling an existing wire away from an input port automatically disconnects it and allows it to be moved or deleted.
- **Visual Feedback:** Wires are styled in black and become selectable for deletion.

### 3. Fancy Event Log Panel
A dedicated dockable window at the bottom of the application provides real-time feedback:
- **Color-Coded Levels:**
  - `[EXEC]` (Cyan): Execution start/stop events.
  - `[OK]` (Green): Successful node completion and output data.
  - `[ERROR]` (Red): Detailed error reports and stack traces.
  - `[INFO]` (Purple): General application status.
- **Auto-Scrolling:** Ensures the latest events are always visible.

### 4. Workflow Execution Engine
- **Asynchronous Execution:** Uses `asyncio` in a dedicated background thread to prevent UI freezing during long-running tasks.
- **Topological Sorting:** Automatically determines the correct execution order based on node connections.
- **Data Propagation:** Seamlessly passes data from widgets and output ports to connected input ports.
- **Visual Status:** Nodes change color based on their state (`running`, `success`, `failed`).

### 5. Canvas Interactions
- **Delete Key:** Quickly remove selected nodes or wires.
- **Panning:** Middle-mouse button dragging for easy navigation across large workflows.
- **Zooming:** Mouse wheel support for zooming in and out.
- **Context Menu:** Right-click on the canvas to quickly add nodes from the registry.

## Example Nodes Included
- **Math Add:** Adds two numbers.
- **String Concat:** Combines strings with a separator.
- **Logic Compare:** Performs greater-than and equality checks.
- **Async Delay:** Demonstrates non-blocking sleep.
- **Fruit Selector:** Showcases the dropdown (QComboBox) widget.
- **Console Print:** Logs input data to the system console and the Log Panel.
- **Message Node:** Simple string passthrough with widget input.

## Technical Improvements
- **Node Registry:** Centralized management of builtin and custom JSON-defined nodes.
- **Robust Serialization:** Workflows can be saved and loaded as JSON, preserving node positions, parameters, and connections.
- **Unified Port Model:** Handles both builtin Python classes and dynamic JSON definitions consistently.
