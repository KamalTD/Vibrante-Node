from src.nodes.base import BaseNode, NodeRegistry
import os

class FileLoaderNode(BaseNode):
    name = "File Loader"
    category = "IO"
    def __init__(self):
        super().__init__()
        self.add_input("file_path", "string", widget_type="file")
        self.add_output("file_data", "string")
        self.icon_path = "icons/folder.svg"

    async def execute(self, inputs):
        path = inputs.get("file_path")
        if not path or not os.path.exists(path):
            return {"file_data": ""}
        try:
            # Use utf-8 with fallback to ignore/replace to handle various file types safely
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
            return {"file_data": data}
        except Exception as e:
            return {"file_data": f"Error reading file: {str(e)}"}

class DataProcessorNode(BaseNode):
    name = "Data Processor"
    category = "General"
    def __init__(self):
        super().__init__()
        self.add_input("data_in")
        self.add_output("data_out")

    async def execute(self, inputs):
        return {"data_out": f"Processed: {inputs.get('data_in')}"}

class ConsoleSinkNode(BaseNode):
    name = "Console Sink"
    category = "IO"
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
