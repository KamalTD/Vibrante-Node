from src.nodes.base import BaseNode

class ListStatsNode(BaseNode):
    name = "List Statistics"
    
    def __init__(self):
        super().__init__()
        self.add_input("numbers", "list")
        self.add_output("sum", "float")
        self.add_output("average", "float")
        self.add_output("max", "float")

    async def execute(self, inputs):
        nums = inputs.get("numbers", [])
        if not nums:
            return {"sum": 0.0, "average": 0.0, "max": 0.0}
        
        valid_nums = [float(n) for n in nums if isinstance(n, (int, float))]
        s = sum(valid_nums)
        return {
            "sum": s,
            "average": s / len(valid_nums) if valid_nums else 0,
            "max": max(valid_nums) if valid_nums else 0
        }

def register_node():
    return ListStatsNode
