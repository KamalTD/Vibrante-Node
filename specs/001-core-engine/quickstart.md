# Quickstart: Core Node-Based Pipeline Engine

## Installation
(Assuming a local library setup for now)
```bash
npm install node-based-pipeline-engine
```

## Basic Usage
```typescript
import { Engine, Pipeline } from 'node-based-pipeline-engine';

const myPipeline = {
  id: 'my-pipeline',
  name: 'Simple Square Pipeline',
  nodes: [
    { id: 'source', type: 'source:static', config: { data: [1, 2, 3] }, inputs: [], outputs: ['val'] },
    { id: 'square', type: 'transform:square', config: {}, inputs: ['val'], outputs: ['result'] },
    { id: 'sink', type: 'sink:console', config: {}, inputs: ['result'], outputs: [] }
  ],
  edges: [
    { id: 'e1', from: { node: 'source', port: 'val' }, to: { node: 'square', port: 'val' } },
    { id: 'e2', from: { node: 'square', port: 'result' }, to: { node: 'sink', port: 'result' } }
  ]
};

const engine = new Engine();
const pipeline = engine.createPipeline(myPipeline);
const result = await engine.executePipeline(pipeline);

console.log('Pipeline finished:', result.status);
```
