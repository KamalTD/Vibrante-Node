from PyQt5.QtWidgets import (QDockWidget, QTextEdit, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QToolBar, QAction, QStyle, QLineEdit, QCheckBox,
                             QLabel, QFrame, QComboBox)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class LogEntry:
    """Represents a single log entry with metadata."""
    message: str
    level: str
    node_name: Optional[str] = None
    entry_type: Optional[str] = None  # 'input', 'output', 'execution', 'error', 'info'

class LogPanel(QDockWidget):
    # Signal to allow thread-safe logging from background threads
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__("Event Log", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Store all log entries
        self._entries: list[LogEntry] = []
        self._is_dark_theme = True
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # === Filter Bar ===
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(4, 4, 4, 4)
        filter_layout.setSpacing(8)
        
        # Node name filter
        filter_layout.addWidget(QLabel("Node:"))
        self.node_filter = QLineEdit()
        self.node_filter.setPlaceholderText("Filter by node name...")
        self.node_filter.setMaximumWidth(200)
        self.node_filter.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.node_filter)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        filter_layout.addWidget(sep1)
        
        # Level filter checkboxes
        filter_layout.addWidget(QLabel("Show:"))
        
        self.filter_error = QCheckBox("Errors")
        self.filter_error.setChecked(True)
        self.filter_error.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_error)
        
        self.filter_warning = QCheckBox("Warnings")
        self.filter_warning.setChecked(True)
        self.filter_warning.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_warning)
        
        self.filter_info = QCheckBox("Info")
        self.filter_info.setChecked(True)
        self.filter_info.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_info)
        
        self.filter_exec = QCheckBox("Execution")
        self.filter_exec.setChecked(True)
        self.filter_exec.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_exec)
        
        self.filter_output = QCheckBox("Outputs")
        self.filter_output.setChecked(True)
        self.filter_output.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_output)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        filter_layout.addWidget(sep2)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMaximumWidth(60)
        self.clear_btn.clicked.connect(self.clear)
        filter_layout.addWidget(self.clear_btn)
        
        filter_layout.addStretch()
        layout.addWidget(filter_container)
        
        # === Log Area ===
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setLineWrapMode(QTextEdit.NoWrap)
        
        font = QFont("Courier New", 10)
        self.log_area.setFont(font)
        
        layout.addWidget(self.log_area)
        self.setWidget(container)
        
        # Connect signal to the internal handler
        self.log_signal.connect(self._handle_log)
        
        # Apply initial theme
        self.apply_theme(is_dark=True)

    def apply_theme(self, is_dark=True):
        self._is_dark_theme = is_dark
        bg_color = "#1e1e1e" if is_dark else "#ffffff"
        text_color = "#d4d4d4" if is_dark else "#000000"
        filter_bg = "#2b2b2b" if is_dark else "#f5f5f5"
        input_bg = "#3c3f41" if is_dark else "#ffffff"
        border_color = "#444" if is_dark else "#ccc"
        
        self.log_area.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: none;")
        
        # Style filter container
        filter_style = f"""
            QWidget {{ background-color: {filter_bg}; color: {text_color}; }}
            QLineEdit {{ 
                background-color: {input_bg}; 
                color: {text_color}; 
                border: 1px solid {border_color};
                padding: 2px 4px;
                border-radius: 3px;
            }}
            QCheckBox {{ color: {text_color}; }}
            QLabel {{ color: {text_color}; }}
            QPushButton {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 2px 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {"#4a4d4e" if is_dark else "#e0e0e0"};
            }}
            QFrame {{ color: {border_color}; }}
        """
        self.widget().findChild(QWidget).setStyleSheet(filter_style)
        self.update()

    def log(self, message: str, level: str = "info"):
        """Thread-safe logging method."""
        self.log_signal.emit(message, level)

    def _extract_node_name(self, message: str) -> Optional[str]:
        """Extract node name from log message."""
        # Patterns like: "Node 'NodeName' ...", "[NodeName] ...", "Node 'NodeName'"
        patterns = [
            r"Node '([^']+)'",
            r"\[([^\]]+)\]",
            r"'([^']+)' (started|output|error|finished)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return None

    def _determine_entry_type(self, message: str, level: str) -> str:
        """Determine the type of log entry for filtering."""
        msg_lower = message.lower()
        if level == "error":
            return "error"
        elif "output" in msg_lower or "->" in message:
            return "output"
        elif "input" in msg_lower:
            return "input"
        elif level == "execution" or "started" in msg_lower or "finished" in msg_lower:
            return "execution"
        else:
            return "info"

    @pyqtSlot(str, str)
    def _handle_log(self, message: str, level: str):
        """Store entry and update display."""
        node_name = self._extract_node_name(message)
        entry_type = self._determine_entry_type(message, level)
        
        entry = LogEntry(
            message=message,
            level=level,
            node_name=node_name,
            entry_type=entry_type
        )
        self._entries.append(entry)
        
        # Check if entry passes current filters before adding
        if self._entry_passes_filter(entry):
            self._append_entry_to_display(entry)

    def _entry_passes_filter(self, entry: LogEntry) -> bool:
        """Check if an entry passes the current filters."""
        # Node name filter
        node_filter_text = self.node_filter.text().strip().lower()
        if node_filter_text:
            if entry.node_name is None:
                return False
            if node_filter_text not in entry.node_name.lower():
                return False
        
        # Level filters
        if entry.level == "error" and not self.filter_error.isChecked():
            return False
        if entry.level == "warning" and not self.filter_warning.isChecked():
            return False
        if entry.level == "info" and not self.filter_info.isChecked():
            return False
        if entry.level == "execution" and not self.filter_exec.isChecked():
            return False
        if entry.level == "success" and entry.entry_type == "output" and not self.filter_output.isChecked():
            return False
        
        return True

    def _append_entry_to_display(self, entry: LogEntry):
        """Add a single entry to the log display."""
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format = QTextCharFormat()
        if entry.level == "error":
            format.setForeground(QColor("#ff5555"))  # Red
            prefix = "[ERROR] "
        elif entry.level == "warning":
            format.setForeground(QColor("#ffb86c"))  # Orange
            prefix = "[WARN]  "
        elif entry.level == "success":
            format.setForeground(QColor("#50fa7b"))  # Green
            prefix = "[OK]    "
        elif entry.level == "execution":
            format.setForeground(QColor("#8be9fd"))  # Cyan
            prefix = "[EXEC]  "
        else:  # info
            format.setForeground(QColor("#bd93f9"))  # Purple
            prefix = "[INFO]  "

        cursor.setCharFormat(format)
        cursor.insertText(f"{prefix}{entry.message}\n")
        self.log_area.setTextCursor(cursor)
        self.log_area.ensureCursorVisible()

    def _apply_filters(self):
        """Re-render the log display based on current filters."""
        self.log_area.clear()
        for entry in self._entries:
            if self._entry_passes_filter(entry):
                self._append_entry_to_display(entry)

    def clear(self):
        """Clear all log entries."""
        self._entries.clear()
        self.log_area.clear()

