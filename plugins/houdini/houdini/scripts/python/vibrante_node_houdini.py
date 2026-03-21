"""
Vibrante-Node Houdini Integration Module
=========================================
Provides functions to launch and integrate Vibrante-Node Pipeline Editor
with SideFX Houdini. This module is automatically importable inside Houdini
when the Vibrante-Node package is installed.

Architecture (Direct hou import):
    Since Python 3.11 is shared between Houdini 20.5 and the system install,
    Vibrante-Node can import the hou module directly without an RPyC bridge.
    The setup_env() function adds Houdini's Python libs and $HFS/bin to the
    environment so that `import hou` works in the Vibrante-Node subprocess.

Functions:
    launch()                      - Launch Vibrante-Node with Houdini Python on PYTHONPATH
    launch_with_context()         - Launch with current HIP file context
    get_houdini_python_path()     - Discover Houdini's Python site-packages path
    setup_env()                   - Build environment dict for subprocess launch
    open_houdini_scripts_folder() - Open the Houdini-specific scripts directory
    open_houdini_nodes_folder()   - Open the Houdini-specific nodes directory
    show_about()                  - Show about dialog
"""

import os
import sys
import glob
import subprocess
import platform


def get_app_root():
    """Return the Vibrante-Node application root directory.

    Resolution order:
    1. VIBRANTE_NODE_APP environment variable (set by package JSON)
    2. Computed from this file's location (plugins/houdini/houdini/scripts/python/)
    """
    env_root = os.environ.get("VIBRANTE_NODE_APP", "")
    if env_root and os.path.isdir(env_root):
        return os.path.normpath(env_root)

    # Fallback: this file is at plugins/houdini/houdini/scripts/python/
    # App root is 5 levels up
    this_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.normpath(os.path.join(this_dir, "..", "..", "..", "..", ".."))
    if os.path.isfile(os.path.join(app_root, "src", "main.py")):
        return app_root

    return ""


def get_houdini_python_path():
    """Discover and return Houdini's Python site-packages directory.

    Houdini ships its own Python installation. The hou module and other
    Houdini Python packages live in a version-specific directory under $HFS.
    Common locations:
        - $HFS/python3.11libs    (Houdini 20.5+)
        - $HFS/python3.10libs    (Houdini 20.0)
        - $HFS/python3.9libs     (Houdini 19.5)
        - $HFS/houdini/python3.Xlibs  (some builds)

    Returns:
        str: Path to Houdini's Python packages directory, or empty string.
    """
    try:
        import hou
        hfs = hou.expandString("$HFS")
    except ImportError:
        hfs = os.environ.get("HFS", "")

    if not hfs:
        return ""

    candidates = []

    # Direct children of $HFS
    for entry in glob.glob(os.path.join(hfs, "python3.*libs")):
        if os.path.isdir(entry):
            candidates.append(entry)

    # Under $HFS/houdini/
    for entry in glob.glob(os.path.join(hfs, "houdini", "python3.*libs")):
        if os.path.isdir(entry):
            candidates.append(entry)

    if not candidates:
        return ""

    # Prefer the highest Python version
    candidates.sort(reverse=True)
    return candidates[0]


def _get_houdini_scripts_dir():
    """Return the path to Houdini-specific scripts inside the plugin."""
    app_root = get_app_root()
    if not app_root:
        return ""
    return os.path.join(app_root, "plugins", "houdini", "v_scripts_houdini")


def _get_houdini_nodes_dir():
    """Return the path to Houdini-specific nodes inside the plugin."""
    app_root = get_app_root()
    if not app_root:
        return ""
    return os.path.join(app_root, "plugins", "houdini", "v_nodes_houdini")


