"""
Houdini Scene Info Script
=========================
Queries the live Houdini session via the command server bridge.
Requires that Vibrante-Node was launched from the Houdini plugin.
"""
from src.utils.hou_bridge import get_bridge, is_available

print("=" * 40)
print("  Houdini Scene Info (Live)")
print("=" * 40)

if not is_available():
    print("Houdini command server not reachable.")
    print("Make sure Vibrante-Node was launched from Houdini.")
else:
    bridge = get_bridge()
    info = bridge.scene_info()
    print(f"HIP File:         {info['hip_file']}")
    print(f"HIP Name:         {info['hip_name']}")
    print(f"Houdini Version:  {info['houdini_version']}")
    print(f"FPS:              {info['fps']}")
    print(f"Current Frame:    {info['frame']}")
    print(f"Frame Range:      {info['frame_range']}")

print("=" * 40)
