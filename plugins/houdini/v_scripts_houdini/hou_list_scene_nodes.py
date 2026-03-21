"""
Houdini List Scene Nodes
========================
Lists all top-level nodes in /obj of the live Houdini session.
"""
from src.utils.hou_bridge import get_bridge, is_available

if not is_available():
    print("Houdini command server not reachable.")
    print("Make sure Vibrante-Node was launched from Houdini.")
else:
    bridge = get_bridge()
    children = bridge.children("/obj")

    print(f"Nodes in /obj ({len(children)}):")
    print("-" * 50)
    for child in children:
        print(f"  {child['name']:20s}  type: {child['type']:15s}  {child['path']}")
    print("-" * 50)
