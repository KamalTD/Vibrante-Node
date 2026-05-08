# Vibrante-Node — Developer Guide for Claude

This file teaches Claude how to create nodes for this node-based pipeline, with special focus on nodes that control Houdini via the bridge plugin.

---

## 1. Node File Format

Every node is a single `.json` file in `nodes/`. It has this structure:

```json
{
    "node_id": "my_node",
    "name": "my_node",
    "description": "What this node does.",
    "category": "Houdini",
    "icon_path": "icons/houdini.svg",
    "use_exec": true,
    "inputs": [
        { "name": "some_input", "type": "string", "widget_type": "text", "options": null, "default": null },
        { "name": "exec_in",   "type": "any",    "widget_type": null,   "options": null, "default": null }
    ],
    "outputs": [
        { "name": "some_output", "type": "string", "widget_type": null, "options": null, "default": null },
        { "name": "exec_out",    "type": "any",    "widget_type": null, "options": null, "default": null }
    ],
    "python_code": "..."
}
```

- **`use_exec: true`** — means the node participates in execution flow. Always include `exec_in` / `exec_out` in the inputs/outputs arrays when true.
- **`category`** — used for grouping in the UI. Use `"Houdini"` for all Houdini-related nodes.
- **`icon_path`** — use `"icons/houdini.svg"` for Houdini nodes, or `null`.
- **`python_code`** — the full Python source as a single JSON string (use `\n` for newlines, `\"` for quotes).

### Port types

| type     | widget_type     | notes                        |
|----------|-----------------|------------------------------|
| `string` | `"text"`        | text input widget            |
| `float`  | `"float"`       | numeric float widget         |
| `int`    | `"int"`         | numeric integer widget       |
| `bool`   | `"checkbox"`    | checkbox widget              |
| `any`    | `null`          | generic exec/data port       |

---

## 2. Python Code Rules

### 2.1 Class skeleton

```python
from src.nodes.base import BaseNode
from src.utils.hou_bridge import get_bridge   # for Houdini nodes

class My_Node(BaseNode):
    name = "my_node"   # must match node_id

    def __init__(self):
        super().__init__()   # IMPORTANT: this already adds exec_in + exec_out
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("some_input", "string", widget_type="text")
        self.add_input("a_float",   "float",  widget_type="float", default=1.0)
        self.add_output("some_output", "string")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        value = inputs.get("some_input", "")
        # ... do work ...
        return {
            "some_output": result,
            "exec_out": True
        }

def register_node():
    return My_Node
```

### 2.2 Critical rules for `__init__`

- `super().__init__()` calls `BaseNode.__init__(use_exec=True)` which **automatically adds `exec_in` and `exec_out`**. Do NOT add them again manually.
- Only add the **extra** ports specific to your node inside the `# [AUTO-GENERATED-PORTS-START]` block.
- Never add ports twice. Duplicate calls to `add_input` / `add_output` for the same name will create duplicate ports in the UI.

### 2.3 `execute` return value

Always return a dict whose keys match your output port names. Always include `"exec_out": True` for exec-flow nodes.

```python
return {
    "my_output": some_value,
    "exec_out": True
}
```

---

## 3. Houdini Bridge

Houdini nodes communicate with a live Houdini session over a local TCP socket (JSON-RPC). The bridge client lives in `src/utils/hou_bridge.py`.

### 3.1 Getting the bridge

```python
from src.utils.hou_bridge import get_bridge

bridge = get_bridge()   # returns the HouBridge singleton
```

**Never** import `hou` directly. **Never** call `hou_bridge.get_hou()` — that function does not exist.

### 3.2 All bridge methods and their return values

#### `bridge.ping()`
Returns: `{"status": "ok", "version": "<houdini version string>"}`

#### `bridge.create_node(parent, node_type, name="")`
Creates a node inside `parent`.
Returns: `{"path": "/obj/geo1", "name": "geo1", "type": "geo"}`
```python
result = bridge.create_node("/obj", "geo", "my_geo")
geo_path = result["path"]   # e.g. "/obj/my_geo"
```

#### `bridge.delete_node(path)`
Returns: `{"deleted": "/obj/my_geo"}`

#### `bridge.set_parm(node, parm, value)`
Sets a single parameter.
Returns: `{"set": True}`
```python
bridge.set_parm("/obj/my_geo/alembic1", "fileName", "/path/to/file.abc")
```

#### `bridge.get_parm(node, parm)`
Returns: `{"value": <current value>}`
```python
result = bridge.get_parm("/obj/my_geo/alembic1", "fileName")
value = result["value"]
```

