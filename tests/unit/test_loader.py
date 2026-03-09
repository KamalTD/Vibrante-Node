import pytest
import os
import tempfile
from src.core.loader import ScriptLoader
from src.nodes.base import NodeRegistry

def test_script_loading():
    script_content = """from src.nodes.base import BaseNode

class DynamicNode(BaseNode):
    name = "DynamicNode"
    def __init__(self):
        super().__init__()
    async def execute(self, inputs):
        return {"result": "success"}

def register_node():
    return DynamicNode
"""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(script_content)
        temp_path = f.name

    try:
        success = ScriptLoader.load_node_from_file(temp_path)
        assert success == True
        assert "DynamicNode" in NodeRegistry.list_nodes()
        
        node_class = NodeRegistry.get_node_class("DynamicNode")
        instance = node_class()
        assert instance.name == "DynamicNode"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
