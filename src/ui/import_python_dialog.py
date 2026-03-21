from src.utils.qt_compat import QtWidgets, QtGui
from src.utils.config_manager import config
from src.utils.highlighter import PythonHighlighter

QDialog = QtWidgets.QDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QPlainTextEdit = QtWidgets.QPlainTextEdit
QPushButton = QtWidgets.QPushButton
QLabel = QtWidgets.QLabel
QFileDialog = QtWidgets.QFileDialog
QMessageBox = QtWidgets.QMessageBox
QProgressBar = QtWidgets.QProgressBar
QFont = QtGui.QFont


class ImportPythonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Python as Workflow")
        self.resize(750, 550)
        self._workflow_model = None
        self._converter = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(
            "Paste Python code below or load from file.\n"
            "Gemini AI will analyze it and generate a node workflow."
        ))

        self.code_input = QPlainTextEdit()
        self.code_input.setPlaceholderText("Paste your Python code here...")
        self.code_input.setFont(QFont("Consolas", 10))
        self._highlighter = PythonHighlighter(self.code_input.document())
        layout.addWidget(self.code_input)

        load_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load from .py File...")
        self.load_btn.clicked.connect(self._load_file)
        load_layout.addWidget(self.load_btn)
        load_layout.addStretch()
        layout.addLayout(load_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #aaa;")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()

        self.convert_btn = QPushButton("Convert with Gemini AI")
        self.convert_btn.clicked.connect(self._start_conversion)
        button_layout.addWidget(self.convert_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Python File", "", "Python Files (*.py);;All Files (*)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.code_input.setPlainText(f.read())
            except IOError as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _start_conversion(self):
        code = self.code_input.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Empty", "Please enter or load Python code first.")
            return

        api_key = config.get_gemini_api_key()
        if not api_key:
            QMessageBox.warning(
                self, "API Key Missing",
                "Gemini API key not set.\nGo to Help -> Link to Gemini."
            )
            return

        self.convert_btn.setEnabled(False)
        self.code_input.setReadOnly(True)
        self.progress_bar.show()

        from src.core.python_to_workflow import PythonToWorkflowConverter
        self._converter = PythonToWorkflowConverter()
        self._converter.conversion_finished.connect(self._on_conversion_done)
        self._converter.status_update.connect(self._on_status_update)
        self._converter.convert(code)

    def _on_status_update(self, msg):
        self.status_label.setText(msg)

    def _on_conversion_done(self, workflow_model, error):
        self.progress_bar.hide()
        self.convert_btn.setEnabled(True)
        self.code_input.setReadOnly(False)

        if error:
            QMessageBox.critical(self, "Conversion Failed", error)
            return

        self._workflow_model = workflow_model
        node_count = len(workflow_model.nodes)
        conn_count = len(workflow_model.connections)
        QMessageBox.information(
            self, "Success",
            f"Conversion successful!\n"
            f"Generated {node_count} nodes and {conn_count} connections."
        )
        self.accept()

    def get_workflow_model(self):
        return self._workflow_model
