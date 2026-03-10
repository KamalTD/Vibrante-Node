from src.nodes.base import BaseNode
import asyncio

class AsyncDelayNode(BaseNode):
    name = "Async Delay"
    
    def __init__(self):
        super().__init__()
        self.add_input("seconds", "float", widget_type="float")
        self.add_input("message_in", "string")
        self.add_output("message_out", "string")

    async def execute(self, inputs):
        sec = float(inputs.get("seconds", 1.0))
        msg = inputs.get("message_in", "Done")
        self.log_info(f"Waiting for {sec} seconds...")
        await asyncio.sleep(sec)
        return {"message_out": msg}

def register_node():
    return AsyncDelayNode
