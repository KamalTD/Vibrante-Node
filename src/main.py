from PyQt5.QtWidgets import QApplication
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import traceback
import os

def exception_hook(exctype, value, tb):
    """Global function to catch unhandled exceptions."""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(error_msg)
    with open("crash.log", "w") as f:
        f.write(error_msg)
    sys.exit(1)

sys.excepthook = exception_hook

from src.ui.window import MainWindow
...
def main():
    print("Starting QApplication...")
    app = QApplication(sys.argv)
    print("Initializing MainWindow...")
    window = MainWindow()
    print("Showing MainWindow...")
    window.show()
    print("Entering Event Loop...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
