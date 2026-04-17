import os
import json
from typing import Dict, List, Type, Optional
from pydantic import ValidationError
from src.core.models import NodeDefinitionJSON, PortModel
from src.nodes.base import BaseNode

class NodeRegistry:
    _definitions: Dict[str, NodeDefinitionJSON] = {}
    _classes: Dict[str, Type[BaseNode]] = {}
    last_error: Optional[str] = None

    @classmethod
    def _prepare_definition(cls, definition: NodeDefinitionJSON) -> NodeDefinitionJSON:
        """
        Normalize selected node families before class generation.
        Prism nodes can auto-resolve the active PrismCore from shared memory,
        so users don't have to wire the `core` output through every node.
        """
        if not definition.python_code:
            return definition

        if definition.node_id.startswith("prism_") and definition.node_id != "prism_core_init":
            code = definition.python_code
            if "resolve_prism_core" not in code:
                code = "from src.utils.prism_core import resolve_prism_core\n" + code
            code = code.replace("core = inputs.get('core')", "core = resolve_prism_core(inputs)")
            code = code.replace('core = inputs.get("core")', "core = resolve_prism_core(inputs)")
            definition.python_code = code

        return definition

    @classmethod
    def load_all(cls, directory: str):
        """
        Scans directory and subdirectories for .json files and registers them.
        """
        # First register builtins
        cls.register_builtins()

        if not os.path.exists(directory):
            os.makedirs(directory)
            return

        cls._load_directory(directory)

    @classmethod
    def load_all_with_extras(cls, default_directory: str):
        """
        Load nodes from the default directory plus any directories
        specified in the v_nodes_dir environment variable.
        """
        cls.load_all(default_directory)

        extra_dirs = os.environ.get('v_nodes_dir', '')
        if extra_dirs:
            for extra_dir in extra_dirs.split(os.pathsep):
                extra_dir = extra_dir.strip()
                if extra_dir and os.path.isdir(extra_dir):
                    print(f"Loading extra nodes from: {extra_dir}")
                    cls._load_directory(extra_dir)

    @classmethod
    def _load_directory(cls, directory: str):
        """Walk a single directory for .json node files and load them."""
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(".json"):
                    path = os.path.join(root, filename)
                    cls.load_node(path)

    @classmethod
    def register_builtins(cls):
        from src.nodes.builtins.nodes import (
            FileLoaderNode, DataProcessorNode, ConsoleSinkNode, 
            SequenceNode, SetVariableNode, GetVariableNode, 
            TwoWaySwitchNode, ForEachNode, ListAppendNode, WhileLoopNode
        )
        cls._register_builtin_class(FileLoaderNode)
        cls._register_builtin_class(DataProcessorNode)
        cls._register_builtin_class(ConsoleSinkNode)
        cls._register_builtin_class(SequenceNode)
        cls._register_builtin_class(SetVariableNode)
        cls._register_builtin_class(GetVariableNode)
        cls._register_builtin_class(TwoWaySwitchNode)
        cls._register_builtin_class(ForEachNode)
        cls._register_builtin_class(WhileLoopNode)
        cls._register_builtin_class(ListAppendNode)

    @classmethod
    def _register_builtin_class(cls, node_class: Type[BaseNode]):
        # Create a definition for builtins
        node_class.node_id = node_class.name # Set node_id
        instance = node_class()
        
        inputs = []
        for p in instance.inputs.values():
            default = p.default
            if default is None:
                if p.data_type == "string": default = ""
                elif p.data_type == "list": default = []
                elif p.data_type == "bool": default = False
                elif p.data_type in ["int", "float", "number"]: default = 0
            inputs.append(PortModel(name=p.name, type=p.data_type, widget_type=p.widget_type, options=p.options, default=default))

        definition = NodeDefinitionJSON(
            node_id=node_class.name,
            name=node_class.name,
            description=node_class.description,
            category=node_class.category,
            icon_path=node_class.icon_path,
            inputs=inputs,
            outputs=[PortModel(name=p.name, type=p.data_type) for p in instance.outputs.values()],
            python_code="" # Not used for builtins
        )

        # Normalize and store
        cls.register_definition(definition)
        cls._classes[definition.node_id] = node_class

    @classmethod
    def load_node(cls, file_path: str) -> bool:
        cls.last_error = None
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            definition = NodeDefinitionJSON.model_validate(data)
            return cls.register_definition(definition)
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            cls.last_error = f"Error loading node from {file_path}: {e}"
            print(cls.last_error)
            return False

    @classmethod
    def register_definition(cls, definition: NodeDefinitionJSON) -> bool:
        definition = cls._prepare_definition(definition)

        # 1. Normalize pins: Ensure at least 'exec_in' and 'exec_out' exist if use_exec is True
        # But allow other 'exec' type pins as well.
        if definition.use_exec:
            # Inputs
            has_exec_in = any(p.name == "exec_in" for p in definition.inputs)
            if not has_exec_in:
                definition.inputs.insert(0, PortModel(name="exec_in", type="exec"))
                
            # Outputs
            has_exec_out = any(p.name == "exec_out" for p in definition.outputs)
            if not has_exec_out:
                definition.outputs.insert(0, PortModel(name="exec_out", type="exec"))

        cls._definitions[definition.node_id] = definition
        if not definition.python_code:
            return True # Builtin already registered
            
        try:
            namespace = {}
            exec(definition.python_code, namespace)
            
            node_class = None
            if 'register_node' in namespace:
                node_class = namespace['register_node']()
            elif 'execute' in namespace:
                # Simplified format: just execute function
                # Create a closure to capture namespace
                local_namespace = namespace.copy()
                
                class DynamicNode(BaseNode):
                    def __init__(self):
                        super().__init__(use_exec=definition.use_exec)
                        # Set metadata on instance
                        self.name = definition.name
                        self.node_id = definition.node_id
                        self.category = definition.category
                        self.description = definition.description
                        self.icon_path = definition.icon_path
                        
                        for inp in definition.inputs:
                            # Skip if already added by super().__init__() via auto-normalize
                            if inp.name in self.inputs: continue
                            self.add_input(inp.name, inp.type, inp.widget_type, inp.options, inp.default)
                        for out in definition.outputs:
                            # Skip if already added by super().__init__()
                            if out.name in self.outputs: continue
                            self.add_output(out.name, out.type)
                            
                    async def execute(self, inputs):
                        return await local_namespace['execute'](self, inputs)
                    
                    async def on_parameter_changed(self, name, value):
                        if 'on_parameter_changed' in local_namespace:
                            await local_namespace['on_parameter_changed'](self, name, value)
                            
                    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
                        if 'on_plug_sync' in local_namespace:
                            local_namespace['on_plug_sync'](self, port_name, is_input, other_node, other_port_name)

                # Move helper functions to class level
                for key, func in local_namespace.items():
                    if key.startswith('_') and callable(func):
                        setattr(DynamicNode, key, func)
                
                # Assign a name to the dynamic class for better debugging
                class_name = "".join(x for x in definition.name.title() if not x.isspace())
                if not class_name.endswith("Node"): class_name += "Node"
                DynamicNode.__name__ = class_name
                node_class = DynamicNode
            
            if node_class and issubclass(node_class, BaseNode):
                # Set class attributes
                node_class.name = definition.name
                node_class.node_id = definition.node_id
                node_class.category = definition.category
                node_class.description = definition.description
                node_class.icon_path = definition.icon_path
                
                cls._classes[definition.node_id] = node_class
                return True
            
            cls.last_error = f"Definition '{definition.node_id}' does not have 'register_node' or 'execute' function."
            return False
        except Exception as e:
            cls.last_error = f"Error generating class for {definition.node_id}: {e}"
            print(cls.last_error)
            return False

    @classmethod
    def get_definition(cls, node_id: str) -> Optional[NodeDefinitionJSON]:
        return cls._definitions.get(node_id)

    @classmethod
    def get_class(cls, node_id: str) -> Optional[Type[BaseNode]]:
        return cls._classes.get(node_id)

    @classmethod
    def list_node_ids(cls) -> List[str]:
        return list(cls._definitions.keys())

    @classmethod
    def delete_node(cls, node_id: str, directory: str):
        if node_id in cls._definitions:
            del cls._definitions[node_id]
        if node_id in cls._classes:
            del cls._classes[node_id]
        
        file_path = os.path.join(directory, f"{node_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
