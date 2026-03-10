from src.nodes.base import BaseNode

class ReactiveConfigNode(BaseNode):
    name = "Reactive Config"
    
    def __init__(self):
        super().__init__()
        self.add_input("trigger", "any")
        self.add_parameter("auto_prefix", str, "NONE")
        self.add_output("result", "string")

    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        # When something plugs into 'trigger', copy its name as a prefix
        if is_input and port_name == "trigger":
            new_prefix = f"FROM_{other_node.name.upper()}_"
            self.parameters["auto_prefix"] = new_prefix
            self.log_info(f"Auto-configured prefix to: {new_prefix}")

    async def execute(self, inputs):
        prefix = self.parameters.get("auto_prefix", "")
        return {"result": f"{prefix}EXECUTED"}

def register_node():
    return ReactiveConfigNode
