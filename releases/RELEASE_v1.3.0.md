# Release v1.3.0: Houdini Geometry Nodes, AI Context Fix & Developer Guide

Version 1.3.0 adds three new Houdini geometry processing nodes, fixes the Gemini AI node builder so it correctly understands the Houdini bridge API, ships a comprehensive `CLAUDE.md` developer guide, and updates all user-facing documentation with YouTube tutorial links.

---

## 🚀 Key Features

### 🔥 New Houdini Geometry Nodes

**Houdini ABC Convert** (`nodes/houdini_abc_convert.json`)
- Imports an Alembic (`.abc`) file into Houdini and automatically converts it to polygons via `alembic` → `convert` SOP chain.
- Outputs the resulting geometry path for downstream nodes.

**Houdini Edges to Curves** (`nodes/houdini_edges_to_curves.json`)
- Converts all edges in a geometry into individual curves using a `convertline` SOP.
- Filters curves by direction — only keeps edges flowing along the **X axis** (configurable threshold).
- Inputs: `geo_path`, `x_threshold` (default 0.9).

**Houdini Color Curves** (`nodes/houdini_color_curves.json`)
- Extracts **red-painted surface regions** from a mesh and generates one clean curve per stripe.
- Pipeline: detect red points → label connected stripes (Connectivity SOP) → project sample positions along stripe axis → snap each sample to nearest surface point → remove original mesh polygons.
- Inputs: `geo_path`, `red_threshold`, `green_max`, `blue_max`, `num_samples`.
- Result: isolated polyline curves, one per red stripe, snapped to the original surface geometry.

### 🤖 Gemini AI Node Builder — Houdini Context Fix
- The system prompt for the Gemini AI assistant is now applied via `system_instruction=` on the `GenerativeModel` constructor, ensuring it persists across **every** message in the conversation.
- The prompt now includes the complete Houdini bridge API reference: all methods, their exact return dict shapes, correct port rules (`super().__init__()` auto-adds exec ports — never add manually), and annotated example nodes.
- Previously the AI would generate broken nodes using `hou` module API directly or wrong port patterns — now it generates correct bridge-aware code.

### 📖 CLAUDE.md — Developer Reference
- New `CLAUDE.md` at the project root documents the full node JSON structure, `BaseNode` rules, all bridge methods with exact return shapes, common mistakes table, and a complete reference node implementation.
- Designed so AI assistants (Claude, Gemini, Copilot) immediately understand the project structure with zero warm-up.

### 🎬 YouTube Channel & Tutorial Integration
- Added `🎬 Video Tutorials` section to `README.md` with badge linking to the official YouTube channel.
- Added a 6-step introduction tutorial (Install → Place Nodes → Connect → Run → Save/Export → AI Builder) directly in the README.
- YouTube channel listed as the first entry in the Documentation section.

---

## 🐞 Bug Fixes & Refinements
- **`houdini_abc_convert`**: Was using non-existent `get_hou()` API and calling `hou` module methods directly — rewritten to use `get_bridge()` with correct RPC calls and dict unpacking.
- **VEX type ambiguity**: Fixed `point(0, "P", i).y` ambiguity in Houdini wrangle VEX by reading individual float components `point(0, "Px", i)` / `"Py"` / `"Pz"`.
- **Gemini context loss**: Fixed `initialized` flag pattern that only injected the system prompt into the first message — replaced with permanent `system_instruction=` on the model.

---

## 📂 Changed Files
- `src/main.py` — Version bump to v1.3.0
- `src/ui/gemini_chat.py` — Permanent system_instruction with Houdini bridge API reference
- `nodes/houdini_abc_convert.json` — Rewritten with correct bridge API usage
- `nodes/houdini_edges_to_curves.json` — New: X-axis edge-to-curve converter
- `nodes/houdini_color_curves.json` — New: Red surface stripe curve extractor
- `CLAUDE.md` — New: Comprehensive developer and AI assistant reference
- `README.md` — YouTube channel section and introduction tutorial added

---

## 📜 License
Permission is granted to use, modify, and test this software for personal and non-commercial purposes.
Commercial use requires written permission from the author.
