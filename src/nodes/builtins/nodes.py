from src.nodes.base import BaseNode, NodeRegistry
from typing import Dict, Any
import os
import asyncio

class FileLoaderNode(BaseNode):
    name = "File Loader"
    category = "IO"
    icon_path = "icons/file-input.svg"
    def __init__(self):
        super().__init__()
        self.add_input("file_path", "string", widget_type="file")
        self.add_output("file_data", "string")

    async def execute(self, inputs):
        path = inputs.get("file_path")
        if not path or not os.path.exists(path):
            return {"file_data": ""}
        try:
            # Use utf-8 with fallback to ignore/replace to handle various file types safely
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
            return {"file_data": data}
        except Exception as e:
            return {"file_data": f"Error reading file: {str(e)}"}

class DataProcessorNode(BaseNode):
    name = "Data Processor"
    category = "General"
    icon_path = "icons/gear.svg"
    def __init__(self):
        super().__init__()
        self.add_input("data_in")
        self.add_output("data_out")

    async def execute(self, inputs):
        return {"data_out": f"Processed: {inputs.get('data_in')}"}

class ConsoleSinkNode(BaseNode):
    name = "Console Sink"
    category = "IO"
    icon_path = "icons/terminal.svg"
    def __init__(self):
        super().__init__()
        self.add_input("data")

    async def execute(self, inputs):
        print(f"SINK: {inputs.get('data')}")
        return {}

class SequenceNode(BaseNode):
    name = "Sequencer"
    category = "Flow"
    description = "Sequences data-only nodes. Triggers 'exec_step' for every item in the sequence."
    icon_path = "icons/list.svg"
    
    def __init__(self):
        # use_exec=False removes both default exec_in and exec_out
        super().__init__(use_exec=False)
        self.add_input("step_0", "any")
        self.add_output("result", "any")
        self.add_exec_output("exec_step") # Trigger for EACH step
        self.add_exec_output("exec_out")  # Trigger when sequence is COMPLETE
        self._step_count = 1

    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        if is_input and port_name.startswith("step_"):
            # Only increment if we actually have a node being connected (not during restoration)
            if not other_node: return
            
            idx = int(port_name.split("_")[1])
            # If we plugged into the last step, add a new empty step
            if idx == self._step_count - 1:
                self.add_input(f"step_{self._step_count}", "any")
                self._step_count += 1
                self.rebuild_ports()

    def on_unplug_sync(self, port_name, is_input):
        if is_input and port_name.startswith("step_"):
            # Shrink the list if multiple empty steps at the end
            self._cleanup_steps()

    def _cleanup_steps(self):
        """Removes trailing empty ports, ensuring exactly one empty port remains at the end."""
        changed = False
        # Ensure we always keep at least step_0
        while self._step_count > 1:
            last_port = f"step_{self._step_count - 1}"
            prev_port = f"step_{self._step_count - 2}"
            
            # If the last port is disconnected AND the one before it is ALSO disconnected,
            # we can safely remove the last one. 
            # This ensures we always have exactly ONE empty slot at the end.
            if not self.is_port_connected(last_port, is_input=True) and \
               not self.is_port_connected(prev_port, is_input=True):
                if last_port in self.inputs:
                    del self.inputs[last_port]
                    if last_port in self.parameters:
                        del self.parameters[last_port]
                    self._step_count -= 1
                    changed = True
                else: break
            else:
                break
        
        if changed:
            self.rebuild_ports()

    def restore_from_parameters(self, parameters: Dict[str, Any]):
        """Restores step_X ports from saved parameters."""
        for key in parameters:
            if key.startswith("step_"):
                try:
                    idx = int(key.split("_")[1])
                    if idx >= self._step_count:
                        for i in range(self._step_count, idx + 1):
                            port_name = f"step_{i}"
                            if port_name not in self.inputs:
                                self.add_input(port_name, "any")
                        self._step_count = idx + 1
                except (ValueError, IndexError):
                    continue

    async def execute(self, inputs):
        """
        The engine pulls upstream data nodes in the order of self.inputs keys.
        Since step_0 was added first, it will be executed first.
        We stream the results out one by one.
        """
        last_val = None
        # Get all step names sorted numerically just to be absolutely safe
        steps = sorted([k for k in self.inputs.keys() if k.startswith("step_")], 
                       key=lambda x: int(x.split("_")[1]))
        
        self.log_info(f"Starting sequence of {len(steps)} steps...")
        
        for step_name in steps:
            if self.is_stopped(): break
            
            val = inputs.get(step_name)
            if val is not None:
                last_val = val
                # STREAM: Update the output result port for EACH step
                self.log_info(f"Triggering result for {step_name}: {val}")
                await self.set_output("result", val)
                
                # TRIGGER: Force downstream full execution for this step
                await self.set_output("exec_step", True)
                
                # Small sleep to allow downstream reactive updates to process
                # Increased slightly for UI stability
                await asyncio.sleep(0.05)

        self.log_success("Sequence complete.")
        return {"result": last_val}

