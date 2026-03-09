import asyncio
from typing import Dict, Any, List, Set, Optional
from uuid import UUID
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from src.core.graph import GraphManager
from src.core.registry import NodeRegistry
from src.utils.runtime import SafeRuntime

class NetworkExecutor(QObject):
    # Signals for UI feedback
    node_started = pyqtSignal(UUID)
    node_finished = pyqtSignal(UUID, str) # node_id, status ('success' or 'failed')
    node_error = pyqtSignal(UUID, str)    # node_id, error_message
    node_output = pyqtSignal(UUID, dict)  # node_id, output_data
    node_log = pyqtSignal(UUID, str, str) # node_id, message, level
    execution_finished = pyqtSignal(bool) # success

    def __init__(self, graph_manager: GraphManager):
        super().__init__()
        self.graph_manager = graph_manager
        self.node_instances: Dict[UUID, Any] = {}
        self.node_results: Dict[UUID, Dict[str, Any]] = {}

    async def run(self):
        """
        Executes the graph in topological order with data flow.
        """
        try:
            order = self.graph_manager.get_topological_sort()
        except Exception as e:
            self.execution_finished.emit(False)
            return

        self.node_results = {}
        self.node_instances = {}

        # Instantiate nodes
        for node_id, node_model in self.graph_manager.nodes.items():
            node_class = NodeRegistry.get_class(node_model.node_id)
            if not node_class:
                self.node_error.emit(node_id, f"Unknown node type: {node_model.node_id}")
                self.execution_finished.emit(False)
                return
            
            instance = node_class()
            # Set parameters
            for p_name, p_val in node_model.parameters.items():
                if p_name in instance.parameters:
                    instance.parameters[p_name] = p_val
            
            self.node_instances[node_id] = instance

        # Execute layer by layer
        for layer in order:
            tasks = []
            for node_id in layer:
                tasks.append(self._run_single_node(node_id))
            
            results = await asyncio.gather(*tasks)
            if not all(results):
                self.execution_finished.emit(False)
                return

        self.execution_finished.emit(True)

    async def _run_single_node(self, node_id: UUID) -> bool:
        self.node_started.emit(node_id)
        
        instance = self.node_instances[node_id]
        
        # Setup logging hook
        def node_logger(msg, level):
            self.node_log.emit(node_id, msg, level)
        instance._on_log = node_logger

        # Collect inputs: start with parameters (widget values)
        inputs = instance.parameters.copy()
        
        # Overwrite with values from connections
        for conn in self.graph_manager.connections:
            if conn.to_node == node_id:
                from_node_results = self.node_results.get(conn.from_node, {})
                if conn.from_port in from_node_results:
                    inputs[conn.to_port] = from_node_results.get(conn.from_port)
        
        print(f"DEBUG EXECUTE {instance.name}: {inputs}")
        success, result, error = await SafeRuntime.run_node_safe(instance.execute, inputs)
        
        if success:
            self.node_results[node_id] = result
            self.node_output.emit(node_id, result)
            self.node_finished.emit(node_id, "success")
            return True
        else:
            self.node_error.emit(node_id, error)
            self.node_finished.emit(node_id, "failed")
            return False
