"""
Vibrante-Node Houdini startup script.
Automatically runs when Houdini starts with the Vibrante-Node package installed.

Note: The Vibrante-Node plugin uses direct `import hou` via PYTHONPATH/PATH
configuration. No RPyC server is required.
"""

print("[Vibrante-Node] Plugin loaded. Use the Vibrante-Node menu or shelf to launch.")
