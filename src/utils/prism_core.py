import os
import sys
from src.nodes.base import BaseNode
from src.utils.qt_compat import ensure_qcolor_from_string, ensure_shiboken_stub


PRISM_CORE_MEMORY_KEY = "_prism_core"
_CACHED_PRISM_CORE = None


def store_prism_core(core):
    """Persist the active PrismCore for the current workflow run."""
    global _CACHED_PRISM_CORE
    if core is not None:
        _CACHED_PRISM_CORE = core
        BaseNode.memory[PRISM_CORE_MEMORY_KEY] = core
    return core


def resolve_prism_core(inputs=None):
    """
    Resolve PrismCore from:
    1. Explicit node input
    2. Shared workflow memory
    3. A live DCC session (__main__.pcore)
    """
    if isinstance(inputs, dict):
        core = inputs.get("core")
        if core is not None:
            return store_prism_core(core)

    core = BaseNode.memory.get(PRISM_CORE_MEMORY_KEY)
    if core is not None:
        return core

    global _CACHED_PRISM_CORE
    if _CACHED_PRISM_CORE is not None:
        BaseNode.memory[PRISM_CORE_MEMORY_KEY] = _CACHED_PRISM_CORE
        return _CACHED_PRISM_CORE

    try:
        import __main__

        core = getattr(__main__, "pcore", None)
        if core is not None:
            return store_prism_core(core)
    except Exception:
        pass

    return None


def bootstrap_prism_core(prism_scripts_path="C:/Program Files/Prism2/Scripts", load_project=True, show_ui=False):
    """
    Synchronously initialize PrismCore on the current thread and cache it.
    Use this only from the Qt main thread.
    """
    core = resolve_prism_core()
    if core is not None:
        return core

    if prism_scripts_path and os.path.isdir(prism_scripts_path) and prism_scripts_path not in sys.path:
        sys.path.append(prism_scripts_path)

    ensure_qcolor_from_string()
    ensure_shiboken_stub()
    import PrismCore

    args = []
    if not show_ui:
        args.append("noUI")
    if load_project:
        args.append("loadProject")

    if show_ui:
        core = PrismCore.show(prismArgs=args)
    else:
        core = PrismCore.create(prismArgs=args)

    return store_prism_core(core)
