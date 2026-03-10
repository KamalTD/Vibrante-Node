# Example: Update all message nodes with a prefix
count = 0
for node in scene.nodes:
    if "message" in node.node_definition.node_id:
        current_val = node.get_parameter("msg", "")
        node.set_parameter("msg", f"PREFIX_{current_val}")
        count += 1
print(f"Updated {count} message nodes.")
