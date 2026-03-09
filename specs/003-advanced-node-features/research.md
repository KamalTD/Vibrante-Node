# Research: Advanced Node Features & Persistence

## Decision: AST-based Code Parsing for Sync
- **Rationale**: The `ast` module allows us to inspect the Python code structure without executing it. We can look for `self.add_input` and `self.add_output` calls in the `__init__` method to update the UI tables.
- **Implementation**: Use `ast.parse` to get the tree, then `ast.NodeVisitor` to find specific method calls. This is safer than regex and more reliable for real-time sync.
- **Alternatives considered**: Regex (too fragile for complex code), `exec()` (unsafe for parsing during typing).

## Decision: JSON-based Node Registry
- **Rationale**: Storing node definitions as JSON makes them language-agnostic at the metadata level and allows for easy persistence. The Python code is stored as a string within the JSON.
- **Implementation**: A central `NodeRegistry` class will watch the `nodes/` directory, load JSONs into Pydantic models, and use `importlib` to turn the `python_code` string into executable classes.
- **Alternatives considered**: Python-only plugins (harder to manage metadata and UI state), Database (overkill for this scale).

## Decision: Execution Context Mapping
- **Rationale**: To pass data between nodes, the engine needs a central "runtime context" mapping `node_id` to its outputs.
- **Implementation**: The `Executor` will maintain a dictionary of results. For each node, it will pull inputs from this dictionary based on connection port mappings.
- **Async Execution**: Use `asyncio` or `QThreadPool`. Given the PyQt5 environment, `QRunnable` with signals for UI feedback is preferred for heavy tasks, but `asyncio` is better for dependency management. We will use `asyncio` for the logic and `Signals` for UI updates.

## Decision: Library Panel for Management
- **Rationale**: A dedicated sidebar (QDockWidget) for the Node Library provides a better UX for browsing and managing node types.
- **Features**: Search, Categories, Right-click for Edit/Delete.
