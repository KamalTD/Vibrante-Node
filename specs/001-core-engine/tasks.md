# Tasks: Core Node-Based Pipeline Engine

**Input**: Design documents from `/specs/001-core-engine/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize TypeScript project in root directory
- [ ] T002 [P] Install dependencies: `zod`, `toposort`, `vitest` in `package.json`
- [ ] T003 [P] Configure `tsconfig.json` and `vitest.config.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core types and graph logic required by all stories

- [ ] T004 Create shared types (Node, Edge, Pipeline) in `src/core/types.ts`
- [ ] T005 Implement Graph validation and cycle detection in `src/core/graph.ts`
- [ ] T006 Implement Node Registry for managing node types in `src/nodes/registry.ts`
- [ ] T007 Implement Base Node classes and interfaces in `src/nodes/base.ts`

---

## Phase 3: User Story 1 - Create and Execute a Simple Pipeline (P1) 🎯 MVP
**Goal**: Run a basic source -> transform -> sink pipeline from JSON.
**Independent Test**: Define a JSON pipeline with static source, square transform, and console sink. Verify output.

- [ ] T008 [P] [US1] Implement Static Source node in `src/nodes/library/source.ts`
- [ ] T009 [P] [US1] Implement Square Transform node in `src/nodes/library/transform.ts`
- [ ] T010 [P] [US1] Implement Console Sink node in `src/nodes/library/sink.ts`
- [ ] T011 [US1] Implement Pipeline Engine runner logic in `src/core/engine.ts`
- [ ] T012 [US1] Add observability logging to node execution in `src/core/engine.ts`
- [ ] T013 [US1] Create integration test for 3-node pipeline in `tests/integration/pipeline.test.ts`

**Checkpoint**: Core MVP is functional.

---

## Phase 4: User Story 2 - Async Node Execution (P1)
**Goal**: Ensure nodes can perform async operations and engine waits correctly.
**Independent Test**: Use a node with a 1s delay and verify completion.

- [ ] T014 [US2] Refactor Base Node and Engine to support async `execute()` in `src/nodes/base.ts` and `src/core/engine.ts`
- [ ] T015 [US2] Implement Delay node for testing async in `src/nodes/library/transform.ts`
- [ ] T016 [US2] Create unit test for async node execution in `tests/unit/engine.test.ts`

---

## Phase 5: User Story 3 - JSON Configuration & Serialization (P2)
**Goal**: Robust loading and saving of pipelines from JSON.
**Independent Test**: Serialize a complex pipeline, deserialize it, and run it.

- [ ] T017 [US3] Implement Zod schema validation for full Pipeline JSON in `src/core/types.ts`
- [ ] T018 [US3] Implement serialization/deserialization helpers in `src/core/engine.ts`
- [ ] T019 [US3] Create unit tests for JSON validation and serialization in `tests/unit/engine.test.ts`

---

## Phase 6: Polish & Cross-Cutting Concerns
**Purpose**: Final touches and documentation.

- [ ] T020 [P] Finalize public API exports in `src/index.ts`
- [ ] T021 [P] Update `README.md` with engine quickstart and examples

---

## Dependencies & Execution Order
- Phase 1 (Setup) -> Phase 2 (Foundational)
- Phase 2 (Foundational) -> Phase 3 (US1)
- Phase 3 (US1) -> Phase 4 (US2) & Phase 5 (US3)
- Phase 6 (Polish) -> All previous complete

## Implementation Strategy
- **MVP First**: Complete Phase 1, 2, and 3 to have a working engine.
- **Incremental**: Add async support (Phase 4) and then full JSON serialization (Phase 5).
