import asyncio
from uuid import uuid4
from src.core.graph import GraphManager
from src.core.models import NodeInstanceModel, ConnectionModel, PortModel, NodeDefinitionJSON
from src.core.engine import NetworkExecutor
from src.core.registry import NodeRegistry

async def reproduce_foreach_issues():
    NodeRegistry.register_builtins()
    
    # Add a custom node for reactive continue (Data Node)
    NodeRegistry.register_definition(NodeDefinitionJSON(
        node_id="skip_b",
        name="Skip B",
        use_exec=False, 
        inputs=[PortModel(name="item", type="string")],
        outputs=[PortModel(name="skip", type="bool")],
        python_code="async def execute(self, inputs):\n    res = inputs.get('item') == 'B'\n    return {'skip': res}\n\nasync def on_parameter_changed(self, name, value):\n    if name == 'item':\n        res = value == 'B'\n        # self.log_info(f'Reactive Skip Check: {value} -> {res}')\n        await self.set_output('skip', res)"
    ))

    gm = GraphManager()
    
    # 1. For Each Node
    fe_id = uuid4()
    gm.add_node(NodeInstanceModel(
        instance_id=fe_id,
        node_id="For Each",
        position=(0,0),
        parameters={"collection": ["A", "B", "C"]}
    ))
    
    # 2. Console Sink Node (to track order)
    cp_id = uuid4()
    gm.add_node(NodeInstanceModel(
        instance_id=cp_id,
        node_id="Console Sink",
        position=(200,0)
    ))
    
    # 3. Skip B Node
    sb_id = uuid4()
    gm.add_node(NodeInstanceModel(instance_id=sb_id, node_id="skip_b", position=(100, 100)))

    # Connections
    # FE.current_item -> CP.data
    gm.add_connection(ConnectionModel(from_node=fe_id, from_port="current_item", to_node=cp_id, to_port="data"))
    # FE.each_item -> CP.exec_in
    gm.add_connection(ConnectionModel(from_node=fe_id, from_port="each_item", to_node=cp_id, to_port="exec_in", is_exec=True))
    # FE.current_item -> SB.item
    gm.add_connection(ConnectionModel(from_node=fe_id, from_port="current_item", to_node=sb_id, to_port="item"))
    # SB.skip -> FE.continue_condition
    gm.add_connection(ConnectionModel(from_node=sb_id, from_port="skip", to_node=fe_id, to_port="continue_condition"))
    
    print("\n--- Testing continue_condition (Expect Skip 'B') ---")
    executor = NetworkExecutor(gm)
    executor.node_log.connect(lambda nid, msg, lvl: print(f"LOG [{nid}]: {msg}"))
    await executor.run()

if __name__ == "__main__":
    asyncio.run(reproduce_foreach_issues())
