# Example: Count and display node types in the current scene
summary = {}
for node in scene.nodes:
    name = node.node_definition.name
    summary[name] = summary.get(name, 0) + 1
print("Scene Summary:")
for name, count in summary.items():
    print(f"- {name}: {count}")
