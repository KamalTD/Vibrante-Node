<!--
<sync_impact_report>
- Version change: 1.0.0 → 2.0.0
- List of modified principles:
  - Node-First Architecture → Modular Python Architecture (Redefined for Python/Desktop)
  - JSON-Driven Pipelines → Workflow Serialization & Integrity
  - Observability by Default → Stability & Sandboxed Execution
  - Extensible Node System → Scriptable Extensibility
  - Robust Error Handling → Separation of Concerns (UI/Logic/Engine)
  - Parallel Execution Support → Performance & Async Execution
- Added sections: User Experience Consistency, Testing Standards
- Removed sections: Hybrid Interface (Replaced by Desktop focus)
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: Update existing research and plan files to reflect Python transition.
</sync_impact_report>
-->

# node_based_app Constitution (Python Edition)

## Core Principles

### I. Modular Python Architecture
The application must maintain a strict separation between UI (View), Node Logic (Controller), and Execution Engine (Model). All code must utilize Type Hints, comprehensive Docstrings (Google style), and modular structure to ensure long-term maintainability.

### II. Scriptable Extensibility
Developers MUST be able to add custom nodes via external Python scripts without modifying the core codebase. The system should dynamically discover and load these nodes at runtime.

### III. Stability & Sandboxed Execution
Invalid node scripts or runtime execution errors MUST be caught and reported gracefully. A single node failure must not crash the entire application or corrupt the UI state. Execution should be sandboxed where possible.

### IV. Workflow Serialization & Integrity
All workflows must be serializable to a structured format (JSON/YAML). Serialization logic must include versioning and integrity checks to ensure compatibility across application updates.

### V. Performance & Async Execution
The engine must support efficient dependency resolution and caching of node results. Heavy processing tasks MUST run asynchronously to keep the UI responsive (e.g., using `asyncio` or QThreads).

### VI. User Experience Consistency
Node creation, connection, and parameter editing must follow consistent UI patterns. The UI must provide immediate visual feedback for invalid connections or state errors.

## Testing Standards
- **Unit Testing**: Mandatory for all node execution logic, graph validation algorithms, and serialization handlers.
- **Integration Testing**: Required for engine-to-UI communication and script loading mechanisms.
- **Validation**: Every connection and parameter change must be validated against a schema before execution.

## Technical Constraints
- **Language**: Python 3.10+
- **Type Safety**: `mypy` or `pyright` for static type checking.
- **UI Framework**: PySide6 (Qt for Python) or similar modern desktop framework.
- **Validation**: `pydantic` or `cattrs` for data integrity.

## Governance
### Amendment Procedure
Changes to these principles require a version bump and a Sync Impact Report.

### Versioning Policy
- MAJOR: Language shift (e.g., JS to Python) or fundamental architectural re-alignment.
- MINOR: New UI patterns or expanded testing requirements.
- PATCH: Clarifications and wording.

**Version**: 2.0.0 | **Ratified**: 2026-03-09 | **Last Amended**: 2026-03-09
