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

    def __init__(self, use_exec: bool = True):
        self.inputs: Dict[str, Port] = {}
        self.outputs: Dict[str, Port] = {}
        self.parameters: Dict[str, Any] = {}
        self.parameter_types: Dict[str, Type] = {}
        self._on_log = None # Hook for engine to capture logs
        self._on_output = None # Hook for engine to capture intermediate outputs
        self._check_stopped = None # Hook for engine to check cancellation
        
        if use_exec:
            # DEFAULT pins if requested
            self.add_exec_input("exec_in")
            self.add_exec_output("exec_out")

    def is_stopped(self) -> bool:
        """Checks if the execution has been requested to stop."""
        if self._check_stopped:
            return self._check_stopped()
        return False

    async def set_output(self, name: str, value: Any):
        """Allows a node to push output data during execution (streaming)."""
        if name in self.outputs:
            self.parameters[name] = value
            if self._on_output:
                await self._on_output(name, value)

    def clear_outputs(self):
        """Resets all output parameters to None before a new execution."""
        for name in self.outputs:
            self.parameters[name] = None

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
        # Always initialize parameter key to ensure it's accessible via .parameters.get()
        if name not in self.parameters:
            self.parameters[name] = None

    def add_exec_input(self, name: str = "exec_in"):
        self.add_input(name, data_type="exec")

    def add_output(self, name: str, data_type: str = "any"):
        self.outputs[name] = Port(name, data_type)
        # ALSO initialize output name in parameters so other nodes can query its 'last known' or 'default' state
        if name not in self.parameters:
            self.parameters[name] = None

    def add_exec_output(self, name: str = "exec_out"):
        self.add_output(name, data_type="exec")

    def add_parameter(self, name: str, param_type: Type, default: Any = None):
        self.parameter_types[name] = param_type
        self.parameters[name] = default

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Safely retrieve a parameter value."""
        return self.parameters.get(name, default)

    def __getitem__(self, key: str) -> Any:
        """Shortcut for get_parameter: node['param_name']"""
        return self.get_parameter(key)

    async def on_plug(self, port_name: str, is_input: bool, other_node: 'BaseNode', other_port_name: str):
        """Called when a connection is established (Async)."""
        pass

    async def on_unplug(self, port_name: str, is_input: bool):
        """Called when a connection is removed (Async)."""
        pass

    def on_plug_sync(self, port_name: str, is_input: bool, other_node: 'BaseNode', other_port_name: str):
        """Called when a connection is established (Sync)."""
        pass

    def on_unplug_sync(self, port_name: str, is_input: bool):
        """Called when a connection is removed (Sync)."""
        pass

    async def on_parameter_changed(self, name: str, value: Any):
        """Called when a parameter/widget value is changed."""
        pass

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
