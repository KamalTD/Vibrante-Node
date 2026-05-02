# Release v1.5.0: Maya Headless, Houdini Headless, Blender Headless & Deadline Submitters

Version 1.5.0 introduces a complete **headless DCC execution system** for Autodesk Maya, SideFX Houdini, and Blender, plus a chainable "Action Node" pattern that lets users compose batch pipelines visually. Deadline render-farm submitter nodes for all three DCCs are also included. Over 55 new nodes ship in this release.

---

## What's New

### Maya Headless Executor

A new `Maya Headless` node launches Maya in batch mode via `mayapy.exe`, runs a list of structured actions, and returns a full results payload.

- **Maya version dropdown** (2022 / 2024 / 2025 / 2026) with dynamic `mayapy.exe` path switching
- **Custom environment injection** via a `.bat` file (parsing `SET` commands) and/or `Maya.env` file, merged into the subprocess environment
- **Structured JSON payload + runner script** pattern — no f-string code injection, runner reports per-action success/error
- **Per-action validation** — actions with missing required fields are skipped with clear error messages, failing the node early
- **Outputs:** `success`, `stdout`, `stderr`, `exit_code`, `executed_actions`, `skipped_actions`

### Houdini Headless Executor

A new `Houdini Headless` node launches Houdini via `hython.exe`, mirroring the Maya Headless design.

- **Houdini version dropdown** — `20.5.445`, `20.5.278`, `20.0.547`, `19.5.493` — with editable `hython.exe` path
- **Custom environment injection** via `.bat` file and/or `houdini.env`
- **Optional /obj vs /stage context** on import nodes for classic vs Solaris/LOPs workflows
- **Same outputs contract** as Maya Headless for drop-in consistency

### Chainable Action Node Pattern

Both Maya and Houdini share a new design: small "Action" nodes each describe one operation and expose `actions_in` / `actions_out` list ports. Users chain them left-to-right and plug the final `actions_out` into the headless executor.

This keeps the graph flat, readable, and lets any action node be inserted/removed without touching others.

### New Maya Action Nodes

| Node | Purpose |
|------|---------|
| `Open Scene` | Open a `.ma`/`.mb` file |
| `Save Scene` | Save scene to a specified path (mayaAscii/mayaBinary) |
| `New Scene` | `cmds.file(new=True, force=True)` |
| `Scene Info` | Query frame range, FPS, units, renderer, project path |
| `Set Frame Range` | Set animation/playback start and end |
| `Import OBJ` | Import `.obj` file |
| `Import FBX` / `Export FBX` | Import/export via `fbxmaya` plugin |
| `Import Alembic` / `Export Alembic` | Import/export via `AbcImport`/`AbcExport` |
| `Reference Scene` | `file(reference=True)` with namespace |
| `Reference Alembic` | Referenced Alembic load |
| `Import Camera` | Auto-detect `.abc`/`.fbx`/`.ma`/`.mb` |
| `Export Camera Alembic` | Alembic export targeted at camera transforms |
| `List References` | Query all scene references into `info` |
| `Playblast` | Render viewport to video/image sequence |
| `Bake Animation` | `bakeResults` over a frame range |
| `Set Render Settings` | Renderer, resolution, frame range, image format, file prefix |
| `Set AOVs` | Create AOVs for Arnold (via `mtoa.aovs.AOVInterface`) or Redshift |
| `Create Render Layer` | Create a `renderSetup` layer with collection members |
| `Assign Material` | Assign shader/shading-group to nodes |
| `Custom Python` | Editable Python action with Script Editor button |

### New Houdini Action Nodes

| Node | Purpose |
|------|---------|
| `Open HIP` / `Save HIP` / `New HIP` | `hou.hipFile` operations |
| `Scene Info` | hip path, FPS, frame range, `$HIP`, `$JOB`, cameras |
| `Set Frame Range` | Playbar and playback range |
| `Import OBJ` | File SOP in `/obj` or SOP Import in `/stage` |
| `Import FBX` | `hou.hipFile.importFBX()` or FBX LOP |
| `Import Alembic` | Alembic SOP or Sublayer LOP |
| `Import Camera` | Alembic Archive or FBX import |
| `Export FBX` / `Export Alembic` / `Export Camera Alembic` | ROP-based exports |
| `Bake Animation` | Keyframe baking on time-dependent parms |
| `Custom Python` | Editable hython action with Script Editor button |

### Blender Headless Executor

