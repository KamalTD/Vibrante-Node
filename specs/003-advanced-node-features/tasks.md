# Tasks: Advanced Node Features & Persistence

**Input**: Design documents from `/specs/003-advanced-node-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Update project structure and dependencies

- [x] T001 [P] Ensure `toposort` and `pydantic` are in `requirements.txt`
- [x] T002 Create `nodes/` and `workflows/` directories in repository root
- [x] T003 [P] Initialize new modules: `src/core/registry.py`, `src/core/persistence.py`, and `src/ui/library_panel.py`

---

## Phase 2: Foundational (Models & Registry)
**Purpose**: Implement persistent models and dynamic discovery

- [x] T004 Implement `NodeDefinitionJSON` and updated `WorkflowModel` in `src/core/models.py`
- [x] T005 Implement `NodeRegistry` with JSON scanning and loading in `src/core/registry.py`
- [x] T006 Implement dynamic class generation from Python code string in `src/core/registry.py`
- [x] T007 Implement `PersistenceManager` for workflow saving/loading in `src/core/persistence.py`

---

## Phase 3: Node Builder (Real-Time Sync)
**Purpose**: Interactive editor with automatic UI/Code synchronization

- [x] T008 [US2] Implement `TableToCodeSync` (UI edits -> Python template update) in `src/ui/node_builder.py`
- [x] T009 [US2] Implement `CodeToTableSync` using `ast` module (Python edits -> UI table update) in `src/ui/node_builder.py`
- [x] T010 [US2] Add debounce mechanism to AST parsing to ensure smooth typing experience
- [x] T011 [US3] Connect "Save" button to `NodeRegistry.save_node` logic

---

## Phase 4: Execution Engine (Networked)
**Purpose**: Data-passing DAG executor with visual feedback

- [x] T012 [US1] Implement `NetworkExecutor` with topological sorting in `src/core/engine.py`
- [x] T013 [US1] Implement runtime context for passing outputs between connected nodes
- [x] T014 [US1] Implement execution status signals (Started, Success, Failed)
- [x] T015 [US1] Update `NodeWidget` to reflect status via background colors (Yellow=Running, Green=Success, Red=Failed)

---

## Phase 5: UI Integration (Library Panel & Management)
**Purpose**: Sidebar for managing nodes and triggered execution

- [x] T016 [US4] Implement `LibraryPanel` (QDockWidget) to display available nodes from registry
- [x] T017 [US4] Add context menu to `LibraryPanel` for "Edit Node" and "Delete Node"
- [x] T018 [US4] Implement "Edit" flow: Registry -> Node Builder -> Registry Update
- [x] T019 [US4] Implement "Delete" flow with safety check for nodes currently in the scene
- [x] T020 [US1] Add "Run Workflow" action to main toolbar

---

## Phase 6: Polish & Cross-Cutting Concerns
**Purpose**: Final refinements and verification

- [x] T021 [P] Add unit tests for AST synchronization in `tests/unit/test_registry.py`
- [x] T022 [P] Add integration test for networked data flow in `tests/integration/test_networked_execution.py`
- [x] T023 Final documentation update for custom node development

---

## Dependencies & Execution Order
- Phase 1 (Setup) -> Phase 2 (Foundational)
- Phase 2 (Foundational) -> Phase 3 (Builder) & Phase 4 (Executor)
- Phase 3 & 4 -> Phase 5 (UI Integration)
- Phase 5 -> Phase 6 (Polish)

## Implementation Strategy
- **MVP First**: Complete Phase 1, 2, and 4 to enable networked execution of builtin nodes.
- **Incremental**: Add real-time sync (Phase 3) and then the management panel (Phase 5).
