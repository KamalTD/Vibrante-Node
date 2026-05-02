# Release v1.1.0: Professional Code Editor, Execution Optimizations & Event Log Enhancements

## Overview

Version 1.1.0 introduces a fully-featured IDE-style Python Code Editor for exported workflows, major execution engine performance optimizations, and a new Silent Mode for the Event Log. This release significantly improves both the developer experience and runtime performance.

---

## New Features

### Professional Python Code Editor (Export Dialog)
The "Export Workflow as Python" dialog has been completely redesigned as a professional IDE-like code editor:
- **Full CodeEditor integration** with line numbers, syntax highlighting (Dracula theme), bracket matching, auto-completion, auto-indentation, and live syntax linting.
- **Code Execution**: Run exported Python scripts directly from the editor with real-time stdout/stderr output via `QProcess`.
- **Stop Button**: Kill running scripts mid-execution.
- **AI-Powered Fix**: Send code with errors to Google Gemini for automatic debugging and correction with accept/reject workflow.
- **Dracula-Themed UI**: Toolbar, editor, output panel, and status bar styled with a consistent dark Dracula color scheme.
- **Status Bar**: Real-time cursor position (Ln/Col) and execution status display.
- **Keyboard Shortcuts**: F5 to Run, Ctrl+S to Save, Ctrl+Shift+C to Copy.

### Event Log Silent Mode
- **Silent Mode toggle** added to the Event Log filter bar.
- When enabled, suppresses all Info, Execution, and Output messages — only Errors and Warnings are displayed.
- **Fast-path optimization**: In silent mode, filtered messages skip all processing (regex, object creation, UI updates) for zero overhead.
- **Signal handler short-circuits**: Node started, output, and log signal handlers in the main window skip log message construction entirely when silent mode is active.

---

## Performance Optimizations

### Execution Engine (engine.py)
- **Eliminated artificial delays**: All `asyncio.sleep(0.05)` and `asyncio.sleep(0.1)` calls in ForEachNode, WhileLoopNode, SequenceNode, and the engine poll loop replaced with `asyncio.sleep(0)`. This removes 150ms of idle time per loop iteration (a ForEach over 100 items saves ~15 seconds).
- **Indexed outgoing connections**: Pre-calculated `_outgoing_data_conns` and `_outgoing_exec_conns` dictionaries keyed by `(node_id, port_name)` replace O(N) full scans of all connections on every `set_output` call with O(1) dict lookups.
- **Cached node widget lookups**: `_find_node_widget` now uses a dictionary cache built once at execution start instead of O(N) linear scan per signal handler call.

### UI Signal Optimization
- `_on_node_started`, `_on_node_output`, and `_on_node_log` handlers skip log message string formatting and signal emission when the Event Log's silent mode is active, reducing per-node UI overhead.

---

## Bug Fixes
- Fixed the "Export Workflow as Python" dialog using a read-only `QPlainTextEdit` with no editing capabilities — now uses the full `CodeEditor` widget.
- Fixed node widget cache not being invalidated after execution finishes.

---

## Files Changed
- `src/ui/export_python_dialog.py` — Complete rewrite (74 lines to ~300 lines)
- `src/ui/log_panel.py` — Silent Mode toggle and fast-path filtering
- `src/core/engine.py` — Indexed connection lookups, reduced sleep delays
- `src/nodes/builtins/nodes.py` — Removed artificial sleep delays from loop nodes
- `src/ui/window.py` — Widget cache, signal handler optimizations

---

**Branch:** `feature/topological-engine-and-foreach-improvements`
