import pytest
import asyncio
from uuid import uuid4
from src.core.graph import GraphManager
from src.core.models import NodeInstanceModel, ConnectionModel
from src.core.engine import DAGEngine
from src.nodes.base import BaseNode, NodeRegistry

class TestNode(BaseNode):
    name = "TestNode"
    def __init__(self):
        super().__init__()
        self.add_input("in")
        self.add_output("out")
    async def execute(self, inputs):
        return {"out": inputs.get("in", 0) + 1}

@pytest.fixture
def setup_nodes():
    NodeRegistry.register(TestNode)

def test_graph_cycle_detection():
    gm = GraphManager()
    n1_id = uuid4()
    n2_id = uuid4()
    
    gm.add_node(NodeInstanceModel(id=n1_id, definition_name="TestNode", position=(0,0)))
    gm.add_node(NodeInstanceModel(id=n2_id, definition_name="TestNode", position=(100,0)))
    
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
    
    gm.add_node(NodeInstanceModel(id=n1_id, definition_name="TestNode", position=(0,0), parameters={}))
    gm.add_node(NodeInstanceModel(id=n2_id, definition_name="TestNode", position=(100,0), parameters={}))
    
    gm.add_connection(ConnectionModel(from_node=n1_id, from_port="out", to_node=n2_id, to_port="in"))
    
    engine = DAGEngine(gm)
    
    # Manually set input for the first node if needed (our TestNode uses 0 as default)
    # n1_id -> out: 1, n2_id -> in: 1, out: 2
    
    success = await engine.execute()
    assert success == True
    assert engine.node_results[n1_id]["out"] == 1
    assert engine.node_results[n2_id]["out"] == 2
