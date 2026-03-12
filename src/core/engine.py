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
        self._active_tasks: Set[asyncio.Task] = set()
        self._finished_event = asyncio.Event()

    def stop(self):
        self._is_stopped = True
        for task in self._active_tasks:
            task.cancel()
        self._finished_event.set()

    def _track_task(self, coro):
        """Helper to create and track a task in the current event loop."""
        if self._is_stopped: return None
        task = asyncio.create_task(coro)
        self._active_tasks.add(task)
        def on_done(t):
            self._active_tasks.discard(t)
            if not self._active_tasks:
                self._finished_event.set()
        task.add_done_callback(on_done)
        return task

    async def run(self):
        """
        Executes the graph. Standardizes on flow-based execution via output triggers.
        """
        self._is_stopped = False
        self._active_tasks.clear()
        self._finished_event.clear()
        
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
                async def handler(name, value):
                    if self._is_stopped: return
                    
                    # Store result immediately
                    self.node_results[nid][name] = value
                    self.node_output.emit(nid, {name: value})
                    
                    # 1. REACTIVE DATA PROPAGATION
                    is_flow_execution = len(exec_conns) > 0
                    for conn in self.graph_manager.connections:
                        if conn.from_node == nid and conn.from_port == name and not conn.is_exec:
                            target_instance = self.node_instances.get(conn.to_node)
                            if target_instance:
                                target_instance.parameters[conn.to_port] = value
                                
                                # Check if target node has an exec_in pin
                                target_has_exec_in = any(p.data_type == 'exec' for p in target_instance.inputs.values())
                                
                                # Trigger reactive updates if:
                                # - We are in classic data-flow mode
                                # - OR target node is a pure data node (no exec_in)
                                if not is_flow_execution or not target_has_exec_in:
                                    await target_instance.on_parameter_changed(conn.to_port, value)

                    # 2. FLOW-BASED ROUTING
                    if value is True: # Strict check for execution pins
                        node_inst = self.node_instances.get(nid)
                        port_def = node_inst.outputs.get(name) if node_inst else None
                        if port_def and getattr(port_def, 'data_type', 'any') == 'exec':
                            for conn in self.graph_manager.connections:
                                if conn.from_node == nid and conn.from_port == name and conn.is_exec:
                                    await self._execute_flow(conn.to_node)
                return handler
            instance._on_output = create_output_handler(node_id)

        # 2. IDENTIFY ENTRY NODES
        exec_conns = [c for c in self.graph_manager.connections if c.is_exec]
        
        if exec_conns:
            # In flow mode, we start:
            # 1. Any node that has an exec_out but no connected exec_in
            # 2. Any pure data node (no exec pins at all) that has connections
            
            connected_nodes = {c.from_node for c in self.graph_manager.connections} | \
                              {c.to_node for c in self.graph_manager.connections}
            has_exec_in_conn = {c.to_node for c in exec_conns}
            
            entry_nodes = []
            for node_id, instance in self.node_instances.items():
                if node_id not in connected_nodes: continue
                
                has_exec_in_pin = any(p.data_type == 'exec' for p in instance.inputs.values())
                has_exec_out_pin = any(p.data_type == 'exec' for p in instance.outputs.values())
                
                if not has_exec_in_pin:
                    # Pure data provider or flow starter
                    entry_nodes.append(node_id)
                elif node_id not in has_exec_in_conn:
                    # Flow node that isn't triggered by anything
                    entry_nodes.append(node_id)

            if entry_nodes:
                for start_node in entry_nodes:
                    self._track_task(self._execute_flow(start_node))
                
                # WAIT FOR ALL FLOWS TO FINISH
                while self._active_tasks and not self._is_stopped:
                    await self._finished_event.wait()
                    self._finished_event.clear()
                    await asyncio.sleep(0.05)
        else:
            # CLASSIC DATA-FLOW
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
        """Executes a single node. Flow continuation is handled EXCLUSIVELY by set_output calls."""
        if self._is_stopped: return
        
        await self._run_single_node_impl(node_id)

    async def _run_single_node(self, node_id: UUID) -> bool:
        # This method is now redundant for internal calls but kept for external/reactive entry points
        return await self._run_single_node_impl(node_id)

    async def _run_single_node_impl(self, node_id: UUID) -> bool:
        """Internal implementation of node execution without locking, to allow recursion for data pulling."""
        if self._is_stopped: return False
        
        instance = self.node_instances[node_id]

        # 1. PULL UPSTREAM DATA NODES
        for conn in self.graph_manager.connections:
            if conn.to_node == node_id and not conn.is_exec:
                from_id = conn.from_node
                from_inst = self.node_instances.get(from_id)
                if from_inst:
                    has_exec_in = any(p.data_type == 'exec' for p in from_inst.inputs.values())
                    if not has_exec_in:
                        await self._run_single_node_impl(from_id)

        self.node_started.emit(node_id)
        
        # Reset all exec outputs to allow re-triggering in subsequent cycles
        for name, port in instance.outputs.items():
            if port.data_type == 'exec':
                instance.parameters[name] = None
        
        # Sync all inputs from current connected output states
        for conn in self.graph_manager.connections:
            if conn.to_node == node_id and not conn.is_exec:
                from_results = self.node_results.get(conn.from_node, {})
                if conn.from_port in from_results:
                    val = from_results.get(conn.from_port)
                    instance.parameters[conn.to_port] = val
                    await instance.on_parameter_changed(conn.to_port, val)
        
        # Pull final inputs for execute call
        inputs = instance.parameters.copy()
        
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
