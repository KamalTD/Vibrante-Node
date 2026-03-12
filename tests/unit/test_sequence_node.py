import pytest
import asyncio
from src.nodes.builtins.nodes import SequenceNode
from src.nodes.base import BaseNode

class MockNode(BaseNode):
    name = "Mock"
    async def execute(self, inputs): return {}

@pytest.mark.asyncio
async def test_sequence_node_init():
    node = SequenceNode()
    # use_exec=False, so no exec pins
    assert "exec_in" not in node.inputs
    assert "step_0" in node.inputs
    assert "exec_out" not in node.outputs
    assert "result" in node.outputs
    assert node._step_count == 1

@pytest.mark.asyncio
async def test_sequence_node_increment():
    node = SequenceNode()
    node._on_ports_changed = lambda: None
    
    # Simulate plugging into step_0
    node.on_plug_sync("step_0", True, MockNode(), "result")
    
    assert "step_1" in node.inputs
    assert node._step_count == 2

@pytest.mark.asyncio
async def test_sequence_node_decrement():
    node = SequenceNode()
    node._on_ports_changed = lambda: None
    
    # Mock is_port_connected
    connections = {"step_0": True, "step_1": False}
    node._is_port_connected = lambda name, is_in: connections.get(name, False)
    
    # Initially 1 step. Plug step_0 -> adds step_1.
    node.on_plug_sync("step_0", True, MockNode(), "result")
    assert node._step_count == 2
    
    # Now unplug step_0.
    connections["step_0"] = False
    node.on_unplug_sync("step_0", True)
    
    # Should have shrunk back to 1 step (step_0)
    assert node._step_count == 1
    assert "step_1" not in node.inputs

@pytest.mark.asyncio
async def test_sequence_node_execution():
    node = SequenceNode()
    
    # Mock inputs simulating pulled data
    inputs = {
        "step_0": "First Value",
        "step_1": "Second Value"
    }
    
    # Manually add ports to match inputs for test
    node.add_input("step_1", "any")
    
    result = await node.execute(inputs)
    
    # Should return the last non-None value
    assert result["result"] == "Second Value"
    assert node.parameters["result"] == "Second Value"
