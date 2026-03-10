# Example: Sequentially update an input and run the pipeline
target_node = scene.find_node_by_name("Message Node")
if target_node:
    for i in range(1, 6):
        target_node.set_parameter("msg", f"Processing Batch {i}")
        app.execute_pipeline()
        print(f"Triggered execution for batch {i}")
else:
    print("Error: 'Message Node' not found in scene.")
