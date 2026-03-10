from src.nodes.base import BaseNode
import random

class RandomListNode(BaseNode):
    name = "Random List"
    
    def __init__(self):
        super().__init__()
        self.add_input("count", "int", widget_type="int")
        self.add_output("result_list", "list")

    async def execute(self, inputs):
        count = int(inputs.get("count", 5))
        data = [random.randint(1, 100) for _ in range(count)]
        return {"result_list": data}

def register_node():
    return RandomListNode
