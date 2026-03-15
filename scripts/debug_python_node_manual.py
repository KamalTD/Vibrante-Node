import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import asyncio
from src.core.registry import NodeRegistry
import json

NodeRegistry.load_all(os.path.abspath('nodes'))

# Load workflow model
wf = json.load(open('workflows/python_script_node.json','r',encoding='utf-8'))
data = wf['nodes']

nodes = {n['instance_id']: n for n in data}

# Instantiate python_script node class
cls = NodeRegistry.get_class('python_script')
if not cls:
    print('python_script class not registered')
    sys.exit(1)

inst = cls()
inst._on_log = lambda msg,lvl: print('LOG:', lvl, msg)

# Simulate node parameters from workflow
node_model = nodes[[k for k in nodes][0]]
params = node_model['parameters']
for k,v in params.items():
    # Copy all workflow parameters into the instance so embedded fields
    # like 'python_code' are available during execute.
    inst.parameters[k] = v

async def run():
    inputs = inst.parameters.copy()
    print('Inputs to execute:', inputs)
    res = await inst.execute(inputs)
    print('Execute returned:', res)

asyncio.run(run())
