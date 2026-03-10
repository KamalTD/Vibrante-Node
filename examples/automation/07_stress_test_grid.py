# Example: Stress test grid generation
rows, cols = 5, 5
spacing_x, spacing_y = 300, 200
scene.clear()
for r in range(rows):
    for c in range(cols):
        scene.add_node_by_name("message_node", (c * spacing_x, r * spacing_y))
print(f"Created a {rows}x{cols} grid of nodes.")