def setup_env(hip_file="", extra_env=None):
    """Build a complete environment dictionary for launching Vibrante-Node.

    Ensures:
    1. PYTHONPATH includes Houdini's Python packages (so import hou works)
    2. PATH includes $HFS/bin (so _hou.pyd / DLLs can be loaded)
    3. v_scripts_path includes Houdini-specific scripts
    4. v_nodes_dir includes Houdini-specific node definitions
    5. VIBRANTE_NODE_APP is set
    6. HIP context variables are passed when applicable

    Args:
        hip_file: Path to current .hip file (empty string if unsaved)
        extra_env: Additional environment variables dict to merge

    Returns:
        dict: Environment dictionary for subprocess.Popen
    """
    env = os.environ.copy()

    # Strip Houdini-specific Python variables that interfere with system Python.
    # Houdini sets PYTHONHOME/PYTHONSTARTUP pointing to its own Python install;
    # if left in place, the system Python cannot find its own standard library.
    for key in ("PYTHONHOME", "PYTHONSTARTUP"):
        env.pop(key, None)

    app_root = get_app_root()
    if app_root:
        env["VIBRANTE_NODE_APP"] = app_root

    # 1. PYTHONPATH -- add Houdini's Python packages so `import hou` works directly
    hou_python = get_houdini_python_path()
    existing_pythonpath = env.get("PYTHONPATH", "")
    pythonpath_parts = [p for p in existing_pythonpath.split(os.pathsep) if p.strip()]

    if hou_python and hou_python not in pythonpath_parts:
        pythonpath_parts.insert(0, hou_python)

    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    # 1b. PATH -- add $HFS/bin so the system Python can load Houdini's
    #     compiled modules (_hou.pyd / _hou.so) and their DLL dependencies.
    try:
        import hou
        hfs = hou.expandString("$HFS")
    except ImportError:
        hfs = os.environ.get("HFS", "")

    if hfs:
        hfs_bin = os.path.join(hfs, "bin")
        existing_path = env.get("PATH", "")
        if hfs_bin not in existing_path:
            env["PATH"] = hfs_bin + os.pathsep + existing_path
        # Preserve HFS so hou module can find Houdini resources
        env["HFS"] = hfs

    # 2. v_scripts_path -- add Houdini-specific scripts directory
    hou_scripts = _get_houdini_scripts_dir()
    if hou_scripts:
        existing_scripts = env.get("v_scripts_path", "")
        if existing_scripts:
            env["v_scripts_path"] = existing_scripts + os.pathsep + hou_scripts
        else:
            env["v_scripts_path"] = hou_scripts

    # 3. v_nodes_dir -- add Houdini-specific nodes directory
    hou_nodes = _get_houdini_nodes_dir()
    if hou_nodes:
        existing_nodes = env.get("v_nodes_dir", "")
        if existing_nodes:
            env["v_nodes_dir"] = existing_nodes + os.pathsep + hou_nodes
        else:
            env["v_nodes_dir"] = hou_nodes

    # 4. Mark that we are running in Houdini integration mode (direct hou import)
    env["VIBRANTE_HOUDINI_MODE"] = "direct"

    # 5. HIP Context
    if hip_file:
        env["VIBRANTE_HIP_FILE"] = hip_file
        env["VIBRANTE_HIP_NAME"] = os.path.splitext(os.path.basename(hip_file))[0]

    # 6. Houdini version info
    try:
        import hou
        env["VIBRANTE_HOUDINI_VERSION"] = ".".join(str(x) for x in hou.applicationVersion())
        env["VIBRANTE_HOUDINI_BUILD"] = str(hou.applicationVersionString())
    except ImportError:
        pass

    if extra_env:
        env.update(extra_env)

    return env


