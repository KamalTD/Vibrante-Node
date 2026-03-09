import os
import json
from typing import Dict, List, Type, Optional
from pydantic import ValidationError
from src.core.models import NodeDefinitionJSON, PortModel
from src.nodes.base import BaseNode

class NodeRegistry:
    _definitions: Dict[str, NodeDefinitionJSON] = {}
    _classes: Dict[str, Type[BaseNode]] = {}

    @classmethod
    def load_all(cls, directory: str):
        """
        Scans directory for .json files and registers them.
        """
        # First register builtins
        cls.register_builtins()

        if not os.path.exists(directory):
            os.makedirs(directory)
            return

        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                path = os.path.join(directory, filename)
                cls.load_node(path)

    @classmethod
    def register_builtins(cls):
        from src.nodes.builtins.nodes import FileLoaderNode, DataProcessorNode, ConsoleSinkNode
        cls._register_builtin_class(FileLoaderNode)
        cls._register_builtin_class(DataProcessorNode)
        cls._register_builtin_class(ConsoleSinkNode)

    @classmethod
    def _register_builtin_class(cls, node_class: Type[BaseNode]):
        # Create a definition for builtins
        node_class.node_id = node_class.name # Set node_id
        instance = node_class()
        definition = NodeDefinitionJSON(
            node_id=node_class.name,
            name=node_class.name,
            description=node_class.description,
            category=node_class.category,
            icon_path=node_class.icon_path,
            inputs=[PortModel(name=p.name, type=p.data_type, widget_type=p.widget_type, options=p.options) for p in instance.inputs.values()],
            outputs=[PortModel(name=p.name, type=p.data_type) for p in instance.outputs.values()],
            python_code="" # Not used for builtins
        )

        cls._definitions[definition.node_id] = definition
        cls._classes[definition.node_id] = node_class

    @classmethod
    def load_node(cls, file_path: str) -> bool:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            definition = NodeDefinitionJSON.model_validate(data)
            return cls.register_definition(definition)
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            print(f"Error loading node from {file_path}: {e}")
            return False

    @classmethod
    def register_definition(cls, definition: NodeDefinitionJSON) -> bool:
        cls._definitions[definition.node_id] = definition
        if not definition.python_code:
            return True # Builtin already registered
            
        try:
            namespace = {}
            exec(definition.python_code, namespace)
            if 'register_node' in namespace:
                node_class = namespace['register_node']()
                if issubclass(node_class, BaseNode):
                    node_class.name = definition.name
                    node_class.node_id = definition.node_id
                    node_class.category = definition.category
                    node_class.icon_path = definition.icon_path # Set icon_path
                    cls._classes[definition.node_id] = node_class
                    return True
            return False
        except Exception as e:
            print(f"Error generating class for {definition.node_id}: {e}")
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
