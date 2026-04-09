"""
Houdini Create Box Demo
========================
Creates a geometry object with a box SOP in the live Houdini session.
Demonstrates using the Houdini bridge from a Vibrante-Node script.
"""
from src.utils.hou_bridge import get_bridge, is_available

if not is_available():
    print("Houdini command server not reachable.")
    print("Make sure Vibrante-Node was launched from Houdini.")
else:
    bridge = get_bridge()

    # Create a geo node in /obj
    geo = bridge.create_node("/obj", "geo", "demo_box")
    print(f"Created geo node: {geo['path']}")

    # Delete the default file1 node
    try:
        bridge.delete_node(geo["path"] + "/file1")
    except Exception:
        pass

    # Create a box SOP inside it
    box = bridge.create_node(geo["path"], "box", "my_box")
    print(f"Created box SOP: {box['path']}")

    # Set the box size
    bridge.set_parms(box["path"], {"sizex": 2.0, "sizey": 3.0, "sizez": 1.5})
    print("Set box size to 2x3x1.5")

    # Set display flag
    bridge.set_display_flag(box["path"], True)
    bridge.set_render_flag(box["path"], True)

    # Layout
    bridge.layout_children(geo["path"])

    print("Done! Check Houdini viewport.")
