# Feature Specification: Advanced Node Features & Persistence

**Feature Branch**: `003-advanced-node-features`  
**Created**: 2026-03-09  
**Status**: Draft  
**Input**: User description: "Extend the node-based workflow application with features for node execution, real-time editing, node management, and persistent storage using JSON definitions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Networked Workflow Execution (Priority: P1)

As a user, I want to execute a network of connected nodes so that data flows from upstream outputs to downstream inputs automatically based on the graph topology.

**Why this priority**: Core functionality that makes the visual graph useful for actual work.

**Independent Test**: Create a workflow with an "Add" node connected to two "Static Value" nodes. Run the workflow and verify the "Add" node's output correctly reflects the sum of its inputs.

**Acceptance Scenarios**:

1. **Given** a connected DAG, **When** "Run Workflow" is clicked, **Then** nodes execute in topological order.
2. **Given** a node execution, **When** running, **Then** the node visually changes color to indicate status.
3. **Given** a failing node, **When** executed, **Then** the engine stops at the failure and highlights the node in red.

---

### User Story 2 - Real-Time Builder Synchronization (Priority: P1)

As a developer, I want the Node Builder UI and the Python code template to stay in sync automatically so I don't have to manually update port definitions in code.

**Why this priority**: Significantly improves developer experience and reduces errors during node creation.

**Independent Test**: Open Node Builder, add an input named "threshold" to the table. Verify that `self.add_input("threshold", ...)` appears instantly in the code editor without overwriting existing `execute()` logic.

**Acceptance Scenarios**:

1. **Given** the Node Builder, **When** an input/output row is added or modified in the table, **Then** the code template updates in real-time.
2. **Given** the Node Builder code editor, **When** code is manually edited to add a port, **Then** the UI table updates to reflect the change.

---

### User Story 3 - Persistent Node Definitions (Priority: P1)

As a user, I want my custom node definitions to be stored as JSON files so that they are easily manageable, versionable, and portable.

**Why this priority**: Enables sharing of node types and decouples node logic from specific workflows.

**Independent Test**: Create a new node in the Builder and save it. Verify a JSON file exists in the `nodes/` directory with the correct schema (name, description, inputs, outputs, python_code).

**Acceptance Scenarios**:

1. **Given** the application startup, **When** scanning the `nodes/` folder, **Then** all valid JSON node definitions are loaded and registered.

---

### User Story 4 - Node Management (Edit/Delete) (Priority: P2)

As a user, I want to edit or delete existing custom nodes from my library so I can refine my tools over time.

**Why this priority**: Essential for maintaining a clean and up-to-date node library.

**Independent Test**: Right-click a node in the library, select "Edit", modify its code, and save. Verify the changes are reflected in existing and new instances of that node.

**Acceptance Scenarios**:

1. **Given** a node type in the library, **When** "Delete" is chosen, **Then** the definition is removed from disk and unlisted from the UI.
2. **Given** a node used in a saved workflow, **When** attempting deletion, **Then** the user is warned of potential breakage.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Engine MUST maintain a runtime dictionary mapping `node_id` to output values.
- **FR-002**: Engine MUST resolve inputs for each node by pulling values from connected upstream outputs in the runtime dictionary.
- **FR-003**: Node Builder MUST use a background AST parser to synchronize code changes back to the UI tables.
- **FR-004**: Node definitions MUST be stored in JSON format containing metadata and Python code as a string.
- **FR-005**: Application MUST scan and load all JSON files in the `nodes/` directory on startup.
- **FR-006**: Visual feedback MUST be provided for "Idle", "Running", "Success", and "Failed" states using node colors.

### Key Entities *(include if feature involves data)*

- **NodeDefinitionJSON**: The persistent schema for a node type.
- **ExecutionContext**: A map of node IDs to their computed output results.
- **SyncManager**: Handles real-time synchronization between the Node Builder UI and the code editor.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Workflow execution starts within 100ms of clicking "Run" for a 20-node graph.
- **SC-002**: Real-time sync latency between table edits and code updates is under 50ms.
- **SC-003**: 100% of custom nodes are successfully re-registered from JSON on application restart.
- **SC-004**: Zero data loss occurs when editing an existing node's logic.
