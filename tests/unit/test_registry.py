import pytest
from src.core.registry import NodeRegistry
from src.core.models import NodeDefinitionJSON, PortModel
from src.nodes.base import BaseNode

def test_dynamic_class_generation():
    # Define a simple node JSON
    definition = NodeDefinitionJSON(
        node_id="test_dynamic",
        name="Test Dynamic",
        category="Test",
        inputs=[
            PortModel(name="a", type="int", default=10),
            PortModel(name="b", type="int", default=20)
        ],
        outputs=[
            PortModel(name="result", type="int")
        ],
        python_code="""
async def execute(self, inputs):
    a = inputs.get('a', 0)
    b = inputs.get('b', 0)
    return {'result': a + b}
"""
    )
    
    # Register it
    success = NodeRegistry.register_definition(definition)
    assert success is True
    
    # Get the generated class
    node_class = NodeRegistry.get_class("test_dynamic")
    assert node_class is not None
    assert issubclass(node_class, BaseNode)
    assert node_class.name == "Test Dynamic"
    
    # Instantiate and check ports
    instance = node_class()
    assert "a" in instance.inputs
    assert "b" in instance.inputs
    assert "result" in instance.outputs
    assert instance.parameters["a"] == 10
    
    # Test execution (simulated)
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def run_test():
        result = await instance.execute({'a': 5, 'b': 7})
        assert result['result'] == 12
        
    loop.run_until_complete(run_test())
    loop.close()

def test_builtin_registration():
    # Ensure builtins are registered
    NodeRegistry.register_builtins()
    ids = NodeRegistry.list_node_ids()
    assert "For Each" in ids
    assert "Sequencer" in ids
    
    sequence_class = NodeRegistry.get_class("Sequencer")
    assert sequence_class is not None
