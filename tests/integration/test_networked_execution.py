import pytest
import asyncio
from uuid import uuid4
from src.core.graph import GraphManager
from src.core.models import NodeInstanceModel, ConnectionModel, NodeDefinitionJSON, PortModel
from src.core.engine import NetworkExecutor
from src.core.registry import NodeRegistry

@pytest.mark.asyncio
async def test_topological_data_flow():
    # 1. Register test nodes
    NodeRegistry.register_definition(NodeDefinitionJSON(
        node_id="add_node", name="Add", category="Math",
        inputs=[PortModel(name="a", type="int"), PortModel(name="b", type="int")],
        outputs=[PortModel(name="out", type="int")],
        python_code="async def execute(self, inputs): return {'out': inputs.get('a', 0) + inputs.get('b', 0)}"
    ))
    
    NodeRegistry.register_definition(NodeDefinitionJSON(
        node_id="const_node", name="Const", category="Math",
        inputs=[PortModel(name="value", type="int", default=0)], 
        outputs=[PortModel(name="val", type="int")],
        python_code="async def execute(self, inputs): return {'val': inputs.get('value', 0)}"
    ))

    # 2. Build Graph: Const(5) -> Add.a, Const(10) -> Add.b
    gm = GraphManager()
    
    c1_id = uuid4()
    gm.add_node(NodeInstanceModel(instance_id=c1_id, node_id="const_node", position=(0,0), parameters={"value": 5}))
    
    c2_id = uuid4()
    gm.add_node(NodeInstanceModel(instance_id=c2_id, node_id="const_node", position=(0,100), parameters={"value": 10}))
    
    add_id = uuid4()
    gm.add_node(NodeInstanceModel(instance_id=add_id, node_id="add_node", position=(200,50)))
    
    gm.add_connection(ConnectionModel(from_node=c1_id, from_port="val", to_node=add_id, to_port="a"))
    gm.add_connection(ConnectionModel(from_node=c2_id, from_port="val", to_node=add_id, to_port="b"))

    # 3. Execute
    executor = NetworkExecutor(gm)
    await executor.run()
    
    # 4. Verify results
    assert executor.node_results[add_id]["out"] == 15

@pytest.mark.asyncio
async def test_execution_cancellation():
    NodeRegistry.register_definition(NodeDefinitionJSON(
        node_id="long_node", name="Long", category="Test",
        inputs=[], outputs=[PortModel(name="out", type="int")],
        python_code="import asyncio\nasync def execute(self, inputs):\n    await asyncio.sleep(1)\n    return {'out': 1}"
    ))
    
    gm = GraphManager()
    n_id = uuid4()
    gm.add_node(NodeInstanceModel(instance_id=n_id, node_id="long_node", position=(0,0)))
    
    executor = NetworkExecutor(gm)
    
    # Start in background
    run_task = asyncio.create_task(executor.run())
    await asyncio.sleep(0.1)
    
    # Cancel
    executor.stop()
    await run_task
    
    assert n_id not in executor._executed_nodes