#### `bridge.set_parms(node, parms)`
Sets multiple parameters at once.
Returns: `{"set": True, "count": N}`
```python
bridge.set_parms("/obj/my_geo/null1", {"tx": 1.0, "ty": 2.0})
```

#### `bridge.get_parms(node)`
Returns a flat dict of all parameter name→value pairs.

#### `bridge.connect_nodes(from_node, to_node, output=0, input_idx=0)`
Wires `from_node`'s output into `to_node`'s input.
Returns: `{"connected": True}`
```python
bridge.connect_nodes(abc_path, convert_path, output=0, input_idx=0)
```

#### `bridge.cook_node(path, force=False)`
Returns: `{"cooked": True}`

#### `bridge.run_code(code)`
Executes arbitrary Python code **inside Houdini**. `hou` is available. Assign to `result` to get a value back.
Returns: `{"result": <value of local variable named 'result', or None>}`
```python
run_result = bridge.run_code(
    "n = hou.node('/obj/my_geo'); result = n.displayNode().path() if n and n.displayNode() else None"
)
display_path = run_result.get("result")   # e.g. "/obj/my_geo/convert1" or None
```

#### `bridge.scene_info()`
Returns: `{"hip_file": ..., "hip_name": ..., "houdini_version": ..., "fps": ..., "frame": ..., "frame_range": [start, end]}`

#### `bridge.node_info(path)`
Returns detailed info about a node:
```python
{
    "path": "/obj/my_geo",
    "name": "my_geo",
    "type": "geo",
    "category": "Object",        # "Object", "Sop", "Shop", etc.
    "input_connectors": 0,
    "output_connectors": 0,
    "inputs": ["/obj/other"],    # list of connected input node paths (or None)
    "outputs": ["/obj/child"],   # list of connected output node paths
    "children": ["alembic1", "convert1"]  # child node names (not full paths)
}
```

#### `bridge.children(path="/obj")`
Lists children of a node.
Returns: list of `{"name": ..., "type": ..., "path": ...}` dicts.
```python
children = bridge.children("/obj/my_geo")
for child in children:
    bridge.delete_node(child["path"])
```

#### `bridge.node_exists(path)`
Returns: `{"exists": True}` or `{"exists": False}`
```python
exists = bridge.node_exists("/obj/my_geo")["exists"]
```

#### `bridge.set_display_flag(path, on=True)`
Returns: `{"set": True}`

#### `bridge.set_render_flag(path, on=True)`
Returns: `{"set": True}`

#### `bridge.layout_children(path="/obj")`
Auto-layouts child nodes.
Returns: `{"done": True}`

#### `bridge.save_hip(path="")`
Returns: `{"saved": "<hip file path>"}`

#### `bridge.set_expression(node, parm, expression, language="hscript")`
Returns: `{"set": True}`
```python
bridge.set_expression("/obj/my_geo/null1", "tx", "sin($F * 0.1)", language="hscript")
bridge.set_expression("/obj/my_geo/null1", "tx", "hou.frame() * 0.1", language="python")
```

#### `bridge.set_keyframe(node, parm, frame, value)`
Returns: `{"set": True}`

#### `bridge.set_frame(frame)`
Returns: `{"frame": <new frame>}`

#### `bridge.set_playback_range(start, end)`
Returns: `{"start": ..., "end": ...}`

---

## 4. Common Houdini Node Patterns

### 4.1 Create a geo container with SOPs inside it

```python
# Create /obj-level geo container
geo_result = bridge.create_node("/obj", "geo", "my_geo")
geo_path = geo_result["path"]

# Clear default nodes Houdini adds automatically
for child in bridge.children(geo_path):
    bridge.delete_node(child["path"])

# Create SOPs inside the geo
sop_result = bridge.create_node(geo_path, "box", "my_box")
sop_path = sop_result["path"]

bridge.set_display_flag(sop_path, True)
bridge.set_render_flag(sop_path, True)
bridge.layout_children(geo_path)
```

### 4.2 Resolve input: Object vs SOP

When a node accepts a `geo_path` that could be either an Object-level geo node or a SOP node:

```python
node_info = bridge.node_info(geo_path)
category = node_info.get("category", "")

if category == "Object":
    # Get the display SOP inside the geo container
    run_result = bridge.run_code(
        f"n = hou.node('{geo_path}'); result = n.displayNode().path() if n and n.displayNode() else None"
    )
    input_sop = run_result.get("result")
    if not input_sop:
        raise Exception(f"No display SOP found inside: {geo_path}")
    sop_context = geo_path
elif category == "Sop":
    sop_context = "/".join(geo_path.rstrip("/").split("/")[:-1])
    input_sop = geo_path
else:
    raise Exception(f"Unsupported category '{category}': {geo_path}")
```

