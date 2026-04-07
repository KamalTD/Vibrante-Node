import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Process PYTHONPATH: add entries to sys.path for external library access
def _apply_pythonpath():
    pythonpath = os.environ.get('PYTHONPATH', '')
    if pythonpath:
        for p in pythonpath.split(os.pathsep):
            p = p.strip()
            if p and os.path.isdir(p) and p not in sys.path:
                sys.path.insert(0, p)
                print(f"Added to sys.path: {p}")

# Register Houdini DLL directories so `import hou` works on Windows.
# Python 3.8+ no longer uses PATH for DLL resolution; os.add_dll_directory()
# must be called explicitly for each directory containing required DLLs.
def _register_houdini_dlls():
    hfs = os.environ.get('HFS', '')
    if not hfs:
        return
    dll_dirs = [
        os.path.join(hfs, 'bin'),
        os.path.join(hfs, 'custom', 'houdini', 'dsolib'),
    ]
    for d in dll_dirs:
        if os.path.isdir(d):
            try:
                os.add_dll_directory(d)
                print(f"Registered DLL directory: {d}")
            except OSError:
                pass

_apply_pythonpath()
_register_houdini_dlls()

from src.utils.qt_compat import QtWidgets, QtGui, QtCore, exec_app
QApplication = QtWidgets.QApplication
QSplashScreen = QtWidgets.QSplashScreen
QProgressBar = QtWidgets.QProgressBar
QPixmap = QtGui.QPixmap
QColor = QtGui.QColor
QFont = QtGui.QFont
QPainter = QtGui.QPainter
Qt = QtCore.Qt
QTimer = QtCore.QTimer

import traceback

def exception_hook(exctype, value, tb):
    """Global function to catch unhandled exceptions."""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(error_msg)
    with open("crash.log", "w") as f:
        f.write(error_msg)
    sys.exit(1)

sys.excepthook = exception_hook


class SplashScreen(QSplashScreen):
    VERSION = "v1.5.0"
    COPYRIGHT = "\u00a9 2026 Mahmoud Kamal - KamalTD"

    def __init__(self):
        splash_path = os.path.join(os.path.dirname(__file__), '..', 'splash.png')
        pixmap = QPixmap(splash_path)
        # Scale to a reasonable splash size while keeping aspect ratio
        pixmap = pixmap.scaled(800, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Paint version and copyright onto the pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Version - top right
        version_font = QFont("Segoe UI", 11, QFont.Bold)
        painter.setFont(version_font)
        painter.setPen(QColor(200, 200, 200, 200))
        painter.drawText(
            pixmap.rect().adjusted(0, 12, -16, 0),
            Qt.AlignTop | Qt.AlignRight,
            self.VERSION
        )

        # Copyright - bottom left
        copyright_font = QFont("Segoe UI", 8)
        painter.setFont(copyright_font)
        painter.setPen(QColor(180, 180, 180, 180))
        painter.drawText(
            pixmap.rect().adjusted(12, 0, 0, -16),
            Qt.AlignBottom | Qt.AlignLeft,
            self.COPYRIGHT
        )

        painter.end()

        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Add a progress bar at the bottom of the splash
        self.progress_bar = QProgressBar(self)
        bar_height = 6
        self.progress_bar.setGeometry(0, pixmap.height() - bar_height, pixmap.width(), bar_height)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(0, 0, 0, 100);
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b44aff, stop:1 #00d4ff);
            }
        """)
        self.progress_bar.setValue(0)

        # Message font
        self._msg_font = QFont("Segoe UI", 9)

    def showMessage(self, message, progress=0):
        self.progress_bar.setValue(progress)
        super().showMessage(
            message,
            Qt.AlignBottom | Qt.AlignHCenter,
            QColor(200, 200, 200)
        )
        QApplication.processEvents()


def main():
    print("Starting QApplication...")
    app = QApplication(sys.argv)

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'vibrante-node-icon.png')
    if os.path.isfile(icon_path):
        app.setWindowIcon(QtGui.QIcon(icon_path))

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()

    splash.showMessage("Loading modules...", 10)

    from src.ui.window import MainWindow

    splash.showMessage("Initializing application...", 40)

    print("Initializing MainWindow...")
    window = MainWindow()

    splash.showMessage("Preparing workspace...", 70)
    QApplication.processEvents()

    splash.showMessage("Almost ready...", 90)
    QApplication.processEvents()

    print("Showing MainWindow...")
    window.show()

    splash.showMessage("Welcome to Vibrante-Node!", 100)
    QApplication.processEvents()

    # Close splash after a brief moment so the user sees 100%
    QTimer.singleShot(500, splash.close)

    print("Entering Event Loop...")
    sys.exit(exec_app(app))

if __name__ == "__main__":
    main()
