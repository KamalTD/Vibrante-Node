# Interface Contract: Core Pipeline Engine

## Overview
The Core Pipeline Engine is exposed as a library for Node.js. It allows users to define, validate, and execute node-based pipelines.

## Engine API (Library)

### `createPipeline(json: string | object): Pipeline`
- **Purpose**: Parses and validates a pipeline from JSON.
- **Input**: Pipeline JSON string or object.
- **Output**: Validated Pipeline instance.
- **Throws**: `ValidationError` if the JSON is malformed or the graph has cycles.

### `executePipeline(pipeline: Pipeline): Promise<PipelineResult>`
- **Purpose**: Asynchronously runs a pipeline.
- **Input**: Validated Pipeline.
- **Output**: Final result object containing success status and node logs.
- **Throws**: `ExecutionError` if a node fails and the error policy is set to stop.

## Node Definition (JSON)
```json
{
  "id": "node-1",
  "type": "transform:square",
  "config": { "multiplier": 2 },
  "inputs": ["val"],
  "outputs": ["result"]
}
```

## Edge Definition (JSON)
```json
{
  "id": "edge-1",
  "from": { "node": "node-1", "port": "result" },
  "to": { "node": "node-2", "port": "val" }
}
```
