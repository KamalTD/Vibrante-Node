from src.nodes.base import BaseNode

class DictSummaryNode(BaseNode):
    name = "Dict Summary"
    
    def __init__(self):
        super().__init__()
        self.add_input("data", "dict")
        self.add_output("keys", "list")
        self.add_output("count", "int")

    async def execute(self, inputs):
        data = inputs.get("data", {})
        keys = list(data.keys())
        return {
            "keys": keys,
            "count": len(keys)
        }

def register_node():
    return DictSummaryNode