class SetVariableNode(BaseNode):
    name = "Set Variable"
    category = "Memory"
    icon_path = "icons/variable-set.svg"
    def __init__(self):
        super().__init__(use_exec=True)
        self.add_input("name", "string", widget_type="text", default="")
        self.add_input("value", "any")
        self.add_output("value_out", "any", default="")

    async def execute(self, inputs):
        var_name = inputs.get("name")
        var_val = inputs.get("value")
        if var_name:
            BaseNode.memory[var_name] = var_val
            self.log_success(f"Stored: {var_name} = {var_val}")
        
        await self.set_output("value_out", var_val)
        await self.set_output("exec_out", True)
        return {"value_out": var_val}

class GetVariableNode(BaseNode):
    name = "Get Variable"
    category = "Memory"
    icon_path = "icons/variable-get.svg"
    def __init__(self):
        super().__init__(use_exec=False)
        self.add_input("name", "string", widget_type="text", default="")
        self.add_output("value", "any")

    async def execute(self, inputs):
        var_name = inputs.get("name")
        var_val = BaseNode.memory.get(var_name)
        self.log_info(f"Retrieved: {var_name} = {var_val}")
        
        await self.set_output("value", var_val)
        return {"value": var_val}

    async def on_parameter_changed(self, name, value):
        if name == "name":
            var_val = BaseNode.memory.get(value)
            await self.set_output("value", var_val)

class ListAppendNode(BaseNode):
    name = "List Append"
    category = "Memory"
    description = "Manages a list in shared memory. Appends items and outputs the full list."
    icon_path = "icons/list-plus.svg"
    
    def __init__(self):
        super().__init__(use_exec=True)
        self.add_input("list_name", "string", widget_type="text")
        self.add_input("item", "any")
        self.add_output("current_list", "list")

    async def execute(self, inputs):
        name = inputs.get("list_name")
        item = inputs.get("item")
        
        if not name:
            return {"current_list": []}
            
        # Initialize list if doesn't exist
        if name not in BaseNode.memory or not isinstance(BaseNode.memory[name], list):
            BaseNode.memory[name] = []
            
        if item is not None:
            BaseNode.memory[name].append(item)
            self.log_info(f"Appended to '{name}': {item}")
            
        full_list = BaseNode.memory[name]
        await self.set_output("current_list", full_list)
        await self.set_output("exec_out", True)
        
        return {"current_list": full_list}

class TwoWaySwitchNode(BaseNode):
    name = "Two Way Switch"
    category = "Logic"
    description = "Switches between input_1 and input_2 based on a condition."
    icon_path = "icons/shuffle.svg"
    
    def __init__(self):
        super().__init__(use_exec=True)
        self.add_input("condition", "bool", widget_type="bool")
        self.add_input("input_1", "any")
        self.add_input("input_2", "any")
        self.add_output("output", "any")

    async def execute(self, inputs):
        cond = bool(inputs.get("condition", False))
        val1 = inputs.get("input_1")
        val2 = inputs.get("input_2")
        
        result = val1 if cond else val2
        
        self.log_info(f"Switch: condition={cond}, result={result}")
        await self.set_output("output", result)
        await self.set_output("exec_out", True)
        
        return {"output": result}

    async def on_parameter_changed(self, name, value):
        if name in ["condition", "input_1", "input_2"]:
            cond = bool(self.get_parameter("condition", False))
            val1 = self.get_parameter("input_1")
            val2 = self.get_parameter("input_2")
            result = val1 if cond else val2
            await self.set_output("output", result)

