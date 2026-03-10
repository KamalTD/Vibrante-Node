# Vibrante-Node: Automation API Reference

The **Scripting Console** (Window -> Show/Hide Scripting Console) allows you to control the entire application using Python. This guide covers all available objects, methods, and practical automation scenarios.

---

## 🌍 Global Objects

When writing scripts in the console, the following objects are pre-loaded into your namespace:

| Object | Type | Description |
| :--- | :--- | :--- |
| `app` | `MainWindow` | Control high-level app features (Tabs, Execution, Themes). |
| `scene` | `NodeScene` | Manipulate the active canvas (Nodes, Wires, Clearing). |
| `registry` | `NodeRegistry` | Access the database of all available node types. |
| `git` | `GitWrapper` | Manage project source control from the script. |
| `print()` | `Function` | Redirects output to both the Console and the Event Log. |

---

## 🛠️ Methods Reference

### 🔹 Scene Manipulation (`scene`)
- **`scene.add_node_by_name(node_id, pos)`**: 
  - `node_id`: String (e.g., `"math_add"`).
  - `pos`: Tuple `(x, y)`.
  - *Returns*: `NodeWidget` object.
- **`scene.connect_nodes(node_a, port_a, node_b, port_b)`**: 
  - `node_a`/`node_b`: Can be `NodeWidget` objects OR their names as strings.
- **`scene.find_node_by_name(name)`**: Returns the first node matching the display name.
- **`scene.clear()`**: Deletes everything from the current tab.

### 🔹 Node Control (`node`)
- **`node.set_parameter(name, value)`**: 
  - Updates a widget value programmatically.
  - Automatically triggers downstream data propagation.
- **`node.node_definition`**: Access the underlying Python logic instance.

### 🔹 Application Control (`app`)
- **`app.add_new_workflow(name)`**: Opens a new empty tab.
- **`app.execute_pipeline()`**: Starts the execution engine for the current tab.
- **`app.save_workflow()`**: Triggers the save dialog or smart-saves if a path exists.

---

## 📖 Practical Automation Scenarios

### 1. The Multiplier Grid (Stress Test)
Generate a 5x5 grid of nodes and chain them all together.

```python
scene.clear()
prev = None
for i in range(5):
    for j in range(5):
        curr = scene.add_node_by_name("message_node", (j*300, i*200))
        curr.set_parameter("msg", f"Link {i}-{j}")
        if prev:
            scene.connect_nodes(prev, "out", curr, "msg")
        prev = curr
print("Chained 25 nodes successfully.")
```

### 2. Batch Data Processing
Update a node's input multiple times and run the workflow for each value.

```python
loader = scene.find_node_by_name("Message Node")
if loader:
    data_list = ["Record_01", "Record_02", "Record_03"]
    for item in data_list:
        loader.set_parameter("msg", item)
        app.execute_pipeline()
        # Execution is async; the log will show results sequentially
```

### 3. Workflow Cleanup & Reset
Find all nodes of a certain type and reset their values.

```python
for node in scene.nodes:
    if node.node_definition.name == "Math Adder":
        node.set_parameter("val_a", 0)
        node.set_parameter("val_b", 0)
print("All math nodes reset to zero.")
```

### 4. Git Integration Workflow
Automate your backup after a successful build.

```python
git.status()
git.commit("Automated workflow backup")
git.push()
print("Workflow pushed to GitHub successfully.")
```
