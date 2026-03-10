# Example: Clear the scene and add a single start node
scene.clear()
start_node = scene.add_node_by_name("message_node", (100, 100))
start_node.set_parameter("msg", "Start Here")
print("Scene reset with start node.")
