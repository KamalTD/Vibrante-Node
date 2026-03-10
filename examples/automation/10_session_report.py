# Example: Generate a summary report of the current session
print("--- Automated Session Report ---")
print(f"Active Scene: {scene.__class__.__name__}")
print(f"Total Nodes: {len(scene.nodes)}")
print(f"Total Connections: {len(scene.connections)}")
print(f"Available Node Types: {len(registry.list_nodes())}")
print("--- End of Report ---")
