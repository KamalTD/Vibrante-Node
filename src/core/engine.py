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
            print(f"ERROR: Graph execution failed during topological sort: {e}")
            self.execution_finished.emit(False)
            return

        self.node_results = {}
        self.node_instances = {}

        # 1. PREPARE ALL NODES
        for node_id, node_model in self.graph_manager.nodes.items():
            node_class = NodeRegistry.get_class(node_model.node_id)
            if not node_class:
                err = f"Unknown node type: {node_model.node_id}"
                self.node_error.emit(node_id, err)
                self.execution_finished.emit(False)
                return
            
            instance = node_class()
            instance.name = node_model.node_id
            
            # Set parameters from model
            for p_name, p_val in node_model.parameters.items():
                if p_name in instance.parameters:
                    instance.parameters[p_name] = p_val
            
            # ENSURE FRESH START: Clear all transient data from previous runs
            instance.clear_outputs()
            instance.clear_input_parameters()
            
            self.node_instances[node_id] = instance
            self.node_results[node_id] = {}

            # SETUP HOOKS (Logging and Real-time data propagation)
            def create_logger(nid):
                return lambda msg, lvl: self.node_log.emit(nid, msg, lvl)
            instance._on_log = create_logger(node_id)

            def create_output_handler(nid):
                def handler(name, value):
                    partial_results = {name: value}
                    self.node_results[nid].update(partial_results)
                    self.node_output.emit(nid, partial_results)
                    
                    # PROPAGATE TO CONNECTED NODES IN REAL-TIME
                    for conn in self.graph_manager.connections:
                        if conn.from_node == nid and conn.from_port == name:
                            t_id = conn.to_node
                            if t_id in self.node_instances:
                                t_inst = self.node_instances[t_id]
                                if conn.to_port in t_inst.parameters:
                                    t_inst.parameters[conn.to_port] = value
                                    t_inst.on_parameter_changed(conn.to_port, value)
                return handler
            
            instance._on_output = create_output_handler(node_id)

        # 2. INITIAL DATA SYNC PASS
        # Ensures that nodes start with values from their connected peers
        for conn in self.graph_manager.connections:
            if conn.from_node in self.node_instances and conn.to_node in self.node_instances:
                f_inst = self.node_instances[conn.from_node]
                t_inst = self.node_instances[conn.to_node]
                val = f_inst.get_parameter(conn.from_port)
                if val is not None:
                    if conn.to_port in t_inst.parameters:
                        t_inst.parameters[conn.to_port] = val
                        t_inst.on_parameter_changed(conn.to_port, val)

        # 3. EXECUTION LOOP
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
        
        # Merge latest parameters with results from upstream neighbors
        inputs = instance.parameters.copy()
        for conn in self.graph_manager.connections:
            if conn.to_node == node_id:
                from_results = self.node_results.get(conn.from_node, {})
                if conn.from_port in from_results:
                    inputs[conn.to_port] = from_results.get(conn.from_port)
        
        success, result, error = await SafeRuntime.run_node_safe(instance.execute, inputs)
        
        if success:
            # Final output emission
            self.node_results[node_id].update(result)
            self.node_output.emit(node_id, result)
            self.node_finished.emit(node_id, "success")
            return True
        else:
            self.node_error.emit(node_id, error)
            self.node_finished.emit(node_id, "failed")
            return False
