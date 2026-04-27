from src.nodes.base import BaseNode

class DropdownSelectorNode(BaseNode):
    name = "Dropdown Selector"
    category = "Examples"
    description = "Demonstrates a dropdown widget. Returns the selected item on execute and reactively on change."

    def __init__(self):
        super().__init__(use_exec=False)
        self.add_input(
            "selection",
            "string",
            widget_type="dropdown",
            options=["Option A", "Option B", "Option C"],
            default="Option A",
        )
        self.add_output("selected_item", "string")

    async def execute(self, inputs):
        selected = inputs.get("selection", "")
        self.log_info(f"Selected: {selected}")
        return {"selected_item": selected}

    async def on_parameter_changed(self, name, value):
        if name == "selection":
            await self.set_output("selected_item", value)

def register_node():
    return DropdownSelectorNode
