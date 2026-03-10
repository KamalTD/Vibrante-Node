from src.nodes.base import BaseNode

class LogicThresholdNode(BaseNode):
    name = "Logic Threshold"
    
    def __init__(self):
        super().__init__()
        self.add_input("value", "float", widget_type="float")
        self.add_input("threshold", "float", widget_type="float")
        self.add_output("above", "bool")
        self.add_output("difference", "float")

    async def execute(self, inputs):
        val = float(inputs.get("value", 0.0))
        thr = float(inputs.get("threshold", 0.0))
        is_above = val > thr
        return {
            "above": is_above,
            "difference": val - thr
        }

def register_node():
    return LogicThresholdNode
