from PyQt5.QtWidgets import QDockWidget, QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

class LogPanel(QDockWidget):
    # Signal to allow thread-safe logging from background threads
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__("Event Log", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setLineWrapMode(QTextEdit.NoWrap)
        
        font = QFont("Courier New", 10)
        self.log_area.setFont(font)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        
        self.setWidget(self.log_area)
        
        # Connect signal to the internal handler
        self.log_signal.connect(self._handle_log)

    def log(self, message: str, level: str = "info"):
        """Thread-safe logging method."""
        self.log_signal.emit(message, level)

    @pyqtSlot(str, str)
    def _handle_log(self, message: str, level: str):
        """Actual UI update (must run on GUI thread)."""
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format = QTextCharFormat()
        if level == "error":
            format.setForeground(QColor("#ff5555")) # Red
            prefix = "[ERROR] "
        elif level == "warning":
            format.setForeground(QColor("#ffb86c")) # Orange
            prefix = "[WARN]  "
        elif level == "success":
            format.setForeground(QColor("#50fa7b")) # Green
            prefix = "[OK]    "
        elif level == "execution":
            format.setForeground(QColor("#8be9fd")) # Cyan
            prefix = "[EXEC]  "
        else: # info
            format.setForeground(QColor("#bd93f9")) # Purple
            prefix = "[INFO]  "

        cursor.setCharFormat(format)
        cursor.insertText(f"{prefix}{message}\n")
        self.log_area.setTextCursor(cursor)
        self.log_area.ensureCursorVisible()

    def clear(self):
        self.log_area.clear()
