from src.nodes.base import BaseNode

class ListItemPickerNode(BaseNode):
    """
    Demonstrates set_parameter for a dropdown inside on_plug_sync.

    Connect any list-producing node to the 'items' port.
    on_plug_sync fires immediately on connection and populates the
    'selection' dropdown with the list contents as string options.
    When disconnected, the dropdown resets to a placeholder.

    Usage pattern
    -------------
    1. Add a dropdown input with add_input(..., widget_type="dropdown").
    2. In on_plug_sync, read data from the other node with get_parameter().
    3. Call self.set_parameter("<dropdown_port>", [list_of_strings])
       to replace the dropdown items AND select the first one automatically.
    """

    name = "list_item_picker"

    def __init__(self):
        super().__init__(use_exec=False)
        # Data input — connect a node that outputs a list here
        self.add_input("items", "list")

        # Dropdown that will be populated dynamically on connection.
        # Start with a placeholder so the widget is visible before any connection.
        self.add_input("selection", "string", widget_type="dropdown",
                       options=["— connect a list —"])

        self.add_output("selected_item", "any")

    # ------------------------------------------------------------------
    # Connection callbacks
    # ------------------------------------------------------------------

    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        if not is_input or port_name != "items":
            return

        # Read whatever value the upstream node currently holds on its port.
        data = other_node.get_parameter(other_port_name)

        if isinstance(data, list) and data:
            # Convert every element to a string so the combo box can display it.
            str_options = [str(item) for item in data]
        else:
            # Upstream node hasn't executed yet or returned something unexpected.
            # Provide a helpful placeholder instead of leaving the dropdown empty.
            str_options = ["— run upstream node first —"]

        # set_parameter with a list on a dropdown port:
        #   • replaces the combo box items with str_options
        #   • selects the first item automatically
        #   • stores that first item as the current parameter value
        self.set_parameter("selection", str_options)
        self.log_info(f"Dropdown populated with {len(str_options)} option(s) "
                      f"from '{other_node.name}.{other_port_name}'.")

    def on_unplug_sync(self, port_name, is_input):
        if is_input and port_name == "items":
            # Reset to placeholder when the upstream node is disconnected.
            self.set_parameter("selection", ["— connect a list —"])
            self.log_info("Upstream disconnected — dropdown reset.")

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, inputs):
        items = inputs.get("items", [])
        selected = self.get_parameter("selection", "")

        # Find the item whose string representation matches the selection.
        for item in items:
            if str(item) == selected:
                return {"selected_item": item}

        # Nothing matched (e.g. upstream list changed since last connection).
        return {"selected_item": None}


def register_node():
    return ListItemPickerNode