### 4.3 VEX wrangle via attribwrangle

```python
vex_code = (
    'vector p0 = point(0, "P", primpoint(0, @primnum, 0));\n'
    'vector p1 = point(0, "P", primpoint(0, @primnum, 1));\n'
    'vector dir = normalize(p1 - p0);\n'
    'if (abs(dot(dir, set(1,0,0))) < 0.9) { removeprim(0, @primnum, 1); }'
)

wrangle_result = bridge.create_node(sop_context, "attribwrangle", "my_wrangle")
wrangle_path = wrangle_result["path"]
bridge.connect_nodes(input_sop, wrangle_path, output=0, input_idx=0)
bridge.set_parm(wrangle_path, "class", 1)       # 0=detail, 1=primitive, 2=point, 3=vertex
bridge.set_parm(wrangle_path, "snippet", vex_code)
```

### 4.4 Standard execute pattern for Houdini nodes

```python
async def execute(self, inputs):
    geo_path = inputs.get("geo_path", "")
    if not geo_path:
        self.log_error("No geo path provided.")
        return {"result_path": "", "exec_out": True}

    try:
        bridge = get_bridge()
        # ... create nodes ...
        return {"result_path": result_path, "exec_out": True}
    except Exception as e:
        self.log_error(f"Houdini operation failed: {str(e)}")
        return {"result_path": "", "exec_out": True}
```

---

## 5. Mistakes to Avoid

| Wrong | Correct |
|-------|---------|
| `from src.utils import hou_bridge; hou_bridge.get_hou()` | `from src.utils.hou_bridge import get_bridge; bridge = get_bridge()` |
| `hou.node("/obj").createNode(...)` | `bridge.create_node("/obj", ...)` |
| `node.parm("x").set(1.0)` | `bridge.set_parm(node_path, "x", 1.0)` |
| `result = bridge.create_node(...); result.path()` | `result = bridge.create_node(...); path = result["path"]` |
| `for c in bridge.children(p): c.destroy()` | `for c in bridge.children(p): bridge.delete_node(c["path"])` |
| Adding `exec_in`/`exec_out` in `__init__` manually | They are added by `super().__init__()` automatically |
| Adding ports twice (once in AUTO block, once below it) | Add each port exactly once inside the AUTO block |

---

## 6. Houdini Plugin Architecture & Environment Variables

The Houdini integration consists of two sides: code running **inside Houdini** and the Vibrante-Node **subprocess**.

### 6.1 Plugin file layout

```
plugins/houdini/
├── vibrante_node.json                  ← Houdini package file (user installs this)
├── v_nodes_houdini/                    ← Houdini-specific node .json definitions
│   ├── hou_create_geo.json
│   └── ...
├── v_scripts_houdini/                  ← Houdini-specific .py scripts (Scripts menu)
│   ├── hou_create_box_demo.py
│   └── ...
└── houdini/                            ← Added to HOUDINI_PATH by package JSON
    ├── MainMenuCommon.xml              ← Adds "Vibrante-Node" menu to Houdini menu bar
    ├── toolbar/vibrante_node.shelf     ← Shelf tool
    └── scripts/python/
        ├── pythonrc.py                 ← Runs at Houdini startup; validates env vars
        ├── vibrante_node_houdini.py    ← launch(), setup_env(), show_about(), etc.
        └── vibrante_hou_server.py      ← JSON-RPC server running inside Houdini
```

### 6.2 vibrante_node.json — what the user must configure

```json
{
    "env": [
        { "VIBRANTE_NODE_APP": "/path/to/node_based_app" },
        { "VIBRANTE_PYTHON_EXE": "C:/Python311/python.exe" }
    ],
    "path": "$VIBRANTE_NODE_APP/plugins/houdini/houdini"
}
```

- `VIBRANTE_NODE_APP` — absolute path to the app root (where `src/main.py` lives). **Must be set.**
- `VIBRANTE_PYTHON_EXE` — path to system Python 3.11 with PyQt5. Optional: auto-detected if missing but slower.
- `path` — adds `plugins/houdini/houdini/` to `HOUDINI_PATH` so Houdini finds `MainMenuCommon.xml`, the shelf, and `pythonrc.py`.

### 6.3 Environment variable flow

When `launch()` is called from Houdini, `setup_env()` builds the subprocess environment:

