import pytest
import asyncio
from uuid import uuid4
from src.core.graph import GraphManager
from src.core.models import NodeInstanceModel, ConnectionModel, NodeDefinitionJSON, PortModel
from src.core.engine import NetworkExecutor
from src.core.registry import NodeRegistry
from src.nodes.base import BaseNode

class TestNode(BaseNode):
    name = "TestNode"
    def __init__(self):
        super().__init__()
        self.add_input("in")
        self.add_output("out")
    async def execute(self, inputs):
        return {"out": (inputs.get("in") or 0) + 1}

@pytest.fixture
def setup_nodes():
    # Register TestNode manually in the correct registry
    NodeRegistry._classes["TestNode"] = TestNode
    # Create a dummy definition for it
    instance = TestNode()
    definition = NodeDefinitionJSON(
        node_id="TestNode",
        name="TestNode",
        description="",
        category="General",
        inputs=[PortModel(name=p.name, type=p.data_type) for p in instance.inputs.values()],
        outputs=[PortModel(name=p.name, type=p.data_type) for p in instance.outputs.values()],
        python_code=""
    )
    NodeRegistry._definitions["TestNode"] = definition

def test_graph_cycle_detection():
    gm = GraphManager()
    n1_id = uuid4()
    n2_id = uuid4()
    
    gm.add_node(NodeInstanceModel(instance_id=n1_id, node_id="TestNode", position=(0,0)))
    gm.add_node(NodeInstanceModel(instance_id=n2_id, node_id="TestNode", position=(100,0)))
    
    # Normal connection
    assert gm.add_connection(ConnectionModel(from_node=n1_id, from_port="out", to_node=n2_id, to_port="in")) == True
    
    # Create cycle
    assert gm.add_connection(ConnectionModel(from_node=n2_id, from_port="out", to_node=n1_id, to_port="in")) == False
    assert len(gm.connections) == 1

@pytest.mark.asyncio
async def test_engine_execution(setup_nodes):
    gm = GraphManager()
    n1_id = uuid4()
    n2_id = uuid4()
    
    gm.add_node(NodeInstanceModel(instance_id=n1_id, node_id="TestNode", position=(0,0), parameters={}))
    gm.add_node(NodeInstanceModel(instance_id=n2_id, node_id="TestNode", position=(100,0), parameters={}))
    
    gm.add_connection(ConnectionModel(from_node=n1_id, from_port="out", to_node=n2_id, to_port="in"))
    
    engine = NetworkExecutor(gm)
    
    # Manually run the execution
    await engine.run()
    
    assert n1_id in engine.node_results
    assert engine.node_results[n1_id]["out"] == 1
    assert n2_id in engine.node_results
    assert engine.node_results[n2_id]["out"] == 2
