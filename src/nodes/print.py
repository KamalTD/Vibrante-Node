from src.nodes.base import BaseNode

class print(BaseNode):
    name = "print"
    
    def __init__(self):
        super().__init__()
        self.add_input("in", "any")
        self.add_output("string", "any")

        # Ports will be auto-injected during save
        
    async def execute(self, inputs):
        # inputs is a dict: {port_name: value}
        # return a dict: {port_name: value}
        return {}

def register_node():
    return print