def _find_system_python():
    """Locate system Python 3.11 that has PyQt5 installed.

    Since Houdini 20.5 uses Python 3.11, the system Python must also be 3.11
    to ensure ABI compatibility when importing the hou module directly.

    Resolution order:
    1. VIBRANTE_PYTHON_EXE environment variable (user override)
    2. Windows Registry (most reliable -- works regardless of PATH)
    3. Windows Python Launcher (py -3.11)
    4. Scan common Windows install paths (python.exe and python*.exe)
    5. Probe common Python names on PATH

    Returns:
        str: Path to Python executable with PyQt5, or empty string.
    """
    # 1. User override -- trust it unconditionally if the file exists.
    # Houdini's environment can interfere with the PyQt5 import test even after
    # stripping PYTHONHOME, causing a valid explicit override to be silently skipped.
    user_python = os.environ.get("VIBRANTE_PYTHON_EXE", "")
    if user_python and os.path.isfile(user_python):
        return user_python

    create_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
    clean_env = _clean_env_for_test()

    # 2. Windows Registry -- find all installed Python versions
    if platform.system() == "Windows":
        found = _find_python_from_registry()
        if found:
            return found

    # 3. Windows Python Launcher (py -3.11)
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["py", "-3.11", "-c", "import PyQt5; import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=10,
                creationflags=create_flags,
                env=clean_env,
            )
            if result.returncode == 0 and result.stdout.strip():
                exe = result.stdout.strip()
                if os.path.isfile(exe):
                    return exe
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    # 4. Scan common Windows install paths (any python*.exe)
    if platform.system() == "Windows":
        search_roots = []
        local_app = os.environ.get("LOCALAPPDATA", "")
        if local_app:
            search_roots.append(os.path.join(local_app, "Programs", "Python"))
        for drive in ("C:", "D:"):
            search_roots.append(drive + "\\")
            search_roots.append(drive + "\\Program Files")

        for root in search_roots:
            if not os.path.isdir(root):
                continue
            for entry in sorted(os.listdir(root), reverse=True):
                if not entry.lower().startswith("python"):
                    continue
                dir_path = os.path.join(root, entry)
                if not os.path.isdir(dir_path):
                    continue
                # Try any python*.exe in this directory
                for exe_name in sorted(glob.glob(os.path.join(dir_path, "python*.exe")), reverse=True):
                    if _test_pyqt5(exe_name):
                        return exe_name

    # 5. Probe common names on PATH
    names = ("python", "python3", "python311", "python3.11")
    for name in names:
        try:
            result = subprocess.run(
                [name, "-c", "import PyQt5; import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=10,
                creationflags=create_flags,
                env=clean_env,
            )
            if result.returncode == 0 and result.stdout.strip():
                exe = result.stdout.strip()
                if os.path.isfile(exe):
                    return exe
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    return ""


def _find_python_from_registry():
    """Search the Windows Registry for installed Python interpreters.

    Checks both HKLM and HKCU under SOFTWARE\\Python\\PythonCore\\
    for InstallPath entries. Tests each found python.exe for PyQt5.

    Returns:
        str: Path to a Python executable with PyQt5, or empty string.
    """
    if platform.system() != "Windows":
        return ""

    import winreg

    candidates = []

    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for view in (winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
                     winreg.KEY_READ | winreg.KEY_WOW64_32KEY):
            try:
                core_key = winreg.OpenKey(hive, r"SOFTWARE\Python\PythonCore", 0, view)
            except OSError:
                continue

            try:
                i = 0
                while True:
                    try:
                        version = winreg.EnumKey(core_key, i)
                        i += 1
                    except OSError:
                        break

                    try:
                        path_key = winreg.OpenKey(
                            hive,
                            rf"SOFTWARE\Python\PythonCore\{version}\InstallPath",
                            0, view
                        )
                        install_path, _ = winreg.QueryValueEx(path_key, "")
                        winreg.CloseKey(path_key)

                        if install_path and os.path.isdir(install_path):
                            # Find any python*.exe in the install directory
                            for exe in glob.glob(os.path.join(install_path, "python*.exe")):
                                if os.path.isfile(exe):
                                    candidates.append(exe)
                    except OSError:
                        pass
            finally:
                winreg.CloseKey(core_key)

    # Test candidates for PyQt5 (prefer higher versions first)
    candidates.sort(reverse=True)
    for exe in candidates:
        if _test_pyqt5(exe):
            return exe

    return ""


def _clean_env_for_test():
    """Create a clean environment for testing system Python.

    Houdini sets PYTHONHOME, PYTHONPATH, etc. pointing to its own Python.
    These interfere with system Python, so we strip them out.
    """
    env = os.environ.copy()
    for key in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP"):
        env.pop(key, None)
    return env


def _test_pyqt5(python_exe):
    """Test whether a Python executable can import PyQt5."""
    try:
        create_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        env = _clean_env_for_test()
        result = subprocess.run(
            [python_exe, "-c", "import PyQt5; print('ok')"],
            capture_output=True, text=True, timeout=10,
            creationflags=create_flags,
            env=env,
        )
        return result.returncode == 0 and "ok" in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def launch(extra_env=None):
    """Launch Vibrante-Node as a subprocess with Houdini Python on PYTHONPATH.

    The application is started as an independent process. Closing Houdini
    will NOT close Vibrante-Node and vice-versa.

    Architecture: Vibrante-Node uses direct `import hou` (no RPyC server needed).
    The hou module is available because Houdini's Python libs and $HFS/bin are
    added to PYTHONPATH and PATH respectively.

    Args:
        extra_env: Additional environment variables to pass
    """
    app_root = get_app_root()
    if not app_root:
        _show_error(
            "Cannot find Vibrante-Node installation.\n\n"
            "Please set VIBRANTE_NODE_APP in vibrante_node.json\n"
            "to the correct path."
        )
        return

    main_script = os.path.join(app_root, "src", "main.py")
    if not os.path.isfile(main_script):
        _show_error(f"Cannot find src/main.py at:\n{app_root}")
        return

    env = setup_env(extra_env=extra_env)

    # Find system Python with PyQt5 (Houdini's Python doesn't have PyQt5)
    python_exe = _find_system_python()
    if not python_exe:
        _show_error(
            "Cannot find a Python 3.11 installation with PyQt5.\n\n"
            "Please install PyQt5 in your system Python 3.11:\n"
            "  pip install PyQt5\n\n"
            "Or set VIBRANTE_PYTHON_EXE to the correct Python path."
        )
        return

    # Log key environment variables for debugging
    print(f"[Vibrante-Node] Python: {python_exe}")
    print(f"[Vibrante-Node] PYTHONPATH: {env.get('PYTHONPATH', '')}")
    print(f"[Vibrante-Node] HFS: {env.get('HFS', '(not set)')}")
    print(f"[Vibrante-Node] Mode: direct hou import (no RPyC)")
    print(f"[Vibrante-Node] PATH (first 3): {os.pathsep.join(env.get('PATH', '').split(os.pathsep)[:3])}")

    try:
        create_flags = subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        proc = subprocess.Popen(
            [python_exe, main_script],
            cwd=app_root,
            env=env,
            creationflags=create_flags,
        )

        _show_status(f"Vibrante-Node launched (PID: {proc.pid})")

    except Exception as e:
        _show_error(f"Failed to launch Vibrante-Node:\n{str(e)}")


def launch_with_context():
    """Launch Vibrante-Node with the current HIP file context.

    Passes the current .hip file path and Houdini version as environment
    variables. Inside Vibrante-Node scripts, these are accessible via:
        os.environ.get('VIBRANTE_HIP_FILE')
        os.environ.get('VIBRANTE_HIP_NAME')
        os.environ.get('VIBRANTE_HOUDINI_VERSION')
    """
    try:
        import hou
        hip_file = hou.hipFile.path()
    except ImportError:
        hip_file = ""

    env = setup_env(hip_file=hip_file)
    launch(extra_env=env)


def launch_inprocess():
    """Launch Vibrante-Node inside Houdini's Python process (PySide2 UI).

    This runs the full Vibrante-Node application inside Houdini, using
    Houdini's PySide2 for the UI instead of PyQt5. The hou module is
    available directly with live session access (no .hip save needed).

    Call from Houdini's Python Shell:
        import vibrante_node_houdini
        vibrante_node_houdini.launch_inprocess()
    """
    app_root = get_app_root()
    if not app_root:
        _show_error(
            "Cannot find Vibrante-Node installation.\n\n"
            "Please set VIBRANTE_NODE_APP in vibrante_node.json\n"
            "to the correct path."
        )
        return

    # Add app root to sys.path so imports work
    if app_root not in sys.path:
        sys.path.insert(0, app_root)

    # Set environment variables for Houdini integration
    os.environ["VIBRANTE_NODE_APP"] = app_root
    os.environ["VIBRANTE_HOUDINI_MODE"] = "direct"

    # Add Houdini scripts and nodes dirs
    hou_scripts = _get_houdini_scripts_dir()
    if hou_scripts:
        existing = os.environ.get("v_scripts_path", "")
        if existing:
            os.environ["v_scripts_path"] = existing + os.pathsep + hou_scripts
        else:
            os.environ["v_scripts_path"] = hou_scripts

    hou_nodes = _get_houdini_nodes_dir()
    if hou_nodes:
        existing = os.environ.get("v_nodes_dir", "")
        if existing:
            os.environ["v_nodes_dir"] = existing + os.pathsep + hou_nodes
        else:
            os.environ["v_nodes_dir"] = hou_nodes

    # Set HIP context
    try:
        import hou
        hip_file = hou.hipFile.path()
        os.environ["VIBRANTE_HIP_FILE"] = hip_file
        os.environ["VIBRANTE_HIP_NAME"] = os.path.splitext(os.path.basename(hip_file))[0]
        os.environ["VIBRANTE_HOUDINI_VERSION"] = ".".join(str(x) for x in hou.applicationVersion())
        os.environ["VIBRANTE_HOUDINI_BUILD"] = str(hou.applicationVersionString())
    except ImportError:
        pass

    print(f"[Vibrante-Node] Launching in-process from: {app_root}")
    print(f"[Vibrante-Node] Mode: in-process (PySide2, live hou session)")

    try:
        from src.ui.window import MainWindow

        # Use Houdini's existing QApplication (don't create a new one)
        from PySide2 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app is None:
            # This shouldn't happen inside Houdini, but just in case
            app = QtWidgets.QApplication(sys.argv)

        window = MainWindow()
        window.setWindowTitle("Vibrante-Node [Houdini Live Session]")
        window.show()

        _show_status("Vibrante-Node launched in-process")

    except Exception as e:
        _show_error(f"Failed to launch Vibrante-Node in-process:\n{str(e)}")


def open_houdini_scripts_folder():
    """Open the Houdini-specific scripts directory in the file manager.

    Creates the directory if it does not exist. Users can place .py scripts
    here that will appear in Vibrante-Node's Scripts menu when launched
    from Houdini.
    """
    scripts_dir = _get_houdini_scripts_dir()
    if not scripts_dir:
        _show_error("Cannot determine Vibrante-Node app root.")
        return

    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)

    _open_folder(scripts_dir)


