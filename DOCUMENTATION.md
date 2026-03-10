# Vibrante-Node - Technical API Documentation

This document provides a comprehensive reference for the Vibrante-Node Scripting API and Workflow Automation system.

---

## 🏗️ Part 1: Node Scripting API (`BaseNode`)

Use these patterns within the **Node Builder** to create functional, reactive custom nodes.

### 🔹 Scenario A: The Basic Calculator
Maintains a simple "Input -> Logic -> Output" flow.

```python
from src.nodes.base import BaseNode

class AddIntegersNode(BaseNode):
    name = "Math Adder"
    
    def __init__(self):
        super().__init__()
        # Define ports with interactive widgets
        self.add_input("val_a", "int", widget_type="int")
        self.add_input("val_b", "int", widget_type="int")
        self.add_output("result", "int")
        
    async def execute(self, inputs):
        # inputs contains the current values of 'val_a' and 'val_b'
        a = inputs.get("val_a", 0)
        b = inputs.get("val_b", 0)
        res = a + b
        self.log_success(f"Calculation complete: {a} + {b} = {res}")
        return {"result": res}

def register_node():
    return AddIntegersNode
```

### 🔹 Scenario B: Reactive Multi-Port Sync
This node immediately copies data between ports upon connection and interaction.

```python
from src.nodes.base import BaseNode

class SyncNode(BaseNode):
    name = "Reactive Buffer"
    
    def __init__(self):
        super().__init__()
        self.add_input("in_a", "string", widget_type="text")
        self.add_output("out_a", "string")
        
    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        if is_input and port_name == "in_a":
            # 1. Grab data from the other node immediately
            data = other_node.get_parameter(other_port_name)
            # 2. Update our own internal parameter and UI widget
            self.set_parameter("in_port", data)
            self.log_info(f"Buffered data from {other_node.name}")

    def on_parameter_changed(self, name, value):
        # 3. Propagate changes live as the user types
        if name == "in_a":
            self.parameters["out_a"] = value

    async def execute(self, inputs):
        return {"out_a": inputs.get("in_a")}

def register_node():
    return SyncNode
```

### 🔹 Scenario C: Background Async Processing
Demonstrates non-blocking execution using `asyncio`.

```python
import asyncio
from src.nodes.base import BaseNode

class HeavyTaskNode(BaseNode):
    name = "Async Worker"
    
    def __init__(self):
        super().__init__()
        self.add_input("task_name", "string", widget_type="text")
        self.add_output("status", "string")
        
    async def execute(self, inputs):
        name = inputs.get("task_name", "Unnamed")
        self.log_info(f"Starting long task: {name}...")
        
        # Simulate heavy work without freezing the UI
        await asyncio.sleep(3.0) 
        
        self.log_success(f"Task {name} finished!")
        return {"status": "Complete"}

def register_node():
    return HeavyTaskNode
```

---

## 🤖 Part 2: Workflow Automation API

Use these scripts in the **Scripting Console** to automate the application.

### 🔹 Scenario D: Programmatic Workflow Building
Builds a complete multi-node pipeline from scratch.

```python
# 1. Start fresh
scene.clear()

# 2. Create nodes at specific coordinates
loader = scene.add_node_by_name("message_node", (50, 100))
worker = scene.add_node_by_name("async_delay", (350, 100))
printer = scene.add_node_by_name("console_print", (650, 100))

# 3. Configure parameters programmatically
if loader and worker and printer:
    loader.set_parameter("msg", "Automated Message 1.0")
    worker.set_parameter("seconds", 2.0)
    
    # 4. Wire them up
    # Connection: loader.out -> worker.input_data
    scene.connect_nodes(loader, "out", worker, "input_data")
    # Connection: worker.output_data -> printer.data
    scene.connect_nodes(worker, "output_data", printer, "data")
    
    print("Network Build Finished.")
```

### 🔹 Scenario E: Batch Parameter Modification
Update values across multiple nodes based on search criteria.

```python
# Find all "Message Node" instances in the current scene
for node in scene.nodes:
    if node.node_definition.name == "Message Node":
        old_val = node.get_parameter("msg")
        new_val = f"UPDATED: {old_val}"
        # This will instantly disable widgets and propagate data downstream
        node.set_parameter("msg", new_val)
        print(f"Updated {node.instance_id}")
```

### 🔹 Scenario F: Automated Batch Execution
Running the workflow multiple times with different inputs.

```python
import time

msg_node = scene.find_node_by_name("Message Node")
if msg_node:
    test_cases = ["Alpha", "Beta", "Gamma"]
    
    for case in test_cases:
        print(f"Testing Case: {case}")
        msg_node.set_parameter("msg", case)
        
        # Trigger actual pipeline execution
        app.execute_pipeline()
        
        # Note: Since execution is async, we might need a delay or 
        # a callback hook for true batching (Coming in v1.1)
```

### 🔹 Scenario G: Source Control Automation
Manage your project's Git status from within the script editor.

```python
# Stage current changes
git.status()
git.commit("Automated backup of current workflow")
git.push()
print("Cloud backup successful.")
```
