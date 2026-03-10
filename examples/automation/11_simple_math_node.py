# Example: Automate building a simple math workflow
n1 = scene.add_node_by_name("add_integers", (100, 100))
n2 = scene.add_node_by_name("console_print", (400, 100))
if n1 and n2:
    n1.set_parameter('a', 10)
    n1.set_parameter('b', 20)
    scene.connect_nodes(n1, "result", n2, "data")
