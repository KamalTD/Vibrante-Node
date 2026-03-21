"""
Houdini Scene Info Script
=========================
Demonstrates using the hou module directly from within Vibrante-Node.
Requires that Vibrante-Node was launched from the Houdini plugin so
that PYTHONPATH and PATH are configured for `import hou`.
"""
import os

hip_file = os.environ.get('VIBRANTE_HIP_FILE', '(not set)')
hip_name = os.environ.get('VIBRANTE_HIP_NAME', '(not set)')
hou_version = os.environ.get('VIBRANTE_HOUDINI_VERSION', '(not set)')

print("=" * 40)
print("  Houdini Scene Info")
print("=" * 40)
print(f"HIP File:         {hip_file}")
print(f"HIP Name:         {hip_name}")
print(f"Houdini Version:  {hou_version}")
print()

# Register Houdini DLL directories (Python 3.8+ on Windows)
import sys
if sys.platform == 'win32':
    hfs = os.environ.get('HFS', '')
    if hfs:
        for _sub in ('bin', os.path.join('custom', 'houdini', 'dsolib')):
            _d = os.path.join(hfs, _sub)
            if os.path.isdir(_d):
                try:
                    os.add_dll_directory(_d)
                except (OSError, AttributeError):
                    pass

try:
    import hou
    print(f"hou module loaded: {hou.applicationVersionString()}")
    print(f"HFS: {hou.expandString('$HFS')}")
    print(f"HIP: {hou.hipFile.path()}")
except ImportError:
    print("hou module not available - ensure Vibrante-Node was launched from the Houdini plugin")
except Exception as e:
    print(f"Error querying Houdini: {e}")

print("=" * 40)
