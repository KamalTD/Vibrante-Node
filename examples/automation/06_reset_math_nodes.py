# Example: Reset all values in math nodes to zero
count = 0
for node in scene.nodes:
    # Match any math-related nodes
    if "math" in node.node_definition.node_id.lower():
        # Check if they have 'a' and 'b' parameters
        if "a" in node.node_definition.parameters:
            node.set_parameter("a", 0)
        if "b" in node.node_definition.parameters:
            node.set_parameter("b", 0)
        count += 1
print(f"Reset {count} math nodes to 0.")
