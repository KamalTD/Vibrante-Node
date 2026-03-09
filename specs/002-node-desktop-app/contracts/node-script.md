# Interface Contract: Custom Node Scripts

## Overview
Custom nodes are defined in independent Python scripts. The application's `ScriptManager` dynamically loads these scripts and registers them in the node library.

## Script Specification

Every script MUST define a class inheriting from `BaseNode` and provide a registration function.

### Node Structure

```python
from node_app.nodes.base import BaseNode

class CustomProcessor(BaseNode):
    name = "Custom Processor"
    description = "Processes data with a custom algorithm"
    
    def __init__(self):
        super().__init__()
        # Define inputs and outputs
        self.add_input("data_in", type="any")
        self.add_output("data_out", type="any")
        
        # Define user-editable parameters
        self.add_parameter("multiplier", float, default=1.0)

    async def execute(self, inputs):
        """
        Main execution logic.
        :param inputs: Dict of input data
        :return: Dict of output data
        """
        val = inputs.get("data_in")
        multiplier = self.get_parameter("multiplier")
        
        # Logic here
        result = val * multiplier
        
        return {"data_out": result}

def register_node():
    return CustomProcessor
```

## Loader Expectations
- The script MUST be a valid Python file (.py).
- The `register_node` function MUST return a class that extends `BaseNode`.
- Syntax errors or runtime exceptions during loading MUST be caught by the app and reported to the user.