class ForEachNode(BaseNode):
    name = "For Each"
    category = "Flow"
    description = "Iterates over a collection. Triggers 'each_item' for every item. Can be stopped via 'break_condition' or skipped via 'continue_condition'."
    icon_path = "icons/repeat.svg"
    
    def __init__(self):
        super().__init__(use_exec=True)
        # Rename default exec_out to finished for clarity
        if "exec_out" in self.outputs:
            del self.outputs["exec_out"]
        
        self.add_input("collection", "any")
        self.add_input("break_condition", "bool", widget_type="bool")
        self.add_input("continue_condition", "bool", widget_type="bool")
        
        self.add_exec_output("each_item") # Trigger for EACH item
        self.add_exec_output("exec_skip") # Trigger if item is skipped
        self.add_exec_output("exec_on_finished") # FINAL trigger when loop is over
        
        self.add_output("completed", "bool") # True if finished normally
        self.add_output("broken", "bool")    # True if broken early
        
        self.add_output("current_item", "any")
        self.add_output("current_index", "int")
        self.add_output("indices", "list")

    async def execute(self, inputs):
        # RESET conditions at start
        self.parameters['break_condition'] = False
        self.parameters['continue_condition'] = False
        await self.set_output("completed", False)
        await self.set_output("broken", False)

        collection = inputs.get("collection")
        if not collection:
            self.log_info("Empty collection, skipping loop.")
            await self.set_output("completed", True)
            await self.set_output("exec_on_finished", True)
            return {"indices": [], "completed": True, "broken": False}
            
        try:
            items = list(collection)
        except TypeError:
            self.log_error(f"Input is not iterable: {type(collection)}")
            await self.set_output("completed", True)
            await self.set_output("exec_on_finished", True)
            return {"indices": [], "completed": True, "broken": False}
            
        indices = list(range(len(items)))
        await self.set_output("indices", indices)
        
        self.log_info(f"Starting loop over {len(items)} items...")
        
        is_broken = False
        for i, item in enumerate(items):
            if self.is_stopped(): break
            
            # Reset conditions for this specific iteration BEFORE updating data
            self.parameters['continue_condition'] = False
            self.parameters['break_condition'] = False

            # 1. Update data outputs FIRST
            # This allows reactive nodes to evaluate the NEW item before we trigger execution
            await self.set_output("current_item", item)
            await self.set_output("current_index", i)
            
            # 2. Yield to allow reactive updates from downstream to propagate back to our parameters
            await asyncio.sleep(0.1)
            
            # 3. Check for PRE-EXECUTION continue (skip)
            cont_cond = bool(self.get_parameter("continue_condition", False))
            if cont_cond:
                self.log_info(f"Skipping index {i} ({item}) - Pre-trigger")
                await self.set_output("exec_skip", True)
                continue

            # 4. Trigger iteration pin (Flow execution)
            await self.set_output("each_item", True)
            
            # 5. Yield again to allow flow-based logic to potentially set conditions for the NEXT item
            # or to check break_condition after this item's execution.
            await asyncio.sleep(0.05)

            # 6. Check for break
            if bool(self.get_parameter("break_condition", False)):
                self.log_info(f"Loop broken at index {i}")
                is_broken = True
                break
            
        if is_broken:
            await self.set_output("broken", True)
        else:
            self.log_success("Loop complete.")
            await self.set_output("completed", True)
            
        await self.set_output("exec_on_finished", True)
        return {"indices": indices, "completed": not is_broken, "broken": is_broken}

class WhileLoopNode(BaseNode):
    name = "While Loop"
    category = "Flow"
    description = "Executes while `condition` is true. Triggers 'each_iteration' for every iteration. Can be stopped via 'break_condition' or skipped via 'continue_condition'."
    icon_path = "icons/repeat.svg"

    def __init__(self):
        super().__init__(use_exec=True)
        # Remove default exec_out for clearer pins
        if "exec_out" in self.outputs:
            del self.outputs["exec_out"]

        self.add_input("condition", "bool", widget_type="bool")
        self.add_input("break_condition", "bool", widget_type="bool")
        self.add_input("continue_condition", "bool", widget_type="bool")
        self.add_input("max_iterations", "int", widget_type="int", default=1000)

        self.add_exec_output("each_iteration")
        self.add_exec_output("exec_skip")
        self.add_exec_output("exec_on_finished")

        self.add_output("completed", "bool")
        self.add_output("broken", "bool")
        self.add_output("current_index", "int")

    async def execute(self, inputs):
        # Reset control flags
        self.parameters['break_condition'] = False
        self.parameters['continue_condition'] = False
        await self.set_output("completed", False)
        await self.set_output("broken", False)

        try:
            max_it = int(inputs.get("max_iterations", 1000))
        except Exception:
            max_it = 1000

        # Initial condition: prefer parameter if present, else input
        cond = bool(self.get_parameter("condition", inputs.get("condition", False)))

        i = 0
        is_broken = False

        self.log_info(f"Starting while-loop with max_iterations={max_it}")

        while cond and not self.is_stopped() and i < max_it:
            # Reset iteration-level control flags
            self.parameters['continue_condition'] = False
            self.parameters['break_condition'] = False

            # Publish current index first so downstream nodes can react
            await self.set_output("current_index", i)

            # Yield for reactive updates
            await asyncio.sleep(0.1)

            # Check for continue (skip this iteration)
            if bool(self.get_parameter("continue_condition", False)):
                self.log_info(f"Skipping iteration {i} - Pre-trigger")
                await self.set_output("exec_skip", True)
                i += 1
                # Re-evaluate condition (allow downstream to change it via parameters)
                cond = bool(self.get_parameter("condition", inputs.get("condition", False)))
                continue

            # Trigger iteration flow
            await self.set_output("each_iteration", True)

            # Small yield to allow flow-triggered nodes to run and potentially set break
            await asyncio.sleep(0.05)

            # Check for break
            if bool(self.get_parameter("break_condition", False)):
                self.log_info(f"Loop broken at iteration {i}")
                is_broken = True
                break

            i += 1
            # Re-evaluate condition for next loop
            cond = bool(self.get_parameter("condition", inputs.get("condition", False)))

        if is_broken:
            await self.set_output("broken", True)
        else:
            await self.set_output("completed", True)

        await self.set_output("exec_on_finished", True)
        return {"completed": not is_broken, "broken": is_broken, "current_index": i}

def register_builtins():
    NodeRegistry.register(FileLoaderNode)
    NodeRegistry.register(DataProcessorNode)
    NodeRegistry.register(ConsoleSinkNode)
    NodeRegistry.register(SequenceNode)
    NodeRegistry.register(SetVariableNode)
    NodeRegistry.register(GetVariableNode)
    NodeRegistry.register(TwoWaySwitchNode)
    NodeRegistry.register(ForEachNode)
