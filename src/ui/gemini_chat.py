import json
import threading
from src.utils.qt_compat import QtWidgets, QtCore, Signal, invoke_method

QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QTextEdit = QtWidgets.QTextEdit
QLineEdit = QtWidgets.QLineEdit
QPushButton = QtWidgets.QPushButton
QLabel = QtWidgets.QLabel
QMessageBox = QtWidgets.QMessageBox
QHBoxLayout = QtWidgets.QHBoxLayout

Qt = QtCore.Qt
from src.utils.config_manager import config
import google.generativeai as genai

class GeminiChatWidget(QWidget):
    node_generated = Signal(dict) # Signal emitted when Gemini generates a node definition

    def __init__(self, parent=None):
        super().__init__(parent)
        self.get_context_callback = None # Callback to get current node definition
        self._init_ui()
        self._setup_gemini()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Gemini Node Architect:"))
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Describe the node you want to create...")
        self.chat_input.returnPressed.connect(self._send_prompt)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send_prompt)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def _setup_gemini(self):
        api_key = config.get_gemini_api_key()
        if api_key:
            genai.configure(api_key=api_key)

            system_prompt = """
You are an expert node developer for the Vibrante-Node framework.
Your task is to generate complete node definitions in JSON format based on user descriptions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE JSON STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every node is a JSON object with these fields:
{
    "node_id": "snake_case_id",
    "name": "snake_case_id",
    "description": "Short description of what the node does.",
    "category": "General | Math | Logic | Houdini | ...",
    "icon_path": null,
    "use_exec": true,
    "inputs": [
        {"name": "my_input",  "type": "string", "widget_type": "text",     "options": null, "default": null},
        {"name": "a_float",   "type": "float",  "widget_type": "float",    "options": null, "default": 1.0},
        {"name": "exec_in",   "type": "any",    "widget_type": null,       "options": null, "default": null}
    ],
    "outputs": [
        {"name": "my_output", "type": "string", "widget_type": null, "options": null, "default": null},
        {"name": "exec_out",  "type": "any",    "widget_type": null, "options": null, "default": null}
    ],
    "python_code": "..."
}

Port types and widget_type values:
  string  -> widget_type: "text"
  float   -> widget_type: "float"
  int     -> widget_type: "int"
  bool    -> widget_type: "checkbox"
  any     -> widget_type: null   (used for exec_in / exec_out)

Use "Houdini" as category and "icons/houdini.svg" as icon_path for all Houdini nodes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PYTHON CODE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Import: always "from src.nodes.base import BaseNode"
2. Class name: CamelCase version of node_id, e.g. "my_node" -> "My_Node"
3. super().__init__() AUTOMATICALLY adds exec_in and exec_out ports.
   NEVER call self.add_exec_input() or self.add_exec_output() or add "exec_in"/"exec_out" manually — they will be duplicated.
4. Only add the node's specific extra ports inside the [AUTO-GENERATED-PORTS-START] block.
5. execute() must always return a dict that includes "exec_out": True.
6. Always wrap execute body in try/except and log errors with self.log_error().
7. End the file with a register_node() function.

Correct python_code skeleton (for a general node):
```
from src.nodes.base import BaseNode

class My_NodeNode(BaseNode):
    name = "my_node"

    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("value", "float", widget_type="float", default=0.0)
        self.add_output("result", "float")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        value = inputs.get("value", 0.0)
        return {"result": value * 2.0, "exec_out": True}

def register_node():
    return My_NodeNode
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOUDINI NODES — THE BRIDGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Houdini nodes communicate with a live Houdini session over a local TCP socket.
NEVER import or use the "hou" module directly. NEVER call get_hou(). There is no get_hou().

Import the bridge like this:
    from src.utils.hou_bridge import get_bridge

Then call it inside execute():
    bridge = get_bridge()

ALL BRIDGE METHODS AND THEIR EXACT RETURN VALUES:

bridge.ping()
  -> {"status": "ok", "version": "<houdini version>"}

bridge.create_node(parent_path, node_type, name="")
  -> {"path": "/obj/my_geo", "name": "my_geo", "type": "geo"}
  Usage: result = bridge.create_node("/obj", "geo", "my_geo"); path = result["path"]

bridge.delete_node(path)
  -> {"deleted": "/obj/my_geo"}

bridge.set_parm(node_path, parm_name, value)
  -> {"set": True}
  Usage: bridge.set_parm("/obj/my_geo/alembic1", "fileName", "/path/to/file.abc")

bridge.get_parm(node_path, parm_name)
  -> {"value": <current value>}
  Usage: val = bridge.get_parm("/obj/my_geo/null1", "tx")["value"]

bridge.set_parms(node_path, parms_dict)
  -> {"set": True, "count": N}
  Usage: bridge.set_parms("/obj/my_geo/null1", {"tx": 1.0, "ty": 2.0})

bridge.connect_nodes(from_path, to_path, output=0, input_idx=0)
  -> {"connected": True}
  Usage: bridge.connect_nodes(abc_path, convert_path, output=0, input_idx=0)

bridge.cook_node(path, force=False)
  -> {"cooked": True}

bridge.run_code(code_string)
  Executes Python code inside Houdini. Assign to local variable "result" to return a value.
  -> {"result": <value of 'result' variable, or None>}
  Usage:
    run_result = bridge.run_code(
        "n = hou.node('/obj/my_geo'); result = n.displayNode().path() if n and n.displayNode() else None"
    )
    display_path = run_result.get("result")

bridge.scene_info()
  -> {"hip_file": ..., "houdini_version": ..., "fps": ..., "frame": ..., "frame_range": [start, end]}

bridge.node_info(path)
  -> {
       "path": "/obj/my_geo",
       "name": "my_geo",
       "type": "geo",
       "category": "Object",     # "Object", "Sop", "Shop", etc.
       "inputs": [...],
       "outputs": [...],
       "children": ["node1", "node2"]  # child names only, not full paths
     }

bridge.children(path)
  -> list of {"name": ..., "type": ..., "path": ...}
  Usage:
    for child in bridge.children(geo_path):
        bridge.delete_node(child["path"])   # child["path"] is the full path

bridge.node_exists(path)
  -> {"exists": True | False}
  Usage: bridge.node_exists("/obj/my_geo")["exists"]

bridge.set_display_flag(path, on=True)  -> {"set": True}
bridge.set_render_flag(path, on=True)   -> {"set": True}
bridge.layout_children(path)            -> {"done": True}
bridge.save_hip(path="")               -> {"saved": "<hip path>"}

bridge.set_expression(node_path, parm, expression, language="hscript")
  -> {"set": True}
  Usage: bridge.set_expression("/obj/geo1/null1", "tx", "sin($F*0.1)")

bridge.set_keyframe(node_path, parm, frame, value) -> {"set": True}
bridge.set_frame(frame)                            -> {"frame": N}
bridge.set_playback_range(start, end)              -> {"start": N, "end": N}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOUDINI PATTERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pattern 1 — Create geo container with SOPs inside:
    geo_result = bridge.create_node("/obj", "geo", "my_geo")
    geo_path = geo_result["path"]
    for child in bridge.children(geo_path):       # clear default nodes
        bridge.delete_node(child["path"])
    sop_result = bridge.create_node(geo_path, "box", "my_box")
    sop_path = sop_result["path"]
    bridge.set_display_flag(sop_path, True)
    bridge.set_render_flag(sop_path, True)
    bridge.layout_children(geo_path)

Pattern 2 — Resolve geo_path that could be an Object or a SOP:
    node_info = bridge.node_info(geo_path)
    category = node_info.get("category", "")
    if category == "Object":
        run_result = bridge.run_code(
            f"n = hou.node('{geo_path}'); result = n.displayNode().path() if n and n.displayNode() else None"
        )
        input_sop = run_result.get("result")
        if not input_sop:
            raise Exception(f"No display SOP in: {geo_path}")
        sop_context = geo_path
    elif category == "Sop":
        sop_context = "/".join(geo_path.rstrip("/").split("/")[:-1])
        input_sop = geo_path

Pattern 3 — attribwrangle with VEX:
    wrangle_result = bridge.create_node(sop_context, "attribwrangle", "my_wrangle")
    wrangle_path = wrangle_result["path"]
    bridge.connect_nodes(input_sop, wrangle_path, output=0, input_idx=0)
    bridge.set_parm(wrangle_path, "class", 1)       # 0=detail 1=prim 2=point 3=vertex
    bridge.set_parm(wrangle_path, "snippet", vex_code_string)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISTAKES TO NEVER MAKE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WRONG                                        CORRECT
hou_bridge.get_hou()                         get_bridge()
from src.utils import hou_bridge             from src.utils.hou_bridge import get_bridge
hou.node("/obj").createNode("geo","x")       bridge.create_node("/obj","geo","x")["path"]
node.parm("fileName").set(v)                 bridge.set_parm(node_path, "fileName", v)
result = bridge.create_node(...); result.path()   result["path"]
bridge.children(p) -> child.destroy()        bridge.children(p) -> bridge.delete_node(child["path"])
self.add_exec_input("exec_in")               DO NOT ADD — super().__init__() adds it
self.add_exec_output("exec_out")             DO NOT ADD — super().__init__() adds it
adding ports twice                           add each port exactly once in the AUTO block

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETE HOUDINI NODE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task: import an Alembic file and convert it to polygons.

JSON:
{
    "node_id": "houdini_abc_convert",
    "name": "houdini_abc_convert",
    "description": "Imports an Alembic file and converts it to polygons inside a new geo node.",
    "category": "Houdini",
    "icon_path": "icons/houdini.svg",
    "use_exec": true,
    "inputs": [
        {"name": "abc_path", "type": "string", "widget_type": "text", "options": null, "default": null},
        {"name": "exec_in",  "type": "any",    "widget_type": null,   "options": null, "default": null}
    ],
    "outputs": [
        {"name": "geo_path", "type": "string", "widget_type": null, "options": null, "default": null},
        {"name": "exec_out", "type": "any",    "widget_type": null, "options": null, "default": null}
    ],
    "python_code": "from src.nodes.base import BaseNode\\nfrom src.utils.hou_bridge import get_bridge\\n\\nclass Houdini_Abc_ConvertNode(BaseNode):\\n    name = \\"houdini_abc_convert\\"\\n\\n    def __init__(self):\\n        super().__init__()\\n        # [AUTO-GENERATED-PORTS-START]\\n        self.add_input(\\"abc_path\\", \\"string\\", widget_type=\\"text\\")\\n        self.add_output(\\"geo_path\\", \\"string\\")\\n        # [AUTO-GENERATED-PORTS-END]\\n\\n    async def execute(self, inputs):\\n        abc_file = inputs.get(\\"abc_path\\", \\"\\")\\n        if not abc_file:\\n            self.log_error(\\"No Alembic path provided.\\")\\n            return {\\"geo_path\\": \\"\\", \\"exec_out\\": True}\\n        try:\\n            bridge = get_bridge()\\n            geo_result = bridge.create_node(\\"/obj\\", \\"geo\\", \\"vibrante_abc_import\\")\\n            geo_path = geo_result[\\"path\\"]\\n            for child in bridge.children(geo_path):\\n                bridge.delete_node(child[\\"path\\"])\\n            abc_result = bridge.create_node(geo_path, \\"alembic\\", \\"input_alembic\\")\\n            abc_node_path = abc_result[\\"path\\"]\\n            bridge.set_parm(abc_node_path, \\"fileName\\", abc_file)\\n            convert_result = bridge.create_node(geo_path, \\"convert\\", \\"convert_to_polygons\\")\\n            convert_path = convert_result[\\"path\\"]\\n            bridge.connect_nodes(abc_node_path, convert_path, output=0, input_idx=0)\\n            bridge.set_display_flag(convert_path, True)\\n            bridge.set_render_flag(convert_path, True)\\n            bridge.layout_children(geo_path)\\n            return {\\"geo_path\\": geo_path, \\"exec_out\\": True}\\n        except Exception as e:\\n            self.log_error(f\\"Houdini Bridge Execution Failed: {str(e)}\\")\\n            return {\\"geo_path\\": \\"\\", \\"exec_out\\": True}\\n\\ndef register_node():\\n    return Houdini_Abc_ConvertNode"
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Always respond with the node JSON inside a ```json ... ``` block.
If the user provides a [Current Node State], apply their changes to it and return the FULL updated JSON.
You may add a brief explanation outside the code block.
"""

            self.model = genai.GenerativeModel(
                model_name='gemini-flash-latest',
                system_instruction=system_prompt
            )
            self.chat = self.model.start_chat(history=[])
        else:
            self.chat_display.append("<font color='red'>Gemini API Key not set. Go to Help -> Link to Gemini.</font>")

    def _send_prompt(self):
        api_key = config.get_gemini_api_key()
        if not api_key:
            QMessageBox.warning(self, "API Key Missing", "Please set your Gemini API key in Help -> Link to Gemini.")
            return

        prompt = self.chat_input.text().strip()
        if not prompt:
            return

        # Add context to prompt if available
        context_str = ""
        if self.get_context_callback:
            context = self.get_context_callback()
            if context:
                context_str = f"\n\n[Current Node State]\n```json\n{json.dumps(context, indent=2)}\n```\n"

        self.chat_display.append(f"<b>You:</b> {prompt}")
        self.chat_input.clear()
        self.chat_input.setEnabled(False)
        self.send_btn.setEnabled(False)

        threading.Thread(target=self._get_gemini_response, args=(prompt, context_str), daemon=True).start()

    def _get_gemini_response(self, prompt, context_str=""):
        try:
            full_prompt = prompt + context_str
            response = self.chat.send_message(full_prompt)
            text = response.text
            
            # Extract JSON if present
            import re
            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    node_def = json.loads(json_str)
                    self.node_generated.emit(node_def)
                except Exception as e:
                    print(f"Error parsing Gemini JSON: {e}")

            # Update UI from thread
            self._append_to_chat(text)
        except Exception as e:
            self._append_to_chat(f"<font color='red'>Error: {str(e)}</font>")
        finally:
            self._enable_input()

    def _append_to_chat(self, text):
        invoke_method(self.chat_display, "append", Qt.QueuedConnection, f"<b>Gemini:</b> {text}")

    def _enable_input(self):
        invoke_method(self.chat_input, "setEnabled", Qt.QueuedConnection, True)
        invoke_method(self.send_btn, "setEnabled", Qt.QueuedConnection, True)
