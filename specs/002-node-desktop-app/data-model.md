# Data Model: Python Node-Based Desktop Application

## Entities

### NodeDefinition (Template)
- **name**: string
- **inputs**: List[PortDefinition]
- **outputs**: List[PortDefinition]
- **script_path**: string (optional, for custom nodes)
- **execution_fn**: callable

### NodeInstance
- **id**: UUID
- **definition_name**: string
- **position**: Tuple[float, float]
- **parameters**: Dict[string, Any]
- **state**: 'idle' | 'running' | 'success' | 'failed'

### PortDefinition
- **name**: string
- **data_type**: string (for compatibility checks)

### Connection
- **id**: UUID
- **from_node**: UUID
- **from_port**: string
- **to_node**: UUID
- **to_port**: string

### Workflow
- **nodes**: List[NodeInstance]
- **connections**: List[Connection]
- **metadata**: Dict[string, Any]

## Validation Rules
- All nodes in a workflow must have unique IDs.
- Connections must only connect outputs to inputs.
- Cycles are forbidden for standard graph execution.
- Data types must be compatible if specified on ports.
