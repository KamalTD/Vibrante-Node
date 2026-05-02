# Release Notes — Vibrante-Node v1.8.3

**Release date:** 2026-04-30
**Build:** Python 3.10 / PyInstaller

---

## Overview

v1.8.3 is a targeted bugfix patch that fixes incorrect `on_parameter_changed` calls being fired during node execution, which caused cascading side effects, premature data propagation, and unexpected flow triggers in complex graphs.

---

## Bug Fixes

### Engine — `on_parameter_changed` Called During Execution (`engine.py`)

- **`on_parameter_changed` called during pre-execute input sync** — Before calling a node's `execute`, the engine synced incoming connection values and called `on_parameter_changed` for each one. Nodes like `TwoWaySwitchNode` that call `set_output` inside `on_parameter_changed` would then eagerly propagate intermediate/stale values to downstream nodes before `execute` had run, causing incorrect or double-propagated results. Fixed by removing the `on_parameter_changed` call from the pre-execute sync phase — parameters are already set directly and `execute` receives the correct values in `inputs`.

- **`on_parameter_changed` called during reactive output propagation** — When a node called `set_output` during its `execute`, the engine's output handler fired `on_parameter_changed` on every downstream data node. This caused cascading `set_output` calls from downstream `on_parameter_changed` implementations while the upstream node's `execute` was still running, potentially triggering flow execution at unexpected times. Fixed by removing the `on_parameter_changed` call from the reactive data propagation in the output handler. Downstream data nodes still receive updated parameter values (the direct parameter assignment is kept) and are correctly pulled via `_run_single_node_impl` when a flow node needs them.

**Nodes not affected:** `WhileLoopNode`, `ForEachNode` — these read `condition`, `break_condition`, and `continue_condition` directly from `self.parameters`, which are still updated reactively by the engine's output handler.
