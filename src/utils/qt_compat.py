"""
Qt Compatibility Layer
======================
Provides a unified import surface for PyQt5 and PySide2/PySide6.

When running inside Houdini, PySide2 (or PySide6) is available.
When running standalone, PyQt5 is used.

Usage in other modules:
    from src.utils.qt_compat import QtWidgets, QtCore, QtGui, Signal, Slot

All modules should import Qt classes through this module instead of
importing directly from PyQt5 or PySide2.
"""

import os
import sys

# Detect which Qt binding is available.
# Priority: PySide2 (Houdini) -> PySide6 -> PyQt5
QT_BINDING = None

# If running inside Houdini, prefer PySide2 via hutil.Qt
_in_houdini = "HIP" in os.environ or "HOUDINI_PATH" in os.environ

if _in_houdini:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        from PySide2.QtCore import Signal, Slot
        try:
            from PySide2 import QtSvg
        except ImportError:
            QtSvg = None
        QT_BINDING = "PySide2"
    except ImportError:
        try:
            from PySide6 import QtWidgets, QtCore, QtGui
            from PySide6.QtCore import Signal, Slot
            try:
                from PySide6 import QtSvg
            except ImportError:
                QtSvg = None
            QT_BINDING = "PySide6"
        except ImportError:
            pass

if QT_BINDING is None:
    try:
        from PyQt5 import QtWidgets, QtCore, QtGui
        from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
        try:
            from PyQt5 import QtSvg
        except ImportError:
            QtSvg = None
        QT_BINDING = "PyQt5"
    except ImportError:
        raise ImportError(
            "No Qt binding found. Install PyQt5 (`pip install PyQt5`) "
            "or run inside Houdini (PySide2/PySide6)."
        )


# ---------------------------------------------------------------------------
# Compatibility helpers
# ---------------------------------------------------------------------------

def exec_app(app):
    """Cross-binding QApplication.exec() / .exec_()."""
    if hasattr(app, "exec"):
        return app.exec()
    return app.exec_()


def exec_dialog(dialog, *args):
    """Cross-binding QDialog.exec() / .exec_().

    Also works for QMenu.exec(pos) / .exec_(pos).
    Pass optional positional args (e.g. a QPoint for menu position).
    """
    if hasattr(dialog, "exec"):
        return dialog.exec(*args)
    return dialog.exec_(*args)


def get_qregexp():
    """Return a regular-expression class compatible with the active binding.

    PyQt5/PySide2 (Qt5) -> QRegExp
    PySide6/PyQt6 (Qt6) -> QRegularExpression from QtCore
    """
    if QT_BINDING in ("PyQt5", "PySide2"):
        return QtCore.QRegExp
    # Qt6 removed QRegExp; use QRegularExpression
    return QtCore.QRegularExpression


def invoke_method(obj, method_name, connection_type, *args):
    """Cross-binding QMetaObject.invokeMethod with Q_ARG support.

    In PyQt5, Q_ARG is used. In PySide2/6, invoke via a queued call.
    """
    if QT_BINDING == "PyQt5":
        from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
        q_args = []
        for val in args:
            if isinstance(val, str):
                q_args.append(Q_ARG(str, val))
            elif isinstance(val, bool):
                q_args.append(Q_ARG(bool, val))
            elif isinstance(val, int):
                q_args.append(Q_ARG(int, val))
        QMetaObject.invokeMethod(obj, method_name, connection_type, *q_args)
    else:
        # PySide2/6: use timer with 0ms to queue the call on the main thread
        method = getattr(obj, method_name)
        QtCore.QTimer.singleShot(0, lambda: method(*args))
