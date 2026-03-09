from src.nodes.base import BaseNode, NodeRegistry

class FileLoaderNode(BaseNode):
    name = "File Loader"
    def __init__(self):
        super().__init__()
        self.add_output("file_data")
        self.add_parameter("file_path", str, "")

    async def execute(self, inputs):
        return {"file_data": f"Content of {self.get_parameter('file_path')}"}

class DataProcessorNode(BaseNode):
    name = "Data Processor"
    def __init__(self):
        super().__init__()
        self.add_input("data_in")
        self.add_output("data_out")

    async def execute(self, inputs):
        return {"data_out": f"Processed: {inputs.get('data_in')}"}

class ConsoleSinkNode(BaseNode):
    name = "Console Sink"
    def __init__(self):
        super().__init__()
        self.add_input("data")

    async def execute(self, inputs):
        print(f"SINK: {inputs.get('data')}")
        return {}

def register_builtins():
    NodeRegistry.register(FileLoaderNode)
    NodeRegistry.register(DataProcessorNode)
    NodeRegistry.register(ConsoleSinkNode)
