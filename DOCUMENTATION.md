# Vibrante-Node - Technical Documentation

This document detail the advanced features and technical architecture of Vibrante-Node.

## 1. Professional Python Code Editor
The Node Builder now features a fully-integrated, professional-grade source code editor.
- **Intelligent Syntax Highlighting:** Dracula-inspired theme for keywords, builtins, decorators, and multi-line strings.
- **Line Numbers & Gutter:** Clear visual tracking of code structure.
- **Auto-Indentation:** Intelligent whitespace handling and automatic 4-space indent after colons (`:`).
- **Bracket Matching:** Instant visual feedback for matching `()`, `[]`, and `{}`.
- **Auto-Closing:** Automatically completes quotes and brackets.
- **Real-time Linting:** Instant syntax error detection with red line highlighting in the gutter.
- **IntelliSense:** Popup completion suggestions for Python keywords and common node methods (`execute`, `on_plug_sync`, etc.).
- **Indentation Control:** Support for block indentation via **Tab** and de-indentation.
- **Font Zooming:** **Ctrl + Mouse Wheel** to scale text size.

## 2. Reactive Lifecycle System
Nodes are designed to be interactive and aware of their state within the graph.
- **Synchronous Triggers:** `on_plug_sync` and `on_unplug_sync` execute immediately on the GUI thread for instant UI feedback.
- **Asynchronous Triggers:** `on_plug` and `on_unplug` run in a background `asyncio` thread for heavy processing or IO tasks.
- **Parameter Change Hook:** `on_parameter_changed` allows nodes to reactively update their outputs or internal state as the user interacts with widgets.
- **Robustness:** All lifecycle events are wrapped in exception handlers to prevent custom code errors from crashing the main application.

## 3. Real-Time Data Propagation
Vibrante-Node implements a recursive data propagation model.
- **Immediate Push:** When a source node's value changes, it recursively identifies all downstream nodes and updates their matching input widgets.
- **Live Monitoring:** Destination widgets update their displayed values in real-time even when disabled, providing a live view of data flowing through the wire.
- **Data Initialization:** All ports (input and output) are initialized in the `parameters` dictionary, ensuring consistent data access during connection events.

## 4. Advanced UI Architecture
- **Dynamic Node Scaling:** Nodes automatically calculate their bounding box based on port count and child widget dimensions.
- **Vertical Centering:** Automated distribution of parameter widgets within the node body.
- **Thread-Safe Logging:** A `pyqtSignal` based logging system ensures that nodes running in background threads can safely update the Event Log UI.
- **Crash Protection:** A global exception hook captures unhandled errors and saves them to `crash.log` for debugging.

## 5. Extended Interactive Widgets
- **File Selector:** Launches a native OS file dialog and stores the absolute path.
- **Slider Control:** Interactive horizontal sliders for numerical range selection.
- **Dropdown (Combo Box):** Configurable list of options defined via CSV in the Node Builder.
- **Multiline Text Area:** Constrained to a specific height to prevent node overflow while allowing large data entry.
