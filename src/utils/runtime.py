import traceback
import asyncio
import threading
import sys
import time
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
    _ready = threading.Event()

    @classmethod
    def _start_loop(cls):
        try:
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            cls._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop)
            print("Background Async Loop Started.")
            cls._ready.set()
            cls._loop.run_forever()
        except Exception as e:
            print(f"CRITICAL: Failed to start background async loop: {e}")

    @classmethod
    def run_coroutine(cls, coro):
        # 1. Start thread if not exists
        if cls._thread is None or not cls._thread.is_alive():
            with cls._lock:
                if cls._thread is None or not cls._thread.is_alive():
                    cls._ready.clear()
                    cls._thread = threading.Thread(target=cls._start_loop, daemon=True)
                    cls._thread.start()

        # 2. Try to schedule
        def schedule():
            # Wait a tiny bit for loop if it was JUST started, but don't block UI indefinitely
            if not cls._ready.wait(timeout=0.5):
                print("Warning: Async loop not ready in time, dropping coroutine.")
                return

            if cls._loop and cls._loop.is_running():
                asyncio.run_coroutine_threadsafe(cls._wrap_coro(coro), cls._loop)
            else:
                print("Warning: Async loop not running, dropping coroutine.")

        # If we are in the main thread (UI), we shouldn't block even for 0.5s if possible, 
        # but for node events like plug/unplug, a small delay is usually okay or we can thread it.
        # Let's run the scheduler in a separate fire-and-forget thread to be 100% safe for UI.
        threading.Thread(target=schedule, daemon=True).start()

    @classmethod
    async def _wrap_coro(cls, coro):
        try:
            if asyncio.iscoroutine(coro):
                await coro
            else:
                # If it's not a coroutine (maybe it was a sync call mistakenly passed), just return
                pass
        except Exception as e:
            print(f"Error in background coroutine: {e}")
            traceback.print_exc()
