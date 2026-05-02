# Release v1.0.5: Loop Execution & Flow Engine Refactor

## 🚀 Overview
This release resolves a critical deadlock in the node execution engine that previously caused "For Loop" and "Loop Body" nodes to stall. It also introduces a more robust flow-based execution model with recursive data pulling.

## 🛠 Key Fixes & Improvements

### 1. Loop Deadlock Resolution
- **Removed Non-Reentrant Lock:** Eliminated the `_exec_lock` in `NetworkExecutor` that was preventing nested flow calls. This allows nodes like `Loop Body` to re-trigger the execution flow for every iteration without hanging the engine.
- **Sequential Consistency:** Maintained execution order through proper `asyncio` task tracking and `await` patterns, ensuring that loops process indices in the correct sequence.

### 2. Advanced Flow Engine Enhancements
- **Recursive Data Pulling:** Nodes now automatically "pull" updated values from upstream data-only nodes (like Variables or Math nodes) immediately before execution. This ensures that every iteration of a loop uses the most current data.
- **Selective Reactive Updates:** Refined the reactive propagation logic. In "Flow Mode," data updates now only trigger downstream nodes if those nodes do not have execution pins (pure data nodes), preventing redundant executions.
- **`use_exec` Property:** Introduced a `use_exec` flag in node definitions. This allows developers to create clean, data-only nodes that don't clutter the UI with execution pins when they aren't needed.

### 3. Node & Workflow Updates
- **For Loop Node:** Streamlined the Python implementation to be more efficient and trigger only the necessary downstream pins.
- **Variable Node:** Added an `on_parameter_changed` hook to cast and propagate values immediately when edited in the UI.
- **Loop Operation Example:** Updated the `loop_operation_example.json` workflow to demonstrate a 50-iteration string concatenation chain, fully verified to run to completion.

## 📦 How to Verify
1. Load the `workflows/loop_operation_example.json` in the application.
2. Click **Run**.
3. Observe the `Log Panel` or terminal output; you should see "Now printing ::====>>> 0" through "49" without any delays or stalls.

---
**Full Commit Hash:** `396c869`
**Tag:** `v1.0.5`
