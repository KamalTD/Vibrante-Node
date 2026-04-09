"""
Vibrante-Node Houdini startup script.
Automatically runs when Houdini starts with the Vibrante-Node package installed.

Note: The Vibrante-Node plugin uses direct `import hou` via PYTHONPATH/PATH
configuration. No RPyC server is required.
"""

import os
import sys

# Add the bundled venv site-packages (pydantic, google-generativeai, etc.).
# This venv intentionally has NO Qt packages to avoid conflicts with
# Houdini's built-in PySide2/shiboken2.  Never add the system Python's
# site-packages here — it contains PyQt5/PySide6 which cause segfaults.
_app_root = os.environ.get("VIBRANTE_NODE_APP", "")
if _app_root:
    _venv_sp = os.path.join(
        _app_root, "plugins", "houdini", "houdini",
        "scripts", "python", "env", "Lib", "site-packages"
    )
    if os.path.isdir(_venv_sp) and _venv_sp not in sys.path:
        sys.path.append(_venv_sp)

print("[Vibrante-Node] Plugin loaded. Use the Vibrante-Node menu or shelf to launch.")
