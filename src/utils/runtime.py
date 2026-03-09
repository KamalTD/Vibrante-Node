import traceback
from typing import Dict, Any, Callable, Optional, Tuple

class SafeRuntime:
    @staticmethod
    async def run_node_safe(node_execute_fn: Callable, inputs: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Executes a node's execute function safely, catching any exceptions.
        :return: (success: bool, result: dict, error_message: str)
        """
        try:
            result = await node_execute_fn(inputs)
            return True, result, None
        except Exception as e:
            error_msg = f"Node execution failed: {str(e)}\n{traceback.format_exc()}"
            return False, None, error_msg
