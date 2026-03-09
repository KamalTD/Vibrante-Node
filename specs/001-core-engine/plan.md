# Implementation Plan: Core Node-Based Pipeline Engine

**Branch**: `001-core-engine` | **Date**: 2026-03-09 | **Spec**: [specs/001-core-engine/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-core-engine/spec.md`

## Summary
Build a robust, async, JSON-driven node-based pipeline engine in TypeScript. The engine will support basic node types (source, transform, sink), use Zod for validation, and Toposort for cycle detection.

## Technical Context
**Language/Version**: TypeScript 5.0+, Node.js 18+  
**Primary Dependencies**: `zod`, `toposort`  
**Storage**: JSON files  
**Testing**: Vitest  
**Target Platform**: Node.js CLI/Service  
**Project Type**: Library/Engine  
**Performance Goals**: <500ms pipeline initialization  
**Constraints**: Directed Acyclic Graph (DAG) only.  
**Scale/Scope**: 10-100 nodes per pipeline.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Node-First Architecture: Every component is a node.
- [x] JSON-Driven Pipelines: Config is serializable to JSON.
- [x] Observability by Default: Built-in logging.
- [x] Extensible Node System: Interface for adding node types.
- [x] Robust Error Handling: Async/Promise-based.
- [x] Parallel Execution Support: Engine will be designed for this.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── engine.ts        # The pipeline runner
│   ├── graph.ts         # DAG validation and sorting
│   └── types.ts         # Shared types (Node, Edge, Pipeline)
├── nodes/
│   ├── base.ts          # Base node classes
│   ├── registry.ts      # Node type registry
│   └── library/         # Built-in node types
│       ├── source.ts
│       ├── transform.ts
│       └── sink.ts
└── index.ts             # Entry point

tests/
├── integration/
│   └── pipeline.test.ts
└── unit/
    ├── engine.test.ts
    └── graph.test.ts
```

**Structure Decision**: Single project TypeScript structure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
