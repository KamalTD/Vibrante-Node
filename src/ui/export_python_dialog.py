from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton,
    QLabel, QFileDialog, QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from src.core.models import WorkflowModel
from src.utils.highlighter import PythonHighlighter


class ExportPythonDialog(QDialog):
    def __init__(self, workflow_model: WorkflowModel, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Workflow as Python")
        self.resize(750, 550)
        self.workflow_model = workflow_model
        self._generated_code = ""
        self._init_ui()
        self._generate()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.info_label = QLabel("Generated Python script:")
        layout.addWidget(self.info_label)

        self.code_display = QPlainTextEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setFont(QFont("Consolas", 10))
        self._highlighter = PythonHighlighter(self.code_display.document())
        layout.addWidget(self.code_display)

        button_layout = QHBoxLayout()

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)

        self.save_btn = QPushButton("Save As...")
        self.save_btn.clicked.connect(self._save_file)
        button_layout.addWidget(self.save_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def _generate(self):
        try:
            from src.core.workflow_to_python import convert_workflow_to_python
            code = convert_workflow_to_python(self.workflow_model)
            self.code_display.setPlainText(code)
            self._generated_code = code
        except Exception as e:
            self.code_display.setPlainText(f"# Error generating Python:\n# {e}")
            self._generated_code = ""

    def _copy_to_clipboard(self):
        QApplication.clipboard().setText(self._generated_code)

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Python Script", "", "Python Files (*.py)"
        )
        if path:
            if not path.endswith(".py"):
                path += ".py"
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._generated_code)
                QMessageBox.information(self, "Saved", f"Script saved to:\n{path}")
            except IOError as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
