"""
source_inspector.py — Extract ground-truth facts from actual application source code.

Uses the stdlib `ast` module to parse Python files and `json` to parse node
definition files.  No assumptions are made — only what is literally present in
the source is recorded.

Public API
----------
SourceInspector(root: Path) — construct with the repo root
    .inspect_all()          — run all inspections
    .nodes                  — dict[node_id, NodeFact]
    .classes                — dict[class_name, ClassFact]
    .json_nodes_with_errors — list[str]  (node file paths that failed to parse)
"""

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PortFact:
    name: str
    data_type: str
    widget_type: Optional[str] = None
    is_exec: bool = False


@dataclass
class NodeFact:
    node_id: str
    display_name: str
    category: str
    description: str
    use_exec: bool
    inputs: List[PortFact] = field(default_factory=list)
    outputs: List[PortFact] = field(default_factory=list)
    source_file: str = ""
    source_type: str = "json"   # "json" | "builtin"


@dataclass
class MethodFact:
    name: str
    is_async: bool = False
    args: List[str] = field(default_factory=list)
    is_property: bool = False


@dataclass
class ClassFact:
    name: str
    methods: List[MethodFact] = field(default_factory=list)
    class_attrs: List[str] = field(default_factory=list)
    instance_attrs: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)   # pyqtSignal names
    source_file: str = ""


@dataclass
class SignalFact:
    name: str
    param_types: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Inspector
# ---------------------------------------------------------------------------

