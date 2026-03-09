# Tasks: Python Node-Based Desktop Application

**Input**: Design documents from `/specs/002-node-desktop-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize Python project structure in `src/` as per implementation plan
- [ ] T002 [P] Create `requirements.txt` with dependencies: `PyQt5`, `pydantic`, `toposort`
- [ ] T003 [P] Configure `pytest` and `pytest-qt` in `pytest.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core logic and models required before UI implementation

- [ ] T004 Create `Node`, `Port`, `Connection`, and `Workflow` models in `src/core/models.py`
- [ ] T005 Implement `BaseNode` abstract class and port management in `src/nodes/base.py`
- [ ] T006 Implement dynamic script loader using `importlib` in `src/core/loader.py`
- [ ] T007 Implement graph manager for node/edge tracking and DAG validation in `src/core/graph.py`
- [ ] T008 [P] Implement safe runtime execution wrapper for nodes in `src/utils/runtime.py`

---

## Phase 3: User Story 1 - Visual Graph Construction (P1) 🎯 MVP
**Goal**: Interactive canvas for creating and connecting nodes.
**Independent Test**: Create two nodes on the canvas and connect them visually; verify connection persistence when moving nodes.

- [ ] T009 [P] [US1] Create main window and basic toolbar in `src/ui/window.py`
- [ ] T010 [P] [US1] Setup `QGraphicsScene` and `QGraphicsView` for the canvas in `src/ui/canvas/`
- [ ] T011 [P] [US1] Implement `NodeWidget` for visual node representation in `src/ui/node_widget.py`
- [ ] T012 [P] [US1] Implement `PortWidget` for input/output connection points in `src/ui/port_widget.py`
- [ ] T013 [US1] Implement visual connection dragging and edge drawing in `src/ui/canvas/edge.py`
- [ ] T014 [US1] Implement node creation context menu in `src/ui/canvas/scene.py`

**Checkpoint**: Basic visual editor is functional - nodes can be created and connected.

---

## Phase 4: User Story 2 - Dynamic Node Script Loading (P1)
**Goal**: Allow runtime extension of node types via external Python scripts.
**Independent Test**: Load a custom node script and verify it appears in the "Add Node" menu and correctly instantiates on the canvas.

- [ ] T015 [US2] Create "nodes/" directory and initial builtin nodes in `src/nodes/builtins/`
- [ ] T016 [US2] Integrate `loader.py` with the UI to scan and register custom scripts in `src/ui/window.py`
- [ ] T017 [US2] Implement node property panel for editing node parameters in `src/ui/properties.py`
- [ ] T018 [US2] Add visual error feedback for failed script loads in `src/ui/window.py`

---

## Phase 5: User Story 3 - Workflow Execution & Dependency Resolution (P1)
**Goal**: Execute the graph in topological order using multi-threading.
**Independent Test**: Execute a 3-node linear pipeline and verify topological execution order and visual status updates.

- [ ] T019 [US3] Implement DAG evaluation engine with `toposort` in `src/core/engine.py`
- [ ] T020 [US3] Implement multi-threaded execution using `QThreadPool` and `QRunnable` in `src/core/engine.py`
- [ ] T021 [US3] Integrate engine with `NodeWidget` to show execution status (Running, Success, Failed) in `src/ui/node_widget.py`
- [ ] T022 [US3] Create integration test for multi-threaded graph execution in `tests/integration/test_engine.py`

---

## Phase 6: User Story 4 - Serialization & Persistence (P2)
**Goal**: Save and load workflows as JSON files.
**Independent Test**: Save a workflow with multiple nodes and connections, clear the canvas, and reload it to verify state restoration.

- [ ] T023 [US4] Implement workflow serialization to JSON using Pydantic in `src/core/graph.py`
- [ ] T024 [US4] Implement workflow deserialization and UI reconstruction in `src/app.py`
- [ ] T025 [US4] Create serialization unit tests in `tests/unit/test_serialization.py`

---

## Phase 7: Polish & Cross-Cutting Concerns
**Purpose**: UI/UX improvements and documentation.

- [ ] T026 [P] Implement canvas zoom and pan functionality in `src/ui/canvas/view.py`
- [ ] T027 [P] Create developer documentation for custom node creation in `docs/custom_nodes.md`
- [ ] T028 [P] Add final builtin nodes (File Loader, Data Processor, Console Sink) in `src/nodes/builtins/`

---

## Phase 8: Node Builder (Extensibility)
**Purpose**: Built-in editor for creating custom nodes dynamically.

- [ ] T029 Create `PythonHighlighter` for syntax highlighting in `src/utils/highlighter.py`
- [ ] T030 Implement `NodeBuilderDialog` with name, description, and port tables in `src/ui/node_builder.py`
- [ ] T031 Integrate code editor with syntax highlighting in `NodeBuilderDialog`
- [ ] T032 Implement Python code generation logic from template in `src/ui/node_builder.py`
- [ ] T033 Implement AST-based code validation in `src/ui/node_builder.py`
- [ ] T034 Implement in-dialog node testing system in `src/ui/node_builder.py`
- [ ] T035 Add "New Node" button to main window to trigger Node Builder

---

## Dependencies & Execution Order
...
### Phase Dependencies
- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories.
- **Phase 3 (Visual Construction)**: Depends on Phase 2.
- **Phase 4, 5, 6 (Features)**: All depend on Phase 3 (Visual Construction) being stable.
- **Phase 7 (Polish)**: Depends on all desired feature phases being complete.

### Implementation Strategy
- **MVP First**: Complete Phase 1, 2, and 3 to achieve a functional visual node editor.
- **Incremental Delivery**:
  1. Setup + Foundation -> Core Engine Ready.
  2. Add US1 (Visual Construction) -> Visual MVP.
  3. Add US2 (Script Loading) -> Extensible MVP.
  4. Add US3 (Execution) -> Functional Application.
  5. Add US4 (Serialization) -> Production-ready Tool.

---

## Parallel Opportunities
- T002 and T003 can be done in parallel with T001.
- T008 can be done in parallel with other foundational tasks in Phase 2.
- T009, T010, T011, and T012 in Phase 3 can mostly run in parallel as they touch different UI components.
- Polish tasks T026, T027, and T028 can run in parallel.