def open_houdini_nodes_folder():
    """Open the Houdini-specific nodes directory in the file manager.

    Creates the directory if it does not exist. Users can place node
    definition .json files here that will appear in Vibrante-Node's
    Library panel when launched from Houdini.
    """
    nodes_dir = _get_houdini_nodes_dir()
    if not nodes_dir:
        _show_error("Cannot determine Vibrante-Node app root.")
        return

    if not os.path.exists(nodes_dir):
        os.makedirs(nodes_dir)

    _open_folder(nodes_dir)


def show_about():
    """Show an about dialog for the Vibrante-Node Houdini integration."""
    app_root = get_app_root()
    hou_python = get_houdini_python_path()
    sys_python = _find_system_python()

    try:
        import hou
        hou_ver = hou.applicationVersionString()
    except ImportError:
        hou_ver = "(not available)"

    msg = (
        "Vibrante-Node Pipeline Editor - Houdini Integration\n"
        "====================================================\n\n"
        f"App Root:            {app_root or '(not found)'}\n"
        f"Houdini Version:     {hou_ver}\n"
        f"Houdini Python Libs: {hou_python or '(not found)'}\n"
        f"System Python:       {sys_python or '(not found)'}\n\n"
        "Architecture:\n"
        "  Vibrante-Node runs in system Python 3.11 (with PyQt5).\n"
        "  Houdini nodes use direct `import hou` to access Houdini's API.\n"
        "  No RPyC server or pythonrc.py startup is required.\n"
        "  The hou module is available via PYTHONPATH and $HFS/bin on PATH.\n\n"
        "Environment Variables:\n"
        "  VIBRANTE_NODE_APP    - Path to Vibrante-Node installation\n"
        "  VIBRANTE_PYTHON_EXE  - Override system Python path\n"
        "  VIBRANTE_HIP_FILE    - Current HIP file (set by Launch with Context)\n\n"
        "Copyright 2026 Mahmoud Kamal - KamalTD\n"
    )

    try:
        import hou
        hou.ui.displayMessage(msg, title="About Vibrante-Node Integration")
    except (ImportError, AttributeError):
        print(msg)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _open_folder(path):
    """Cross-platform folder opener."""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _show_error(message):
    """Show an error message in Houdini UI or print to console."""
    try:
        import hou
        hou.ui.displayMessage(
            message,
            title="Vibrante-Node",
            severity=hou.severityType.Error
        )
    except (ImportError, AttributeError):
        print(f"ERROR: {message}")


def _show_status(message):
    """Show a status message in Houdini or print to console."""
    try:
        import hou
        hou.ui.setStatusMessage(message, severity=hou.severityType.Message)
    except (ImportError, AttributeError):
        print(message)
