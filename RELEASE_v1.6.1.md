# Release Notes — Vibrante-Node v1.6.1

**Release date:** 2026-04-18
**Branch:** `feature/python-script-while-loop-nodes`

---

## Overview

v1.6.1 is a stability patch that resolves a persistent Qt threading warning introduced alongside the v1.6.0 asyncio execution engine, and fixes the Prism Pipeline auto-bootstrap that was missing from the engine.

---

## Bug Fixes

### Fix: `QBasicTimer::start: Timers cannot be started from another thread`

**Root cause:** The `NetworkExecutor` (a `QObject`) was moved into a background `QThread` so that signals would originate from that thread. Qt's cross-thread signal delivery still required a `QBasicTimer` inside the worker thread, which had no Qt event dispatcher — producing the warning on every execution.

**Fix:** Replaced `_AsyncWorker(QThread)` in `src/ui/window.py` with `_EventLoopRunner` — a lightweight class that drives the asyncio event loop **on the main Qt thread** using a zero-delay `QTimer`. Each timer tick calls `loop.call_soon(loop.stop); loop.run_forever()` to process one round of ready asyncio callbacks without blocking the Qt event loop. Because all asyncio callbacks and signal emissions now originate from the main thread, Qt's cross-thread delivery machinery is never activated and the warning is structurally impossible.

### Fix: Prism auto-bootstrap not implemented in engine

**Root cause:** The `CLAUDE.md` and documentation described a Prism auto-bootstrap phase where the engine would initialise `PrismCore` before graph execution if a `prism_core_init` node was present — but the code in `engine.py` never implemented this. All `prism_*` nodes would fail with "No PrismCore provided." unless explicitly wired.

**Fix:** Added `_bootstrap_prism_if_needed()` async method to `NetworkExecutor` in `src/core/engine.py`. It is called at the start of `run()`, detects any `prism_core_init` node in the graph, and calls `bootstrap_prism_core()` with that node's parameters before any node executes. All subsequent `prism_*` nodes share the cached `PrismCore` instance automatically.

### Fix: `prism_core_init` silently breaks exec chain on bootstrap failure

**Root cause:** When `bootstrap_prism_core()` raised an exception inside `prism_core_init`, the node returned `{'core': None, 'version': ''}` without emitting `exec_out`. Any nodes connected downstream via execution wire were never triggered.

**Fix:** Added `await self.set_output('exec_out', True)` to the error path so the execution chain always continues even when Prism initialisation fails.

### Fix: Unhelpful "No PrismCore provided." error across all Prism nodes

**Root cause:** All 31 `prism_*` nodes used the generic message `"No PrismCore provided."` which gave no actionable guidance.

**Fix:** Updated all 31 nodes to emit: `"No PrismCore found. Add a prism_core_init node to your graph and run it before this node."` — directing users to the correct fix immediately.

---

## Changed Files

| File | Change |
|------|--------|
| `src/ui/window.py` | Replaced `_AsyncWorker(QThread)` with `_EventLoopRunner` (main-thread asyncio pump via `QTimer`) |
| `src/core/engine.py` | Added `_bootstrap_prism_if_needed()`, guarded `_finished_event` in `stop()` |
| `src/main.py` | Version bump `v1.6.0` → `v1.6.1` |
| `nodes/prism_core_init.json` | Emit `exec_out` on error path |
| `nodes/prism_add_integration.json` | Improved error message |
| `nodes/prism_*.json` (29 others) | Improved "no core" error messages |

---

## Upgrade Notes

No workflow changes required. Existing `.json` workflow files load and execute identically. The Prism auto-bootstrap is automatic — no new wiring needed.