A new `Blender Headless` node launches Blender in `--background` mode, mirroring the Maya/Houdini headless design.

- **Blender version dropdown** — `4.3`, `4.2`, `4.1`, `4.0`, `3.6` — with editable `blender.exe` path
- **Custom environment injection** via `.bat` file and/or `blender.env`
- **bpy-version-aware OBJ import/export** — uses `wm.obj_import` on Blender 4.0+ and `import_scene.obj` on 3.x automatically
- **Full traceback capture** per action for easier debugging
- **Same outputs contract** as Maya/Houdini Headless for drop-in consistency

### New Blender Action Nodes

| Node | Purpose |
|------|---------|
| `Open Blend` | Open a `.blend` file |
| `Save Blend` | Save scene to a specified path |
| `New Blend` | Create a fresh scene |
| `Scene Info` | Query scene name, FPS, frame range, active camera |
| `Set Frame Range` | Set animation start and end frames |
| `Import OBJ` | Version-aware OBJ import |
| `Import FBX` | FBX import |
| `Import Alembic` | Alembic cache import |
| `Import glTF` | glTF/GLB import |
| `Export OBJ` | Version-aware OBJ export |
| `Export FBX` | FBX export |
| `Export Alembic` | Alembic export |
| `Export glTF` | glTF/GLB export |
| `Export USD` | USD export |
| `Set Render Settings` | Engine (Cycles/EEVEE/EEVEE_NEXT/Workbench), resolution, samples, GPU, output format |
| `Render` | Still frame or animation render |
| `Bake Animation` | NLA bake with visual keying and configurable step |
| `Custom Python` | Editable bpy action with Script Editor button |
| `Blender: Get Action Result` | Extract a single action from `executed_actions` by type or index |

### Deadline Render Farm Submitters (DCCs category)

Four new nodes for submitting jobs to a Deadline render farm via `deadlinecommand`:

| Node | Purpose |
|------|---------|
| `Deadline: Submit Maya` | Submit a Maya render job (Arnold/VRay/Redshift/RenderMan/Software/Hardware2) |
| `Deadline: Submit Houdini` | Submit a Houdini ROP job with `houdini_version` auto-extraction from build string |
| `Deadline: Submit Blender` | Submit a Blender render job (CYCLES/EEVEE/EEVEE_NEXT/WORKBENCH) |
| `Deadline: Job Status` | Query job status and progress; optional `poll_until_done` mode with configurable timeout |

All submitters:
- Write Job Info + Plugin Info temp files and submit via `deadlinecommand`
- Parse `JobID` from output (`JobID=` line or 24-hex fallback)
- Support `extra_job_args` text area for arbitrary extra key=value job info lines
- Clean up temp files in a `finally` block
- Output: `success`, `job_id`, `stdout`, `stderr`

`Deadline: Job Status` outputs: `status`, `progress`, `tasks_total`, `tasks_complete`, `tasks_failed`, `is_complete`, `is_failed`, `details`

### Helper Nodes

`Maya: Get Action Result`, `Houdini: Get Action Result`, and `Blender: Get Action Result` — extract a single action from the `executed_actions` list by type (first match) or index. Outputs the matched dict, its `info` field, and a best-guess `path` field, so downstream nodes don't have to filter the list manually.

### UI: file_save Widget Type

New `file_save` widget on string ports opens a **Save File** dialog instead of an Open dialog. Used throughout the export action nodes so save paths feel natural.

### UI: Safer Node Drop

Node instantiation during drag-and-drop is now wrapped in try/except in `scene.py` and `view.py`. A failing node constructor logs an error instead of crashing the UI, and undo history is only pushed on successful spawn.

### UI: Custom Action Script Editor

The `Edit Script` button (previously only on `python_script` nodes) now also appears on `maya_action_custom` and `houdini_action_custom`, letting users duplicate those nodes and write their own DCC actions. The button reads/writes `python_code` via `get_parameter`/`set_parameter` so the editor always reflects the current code.

---

## Upgrade Notes

- No breaking changes to existing nodes or workflows.
- The Houdini Headless executor is a **subprocess pattern** and runs alongside the existing `hou_bridge` live-session pattern documented in `CLAUDE.md`. Both can be used in the same project.
- `Maya Headless`' success criterion only checks process exit code + structured action errors. Maya's stderr warnings no longer cause false failures.
- Deadline nodes are in the **DCCs** category in the node library.
- Blender's OBJ import/export API changed in 4.0; the runner script handles this automatically based on the detected bpy version.
