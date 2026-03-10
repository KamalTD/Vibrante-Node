from src.nodes.base import BaseNode

class StringReverseNode(BaseNode):
    name = "String Reverse"
    
    def __init__(self):
        super().__init__()
        self.add_input("text", "string", widget_type="text")
        self.add_output("reversed", "string")

    async def execute(self, inputs):
        text = str(inputs.get("text", ""))
        return {"reversed": text[::-1]}

def register_node():
    return StringReverseNode
