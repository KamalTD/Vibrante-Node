# Data Model: Core Node-Based Pipeline Engine

## Entities

### Node
- **id**: string (UUID or human-readable unique string)
- **type**: string (from Node Registry)
- **config**: object (node-specific configuration)
- **inputs**: string[] (list of port names)
- **outputs**: string[] (list of port names)

### Edge
- **id**: string
- **fromNodeId**: string
- **fromPort**: string
- **toNodeId**: string
- **toPort**: string

### Pipeline
- **id**: string
- **name**: string
- **nodes**: Node[]
- **edges**: Edge[]

## Validation Rules
- All nodes in a pipeline must have unique IDs.
- Edges must connect valid node output ports to valid node input ports.
- The pipeline graph must be a Directed Acyclic Graph (DAG) - no cycles allowed.

## Execution State (Internal)
- **status**: 'idle' | 'running' | 'completed' | 'failed'
- **nodeStatus**: Map<string, NodeExecutionState>
- **results**: Map<string, any> (data passed between nodes)
