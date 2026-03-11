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
        self._is_stopped = False

    def stop(self):
        self._is_stopped = True

    async def run(self):
        """
        Executes the graph. Follows 'exec' pins if present, otherwise uses topological sort.
        """
        self._is_stopped = False
        
        # 1. PREPARE ALL NODES
        self.node_results = {}
        self.node_instances = {}
        for node_id, node_model in self.graph_manager.nodes.items():
            if self._is_stopped:
                self.execution_finished.emit(False)
                return
            
            node_class = NodeRegistry.get_class(node_model.node_id)
            if not node_class:
                from src.nodes.base import NodeRegistry as BaseRegistry
                node_class = BaseRegistry.get_node_class(node_model.node_id)
                
            if not node_class:
                err = f"Unknown node type: {node_model.node_id}"
                self.node_error.emit(node_id, err)
                self.execution_finished.emit(False)
                return
            
            instance = node_class()
            instance.name = node_model.node_id
            for p_name, p_val in node_model.parameters.items():
                if p_name in instance.parameters:
                    instance.parameters[p_name] = p_val
            
            instance.clear_outputs()
            self.node_instances[node_id] = instance
            self.node_results[node_id] = {}

            # SETUP HOOKS
            instance._check_stopped = lambda: self._is_stopped
            def create_logger(nid):
                return lambda msg, lvl: self.node_log.emit(nid, msg, lvl)
            instance._on_log = create_logger(node_id)

            def create_output_handler(nid):
                def handler(name, value):
                    self.node_results[nid][name] = value
                    self.node_output.emit(nid, {name: value})
                return handler
            instance._on_output = create_output_handler(node_id)

        # 2. IDENTIFY EXECUTION STRATEGY
        # Find 'entry' nodes: nodes with 'exec' output but no 'exec' input, OR no 'exec' pins at all
        exec_conns = [c for c in self.graph_manager.connections if c.is_exec]
        
        if exec_conns:
            # FLOW-BASED EXECUTION
            # Find nodes that have exec_out connected but no exec_in connected
            has_exec_in = {c.to_node for c in exec_conns}
            has_exec_out = {c.from_node for c in exec_conns}
            entry_nodes = list(has_exec_out - has_exec_in)
            
            if not entry_nodes:
                # If it's a closed loop or single node with exec, pick the first one with an exec pin
                entry_nodes = [list(has_exec_out)[0]] if has_exec_out else []

            for start_node in entry_nodes:
                await self._execute_flow(start_node)
        else:
            # CLASSIC DATA-FLOW (TOPOLOGICAL)
            try:
                order = self.graph_manager.get_topological_sort()
                for layer in order:
                    if self._is_stopped: break
                    tasks = [self._run_single_node(nid) for nid in layer]
                    await asyncio.gather(*tasks)
            except Exception as e:
                print(f"Classic execution failed: {e}")

        self.execution_finished.emit(not self._is_stopped)

    async def _execute_flow(self, node_id: UUID):
        """Recursively follows the execution chain."""
        if self._is_stopped: return

        # 1. Run the current node
        success = await self._run_single_node(node_id)
        if not success or self._is_stopped: return

        # 2. Find next node(s) via 'exec' pins
        # We handle standard 'out' pin first
        next_conns = [c for c in self.graph_manager.connections if c.from_node == node_id and c.is_exec]
        
        # Sort by port name if multiple (usually just one 'out')
        for conn in sorted(next_conns, key=lambda c: c.from_port):
            await self._execute_flow(conn.to_node)

    async def _run_single_node(self, node_id: UUID) -> bool:
        if self._is_stopped: return False
        self.node_started.emit(node_id)
        instance = self.node_instances[node_id]
        
        # Pull data inputs
        inputs = instance.parameters.copy()
        for conn in self.graph_manager.connections:
            if conn.to_node == node_id and not conn.is_exec:
                from_results = self.node_results.get(conn.from_node, {})
                if conn.from_port in from_results:
                    inputs[conn.to_port] = from_results.get(conn.from_port)
        
        success, result, error = await SafeRuntime.run_node_safe(instance.execute, inputs)
        
        if success:
            self.node_results[node_id].update(result)
            self.node_output.emit(node_id, result)
            self.node_finished.emit(node_id, "success")
            return True
        else:
            self.node_error.emit(node_id, error)
            self.node_finished.emit(node_id, "failed")
            return False
