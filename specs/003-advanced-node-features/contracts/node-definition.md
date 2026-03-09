# Interface Contract: Node Persistence & Registry

## Node Definition JSON Schema
Custom nodes are stored as `.json` files in the `nodes/` directory.

```json
{
  "node_id": "math_multiply",
  "name": "Multiply",
  "description": "Multiplies two numbers",
  "inputs": [
    {"name": "a", "type": "float"},
    {"name": "b", "type": "float"}
  ],
  "outputs": [
    {"name": "result", "type": "float"}
  ],
  "python_code": "from src.nodes.base import BaseNode\n\nclass MultiplyNode(BaseNode):\n    name = \"Multiply\"\n    def __init__(self):\n        super().__init__()\n        self.add_input(\"a\", \"float\")\n        self.add_input(\"b\", \"float\")\n        self.add_output(\"result\", \"float\")\n\n    async def execute(self, inputs):\n        return {'result': inputs['a'] * inputs['b']}\n\ndef register_node():\n    return MultiplyNode"
}
```

## Registry API (Internal)

### `NodeRegistry.load_all()`
- Scans `nodes/` directory.
- Validates and registers each JSON definition.

### `NodeRegistry.save_node(definition: NodeDefinitionJSON)`
- Writes definition to `nodes/{node_id}.json`.
- Updates internal cache.

### `NodeRegistry.delete_node(node_id: string)`
- Removes JSON file.
- Checks if node is in use in any open workflow.

## Execution Engine Contract

### `Executor.run(workflow: WorkflowModel)`
- Builds dependency graph using `toposort`.
- Executes nodes layer by layer.
- Emits signals for UI updates (node started, node finished, error).
