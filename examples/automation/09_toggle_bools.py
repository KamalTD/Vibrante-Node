# Example: Toggle all boolean parameters to True
count = 0
for node in scene.nodes:
    for name, p_type in node.node_definition.parameter_types.items():
        if p_type == bool:
            node.set_parameter(name, True)
            count += 1
print(f"Toggled {count} boolean parameters to True.")
