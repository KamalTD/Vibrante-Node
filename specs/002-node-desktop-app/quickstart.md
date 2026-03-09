# Quickstart: Python Node-Based Desktop Application

## Getting Started
(Assuming a local Python installation)
```bash
pip install PySide6 pydantic toposort
python src/app.py
```

## Basic Workflow Design
1. **Add Nodes**: Right-click on the canvas to open the node library and select a node type (e.g., File Loader, Image Processor).
2. **Connect Nodes**: Drag from an output port (right side of node) to an input port (left side of node) to create a connection.
3. **Edit Parameters**: Click on a node to reveal its parameters in the side panel or on the node itself.
4. **Execute**: Click the "Execute" button in the toolbar. Watch node indicators change status (Idle -> Running -> Success).
5. **Save/Load**: Use File -> Save to store your workflow as a JSON file.

## Creating a Custom Node
Create a file named `my_node.py` with the following content:
```python
from node_app.nodes.base import BaseNode

class MultiplyNode(BaseNode):
    name = "Multiply"
    
    def __init__(self):
        super().__init__()
        self.add_input("a", float)
        self.add_input("b", float)
        self.add_output("result", float)

    async def execute(self, inputs):
        return {"result": inputs["a"] * inputs["b"]}

def register_node():
    return MultiplyNode
```
Load this script via the app's "Load Custom Node" menu.
