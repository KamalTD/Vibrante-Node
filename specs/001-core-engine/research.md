# Research: Core Node-Based Pipeline Engine

## Decision: TypeScript & Node.js
- **Rationale**: Provides type safety and async support out of the box. Essential for a robust engine.
- **Alternatives considered**: Python (good for data, but less common for node-based visual UIs in the same ecosystem), Go (great performance, but higher barrier for extensibility in a JS-heavy world).

## Decision: Zod for Schema Validation
- **Rationale**: Industry standard for TypeScript schema validation. Very powerful and type-safe.
- **Alternatives considered**: Joi (less type-safe), AJV (more for JSON Schema specifically, more verbose).

## Decision: Toposort for Cycle Detection
- **Rationale**: Simple, battle-tested library for topological sorting, perfect for detecting cycles in a DAG.
- **Alternatives considered**: Custom DFS (more error-prone to implement manually).

## Decision: Vitest for Testing
- **Rationale**: Fast, modern test runner with excellent TypeScript support.
- **Alternatives considered**: Jest (slower, more configuration needed for TS).
