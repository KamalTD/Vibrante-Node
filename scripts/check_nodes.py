import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.core.registry import NodeRegistry

NodeRegistry.load_all('nodes')
for nid in NodeRegistry.list_node_ids():
    d = NodeRegistry.get_definition(nid)
    name = getattr(d, 'name', None)
    category = getattr(d, 'category', None)
    print(f"node_id={nid!r}, display name={name!r}, category={category!r}")
