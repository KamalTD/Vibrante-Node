from src.nodes.base import BaseNode
import os

class EnvReaderNode(BaseNode):
    name = "Env Reader"
    
    def __init__(self):
        super().__init__()
        self.add_input("var_name", "string", widget_type="text")
        self.add_output("value", "string")

    async def execute(self, inputs):
        vn = str(inputs.get("var_name", ""))
        val = os.environ.get(vn, "")
        return {"value": val}

def register_node():
    return EnvReaderNode
