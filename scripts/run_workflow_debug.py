import sys
import os
import asyncio
import json
# Ensure project root is importable so 'src' package imports work
sys.path.insert(0, os.path.abspath('.'))
from src.core.graph import GraphManager
from src.core.models import WorkflowModel
from src.core.engine import NetworkExecutor
from src.core.registry import NodeRegistry
import os


def main():
    data = json.load(open('workflows/python_script_node.json','r',encoding='utf-8'))
    model = WorkflowModel.model_validate(data)
    # Ensure JSON node definitions are loaded so dynamic node classes exist
    NodeRegistry.load_all(os.path.abspath('nodes'))

    gm = GraphManager()
    gm.from_model(model)

    # Diagnostics
    print('Loaded node definitions:', NodeRegistry.list_node_ids())
    print('Graph nodes:', list(gm.nodes.keys()))
    print('Graph connections:', len(gm.connections))
    print('python_script class:', NodeRegistry.get_class('python_script'))

    execer = NetworkExecutor(gm)

    execer.node_output.connect(lambda nid, out: print('NODE_OUTPUT', nid, out))
    execer.node_log.connect(lambda nid, msg, lvl: print('LOG', nid, lvl, msg))
    execer.node_finished.connect(lambda nid, status: print('FIN', nid, status))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(execer.run())


if __name__ == '__main__':
    main()
