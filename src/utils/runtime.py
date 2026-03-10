import traceback
import asyncio
import threading
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

class AsyncRuntime:
    """Helper to run async coroutines from a synchronous context (like UI thread)."""
    _loop: Optional[asyncio.AbstractEventLoop] = None
    _thread: Optional[threading.Thread] = None
    _lock = threading.Lock()

    @classmethod
    def _start_loop(cls):
        try:
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            cls._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop)
            print("Background Async Loop Started.")
            cls._loop.run_forever()
        except Exception as e:
            print(f"CRITICAL: Failed to start background async loop: {e}")

    @classmethod
    def run_coroutine(cls, coro):
        # 1. Start thread if not exists, but DON'T WAIT for it
        if cls._thread is None or not cls._thread.is_alive():
            with cls._lock:
                if cls._thread is None or not cls._thread.is_alive():
                    cls._thread = threading.Thread(target=cls._start_loop, daemon=True)
                    cls._thread.start()

        # 2. Try to schedule, if loop isn't ready yet, it will fail silently or we can retry
        # But we MUST NOT block the UI thread here.
        if cls._loop and cls._loop.is_running():
            asyncio.run_coroutine_threadsafe(cls._wrap_coro(coro), cls._loop)
        else:
            # Loop might be starting, try again in a very short moment without blocking
            # Or just ignore this specific event to prevent freeze
            pass

    @classmethod
    async def _wrap_coro(cls, coro):
        try:
            await coro
        except Exception as e:
            print(f"Error in background coroutine: {e}")
            traceback.print_exc()
