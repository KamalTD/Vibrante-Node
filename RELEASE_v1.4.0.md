# Release v1.4.0: Node Builder Fix, VFX Pipeline Nodes & BaseNode Improvements

Version 1.4.0 fixes a critical bug in the Node Builder where manually edited Python code was erased on Save & Register, adds `set_parameter()` to BaseNode, improves engine error handling, and ships three new VFX pipeline nodes.

---

## What's New

### Bug Fix: Node Builder "Save & Register" No Longer Clears Manual Code Edits

The `save_node()` function previously called `_sync_ui_to_code()` as its first step, which regenerated the code from the UI tables — overwriting any hand-written logic in the execute method if the 1-second debounce timer hadn't fired yet.

**Fix:** `save_node()` now stops the pending timer and calls `_sync_code_to_ui()` instead, parsing the latest code to update the tables. The code editor is always the source of truth.

### BaseNode: `set_parameter()` Added

`BaseNode.set_parameter(name, value)` is now available. It handles the special case of dropdown ports: if `value` is a list, it updates the port's options and selects the first item. This fixes an `AttributeError` crash when nodes that call `set_parameter()` in `__init__` were dropped onto the canvas.

### Engine: Safer Node Initialization

Node instantiation in `NetworkExecutor` is now wrapped in try/except. If a node's `__init__` raises an error, it is reported cleanly via `node_error` signal instead of crashing the executor.

### New Nodes: VFX Pipeline

| Node | Category | Description |
|------|----------|-------------|
| `Get_Project` | VFX_Pipeline | Retrieves project context/path |
| `Parse_Path` | VFX_Pipeline | Parses and splits file paths |
| `Test` | General | Utility test node |

### UI: Dark Theme Checkbox Styles

QCheckBox widgets in the Node Builder dialog are now properly styled for the dark theme — white label text, dark background indicator, and a green highlight when checked.

### Other

- `.gitignore` now ignores the `main/` directory.
- Node categories renamed from `Trend_Pipeline` → `VFX_Pipeline`.

---

## Upgrade Notes

No breaking changes. Existing node JSON files and workflows remain compatible.
