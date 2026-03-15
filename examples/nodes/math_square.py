from src.nodes.base import BaseNode

class MathSquareNode(BaseNode):
    name = "Math Square"
    category = "Math"
    description = "Calculates the square of the input value."

    def __init__(self):
        super().__init__(use_exec=False)
        self.add_input("value", "float", widget_type="float", default=0.0)
        self.add_output("result", "float")
        self.icon_path = "icons/multiply.svg"

    async def execute(self, inputs):
        val = float(inputs.get("value", 0.0))
        result = val * val
        self.log_info(f"Squaring {val} -> {result}")
        await self.set_output("result", result)
        return {"result": result}

    async def on_parameter_changed(self, name, value):
        if name == "value":
            try:
                val = float(value)
                await self.set_output("result", val * val)
            except:
                pass

def register_node():
    return MathSquareNode
