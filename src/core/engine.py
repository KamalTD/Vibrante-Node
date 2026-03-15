import asyncio
from typing import Dict, Any, List, Set, Optional
from uuid import UUID
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from src.core.graph import GraphManager
from src.core.registry import NodeRegistry
from src.utils.runtime import SafeRuntime
from src.nodes.base import BaseNode

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
        self._executed_nodes: Set[UUID] = set() # Nodes that finished successfully
        self._currently_executing: Set[UUID] = set() # Nodes currently in the stack
        self._is_stopped = False
        self._active_tasks: Set[asyncio.Task] = set()
        self._finished_event = asyncio.Event()
        
        # Pre-calculated lookup maps
        self._incoming_data_conns: Dict[UUID, List[Any]] = {} 
        self._driven_by_flow: Set[UUID] = set()

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
        from src.nodes.base import BaseNode
        BaseNode.memory.clear()
        
        self._executed_nodes.clear()
        self._currently_executing.clear()
        self._is_stopped = False
        self._active_tasks.clear()
        self._finished_event.clear()
        
        # 1. PRE-CALCULATE LOOKUP MAPS
        self._incoming_data_conns = {}
        self._driven_by_flow = set()
        for conn in self.graph_manager.connections:
            if conn.is_exec:
                self._driven_by_flow.add(conn.to_node)
            else:
                self._incoming_data_conns.setdefault(conn.to_node, []).append(conn)

        # 2. PREPARE ALL NODES
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
            
            # 1. RESTORE DYNAMIC PORTS
            instance.restore_from_parameters(node_model.parameters)
            
            # 2. SYNC PARAMETERS
            # Ignore saved parameter values for ports that have incoming data connections,
            # so they start with their default state for each run.
            incoming_ports = {c.to_port for c in self._incoming_data_conns.get(node_id, [])}
            
            for p_name, p_val in node_model.parameters.items():
                if p_name in instance.parameters:
                    if p_name in incoming_ports:
                        # Reset to port default if it will be driven by a connection
                        port_obj = instance.inputs.get(p_name)
                        default = getattr(port_obj, 'default', None) if port_obj else None
                        instance.parameters[p_name] = default
                    else:
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
                    # exec_conns is defined below, but Python closures will find it
                    for conn in self.graph_manager.connections:
                        if conn.from_node == nid and conn.from_port == name and not conn.is_exec:
                            target_instance = self.node_instances.get(conn.to_node)
                            if target_instance:
                                # Sync both parameter and result cache
                                target_instance.parameters[conn.to_port] = value
                                self.node_results[conn.to_node][conn.to_port] = value
                                
                                # ALWAYS trigger on_parameter_changed for data connections.
                                # This allows nodes (like For Each) to react to data changes
                                # even if they are primarily driven by flow pins.
                                await target_instance.on_parameter_changed(conn.to_port, value)

                    # 2. FLOW-BASED ROUTING
                    if bool(value) is True: # Handle both True and truthy values for execution pins
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
        
        try:
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
                    
                    # Logic:
                    # 1. If it has no exec_in pin, it's a potential starter (data node or flow starter)
                    # 2. If it HAS an exec_in pin but NO connection to it, it's a flow starter
                    if not has_exec_in_pin:
                        entry_nodes.append(node_id)
                    elif node_id not in has_exec_in_conn:
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
                # CLASSIC DATA-FLOW (Using Topological Sorting)
                # Execute the graph layer by layer as mandated by GEMINI.md
                layers = self.graph_manager.get_topological_sort()
                
                for layer in layers:
                    if self._is_stopped: break
                    
                    # Track each node execution as a task so it can be cancelled
                    tasks = [self._track_task(self._run_single_node(nid)) for nid in layer]
                    # Filter out None if _track_task returned None due to stop
                    tasks = [t for t in tasks if t is not None]
                    
                    if tasks:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Check for errors or cancellation in layer
                        for res in results:
                            if isinstance(res, asyncio.CancelledError):
                                self._is_stopped = True
                                break
                            if isinstance(res, Exception):
                                print(f"Error in layer execution: {res}")

        finally:
            self.execution_finished.emit(not self._is_stopped)

    async def _execute_flow(self, node_id: UUID):
        """Executes a single node. Flow continuation is handled EXCLUSIVELY by set_output calls."""
        if self._is_stopped: return
        
        await self._run_single_node_impl(node_id, is_data_pull=False)

    async def _run_single_node(self, node_id: UUID) -> bool:
        # This method is now redundant for internal calls but kept for external/reactive entry points
        return await self._run_single_node_impl(node_id, is_data_pull=False)

    async def _run_single_node_impl(self, node_id: UUID, is_data_pull: bool = False) -> bool:
        """Internal implementation of node execution without locking, to allow recursion for data pulling."""
        if self._is_stopped: return False
        
        # Guard 1: Data Pulling Guard
        # If we are just pulling data dependencies, don't run the same node twice.
        # Flow triggers (is_data_pull=False) are allowed to re-run nodes (e.g. in loops).
        if is_data_pull and node_id in self._executed_nodes:
            return True
            
        # Guard 2: Re-entrancy Guard (Recursion Guard)
        # Prevents infinite stack depth if there's a cycle.
        if node_id in self._currently_executing:
            return True
            
        self._currently_executing.add(node_id)
        
        try:
            instance = self.node_instances[node_id]

            # 1. PULL UPSTREAM DATA NODES (In Port Order)
            incoming = self._incoming_data_conns.get(node_id, [])
            
            for port_name in instance.inputs:
                for conn in incoming:
                    if conn.to_port == port_name:
                        from_id = conn.from_node
                        from_inst = self.node_instances.get(from_id)
                        if from_inst:
                            # Check if source node is pullable (either no exec_in, or it's not driven by flow)
                            is_driven_by_flow = from_id in self._driven_by_flow
                            if not is_driven_by_flow:
                                await self._run_single_node_impl(from_id, is_data_pull=True)

            self.node_started.emit(node_id)
            
            # Reset all exec outputs
            for name, port in instance.outputs.items():
                if port.data_type == 'exec':
                    instance.parameters[name] = None
            
            # Sync all inputs
            for conn in incoming:
                from_results = self.node_results.get(conn.from_node, {})
                if conn.from_port in from_results:
                    val = from_results.get(conn.from_port)
                    instance.parameters[conn.to_port] = val
                    await instance.on_parameter_changed(conn.to_port, val)
            
            inputs = instance.parameters.copy()
            success, result, error = await SafeRuntime.run_node_safe(instance.execute, inputs)
            
            if success:
                self._executed_nodes.add(node_id)
                self.node_results[node_id].update(result)
                self.node_output.emit(node_id, result)
                self.node_finished.emit(node_id, "success")
                return True
            else:
                self.node_error.emit(node_id, error)
                self.node_finished.emit(node_id, "failed")
                return False
        finally:
            self._currently_executing.discard(node_id)
