from PyQt5.QtWidgets import QDockWidget, QTextEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QToolBar, QAction, QStyle
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

class LogPanel(QDockWidget):
    # Signal to allow thread-safe logging from background threads
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__("Event Log", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar for actions
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(self.toolbar.iconSize() / 1.5) # Smaller icons
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("background-color: #333; border: none;")
        
        self.clear_action = QAction(self.style().standardIcon(QStyle.SP_DialogDiscardButton), "Clear Log", self)
        self.clear_action.triggered.connect(self.clear)
        self.toolbar.addAction(self.clear_action)
        
        layout.addWidget(self.toolbar)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setLineWrapMode(QTextEdit.NoWrap)
        
        font = QFont("Courier New", 10)
        self.log_area.setFont(font)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; border: none;")
        
        layout.addWidget(self.log_area)
        self.setWidget(container)
        
        # Connect signal to the internal handler
        self.log_signal.connect(self._handle_log)

    def apply_theme(self, is_dark=True):
        bg_color = "#1e1e1e" if is_dark else "#ffffff"
        text_color = "#d4d4d4" if is_dark else "#000000"
        toolbar_bg = "#333" if is_dark else "#f0f0f0"
        
        self.log_area.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: none;")
        self.toolbar.setStyleSheet(f"background-color: {toolbar_bg}; border: none;")
        self.update()

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
