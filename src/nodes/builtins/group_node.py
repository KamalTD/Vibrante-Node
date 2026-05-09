from src.nodes.base import BaseNode


class GroupInNode(BaseNode):
    """Input boundary marker inside a subgraph.

    The GroupNode sets parameters['value'] to the external input before
    running the sub-executor.  execute() simply returns that value so
    downstream nodes inside the subgraph can read it via data connections.
    """
    name = "group_in"
    description = "Subgraph input boundary — provides an external value to the internal graph"
    category = "Group"

    def __init__(self):
        super().__init__(use_exec=False)
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("port_name", "string", widget_type="text", default="")
        self.add_output("value", "any")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        return {"value": self.parameters.get("value")}


class GroupOutNode(BaseNode):
    """Output boundary marker inside a subgraph.

    After the sub-executor finishes, GroupNode reads node_results[id]['value']
    and maps it to the corresponding group output port.
    """
    name = "group_out"
    description = "Subgraph output boundary — returns a value to the parent graph"
    category = "Group"

    def __init__(self):
        super().__init__(use_exec=False)
        # [AUTO-GENERATED-PORTS-START]
        self.add_input("port_name", "string", widget_type="text", default="")
        self.add_input("value", "any")
        self.add_output("value", "any")
        # [AUTO-GENERATED-PORTS-END]

    async def execute(self, inputs):
        return {"value": inputs.get("value")}


class GroupNode(BaseNode):
    """Collapsed subgraph node.

    Stores a complete WorkflowModel in parameters['__workflow__'] and
    executes it with a headless NetworkExecutor when triggered.
    Dynamic input/output ports are recreated from parameters['__port_defs__']
    via restore_from_parameters() which the engine calls before each run.
    """
    name = "group_node"
    description = "Collapsed group of nodes — double-click to inspect"
    category = "Group"

    def __init__(self):
        super().__init__(use_exec=True)
        # Dynamic ports are added at group-creation time and restored at load time.
        # These three keys are always present so serialization has stable keys.
        self.parameters.setdefault("__workflow__", {})
        self.parameters.setdefault("__port_defs__", [])
        self.parameters.setdefault("__name__", "Group")

    # ------------------------------------------------------------------
    # Port restoration (called by engine before each execution)
    # ------------------------------------------------------------------

    def restore_from_parameters(self, parameters):
        port_defs = parameters.get("__port_defs__", [])
        for pd in port_defs:
            name = pd.get("name", "")
            data_type = pd.get("type", "any")
            if not name:
                continue
            if pd.get("is_input", True):
                if name not in self.inputs:
                    self.add_input(name, data_type)
            else:
                if name not in self.outputs:
                    self.add_output(name, data_type)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, inputs):
        from src.core.models import WorkflowModel
        from src.core.graph import GraphManager
        from src.core.engine import NetworkExecutor
        from src.nodes.base import BaseNode as _BaseNode

        workflow_json = self.parameters.get("__workflow__", {})
        if not workflow_json:
            self.log_error("Group node has no internal workflow.")
            await self.set_output("exec_out", True)
            return {"exec_out": True}

        try:
            workflow = WorkflowModel.model_validate(workflow_json)
        except Exception as e:
            self.log_error(f"Failed to load internal workflow: {e}")
            await self.set_output("exec_out", True)
            return {"exec_out": True}

        # Inject external input values into group_in nodes
        for node_model in workflow.nodes:
            if node_model.node_id == "group_in":
                port_name = node_model.parameters.get("port_name", "")
                if port_name and port_name in inputs:
                    node_model.parameters["value"] = inputs[port_name]

        gm = GraphManager()
        gm.from_model(workflow)

        # Preserve outer execution memory — the sub-executor clears it on entry
        saved_memory = dict(_BaseNode.memory)
        sub_executor = NetworkExecutor(gm)
        try:
            await sub_executor.run()
        finally:
            _BaseNode.memory.clear()
            _BaseNode.memory.update(saved_memory)

        # Collect outputs from group_out nodes
        data_results = {}
        for inst_id, node_model in gm.nodes.items():
            if node_model.node_id == "group_out":
                port_name = node_model.parameters.get("port_name", "")
                if port_name:
                    node_result = sub_executor.node_results.get(inst_id, {})
                    data_results[port_name] = node_result.get("value")

        group_name = self.parameters.get("__name__", "Group")
        self.log_info(f"Group '{group_name}' finished with {len(data_results)} output(s).")

        # Push data outputs reactively before triggering exec flow so downstream
        # nodes see correct values when the exec chain continues.
        for port_name, value in data_results.items():
            await self.set_output(port_name, value)

        # Propagate exec flow — mirrors the set_output("exec_out", True) pattern
        # used by every other exec node; without this call downstream nodes never run.
        await self.set_output("exec_out", True)

        data_results["exec_out"] = True
        return data_results
