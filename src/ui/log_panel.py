from PyQt5.QtWidgets import QDockWidget, QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt

class LogPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Event Log", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setLineWrapMode(QTextEdit.NoWrap)
        
        # Set a monospaced font for the log
        font = QFont("Courier New", 10)
        self.log_area.setFont(font)
        
        # Set dark background for "fancy" look
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        
        self.setWidget(self.log_area)

    def log(self, message: str, level: str = "info"):
        """
        Log a message with a specific level (info, success, warning, error, execution).
        """
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
        
        # Auto-scroll
        self.log_area.setTextCursor(cursor)
        self.log_area.ensureCursorVisible()

    def clear(self):
        self.log_area.clear()
