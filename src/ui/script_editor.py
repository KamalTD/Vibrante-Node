from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from src.ui.code_editor import CodeEditor
from src.utils.highlighter import PythonHighlighter


class ScriptEditorDialog(QDialog):
    def __init__(self, parent=None, initial_code=None):
        super().__init__(parent)
        self.setWindowTitle("Python Script Editor")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Write a Python script that reads `inputs` and `params` and sets `result` variable."))

        self.editor = CodeEditor()
        self.highlighter = PythonHighlighter(self.editor.document())
        if initial_code:
            self.editor.setPlainText(initial_code)
        else:
            self.editor.setPlainText(self._get_sample())
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _get_sample(self):
        return (
            "# Example script:\n"
            "# - `inputs` is a dict of input port values (e.g. inputs.get('data'))\n"
            "# - `params` is a dict of node parameters\n"
            "# Set the variable `result` to return data to the output port.\n\n"
            "value = inputs.get('data')\n"
            "# simple transformation example\n"
            "if isinstance(value, str):\n"
            "    result = value.upper()\n"
            "else:\n"
            "    result = value\n"
        )

    def get_code(self):
        return self.editor.toPlainText()
