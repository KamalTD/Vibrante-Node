from src.nodes.base import BaseNode

class ConnectionLoggerNode(BaseNode):
    name = "Connection Logger"
    
    def __init__(self):
        super().__init__()
        self.add_input("in_a")
        self.add_input("in_b")
        self.add_output("out")

    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        type_str = "Input" if is_input else "Output"
        self.log_info(f"PLUG EVENT: {type_str} port '{port_name}' connected to node '{other_node.name}'")

    def on_unplug_sync(self, port_name, is_input):
        type_str = "Input" if is_input else "Output"
        self.log_error(f"UNPLUG EVENT: {type_str} port '{port_name}' disconnected!")

    async def execute(self, inputs):
        # Simply return one of the inputs if it exists
        return {"out": inputs.get("in_a") or inputs.get("in_b")}

def register_node():
    return ConnectionLoggerNode
