from src.nodes.base import BaseNode

class MathSquareNode(BaseNode):
    name = "Math Square"
    
    def __init__(self):
        super().__init__()
        self.add_input("x", "float", widget_type="float")
        self.add_output("result", "float")

    async def execute(self, inputs):
        x = float(inputs.get("x", 0.0))
        return {"result": x * x}

def register_node():
    return MathSquareNode