| Variable | Set by | Consumed by |
|----------|--------|-------------|
| `VIBRANTE_NODE_APP` | `vibrante_node.json` | `vibrante_node_houdini.get_app_root()` |
| `VIBRANTE_PYTHON_EXE` | `vibrante_node.json` | `vibrante_node_houdini._find_system_python()` |
| `VIBRANTE_HOUDINI_MODE` | `setup_env()` → `"subprocess"` | `src/utils/qt_compat.py` (selects PyQt5) |
| `VIBRANTE_HOU_PORT` | `setup_env()` after server starts | `src/utils/hou_bridge.py` (default: 18811) |
| `VIBRANTE_HIP_FILE` | `setup_env()` with hip path | Available in node python_code via `os.environ` |
| `v_nodes_dir` | `setup_env()` → path to `v_nodes_houdini/` | `NodeRegistry.load_all_with_extras()` in `window.py` |
| `v_scripts_path` | `setup_env()` → path to `v_scripts_houdini/` | `MainWindow._populate_scripts_menu()` in `window.py` |

**Critical**: `v_nodes_dir` and `v_scripts_path` are only set in the **subprocess** environment (not in Houdini itself). They are computed by `setup_env()` each time `launch()` is called.

### 6.4 Node loading at startup

`src/ui/window.py` initialises the registry in this order:
1. `NodeRegistry.load_all_with_extras(bundled_nodes)` — loads bundled nodes **and** any paths in `v_nodes_dir`
2. `NodeRegistry._load_directory(self.nodes_dir)` — loads user-created nodes from next to the exe

Always use `load_all_with_extras`, never plain `load_all`, or the Houdini nodes will be silently skipped.

### 6.5 Scripts menu

`MainWindow._populate_scripts_menu()` scans every directory in `v_scripts_path` for `.py` files and adds a clickable menu item for each. Scripts run via `exec()` with `{'window': self, 'scene': self.get_current_scene()}` as globals. A "Refresh Scripts" item re-scans without restarting.

Scripts in `v_scripts_houdini/` can use `get_bridge()` exactly like node python_code.

### 6.6 Startup diagnostics

