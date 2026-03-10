from src.nodes.base import BaseNode

class SafetyResetNode(BaseNode):
    name = "Safety Reset"
    
    def __init__(self):
        super().__init__()
        self.add_input("data_in")
        self.add_parameter("secure_data", str, "LOCKED")
        self.add_output("data_out")

    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        if is_input:
            # Unlock when a connection is made
            self.parameters["secure_data"] = "UNLOCKED"
            self.log_success("Data connection verified. Unlocking...")

    def on_unplug_sync(self, port_name, is_input):
        if is_input:
            # Immediate lockout on disconnection
            self.parameters["secure_data"] = "LOCKED"
            self.log_error("Connection lost! Locking down secure data.")

    async def execute(self, inputs):
        status = self.parameters.get("secure_data", "LOCKED")
        if status == "LOCKED":
            return {"data_out": "ERROR: LOCKDOWN"}
        return {"data_out": f"Flow: {inputs.get('data_in')}"}

def register_node():
    return SafetyResetNode
