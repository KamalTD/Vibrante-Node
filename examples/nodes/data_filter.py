from src.nodes.base import BaseNode

class DataFilterNode(BaseNode):
    name = "Data Filter"
    
    def __init__(self):
        super().__init__()
        self.add_input("list", "list")
        self.add_input("pattern", "string", widget_type="text")
        self.add_output("filtered_list", "list")

    async def execute(self, inputs):
        lst = inputs.get("list", [])
        pattern = str(inputs.get("pattern", ""))
        filtered = [item for item in lst if pattern in str(item)]
        return {"filtered_list": filtered}

def register_node():
    return DataFilterNode