`pythonrc.py` runs inside Houdini on every startup and prints to the Houdini Python console:
- `VIBRANTE_NODE_APP` — OK / ERROR (not set or path doesn't exist)
- `VIBRANTE_PYTHON_EXE` — OK / WARNING (missing or path not found)
- `v_nodes_houdini/` — OK / MISSING
- `v_scripts_houdini/` — OK / MISSING

Use **Vibrante-Node → About Vibrante-Node Integration** in Houdini's menu bar to see the same info on demand, including real-time OK/MISSING status for both plugin folders.

### 6.7 Houdini command server (vibrante_hou_server.py) — known behaviours

- `hou.playbar.frameRange()` raises `AttributeError` in headless Houdini (hbatch / hython). The server catches this and returns `[1, 240]` as fallback.
- `setDisplayFlag` / `setRenderFlag` raise `hou.OperationFailed` on node types that don't support flags (e.g. `null` at Object level). The server catches and re-raises as `ValueError` with a clear message.
- `start()` / `stop()` are guarded by a module-level `threading.Lock` to prevent double-bind race conditions.

### 6.8 HouBridge client (src/utils/hou_bridge.py) — known behaviours

- Each `HouBridge` instance has its own `threading.Lock`; `_send()` is thread-safe.
- `socket.TCP_NODELAY` is set on connect to avoid ~40 ms Nagle delay on Windows.
- A 30-second `socket.timeout` is set. If the server doesn't respond (e.g. Houdini is blocked cooking), `ConnectionError` is raised with a clear message and the socket is closed so the next call reconnects.
- On `BrokenPipeError` / `ConnectionResetError` the client reconnects once automatically.

---

## 7. Headless Action Nodes (v1.5.0)

Headless action nodes (Maya, Houdini, Blender) follow a "list-builder" pattern. They don't perform work themselves; they just append a dictionary to a list that is later processed by the Headless Executor.

### 7.1 Action Node Skeleton

```python
class DCC_Action_Node(BaseNode):
    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("actions_in", "list")
        self.add_input("some_param", "string", widget_type="text")
        self.add_output("actions_out", "list")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        actions = list(inputs.get("actions_in") or [])
        
        # Build the action dictionary
        action = {
            "type": "my_action_type",
            "some_param": inputs.get("some_param", "")
        }
        
        actions.append(action)
        
        return {
            "actions_out": actions,
            "exec_out": True
        }
```

### 7.2 Conventions for Action Nodes

- **`node_id`** should follow the pattern: `maya_action_...`, `houdini_action_...`, or `blender_action_...`.
- **`category`** should be `"Maya"`, `"Houdini"`, or `"Blender"`.
- **`actions_in` / `actions_out`** are mandatory for chaining.
- Always use `list(inputs.get("actions_in") or [])` to avoid mutating the original list or failing on None.
- The `type` field in the dictionary must match a handler in the corresponding DCC runner script.

---

## 8. Prism Pipeline Integration (v1.6.0)

Prism nodes communicate with the Prism Pipeline studio-management system. PrismCore is resolved automatically — you never need to wire it between nodes.

### 8.1 Core resolution

```python
from src.utils.prism_core import resolve_prism_core

async def execute(self, inputs):
    core = resolve_prism_core(inputs)   # checks inputs, global cache, shared memory
    if core is None:
        self.log_error("PrismCore not initialized. Add a prism_core_init node to the graph.")
        return {"exec_out": True}
    # use core normally
```

The registry automatically rewrites `core = inputs.get('core')` → `core = resolve_prism_core(inputs)` for any node whose `node_id` starts with `prism_`. You never need to do this manually.

### 8.2 Auto-bootstrap

Place a `prism_core_init` node anywhere in the graph. Before the main execution starts, the engine detects it and calls `bootstrap_prism_core()` on the Qt main thread. All subsequent `prism_*` nodes share the same `PrismCore` instance without any wiring.

### 8.3 Prism node skeleton

```python
from src.nodes.base import BaseNode
from src.utils.prism_core import resolve_prism_core

class Prism_Get_Assets(BaseNode):
    name = "prism_get_assets"

    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("entity",  "string", widget_type="text")
        self.add_output("assets", "list")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        core = resolve_prism_core(inputs)
        if core is None:
            self.log_error("PrismCore not available.")
            return {"assets": [], "exec_out": True}
        try:
            assets = core.getAssets(entity=inputs.get("entity", ""))
            return {"assets": assets, "exec_out": True}
        except Exception as e:
            self.log_error(f"Prism error: {e}")
            return {"assets": [], "exec_out": True}

def register_node():
    return Prism_Get_Assets
```

### 8.4 Conventions for Prism nodes

- **`node_id`** must start with `prism_` (e.g., `prism_get_assets`).
- **`category`** must be `"Prism"`.
- **`icon_path`** use `"icons/prism_icon.png"`.
- Never add a `core` input port — it is resolved automatically.
- Always guard with `if core is None` and return a safe default.
- Use `list(...)` or `{}` as safe empty defaults for list/dict outputs.

### 8.5 Qt compatibility

If a node needs Qt features that differ between Qt5 and Qt6, import from `src.utils.qt_compat`:

```python
from src.utils.qt_compat import QtWidgets, QtGui, QtCore
```

The compat module also ensures `QColor.fromString()` and shiboken stubs exist, which Prism requires at import time.

---

## 9. Code Editor & QScintilla (v1.8.5+)

`src/ui/code_editor.py` provides `CodeEditor`, a Python-aware code editor used in the Node Builder, Script Editor dialog, and Scripting Console.

### 9.1 QScintilla is optional

QScintilla (`PyQt5.Qsci`) is tried first. If it is not installed, the module silently falls back to a `QPlainTextEdit`-based implementation with a `QSyntaxHighlighter`. **Do not re-raise `ImportError`** if QScintilla is missing — the app must still start.

```python
# Correct pattern inside code_editor.py
try:
    from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
    _QSCINTILLA_AVAILABLE = True
except ImportError:
    _QSCINTILLA_AVAILABLE = False
    # fallback class defined below

# Do NOT do this — it crashed the app on systems without QScintilla:
# raise ImportError("QScintilla is required...")
```

To install the full editor:
```
pip install QScintilla
```

### 9.2 Public API — same in both implementations

| Method / attribute | Notes |
|--------------------|-------|
| `setPlainText(text)` | Set editor content |
| `toPlainText()` | Get editor content |
| `textChanged` signal | Emitted on every keystroke |
| `lineNumberArea.hide()` / `.show()` | Compatibility shim |
| `apply_theme(is_dark: bool)` | Switch Dracula-dark / One-Light palette |
| `set_completer_list(words)` | Replace autocomplete word list |
| `append_completer_list(words)` | Add words to autocomplete list |
| `error_line` | Line number of last syntax error (-1 if none) |
| Ctrl+Wheel | Zoom in/out |

---

## 10. Bug History & What NOT to Revert (v1.8.5+)

These bugs were found and fixed. Do not revert these changes.

### 10.1 `code_editor.py` — hard crash when QScintilla missing
**Symptom**: `ImportError: No module named 'PyQt5.Qsci'` on startup, app exits immediately.  
**Fix**: Wrap import in `try/except`; define a `QPlainTextEdit`-based fallback `CodeEditor` class instead of raising.  
**File**: `src/ui/code_editor.py`

### 10.2 `hou_bridge.py` — socket issues on Windows
**Symptoms**: ~40 ms latency per RPC call; silent hangs when Houdini was busy; concurrent node calls corrupted the response stream.  
**Fixes**:
- `socket.TCP_NODELAY` set on connect to disable Nagle's algorithm
- `threading.Lock` per instance; `_send()` acquires lock before touching the socket
- `socket.timeout` (30 s) caught in `recv()` loop — disconnects and raises `ConnectionError` with a clear message
- Reconnect retry `sendall` wrapped in `try/except OSError`  
**File**: `src/utils/hou_bridge.py`

### 10.3 `vibrante_hou_server.py` — crashes in headless / non-interactive Houdini
**Symptoms**: `AttributeError` on `hou.playbar.frameRange()` when running hbatch or hython; `hou.OperationFailed` when setting display/render flags on unsupported nodes; port double-bind if `start()` called twice concurrently.  
**Fixes**:
- `hou.playbar.frameRange()` wrapped in `try/except AttributeError`; fallback `[1, 240]`
- `setDisplayFlag` / `setRenderFlag` guarded with `getattr` capability check + `try/except hou.OperationFailed`
- Module-level `threading.Lock` around `start()` / `stop()`  
**File**: `plugins/houdini/houdini/scripts/python/vibrante_hou_server.py`

### 10.4 `vibrante_node_houdini.py` — double `setup_env()` call
**Symptom**: Environment variables like `PYTHONHOME` were being stripped twice; `v_nodes_dir` / `v_scripts_path` were appended twice causing duplicate entries.  
**Fix**: `launch()` accepts `hip_file=""` directly and calls `setup_env()` once internally. `launch_with_context()` calls `launch(hip_file=hip_file)` — no longer calls `setup_env()` itself.  
**File**: `plugins/houdini/houdini/scripts/python/vibrante_node_houdini.py`

### 10.8 Live Wire Value Inspector (v1.8.6+)

**Feature**: Hover over any connected wire during or after execution to see the last value that flowed through it as a tooltip (`port_name: repr(value)`, capped at 300 chars).

**How it works:**
- `Edge.set_live_value(value)` stores the value and calls `self.setToolTip(label)`. Qt shows the tooltip automatically on hover.
- `Edge.shape()` overrides the default 2 px hit area with a 12 px stroked path so the wire is easy to hover over.
- `Edge.clear_live_value()` resets both `_live_value` and the tooltip.
- `NodeScene.update_edge_value(node_widget, port_name, value)` finds every edge whose `from_port.parentItem() is node_widget` and `from_port.port_definition.name == port_name`, then calls `set_live_value()`.
- `NodeScene.clear_edge_values()` clears all edges — called at the start of each execution run.
- `MainWindow._on_node_output` calls `scene.update_edge_value()` for every port in `results` immediately after calling `widget.set_parameter()`.

**Values persist after execution** so the user can inspect the final state of every wire without re-running. They are cleared only when the next execution starts.

### 10.7 Autosave / Crash Recovery (v1.8.6+)

**Feature**: A `QTimer` fires every 2 minutes and writes all non-empty open tabs to `~/.vibrante_node_autosave.json`. On the next launch, if that file exists, the user is offered a restore dialog. On clean exit (`closeEvent`), the file is deleted so the dialog is never shown unnecessarily.

**Format**:
```json
{"version": 1, "tabs": [{"name": "tab label", "file_path": "/saved/path.json or ''", "workflow": {...WorkflowModel dict...}}]}
```

**Key methods in `MainWindow`**:
- `_autosave()` — serialises all tabs; skips empty tabs and skips if `_is_executing`; silent on failure (prints to console only)
- `_try_restore_autosave()` — called in `__init__` before `add_new_workflow()`; returns `True` if any tab was restored (suppresses default empty tab); always deletes the autosave file after the dialog regardless of user choice
- `closeEvent` — calls `os.remove(_autosave_path)` after `_save_user_settings()`

**Guarded against**: execution in progress (`_is_executing`), empty tabs, corrupt autosave file (silently deleted), missing file on removal.

### 10.6 Recent Files (v1.8.6+)

**Feature**: File menu → **Open Recent** submenu lists the last 10 saved/loaded workflows. Entries for files that no longer exist on disk are shown grayed-out (disabled). "Clear Recent Files" wipes the list.

**Storage**: `config.get_recent_files()` / `config.add_recent_file(path)` / `config.clear_recent_files()` in `src/utils/config_manager.py`. Key: `"recent_files"` (JSON list of absolute paths, max 10, newest first).

**Registration**: `MainWindow._add_recent_file(path)` is called at the end of every successful `save_workflow`, `save_workflow_as`, and `load_workflow`. Opening from the menu calls `_load_workflow_from_path(path)` — same logic as `load_workflow` but without the file dialog.

**Menu rebuild**: `file_menu.aboutToShow` triggers `_rebuild_recent_menu()` so the list is always fresh when the File menu opens.

### 10.5 `window.py` — Houdini nodes and scripts never loaded
**Symptoms**: Nodes from `v_nodes_houdini/` did not appear in the Library after launching from Houdini. No Scripts menu. `v_scripts_path` env var was set but never read.  
**Fixes**:
- Changed `NodeRegistry.load_all(bundled_nodes)` → `NodeRegistry.load_all_with_extras(bundled_nodes)` so `v_nodes_dir` is honoured
- Added `&Scripts` menu in `_init_menu()` populated by `_populate_scripts_menu()` which scans `v_scripts_path`
- Added `_run_script_file(path)` to execute scripts in window/scene context  
**File**: `src/ui/window.py`

### 10.9 Canvas Search Bar — Ctrl+F (v1.8.7+)

**Feature**: Press Ctrl+F (or Edit → Find in Canvas…) to open a floating search bar centred at the top of the canvas. Type to filter `scene.nodes` by display name or `node_id`. The matched node is selected and the view pans to it. Enter/▼ cycles forward; Shift+Enter/▲ cycles backward. Match counter shows "X / N". Escape closes.

**Architecture:**
- `src/ui/canvas/canvas_search_bar.py` — `CanvasSearchBar(QFrame)`, child widget of `NodeView`. Positioned with `move(x, 8)` on show; repositioned in `NodeView.resizeEvent` if visible.
- `NodeView` — instantiates `_canvas_search_bar` in `__init__`; exposes `show_canvas_search()`.
- `MainWindow._init_menu()` — Edit menu separator + "Find in Canvas… Ctrl+F" action → `_find_in_canvas()`.
- Theme detected from `scene.backgroundBrush().color().lightness() < 128` (same pattern as `NodeSearchPopup`).

**Key search logic** (in `CanvasSearchBar._on_text_changed`):
```python
self._matches = [
    w for w in scene.nodes
    if t in w.node_definition.name.lower()
    or t in getattr(w.node_definition, 'node_id', '').lower()
]
```
Panning: `self._view.centerOn(node)` after `node.setSelected(True)`.

### 10.10 Node Execution Timing (v1.8.7+)

**Feature**: The log panel now shows how long each node took to execute — e.g. `Node 'Get Asset' finished in 0.34s`.

**Implementation** — 4 surgical changes to `src/ui/window.py` only:
- `import time` added to stdlib imports.
- `self._node_start_times = {}` reset in `execute_pipeline` before the executor is created (per-run isolation).
- `_on_node_started`: `self._node_start_times[node_instance_id] = time.perf_counter()`
- `_on_node_finished`: pops the start time, computes `elapsed = time.perf_counter() - t0`, logs `"Node 'X' finished in {elapsed:.2f}s"` at level `"info"`. `dict.pop(key, None)` guards against any race where finish fires without a matching start.

No changes to `engine.py` or any signal signatures.

### 10.11 Mini-map (v1.8.7+)

**Feature**: A 200×150 px thumbnail of the full canvas is always visible in the bottom-right corner of each `NodeView`. A blue semi-transparent rectangle shows the current viewport. Click or drag the mini-map to pan the main view. Toggle with Ctrl+M or Window → Toggle Mini-map.

**Architecture:**
- `src/ui/canvas/mini_map.py` — `MiniMap(QGraphicsView)`, child widget of `NodeView`. Shares the same `QGraphicsScene` — Qt renders the scene automatically.
- `setInteractive(False)` prevents scene items from receiving mouse events through the mini-map; `mousePressEvent`/`mouseMoveEvent` are overridden to call `self._main_view.centerOn(scene_pos)`.
- `drawForeground()` draws the viewport indicator in scene coordinates: maps `main_view.viewport().rect()` corners to scene space via `main_view.mapToScene()`, then draws a `QRectF`.
- `_do_fit()` calls `self.fitInView(scene.itemsBoundingRect() + padding, Qt.KeepAspectRatio)` and is debounced at 80 ms via a single-shot `QTimer` connected to `scene.changed`.
- `NodeView.__init__`: instantiates mini-map, calls `attach_scene(scene)`, connects `horizontalScrollBar().valueChanged` and `verticalScrollBar().valueChanged` to `mini_map.refresh()` (which just calls `update()`). Also calls `mini_map.refresh()` after `scale()` in `wheelEvent` and `mini_map.reposition()` in `resizeEvent`.
- `NodeView.apply_theme(is_dark)` cascades to `mini_map.apply_theme()` — called from `MainWindow._apply_dark_theme()` / `_apply_light_theme()`.
- `MainWindow._toggle_mini_map()` toggles `view._mini_map.setVisible(...)` for the current tab.

**Do not** call `setInteractive(True)` on the mini-map — scene item events must stay suppressed.

### 10.12 Subgraph / Group Node (v1.9.0+)

**Feature**: Select 2+ connected nodes and press **Ctrl+Shift+G** (Edit → Group Selection) to collapse them into a single `GroupNode` that stores the subgraph as an embedded `WorkflowModel`. Double-click the GroupNode to open the subgraph in a new tab (read-only view — edits there don't propagate back yet).

**Node classes** (`src/nodes/builtins/group_node.py`):
- `GroupInNode` (`group_in`): `use_exec=False`; input `port_name` (text widget); output `value`. Returns `{"value": self.parameters.get("value")}`.
- `GroupOutNode` (`group_out`): `use_exec=False`; inputs `port_name` (text widget) + `value`; output `value`. Returns `{"value": inputs.get("value")}`.
- `GroupNode` (`group_node`): `use_exec=True`; stores `__workflow__` (WorkflowModel dict), `__port_defs__` (list of `{name, type, is_input}`), `__name__` (display name) in `self.parameters`. Dynamic ports are re-added at load time via `restore_from_parameters()`.

**Registry registration** (`src/core/registry.py`):
```python
from src.nodes.builtins.group_node import GroupInNode, GroupOutNode, GroupNode
for _cls in (GroupInNode, GroupOutNode, GroupNode):
    _cls.node_id = _cls.name
    cls._classes[_cls.name] = _cls
```
Registered in `_classes` only (not `_definitions`) → hidden from the node search popup but still executable and loadable from saved workflows.

**Collapsing** (`NodeScene.group_selection()` in `src/ui/canvas/scene.py`):
1. Classify all edges incident on selected nodes as boundary_in (external→selected), boundary_out (selected→external), boundary_exec_in, boundary_exec_out, or internal.
2. Build a `WorkflowModel` with: all selected `NodeInstanceModel`s + one `GroupInNode` per unique boundary_in port + one `GroupOutNode` per unique boundary_out port, wired to the corresponding inner node inputs/outputs.
3. Remove selected nodes and their edges from the scene.
4. Create a `GroupNode` widget at the centroid; set `__workflow__`, `__port_defs__`, `__name__` parameters; call `rebuild_ports()` to materialize the dynamic ports.
5. Reconnect external boundary edges to the new GroupNode's ports.

**UUID safety**: `widget.instance_id` can be a `UUID` object or a string UUID (paste path). Always compare with `str(instance_id)`.

**Double-click to inspect** (`NodeScene.mouseDoubleClickEvent`):
```python
def mouseDoubleClickEvent(self, event):
    for item in self.items(event.scenePos()):
        target = item
        while target is not None and not isinstance(target, NodeWidget):
            target = target.parentItem()
        if isinstance(target, NodeWidget) and getattr(target.node_definition, 'node_id', '') == 'group_node':
            parent = self.parent()
            if parent and hasattr(parent, '_open_subgraph_tab'):
                parent._open_subgraph_tab(target)
            event.accept()
            return
    super().mouseDoubleClickEvent(event)
```

**Tab opener** (`MainWindow._open_subgraph_tab(group_widget)`):
- Reads `group_widget.node_definition.parameters["__workflow__"]`
- Validates as `WorkflowModel`
- Calls `add_new_workflow(f"[{group_name}]")` → `view.scene().from_workflow_model(workflow_model)`

**Keyboard shortcut conflict note**: Ctrl+G is already used by "Wrap in Backdrop" in `view.keyPressEvent`. Group Selection uses **Ctrl+Shift+G** instead.
