"""
Converts a WorkflowModel into a standalone Python script.

The generated script replicates the workflow logic using plain Python
and can run independently without Vibrante-Node.
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from uuid import UUID
from collections import defaultdict
from src.core.models import WorkflowModel, NodeInstanceModel, ConnectionModel
from src.core.graph import GraphManager
from src.core.registry import NodeRegistry


class WorkflowToPythonConverter:
    def __init__(self, workflow: WorkflowModel):
        self.workflow = workflow
        self.nodes: Dict[UUID, NodeInstanceModel] = {
            n.instance_id: n for n in workflow.nodes
        }
        self.connections = workflow.connections

        # Index connections for fast lookup
        self.data_conns_to: Dict[UUID, List[ConnectionModel]] = defaultdict(list)
        self.data_conns_from: Dict[UUID, List[ConnectionModel]] = defaultdict(list)
        self.exec_conns_from: Dict[UUID, List[ConnectionModel]] = defaultdict(list)
        self.exec_conns_to: Dict[UUID, List[ConnectionModel]] = defaultdict(list)

        for conn in self.connections:
            if conn.is_exec:
                self.exec_conns_from[conn.from_node].append(conn)
                self.exec_conns_to[conn.to_node].append(conn)
            else:
                self.data_conns_to[conn.to_node].append(conn)
                self.data_conns_from[conn.from_node].append(conn)

        # Variable naming state
        self._var_map: Dict[Tuple[UUID, str], str] = {}
        self._node_counters: Dict[str, int] = defaultdict(int)
        self._emitted: Set[UUID] = set()
        self._lines: List[str] = []

    def convert(self) -> str:
        has_exec = any(c.is_exec for c in self.connections)

        header = self._generate_header()
        if has_exec:
            body = self._generate_flow_based()
        else:
            body = self._generate_data_flow()

        return header + "\n" + body + "\n"

    # ── Header ──────────────────────────────────────────────────

    def _generate_header(self) -> str:
        lines = [
            '"""',
            'Auto-generated Python script from Vibrante-Node workflow.',
            '"""',
        ]

        # Detect which imports are needed
        node_ids = {n.node_id for n in self.workflow.nodes}
        imports = set()
        if node_ids & {"delay_timer"}:
            imports.add("import time")
        if node_ids & {"example_random_float"}:
            imports.add("import random")
        if node_ids & {"file_write", "append_file", "File Loader", "list_directory", "create_folder"}:
            imports.add("import os")
        if node_ids & {"create_folder"}:
            imports.add("from pathlib import Path")

        if imports:
            lines.append("")
            lines.extend(sorted(imports))

        # Shared variable store for Set/Get Variable nodes
        if node_ids & {"Set Variable", "Get Variable", "List Append"}:
            lines.append("")
            lines.append("variables = {}")

        lines.append("")
        return "\n".join(lines)

    # ── Data-flow mode (topological) ────────────────────────────

    def _generate_data_flow(self) -> str:
        gm = GraphManager()
        gm.from_model(self.workflow)
        try:
            layers = gm.get_topological_sort()
        except Exception:
            # Fallback: emit nodes in arbitrary order
            layers = [{nid for nid in self.nodes}]

        lines = []
        for layer in layers:
            for node_id in layer:
                if node_id not in self._emitted:
                    lines.extend(self._emit_node(node_id, indent=0))
        return "\n".join(lines)

    # ── Flow-based mode (exec chains) ──────────────────────────

    def _generate_flow_based(self) -> str:
        has_exec_in_conn = {c.to_node for c in self.connections if c.is_exec}
        entry_nodes = []

        for node_id, node in self.nodes.items():
            has_exec_out = bool(self.exec_conns_from.get(node_id))
            has_exec_in = node_id in has_exec_in_conn
            if has_exec_out and not has_exec_in:
                entry_nodes.append(node_id)

        # Also include orphan data-only nodes that no flow node depends on
        # (they'll be pulled as dependencies)

        lines = []
        for entry in entry_nodes:
            lines.extend(self._follow_exec_chain(entry, indent=0))
        return "\n".join(lines)

    def _follow_exec_chain(self, node_id: UUID, indent: int) -> List[str]:
        if node_id in self._emitted:
            return []

        node = self.nodes.get(node_id)
        if node is None:
            return []

        lines = []

        # First resolve any upstream data-only dependencies
        self._resolve_data_deps(node_id, indent, lines)

        # Control flow nodes get special treatment (unless bypassed)
        is_bypassed = getattr(node, 'bypassed', False)
        
        if node.node_id == "if_condition" and not is_bypassed:
            lines.extend(self._emit_if(node_id, indent))
        elif node.node_id in ("for_loop",) and not is_bypassed:
            lines.extend(self._emit_for_loop(node_id, indent))
        elif node.node_id == "For Each" and not is_bypassed:
            lines.extend(self._emit_for_each(node_id, indent))
        elif node.node_id in ("While Loop", "while_loop") and not is_bypassed:
            lines.extend(self._emit_while(node_id, indent))
        elif node.node_id == "loop_body" and not is_bypassed:
            lines.extend(self._emit_loop_body(node_id, indent))
        else:
            # Regular node or BYPASSED control flow node
            lines.extend(self._emit_node(node_id, indent))
            # Follow exec_out
            for conn in self.exec_conns_from.get(node_id, []):
                if conn.from_port == "exec_out":
                    lines.extend(self._follow_exec_chain(conn.to_node, indent))

        return lines

    def _resolve_data_deps(self, node_id: UUID, indent: int, lines: List[str]):
        """Emit any upstream data-only nodes that haven't been emitted yet."""
        for conn in self.data_conns_to.get(node_id, []):
            src = conn.from_node
            if src not in self._emitted and src in self.nodes:
                # Only auto-emit if the source is NOT driven by exec flow
                if src not in {c.to_node for c in self.connections if c.is_exec}:
                    self._resolve_data_deps(src, indent, lines)
                    lines.extend(self._emit_node(src, indent))

    # ── Node emission ──────────────────────────────────────────

    def _emit_node(self, node_id: UUID, indent: int) -> List[str]:
        if node_id in self._emitted:
            return []
        self._emitted.add(node_id)

        node = self.nodes.get(node_id)
        if node is None:
            return []

        prefix = "    " * indent
        
        # Bypass support: map outputs to first input
        if getattr(node, 'bypassed', False):
            lines = [f"{prefix}# Node {node.node_id} is bypassed"]
            
            # Find first data input
            # We don't have easy access to PortDefinitions here, 
            # so we look at data connections or params
            first_input_val = "None"
            for p_name in node.parameters:
                if p_name not in ('exec_in', 'exec_out', 'exec_false', 'exec_on_finished'):
                    first_input_val = self._inp(node_id, p_name)
                    break
            
            # Assign to all outputs that are used
            for conn in self.data_conns_from.get(node_id, []):
                var = self._var(node_id, conn.from_port)
                lines.append(f"{prefix}{var} = {first_input_val}")
                
            return lines

        try:
            return self._emit_node_impl(node_id, node, prefix)
        except Exception as e:
            return [f"{prefix}# ERROR generating code for {node.node_id}: {e}"]

    def _emit_node_impl(self, node_id: UUID, node: NodeInstanceModel, prefix: str) -> List[str]:
        nid = node.node_id

        # ── Math ──
        if nid == "math_add":
            return [f"{prefix}{self._var(node_id, 'result')} = float({self._inp(node_id, 'a')}) + float({self._inp(node_id, 'b')})"]
        if nid == "add_integers":
            return [f"{prefix}{self._var(node_id, 'result')} = int({self._inp(node_id, 'a')}) + int({self._inp(node_id, 'b')})"]
        if nid == "math_subtract":
            return [f"{prefix}{self._var(node_id, 'result')} = float({self._inp(node_id, 'a')}) - float({self._inp(node_id, 'b')})"]
        if nid == "math_multiply":
            return [f"{prefix}{self._var(node_id, 'result')} = float({self._inp(node_id, 'a')}) * float({self._inp(node_id, 'b')})"]
        if nid == "math_divide":
            b = self._inp(node_id, 'b')
            return [f"{prefix}{self._var(node_id, 'result')} = float({self._inp(node_id, 'a')}) / float({b}) if float({b}) != 0 else 0"]
        if nid == "math_modulo":
            b = self._inp(node_id, 'b')
            return [f"{prefix}{self._var(node_id, 'result')} = float({self._inp(node_id, 'a')}) % float({b}) if float({b}) != 0 else 0"]
        if nid == "example_random_float":
            return [f"{prefix}{self._var(node_id, 'value')} = random.uniform(float({self._inp(node_id, 'min')}), float({self._inp(node_id, 'max')}))"]

        # ── String ──
        if nid == "string_concat":
            # Two variants exist (concat.json and string_concat.json)
            params = node.parameters
            if "str1" in params or "str2" in params:
                sep = self._inp(node_id, 'separator')
                return [f"{prefix}{self._var(node_id, 'combined')} = str({self._inp(node_id, 'str1')}) + str({sep}) + str({self._inp(node_id, 'str2')})"]
            else:
                sep = self._inp(node_id, 'sep')
                return [f"{prefix}{self._var(node_id, 'result')} = str({self._inp(node_id, 'a')}) + str({sep}) + str({self._inp(node_id, 'b')})"]
        if nid == "string_uppercase":
            return [f"{prefix}{self._var(node_id, 'result')} = str({self._inp(node_id, 'text')}).upper()"]
        if nid == "string_lowercase":
            return [f"{prefix}{self._var(node_id, 'result')} = str({self._inp(node_id, 'text')}).lower()"]
        if nid == "string_replace":
            return [f"{prefix}{self._var(node_id, 'result')} = str({self._inp(node_id, 'text')}).replace(str({self._inp(node_id, 'old')}), str({self._inp(node_id, 'new')}))"]
        if nid == "string_split":
            sep = self._inp(node_id, 'separator')
            return [f"{prefix}{self._var(node_id, 'items')} = str({self._inp(node_id, 'text')}).split({sep} or None)"]
        if nid == "string_length":
            return [f"{prefix}{self._var(node_id, 'length')} = len(str({self._inp(node_id, 'text')}))"]
        if nid == "message_node":
            var = self._var(node_id, 'out')
            msg = self._inp(node_id, 'msg')
            return [f"{prefix}{var} = str({msg})"]

        # ── Logic ──
        if nid == "compare":
            op = node.parameters.get("operation", "==")
            return [f"{prefix}{self._var(node_id, 'result')} = ({self._inp(node_id, 'a')} {op} {self._inp(node_id, 'b')})"]
        if nid == "logical_gate":
            op = node.parameters.get("operation", "AND")
            a = self._inp(node_id, 'a')
            b = self._inp(node_id, 'b')
            var = self._var(node_id, 'result')
            if op == "AND":
                return [f"{prefix}{var} = bool({a}) and bool({b})"]
            elif op == "OR":
                return [f"{prefix}{var} = bool({a}) or bool({b})"]
            elif op == "NOT":
                return [f"{prefix}{var} = not bool({a})"]
            return [f"{prefix}{var} = bool({a})"]

        # ── Variables / Data ──
        if nid == "variable_node":
            vtype = node.parameters.get("type", "string")
            val = self._inp(node_id, 'value')
            cast_fn = {"int": "int", "float": "float", "bool": "bool"}.get(vtype, "str")
            return [f"{prefix}{self._var(node_id, 'out')} = {cast_fn}({val})"]
        if nid == "Set Variable":
            return [f"{prefix}variables[{self._inp(node_id, 'name')}] = {self._inp(node_id, 'value')}"]
        if nid == "Get Variable":
            return [f"{prefix}{self._var(node_id, 'value')} = variables.get({self._inp(node_id, 'name')})"]
        if nid == "List Append":
            return [
                f"{prefix}variables.setdefault({self._inp(node_id, 'list_name')}, []).append({self._inp(node_id, 'item')})",
                f"{prefix}{self._var(node_id, 'current_list')} = variables[{self._inp(node_id, 'list_name')}]",
            ]
        if nid == "Two Way Switch":
            cond = self._inp(node_id, 'condition')
            return [f"{prefix}{self._var(node_id, 'output')} = {self._inp(node_id, 'input_1')} if bool({cond}) else {self._inp(node_id, 'input_2')}"]

        # ── Lists / Dicts ──
        if nid == "create_list":
            return [f"{prefix}{self._var(node_id, 'current_list')} = list({self._inp(node_id, 'items')} or [])"]
        if nid == "get_list_item":
            lst = self._inp(node_id, 'list')
            idx = self._inp(node_id, 'index')
            var = self._var(node_id, 'item')
            return [
                f"{prefix}try:",
                f"{prefix}    {var} = {lst}[int({idx})]",
                f"{prefix}except (IndexError, TypeError):",
                f"{prefix}    {var} = None",
            ]
        if nid == "list_length":
            return [f"{prefix}{self._var(node_id, 'length')} = len({self._inp(node_id, 'list')} or [])"]
        if nid == "create_dictionary":
            return [f"{prefix}{self._var(node_id, 'current_dict')} = dict({self._inp(node_id, 'entries')} or {{}})"]
        if nid == "get_dict_value":
            d = self._inp(node_id, 'dict')
            key = self._inp(node_id, 'key')
            return [f"{prefix}{self._var(node_id, 'value')} = ({d} or {{}}).get({key})"]
        if nid == "set_dict_value":
            d = self._inp(node_id, 'dict')
            key = self._inp(node_id, 'key')
            val = self._inp(node_id, 'value')
            return [
                f"{prefix}{d}[{key}] = {val}",
                f"{prefix}{self._var(node_id, 'result_dict')} = {d}",
            ]

        # ── IO ──
        if nid == "console_print":
            data = self._inp(node_id, 'data')
            var = self._var(node_id, 'out')
            return [f"{prefix}print({data})", f"{prefix}{var} = {data}"]
        if nid == "Console Sink":
            return [f"{prefix}print({self._inp(node_id, 'data')})"]
        if nid == "file_write":
            return [
                f"{prefix}with open(str({self._inp(node_id, 'path')}), 'w', encoding=str({self._inp(node_id, 'encoding')} or 'utf-8')) as _f:",
                f"{prefix}    _f.write(str({self._inp(node_id, 'content')}))",
                f"{prefix}{self._var(node_id, 'result')} = True",
            ]
        if nid == "append_file":
            return [
                f"{prefix}with open(str({self._inp(node_id, 'path')}), 'a', encoding=str({self._inp(node_id, 'encoding')} or 'utf-8')) as _f:",
                f"{prefix}    _f.write(str({self._inp(node_id, 'content')}))",
                f"{prefix}{self._var(node_id, 'result')} = True",
            ]
        if nid == "File Loader":
            return [
                f"{prefix}with open(str({self._inp(node_id, 'file_path')}), 'r') as _f:",
                f"{prefix}    {self._var(node_id, 'file_data')} = _f.read()",
            ]
        if nid == "list_directory":
            path = self._inp(node_id, 'path')
            var = self._var(node_id, 'result')
            return [f"{prefix}{var} = os.listdir(str({path}))"]
        if nid == "create_folder":
            return [f"{prefix}Path(str({self._inp(node_id, 'path')})).mkdir(parents=True, exist_ok=True)"]

        # ── Control ──
        if nid == "delay_timer":
            return [f"{prefix}time.sleep(float({self._inp(node_id, 'delay')}))"]

        # ── Scripting ──
        if nid == "python_script":
            return self._emit_python_script(node_id, prefix)

        # ── Data Processor (builtin) ──
        if nid == "Data Processor":
            return [f"{prefix}{self._var(node_id, 'data_out')} = f\"Processed: {{{self._inp(node_id, 'data_in')}}}\""]

        # ── Sequencer ──
        if nid == "Sequencer":
            # Sequencer just passes data through steps; treat as pass-through
            return [f"{prefix}# Sequencer (pass-through)"]

        # ── Unknown ──
        return [f"{prefix}# Unsupported node: {nid} ({node_id})"]

    # ── Control flow emitters ──────────────────────────────────

    def _emit_if(self, node_id: UUID, indent: int) -> List[str]:
        self._emitted.add(node_id)
        prefix = "    " * indent
        node = self.nodes[node_id]
        cond = self._inp(node_id, 'condition')
        result_var = self._var(node_id, 'result')

        lines = [f"{prefix}{result_var} = bool({cond})"]

        # True branch (exec_out)
        true_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_out"]
        false_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_false"]

        lines.append(f"{prefix}if {result_var}:")
        if true_targets:
            for t in true_targets:
                lines.extend(self._follow_exec_chain(t, indent + 1))
        else:
            lines.append(f"{prefix}    pass")

        if false_targets:
            lines.append(f"{prefix}else:")
            for t in false_targets:
                lines.extend(self._follow_exec_chain(t, indent + 1))

        return lines

    def _emit_for_loop(self, node_id: UUID, indent: int) -> List[str]:
        self._emitted.add(node_id)
        prefix = "    " * indent

        start = self._inp(node_id, 'start')
        end = self._inp(node_id, 'end')
        step = self._inp(node_id, 'step')
        indices_var = self._var(node_id, 'indices')
        index_var = self._var(node_id, 'current_index')

        lines = [f"{prefix}{indices_var} = list(range(int({start}), int({end}), int({step})))"]

        body_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_out"]
        if body_targets:
            lines.append(f"{prefix}for {index_var} in {indices_var}:")
            for t in body_targets:
                lines.extend(self._follow_exec_chain(t, indent + 1))
        else:
            lines.append(f"{prefix}for {index_var} in {indices_var}:")
            lines.append(f"{prefix}    pass")

        return lines

    def _emit_loop_body(self, node_id: UUID, indent: int) -> List[str]:
        self._emitted.add(node_id)
        prefix = "    " * indent

        indices = self._inp(node_id, 'indices')
        index_var = self._var(node_id, 'current_index')

        lines = [f"{prefix}for {index_var} in ({indices} or []):"]

        body_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_out"]
        if body_targets:
            for t in body_targets:
                lines.extend(self._follow_exec_chain(t, indent + 1))
        else:
            lines.append(f"{prefix}    pass")

        # exec_on_finished follows after the loop
        finished_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_on_finished"]
        for t in finished_targets:
            lines.extend(self._follow_exec_chain(t, indent))

        return lines

    def _emit_for_each(self, node_id: UUID, indent: int) -> List[str]:
        self._emitted.add(node_id)
        prefix = "    " * indent

        collection = self._inp(node_id, 'collection')
        item_var = self._var(node_id, 'current_item')
        index_var = self._var(node_id, 'current_index')

        lines = [f"{prefix}for {index_var}, {item_var} in enumerate({collection} or []):"]

        body_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "each_item"]
        if body_targets:
            for t in body_targets:
                lines.extend(self._follow_exec_chain(t, indent + 1))
        else:
            lines.append(f"{prefix}    pass")

        # exec_on_finished follows after the loop
        finished_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_on_finished"]
        for t in finished_targets:
            lines.extend(self._follow_exec_chain(t, indent))

        return lines

    def _emit_while(self, node_id: UUID, indent: int) -> List[str]:
        self._emitted.add(node_id)
        prefix = "    " * indent
        node = self.nodes[node_id]

        max_iter = node.parameters.get("max_iterations", 100)
        index_var = self._var(node_id, 'current_index')
        cond_var = self._var(node_id, '_condition')

        lines = [
            f"{prefix}{index_var} = 0",
            f"{prefix}while {index_var} < {max_iter}:",
        ]

        # Body targets from each_iteration exec
        body_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port in ("each_iteration", "exec_out")]
        if body_targets:
            for t in body_targets:
                lines.extend(self._follow_exec_chain(t, indent + 1))
        else:
            lines.append(f"{prefix}    pass")

        lines.append(f"{prefix}    {index_var} += 1")

        # exec_on_finished follows after the loop
        finished_targets = [c.to_node for c in self.exec_conns_from.get(node_id, []) if c.from_port == "exec_on_finished"]
        for t in finished_targets:
            lines.extend(self._follow_exec_chain(t, indent))

        return lines

    # ── Python script node (inline user code) ──────────────────

    def _emit_python_script(self, node_id: UUID, prefix: str) -> List[str]:
        node = self.nodes[node_id]
        user_code = node.parameters.get("python_code", "")
        if not user_code.strip():
            return [f"{prefix}# (empty python_script node)"]

        data_input = self._inp(node_id, 'data')
        result_var = self._var(node_id, 'result')

        lines = [f"{prefix}# --- Inline Python Script ---"]
        lines.append(f"{prefix}inputs = {{'data': {data_input}}}")
        lines.append(f"{prefix}params = {repr(node.parameters)}")
        for line in user_code.splitlines():
            lines.append(f"{prefix}{line}")
        lines.append(f"{prefix}{result_var} = locals().get('result')")
        lines.append(f"{prefix}# --- End Inline Script ---")
        return lines

    # ── Input resolution helpers ───────────────────────────────

    def _inp(self, node_id: UUID, port_name: str) -> str:
        """Resolve an input: return variable reference if connected, else literal."""
        for conn in self.data_conns_to.get(node_id, []):
            if conn.to_port == port_name:
                return self._var(conn.from_node, conn.from_port)

        # Fall back to parameter literal
        node = self.nodes[node_id]
        val = node.parameters.get(port_name)
        if val is None:
            return "None"
        return repr(val)

    def _var(self, node_id: UUID, port_name: str) -> str:
        """Get or create a variable name for a node output port."""
        key = (node_id, port_name)
        if key not in self._var_map:
            node = self.nodes.get(node_id)
            if node is None:
                base = "unknown"
            else:
                base = node.node_id.replace(" ", "_").lower()
            count = self._node_counters[base]
            self._node_counters[base] += 1
            if port_name in ("result", "out", "output", "value"):
                self._var_map[key] = f"{base}_{count}"
            else:
                self._var_map[key] = f"{base}_{count}_{port_name}"
        return self._var_map[key]


def convert_workflow_to_python(workflow: WorkflowModel) -> str:
    """Public API: converts a WorkflowModel to a standalone Python script string."""
    converter = WorkflowToPythonConverter(workflow)
    return converter.convert()
