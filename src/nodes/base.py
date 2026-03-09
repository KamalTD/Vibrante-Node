from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

class Port:
    def __init__(self, name: str, data_type: str = "any", widget_type: str = None, options: List[str] = None):
        self.name = name
        self.data_type = data_type
        self.widget_type = widget_type
        self.options = options

class BaseNode(ABC):
    name: str = "BaseNode"
    description: str = ""
    category: str = "General"
    icon_path: Optional[str] = None

    def __init__(self):
        self.inputs: Dict[str, Port] = {}
        self.outputs: Dict[str, Port] = {}
        self.parameters: Dict[str, Any] = {}
        self.parameter_types: Dict[str, Type] = {}
        self._on_log = None # Hook for engine to capture logs

    def log_info(self, msg: str):
        if self._on_log: self._on_log(msg, "info")
        else: print(f"INFO: {msg}")

    def log_success(self, msg: str):
        if self._on_log: self._on_log(msg, "success")
        else: print(f"SUCCESS: {msg}")

    def log_error(self, msg: str):
        if self._on_log: self._on_log(msg, "error")
        else: print(f"ERROR: {msg}")

    def add_input(self, name: str, data_type: str = "any", widget_type: str = None, options: List[str] = None):
        self.inputs[name] = Port(name, data_type, widget_type, options)
        if widget_type:
            # Initialize parameter for the widget
            self.parameters[name] = None

    def add_output(self, name: str, data_type: str = "any"):
        self.outputs[name] = Port(name, data_type)

    def add_parameter(self, name: str, param_type: Type, default: Any = None):
        self.parameter_types[name] = param_type
        self.parameters[name] = default

    def get_parameter(self, name: str) -> Any:
        return self.parameters.get(name)

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution logic for the node.
        :param inputs: Dictionary of input data from connected nodes.
        :return: Dictionary of output data.
        """
        pass

class NodeRegistry:
    _nodes: Dict[str, Type[BaseNode]] = {}

    @classmethod
    def register(cls, node_class: Type[BaseNode]):
        cls._nodes[node_class.name] = node_class

    @classmethod
    def get_node_class(cls, name: str) -> Optional[Type[BaseNode]]:
        return cls._nodes.get(name)

    @classmethod
    def list_nodes(cls) -> List[str]:
        return list(cls._nodes.keys())
