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
- **IntelliSense:** Popup completion suggestions for Python keywords and common node methods (`execute`, `add_input`, etc.).
- **Indentation Control:** Support for block indentation via **Tab** and de-indentation.
- **Font Zooming:** **Ctrl + Mouse Wheel** to scale text size.

## 2. Dynamic Node Library
- **Categorized View:** Nodes are organized into logical groups (Math, IO, String, Logic, Utility) using an expandable tree structure.
- **Search & Filter:** Real-time filtering of the library based on node names.
- **Rich Metadata:** Displays high-quality **SVG icons** for every node.
- **Context Actions:** Right-click to edit or delete nodes directly from the library.

## 3. Advanced UI & Theming
- **Global Theme System:** Seamless switching between **Dark** and **Light** themes via the "Themes" menu.
- **Stylized Toolbar:** Functional icons with descriptive tooltips for workflow management.
- **Window Management:** A "Window" menu to toggle the visibility of side panels (Library and Event Log).
- **Port Labeling:** Nodes on the canvas now display clear text labels next to every input and output port.

## 4. Extended Interactive Widgets
- **File Selector:** A new widget type that provides a "..." button to launch a native OS file dialog.
- **Slider Control:** Interactive horizontal sliders for numerical range selection.
- **Dropdown (Combo Box):** Configurable list of options defined via CSV in the Node Builder.
- **Multiline Text Area:** For handling large blocks of string data.

## 5. Technical Improvements
- **Automatic Code Sync:** The Node Builder now automatically updates Python class names and node metadata in the script based on UI changes.
- **Name Validation:** Node names are automatically sanitized (replacing spaces/special chars with underscores) to ensure safe execution and file naming.
- **SVG Rendering:** Native support for rendering vector graphics in node headers and the library list.
