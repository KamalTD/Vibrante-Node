# Release Notes — Vibrante-Node v1.8.1

**Release date:** 2026-04-26
**Build:** Python 3.10 / PyInstaller

---

## Overview

v1.8.1 is a targeted bugfix patch addressing reactive data-flow issues in the node widget and a code-preservation bug in the Node Builder.

---

## Bug Fixes

### Reactive Data Flow (`node_widget.py`)
- **`on_parameter_changed` stale value** — Downstream nodes were receiving the previous output value on the first change after a wire was plugged. Root cause: `_propagate_all_outputs()` ran synchronously before the `on_parameter_changed` coroutine had a chance to execute and update outputs via `set_output()`. Both `set_parameter` and `_update_param` now await `on_parameter_changed` to completion before triggering downstream propagation.

### Node Builder (`node_builder.py`)
- **Execute method reset on port edit** — Editing inputs or outputs in the Node Builder table was silently overwriting user-written code inside the `async def execute` method. The `[SET-OUTPUT-START/END]` and `[EXEC-OUT-START/END]` blocks were being regenerated on every table/metadata change. These blocks are now only regenerated when the exec checkboxes change (`update_exec_hints` flag), preserving custom execute logic during port edits.
