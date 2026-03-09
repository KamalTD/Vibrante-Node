# Data Model: Advanced Node Features & Persistence

## Persistent Entities

### NodeDefinitionJSON
- **node_id**: string (slug format, e.g., "add_numbers")
- **name**: string (display name)
- **description**: string
- **inputs**: List[PortModel]
- **outputs**: List[PortModel]
- **python_code**: string (full source code of the node class)

### PortModel
- **name**: string
- **type**: string (e.g., "float", "string", "any")

### WorkflowModel (Updated)
- **nodes**: List[NodeInstanceModel]
- **connections**: List[ConnectionModel]
- **metadata**: Dict[str, Any]

### NodeInstanceModel (Updated)
- **instance_id**: UUID
- **node_id**: string (reference to NodeDefinitionJSON.node_id)
- **position**: Tuple[float, float]
- **parameters**: Dict[str, Any]

## Runtime Entities

### ExecutionContext
- **results**: Map[UUID, Dict[str, Any]] (instance_id -> {port_name: value})
- **status**: Map[UUID, string] (idle, running, success, failed)
- **errors**: Map[UUID, string] (error messages)

## Validation Rules
- `node_id` must be unique across the system.
- `python_code` must be valid Python and contain a `register_node` function.
- `Workflow` nodes must reference existing `node_id`s in the registry.
