from src.utils.qt_compat import QtWidgets
from src.utils.config_manager import config

QDialog = QtWidgets.QDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QLineEdit = QtWidgets.QLineEdit
QPushButton = QtWidgets.QPushButton
QLabel = QtWidgets.QLabel
QHBoxLayout = QtWidgets.QHBoxLayout

class GeminiApiDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Link to Gemini")
        self.setFixedWidth(400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Paste your Gemini API Key here:"))
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setText(config.get_gemini_api_key())
        layout.addWidget(self.api_key_edit)
        
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_api_key)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def _save_api_key(self):
        api_key = self.api_key_edit.text().strip()
        config.set_gemini_api_key(api_key)
        self.accept()
