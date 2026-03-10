from src.nodes.base import BaseNode

class DictMergeNode(BaseNode):
    name = "Dict Merge"
    
    def __init__(self):
        super().__init__()
        self.add_input("dict_a", "dict")
        self.add_input("dict_b", "dict")
        self.add_output("merged", "dict")

    async def execute(self, inputs):
        a = inputs.get("dict_a", {})
        b = inputs.get("dict_b", {})
        res = a.copy()
        res.update(b)
        return {"merged": res}

def register_node():
    return DictMergeNode
