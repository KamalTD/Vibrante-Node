# Example: Generate a linear chain of nodes
scene.clear()
prev = None
for i in range(10):
    curr = scene.add_node_by_name("message_node", (i * 250, 100))
    curr.set_parameter("msg", f"Node {i}")
    if prev:
        scene.connect_nodes(prev, "out", curr, "msg")
    prev = curr
print("Linear chain of 10 nodes created.")
