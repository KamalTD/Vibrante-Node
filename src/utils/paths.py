"""
Runtime path resolution for both dev and PyInstaller frozen builds.

PyInstaller extracts bundled data to sys._MEIPASS (the _internal folder).
All read-only assets must be resolved through resource_path().
User-writable data (custom nodes, workflows) lives next to the exe via app_dir().
"""
import os
import sys


def _frozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def resource_path(*parts):
    """Absolute path to a read-only bundled asset (icons, docs, nodes, images)."""
    base = sys._MEIPASS if _frozen() else os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, *parts)


def app_dir():
    """
    Writable directory next to the executable.
    Use for user-created nodes, workflows, and other mutable data.
    """
    if _frozen():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
