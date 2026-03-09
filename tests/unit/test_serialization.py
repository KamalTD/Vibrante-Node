import pytest
from uuid import uuid4
from src.core.graph import GraphManager
from src.core.models import NodeInstanceModel, ConnectionModel, WorkflowModel

def test_workflow_serialization():
    gm = GraphManager()
    n1_id = uuid4()
    n2_id = uuid4()
    
    gm.add_node(NodeInstanceModel(id=n1_id, definition_name="SourceNode", position=(0,0), parameters={"val": 10}))
    gm.add_node(NodeInstanceModel(id=n2_id, definition_name="SinkNode", position=(200,0)))
    
    gm.add_connection(ConnectionModel(from_node=n1_id, from_port="out", to_node=n2_id, to_port="in"))
    
    model = gm.to_model()
    json_data = model.json()
    
    # Deserialize
    new_model = WorkflowModel.parse_raw(json_data)
    assert len(new_model.nodes) == 2
    assert len(new_model.connections) == 1
    
    new_gm = GraphManager()
    new_gm.from_model(new_model)
    assert n1_id in new_gm.nodes
    assert new_gm.nodes[n1_id].parameters["val"] == 10