class SourceInspector:
    def __init__(self, root: Path):
        self.root = root
        self.nodes: Dict[str, NodeFact] = {}
        self.classes: Dict[str, ClassFact] = {}
        self.signals: Dict[str, List[SignalFact]] = {}   # class_name -> signals
        self.json_nodes_with_errors: List[str] = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def inspect_all(self):
        self._load_json_nodes()
        self._load_builtin_nodes()
        self._inspect_python_class(self.root / "src/nodes/base.py", "BaseNode")
        self._inspect_python_class(self.root / "src/core/engine.py", "NetworkExecutor")
        self._inspect_python_class(self.root / "src/core/graph.py", "GraphManager")
        self._inspect_python_class(self.root / "src/core/registry.py", "NodeRegistry")
        self._inspect_pydantic_models(self.root / "src/core/models.py")

    # ------------------------------------------------------------------
    # JSON nodes (nodes/*.json)
    # ------------------------------------------------------------------

    def _load_json_nodes(self):
        nodes_dir = self.root / "nodes"
        if not nodes_dir.exists():
            return

        for jf in sorted(nodes_dir.glob("*.json")):
            try:
                raw = jf.read_text(encoding="utf-8", errors="replace")
                data = json.loads(raw)
            except Exception:
                self.json_nodes_with_errors.append(str(jf.relative_to(self.root)))
                continue

            node_id = data.get("node_id") or jf.stem
            use_exec = data.get("use_exec", True)

            inputs: List[PortFact] = []
            outputs: List[PortFact] = []

            for p in data.get("inputs", []):
                pname = p.get("name", "")
                ptype = p.get("type", "any")
                wtype = p.get("widget_type")
                is_exec = pname in ("exec_in",) or ptype in ("exec",)
                inputs.append(PortFact(pname, ptype, wtype, is_exec))

            for p in data.get("outputs", []):
                pname = p.get("name", "")
                ptype = p.get("type", "any")
                is_exec = pname in ("exec_out",) or ptype in ("exec",)
                outputs.append(PortFact(pname, ptype, None, is_exec))

            self.nodes[node_id] = NodeFact(
                node_id=node_id,
                display_name=data.get("name", node_id),
                category=data.get("category", ""),
                description=data.get("description", ""),
                use_exec=use_exec,
                inputs=inputs,
                outputs=outputs,
                source_file=str(jf.relative_to(self.root)),
                source_type="json",
            )

    # ------------------------------------------------------------------
    # Built-in Python nodes (src/nodes/builtins/)
    # ------------------------------------------------------------------

    def _load_builtin_nodes(self):
        for py_file in [
            self.root / "src/nodes/builtins/nodes.py",
            self.root / "src/nodes/builtins/group_node.py",
        ]:
            if py_file.exists():
                self._parse_node_py_file(py_file)

    def _parse_node_py_file(self, path: Path):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            return

        for cls_node in ast.walk(tree):
            if not isinstance(cls_node, ast.ClassDef):
                continue
            base_names = {
                getattr(b, "id", None) or getattr(b, "attr", None)
                for b in cls_node.bases
            }
            if "BaseNode" not in base_names:
                continue

            node_id: Optional[str] = None
            display_name: Optional[str] = None
            category = ""
            description = ""
            use_exec = True
            inputs: List[PortFact] = []
            outputs: List[PortFact] = []

            for item in cls_node.body:
                # Class-level assignments: name = "...", category = "..."
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if not isinstance(target, ast.Name):
                            continue
                        val = item.value
                        if not isinstance(val, ast.Constant):
                            continue
                        if target.id == "name":
                            node_id = val.value
                            display_name = val.value
                        elif target.id == "category":
                            category = val.value
                        elif target.id == "description":
                            description = val.value

                # __init__ method
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                    # Detect use_exec from super().__init__(use_exec=...)
                    for stmt in ast.walk(item):
                        if not isinstance(stmt, ast.Call):
                            continue
                        func = stmt.func
                        # super().__init__(use_exec=False)
                        if isinstance(func, ast.Attribute) and func.attr == "__init__":
                            for kw in stmt.keywords:
                                if kw.arg == "use_exec" and isinstance(kw.value, ast.Constant):
                                    use_exec = bool(kw.value.value)

                    # Collect add_input / add_output / add_exec_output calls
                    for stmt in ast.walk(item):
                        if not isinstance(stmt, ast.Call):
                            continue
                        func = stmt.func
                        method = getattr(func, "attr", None)
                        if method not in ("add_input", "add_output", "add_exec_output", "add_exec_input"):
                            continue
                        args = stmt.args
                        kwargs = {kw.arg: kw.value for kw in stmt.keywords}

                        def _str(node) -> str:
                            return node.value if isinstance(node, ast.Constant) else "?"

                        pname = _str(args[0]) if args else kwargs.get("name", ast.Constant("?"))
                        if not isinstance(pname, str):
                            pname = _str(pname)
                        ptype = _str(args[1]) if len(args) > 1 else (
                            _str(kwargs["data_type"]) if "data_type" in kwargs else "any"
                        )
                        wtype_node = kwargs.get("widget_type")
                        wtype = _str(wtype_node) if wtype_node and not isinstance(wtype_node, ast.Constant) else (
                            wtype_node.value if isinstance(wtype_node, ast.Constant) else None
                        )

                        if method in ("add_input", "add_exec_input"):
                            is_exec = method == "add_exec_input" or pname == "exec_in"
                            inputs.append(PortFact(pname, ptype, wtype, is_exec))
                        elif method in ("add_output", "add_exec_output"):
                            is_exec = method == "add_exec_output" or pname == "exec_out"
                            outputs.append(PortFact(pname, ptype, None, is_exec))

            if node_id:
                # super().__init__() adds exec_in/exec_out automatically when use_exec=True
                # They are NOT explicitly listed in add_input/add_output calls
                if use_exec:
                    has_exec_in = any(p.name == "exec_in" for p in inputs)
                    has_exec_out = any(p.name == "exec_out" for p in outputs)
                    if not has_exec_in:
                        inputs.insert(0, PortFact("exec_in", "any", None, True))
                    if not has_exec_out:
                        outputs.insert(0, PortFact("exec_out", "any", None, True))

                self.nodes[node_id] = NodeFact(
                    node_id=node_id,
                    display_name=display_name or node_id,
                    category=category,
                    description=description,
                    use_exec=use_exec,
                    inputs=inputs,
                    outputs=outputs,
                    source_file=str(path.relative_to(self.root)),
                    source_type="builtin",
                )

    # ------------------------------------------------------------------
    # Python class inspection (methods + signals)
    # ------------------------------------------------------------------

    def _inspect_python_class(self, path: Path, class_name: str):
        if not path.exists():
            return
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            return

        fact = ClassFact(name=class_name, source_file=str(path.relative_to(self.root)))
        signals: List[SignalFact] = []

        for cls_node in ast.walk(tree):
            if not isinstance(cls_node, ast.ClassDef) or cls_node.name != class_name:
                continue

            for item in cls_node.body:
                # Class-level attribute assignments
                if isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name) and not t.id.startswith("__"):
                            # Detect pyqtSignal
                            val = item.value
                            if isinstance(val, ast.Call):
                                func_name = getattr(val.func, "id", None) or getattr(val.func, "attr", None)
                                if func_name == "pyqtSignal":
                                    param_types = []
                                    for arg in val.args:
                                        if isinstance(arg, ast.Name):
                                            param_types.append(arg.id)
                                        elif isinstance(arg, ast.Attribute):
                                            param_types.append(f"{getattr(arg.value,'id','')}.{arg.attr}")
                                        elif isinstance(arg, ast.Constant):
                                            param_types.append(repr(arg.value))
                                    signals.append(SignalFact(name=t.id, param_types=param_types))
                                    fact.signals.append(t.id)
                                    continue
                            if not t.id.startswith("_"):
                                fact.class_attrs.append(t.id)

                # Annotated assignments (type: value)
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    name = item.target.id
                    if not name.startswith("__"):
                        fact.class_attrs.append(name)

                # Methods — also scan __init__ for self.xxx instance attributes
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == "__init__":
                        self._collect_instance_attrs(item, fact)
                    if item.name.startswith("__") and item.name != "__init__":
                        continue
                    margs = [
                        a.arg for a in item.args.args
                        if a.arg not in ("self", "cls")
                    ]
                    fact.methods.append(MethodFact(
                        name=item.name,
                        is_async=isinstance(item, ast.AsyncFunctionDef),
                        args=margs,
                    ))

            break  # found the class, stop

        self.classes[class_name] = fact
        self.signals[class_name] = signals

    def _collect_instance_attrs(self, init_node: ast.FunctionDef, fact: "ClassFact"):
        """Scan __init__ body for `self.xxx = ...` and `self.xxx: T = ...` assignments."""
        for node in ast.walk(init_node):
            # self.attr = value
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if (isinstance(t, ast.Attribute)
                            and isinstance(t.value, ast.Name)
                            and t.value.id == "self"
                            and not t.attr.startswith("__")):
                        if t.attr not in fact.instance_attrs:
                            fact.instance_attrs.append(t.attr)
            # self.attr: Type = value
            elif isinstance(node, ast.AnnAssign):
                if (isinstance(node.target, ast.Attribute)
                        and isinstance(node.target.value, ast.Name)
                        and node.target.value.id == "self"
                        and not node.target.attr.startswith("__")):
                    if node.target.attr not in fact.instance_attrs:
                        fact.instance_attrs.append(node.target.attr)

    # ------------------------------------------------------------------
    # Pydantic models (src/core/models.py)
    # ------------------------------------------------------------------

    def _inspect_pydantic_models(self, path: Path):
        if not path.exists():
            return
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            return

        for cls_node in ast.walk(tree):
            if not isinstance(cls_node, ast.ClassDef):
                continue
            base_names = {getattr(b, "id", None) for b in cls_node.bases}
            if "BaseModel" not in base_names:
                continue

            fact = ClassFact(name=cls_node.name, source_file=str(path.relative_to(self.root)))
            for item in cls_node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fact.class_attrs.append(item.target.id)

            self.classes[cls_node.name] = fact

    # ------------------------------------------------------------------
    # Convenience queries
    # ------------------------------------------------------------------

    def node_exists(self, node_id: str) -> bool:
        return node_id in self.nodes

    def get_node_input_names(self, node_id: str) -> List[str]:
        node = self.nodes.get(node_id)
        return [p.name for p in node.inputs] if node else []

    def get_node_output_names(self, node_id: str) -> List[str]:
        node = self.nodes.get(node_id)
        return [p.name for p in node.outputs] if node else []

    def class_has_method(self, class_name: str, method_name: str) -> bool:
        cls = self.classes.get(class_name)
        if not cls:
            return False
        return any(m.name == method_name for m in cls.methods)

    def class_has_signal(self, class_name: str, signal_name: str) -> bool:
        return signal_name in (self.classes.get(class_name) or ClassFact("")).signals

    def get_all_node_ids(self) -> List[str]:
        return sorted(self.nodes.keys())

    def get_all_display_names(self) -> List[str]:
        return sorted(n.display_name for n in self.nodes.values())
