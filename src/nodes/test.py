from src.nodes.base import BaseNode

class test(BaseNode):
    name = "test"
    
    def __init__(self):
        super().__init__()
        self.add_input("port_0", "any")
        self.add_output("port_0", "any")

        # Ports will be auto-injected during save
        
    async def execute(self, inputs):
        # inputs is a dict: {port_name: value}
        # return a dict: {port_name: value}
        return {}

def register_node():
    return test
