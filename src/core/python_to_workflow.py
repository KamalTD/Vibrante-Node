"""
Converts Python code into a WorkflowModel using Gemini AI.

Sends the Python source along with the full node catalog to Gemini,
which returns a WorkflowModel JSON that can be loaded into the scene.
"""

import json
import re
import threading
from src.utils.qt_compat import QtCore, Signal
QObject = QtCore.QObject
import google.generativeai as genai
from src.utils.config_manager import config
from src.core.models import WorkflowModel
from src.core.registry import NodeRegistry


GEMINI_SYSTEM_PROMPT = """
You are an expert at converting Python scripts into Vibrante-Node visual workflow definitions.

Your task: Given a Python script, produce a JSON object matching the WorkflowModel schema that
recreates the script's logic using the available nodes.

## WorkflowModel JSON Schema:
{{
  "nodes": [
    {{
      "instance_id": "<uuid4 string>",
      "node_id": "<must match one of the available node_ids below>",
      "position": [x, y],
      "parameters": {{ "<port_name>": <value>, ... }},
      "state": "idle"
    }}
  ],
  "connections": [
    {{
      "id": "<uuid4 string>",
      "from_node": "<instance_id of source node>",
      "from_port": "<output port name>",
      "to_node": "<instance_id of target node>",
      "to_port": "<input port name>",
      "is_exec": <true if both ports are exec type, false for data>
    }}
  ],
  "sticky_notes": [],
  "backdrops": [],
  "metadata": {{}}
}}

## Available Nodes:
{node_catalog}

## Rules:
1. Every instance_id and connection id must be a valid UUID4 string (e.g. "550e8400-e29b-41d4-a716-446655440000").
2. node_id MUST exactly match one from the available nodes listed above.
3. For nodes with use_exec=True, create exec connections (is_exec: true) between exec_out of the
   previous node and exec_in of the next to define execution order.
4. Data connections (is_exec: false) connect output data ports to input data ports.
5. Set parameter values in "parameters" for inputs NOT connected to another node.
   Include exec ports as null in parameters.
6. Position nodes left-to-right with ~350px horizontal spacing and sensible vertical layout.
7. For loops: use "for_loop" (generates range) connected to "loop_body" via exec and data,
   or use the builtin "For Each" for iterating collections.
8. For if/else: use "if_condition". Connect exec_out for true branch, exec_false for false.
9. For constants/variables: use "variable_node" with type and value parameters.
10. For print: use "console_print" with a "data" input.
11. For code that does not map to any node: use "python_script" with the code in "python_code" param.
12. Only use nodes from the available list. Do NOT invent node_ids.
13. Return ONLY the JSON inside a ```json``` code block. No extra text outside the block.
"""


class PythonToWorkflowConverter(QObject):
    conversion_finished = Signal(object, str)  # (WorkflowModel or None, error_message)
    status_update = Signal(str)

    def __init__(self):
        super().__init__()

    def convert(self, python_code: str):
        """Start conversion in a background thread."""
        self.status_update.emit("Preparing node catalog...")
        thread = threading.Thread(
            target=self._run_conversion,
            args=(python_code,),
            daemon=True,
        )
        thread.start()

    def _build_node_catalog(self) -> str:
        catalog_lines = []
        for node_id in NodeRegistry.list_node_ids():
            defn = NodeRegistry.get_definition(node_id)
            if defn is None:
                continue
            inputs_desc = ", ".join(
                f"{p.name}:{p.type}" + (f"={p.default}" if p.default is not None else "")
                for p in defn.inputs if p.type != "exec"
            )
            outputs_desc = ", ".join(
                f"{p.name}:{p.type}"
                for p in defn.outputs if p.type != "exec"
            )
            catalog_lines.append(
                f"- node_id=\"{defn.node_id}\", name=\"{defn.name}\", "
                f"inputs=[{inputs_desc}], outputs=[{outputs_desc}], "
                f"use_exec={defn.use_exec}"
            )

        # Also list builtin nodes that may not have JSON definitions
        builtins_extra = [
            '- node_id="File Loader", name="File Loader", inputs=[file_path:string], outputs=[file_data:string], use_exec=True',
            '- node_id="Console Sink", name="Console Sink", inputs=[data:any], outputs=[], use_exec=True',
            '- node_id="Sequencer", name="Sequencer", inputs=[step_0:any], outputs=[result:any], use_exec=True',
            '- node_id="Set Variable", name="Set Variable", inputs=[name:string, value:any], outputs=[value_out:any], use_exec=True',
            '- node_id="Get Variable", name="Get Variable", inputs=[name:string], outputs=[value:any], use_exec=False',
            '- node_id="Two Way Switch", name="Two Way Switch", inputs=[condition:bool, input_1:any, input_2:any], outputs=[output:any], use_exec=True',
            '- node_id="For Each", name="For Each", inputs=[collection:any, break_condition:bool, continue_condition:bool], outputs=[current_item:any, current_index:int, indices:list, completed:bool, broken:bool], use_exec=True',
            '- node_id="While Loop", name="While Loop", inputs=[condition:bool, break_condition:bool, continue_condition:bool, max_iterations:int], outputs=[current_index:int, completed:bool, broken:bool], use_exec=True',
            '- node_id="List Append", name="List Append", inputs=[list_name:string, item:any], outputs=[current_list:list], use_exec=True',
        ]
        catalog_lines.extend(builtins_extra)
        return "\n".join(catalog_lines)

    def _run_conversion(self, python_code: str):
        try:
            api_key = config.get_gemini_api_key()
            if not api_key:
                self.conversion_finished.emit(None, "Gemini API key not configured.\nGo to Help -> Link to Gemini.")
                return

            self.status_update.emit("Building node catalog...")
            catalog = self._build_node_catalog()
            system_prompt = GEMINI_SYSTEM_PROMPT.format(node_catalog=catalog)

            self.status_update.emit("Sending to Gemini AI...")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')

            full_prompt = (
                system_prompt
                + "\n\n## Python Code to Convert:\n```python\n"
                + python_code
                + "\n```"
            )
            response = model.generate_content(full_prompt)
            text = response.text

            self.status_update.emit("Parsing Gemini response...")

            # Extract JSON from response
            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if not json_match:
                self.conversion_finished.emit(
                    None,
                    f"Gemini did not return valid JSON.\n\nResponse:\n{text[:500]}"
                )
                return

            json_str = json_match.group(1)
            data = json.loads(json_str)
            workflow = WorkflowModel.model_validate(data)

            self.status_update.emit("Conversion complete!")
            self.conversion_finished.emit(workflow, "")

        except json.JSONDecodeError as e:
            self.conversion_finished.emit(None, f"Failed to parse JSON from Gemini response:\n{e}")
        except Exception as e:
            self.conversion_finished.emit(None, f"Conversion failed:\n{e}")
