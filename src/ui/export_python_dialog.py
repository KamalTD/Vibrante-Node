import sys
import os
import re
import ast
import tempfile
import threading

from src.utils.qt_compat import QtWidgets, QtGui, QtCore, Signal, Slot

QDialog = QtWidgets.QDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QPlainTextEdit = QtWidgets.QPlainTextEdit
QPushButton = QtWidgets.QPushButton
QLabel = QtWidgets.QLabel
QFileDialog = QtWidgets.QFileDialog
QMessageBox = QtWidgets.QMessageBox
QApplication = QtWidgets.QApplication
QSplitter = QtWidgets.QSplitter
QWidget = QtWidgets.QWidget
QToolBar = QtWidgets.QToolBar
QAction = QtWidgets.QAction
QStatusBar = QtWidgets.QStatusBar
QStyle = QtWidgets.QStyle

QFont = QtGui.QFont
QColor = QtGui.QColor
QTextCursor = QtGui.QTextCursor
QTextCharFormat = QtGui.QTextCharFormat

Qt = QtCore.Qt
QProcess = QtCore.QProcess

from src.core.models import WorkflowModel
from src.ui.code_editor import CodeEditor
from src.utils.highlighter import PythonHighlighter
from src.utils.config_manager import config


class GeminiFixWorker(threading.Thread):
    """Background thread that sends code + error to Gemini for AI-powered fixing."""

    def __init__(self, code, error, callback_fn):
        super().__init__(daemon=True)
        self.code = code
        self.error = error
        self.callback_fn = callback_fn

    def run(self):
        try:
            import google.generativeai as genai

            api_key = config.get_gemini_api_key()
            if not api_key:
                self.callback_fn("", "Gemini API key not set. Go to Help -> Link to Gemini.")
                return

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')

            prompt = (
                "You are a Python debugging assistant. The following Python script has errors.\n"
                "Fix the code and return ONLY the corrected Python code inside a ```python ... ``` block.\n"
                "Do not include explanations outside the code block.\n\n"
                f"--- Script ---\n```python\n{self.code}\n```\n\n"
                f"--- Error Output ---\n```\n{self.error}\n```\n"
            )

            response = model.generate_content(prompt)
            text = response.text

            match = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                self.callback_fn(match.group(1), "")
            else:
                self.callback_fn("", f"Gemini did not return a code block.\nResponse:\n{text[:500]}")

        except Exception as e:
            self.callback_fn("", f"Gemini API error: {e}")


class ExportPythonDialog(QDialog):
    """Professional IDE-like dialog for viewing, editing, running, and AI-fixing exported Python code."""

    _ai_result_signal = Signal(str, str)

    def __init__(self, workflow_model: WorkflowModel, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Python Code Editor - Export")
        self.resize(1050, 720)
        self.setMinimumSize(700, 500)
        self.workflow_model = workflow_model
        self._generated_code = ""
        self._process = None
        self._ai_worker = None
        self._last_error_output = ""
        self._temp_file_path = None
        self._init_ui()
        self._generate()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._ai_result_signal.connect(self._handle_ai_result)

        # Apply Dracula theme to entire dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #21222c;
                color: #f8f8f2;
            }
            QToolBar {
                background-color: #282a36;
                border-bottom: 1px solid #44475a;
                spacing: 4px;
                padding: 2px 4px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                color: #f8f8f2;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px 10px;
                font-size: 10pt;
            }
            QToolBar QToolButton:hover {
                background-color: #44475a;
                border: 1px solid #6272a4;
            }
            QToolBar QToolButton:pressed {
                background-color: #6272a4;
            }
            QToolBar QToolButton:disabled {
                color: #6272a4;
            }
            QToolBar::separator {
                background-color: #44475a;
                width: 1px;
                margin: 4px 6px;
            }
            QSplitter::handle {
                background-color: #44475a;
                height: 2px;
            }
            QLabel {
                color: #f8f8f2;
            }
            QPushButton {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #6272a4;
                border-radius: 3px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: #6272a4;
            }
            QStatusBar {
                background-color: #191a21;
                color: #6272a4;
                border-top: 1px solid #44475a;
            }
            QStatusBar QLabel {
                color: #6272a4;
                font-size: 9pt;
                padding: 0 8px;
            }
        """)

        # --- Toolbar ---
        self._init_toolbar(layout)

        # --- Splitter: editor + output ---
        splitter = QSplitter(Qt.Vertical)

        self._init_editor()
        splitter.addWidget(self.code_editor)

        output_container = self._init_output_panel()
        splitter.addWidget(output_container)

        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter, 1)

        # --- Status bar ---
        self._init_status_bar(layout)

    def _init_toolbar(self, parent_layout):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(toolbar.iconSize())
        style = self.style()

        self.run_action = QAction(style.standardIcon(QStyle.SP_MediaPlay), "Run", self)
        self.run_action.setShortcut("F5")
        self.run_action.setToolTip("Run script (F5)")
        self.run_action.triggered.connect(self._run_code)
        toolbar.addAction(self.run_action)

        self.stop_action = QAction(style.standardIcon(QStyle.SP_MediaStop), "Stop", self)
        self.stop_action.setToolTip("Stop running script")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self._stop_code)
        toolbar.addAction(self.stop_action)

        toolbar.addSeparator()

        self.ai_fix_action = QAction("Fix with AI", self)
        self.ai_fix_action.setToolTip("Send code and errors to Gemini AI for automatic fixing")
        self.ai_fix_action.setEnabled(False)
        self.ai_fix_action.triggered.connect(self._fix_with_ai)
        toolbar.addAction(self.ai_fix_action)

        toolbar.addSeparator()

        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut("Ctrl+Shift+C")
        self.copy_action.setToolTip("Copy code to clipboard (Ctrl+Shift+C)")
        self.copy_action.triggered.connect(self._copy_to_clipboard)
        toolbar.addAction(self.copy_action)

        self.save_action = QAction(style.standardIcon(QStyle.SP_DialogSaveButton), "Save As...", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setToolTip("Save script to file (Ctrl+S)")
        self.save_action.triggered.connect(self._save_file)
        toolbar.addAction(self.save_action)

        # Spacer to push Close to the right
        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().horizontalPolicy(),
            spacer.sizePolicy().verticalPolicy()
        )
        QSizePolicy = QtWidgets.QSizePolicy
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self.close_action = QAction("Close", self)
        self.close_action.setToolTip("Close dialog")
        self.close_action.triggered.connect(self.reject)
        toolbar.addAction(self.close_action)

        parent_layout.addWidget(toolbar)

    def _init_editor(self):
        self.code_editor = CodeEditor()
        self._highlighter = PythonHighlighter(self.code_editor.document())
        self.code_editor.cursorPositionChanged.connect(self._update_cursor_pos)

        # Dracula-themed professional styling
        self.code_editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #282a36;
                color: #f8f8f2;
                selection-background-color: #44475a;
                selection-color: #f8f8f2;
                border: none;
                border-top: 1px solid #44475a;
                border-bottom: 1px solid #44475a;
            }
        """)

    def _init_output_panel(self):
        container = QWidget()
        vlayout = QVBoxLayout(container)
        vlayout.setContentsMargins(4, 2, 4, 0)
        vlayout.setSpacing(2)

        header = QHBoxLayout()
        header.addWidget(QLabel("Output"))
        header.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(lambda: self.output_display.clear())
        header.addWidget(clear_btn)
        vlayout.addLayout(header)

        self.output_display = QPlainTextEdit()
        self.output_display.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.output_display.setFont(font)
        self.output_display.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.output_display.setStyleSheet(
            "background-color: #191a21; color: #f8f8f2; border: none; border-top: 1px solid #44475a;"
        )

        vlayout.addWidget(self.output_display, 1)
        return container

    def _init_status_bar(self, parent_layout):
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)

        self._cursor_label = QLabel("Ln 1, Col 1")
        self._cursor_label.setMinimumWidth(120)
        self.status_bar.addWidget(self._cursor_label)

        self._status_message = QLabel("Ready")
        self.status_bar.addPermanentWidget(self._status_message)

        parent_layout.addWidget(self.status_bar)

    # ---- Code Generation ----

    def _generate(self):
        try:
            from src.core.workflow_to_python import convert_workflow_to_python
            code = convert_workflow_to_python(self.workflow_model)
            self.code_editor.setPlainText(code)
            self._generated_code = code
        except Exception as e:
            self.code_editor.setPlainText(f"# Error generating Python:\n# {e}")
            self._generated_code = ""

    # ---- Code Execution ----

    def _run_code(self):
        if self._process is not None:
            return

        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        # Write to temp file
        try:
            fd, path = tempfile.mkstemp(suffix='.py', prefix='vibrante_run_')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            self._temp_file_path = path
        except OSError as e:
            self._append_output(f">>> Failed to create temp file: {e}\n", color="#ff5555")
            return

        self.output_display.clear()
        self._last_error_output = ""
        self._append_output(">>> Running script...\n", color="#8be9fd")

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout_ready)
        self._process.readyReadStandardError.connect(self._on_stderr_ready)
        self._process.finished.connect(self._on_process_finished)
        self._process.errorOccurred.connect(self._on_process_error)
        self._process.start(sys.executable, [self._temp_file_path])

        self._update_button_states()
        self._status_message.setText("Running...")

    def _stop_code(self):
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._append_output("\n>>> Process killed by user.\n", color="#ff5555")

    @Slot()
    def _on_stdout_ready(self):
        if self._process is None:
            return
        data = self._process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self._append_output(data)

    @Slot()
    def _on_stderr_ready(self):
        if self._process is None:
            return
        data = self._process.readAllStandardError().data().decode('utf-8', errors='replace')
        self._last_error_output += data
        self._append_output(data, color="#ff5555")

    @Slot(int, QProcess.ExitStatus)
    def _on_process_finished(self, exit_code, exit_status):
        status_text = "finished successfully" if exit_code == 0 else f"exited with code {exit_code}"
        color = "#50fa7b" if exit_code == 0 else "#ff5555"
        self._append_output(f"\n>>> Process {status_text}.\n", color=color)
        self._status_message.setText(f"Exit code: {exit_code}")

        self._cleanup_temp()
        self._process = None
        self._update_button_states()

    @Slot(QProcess.ProcessError)
    def _on_process_error(self, error):
        error_map = {
            QProcess.FailedToStart: "Failed to start Python interpreter",
            QProcess.Crashed: "Python process crashed",
            QProcess.Timedout: "Process timed out",
        }
        msg = error_map.get(error, f"Process error: {error}")
        self._append_output(f"\n>>> ERROR: {msg}\n", color="#ff5555")
        self._status_message.setText("Error")
        self._cleanup_temp()
        self._process = None
        self._update_button_states()

    def _append_output(self, text, color=None):
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        if color:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
        else:
            fmt = QTextCharFormat()
            cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.output_display.setTextCursor(cursor)
        self.output_display.ensureCursorVisible()

    def _cleanup_temp(self):
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                os.unlink(self._temp_file_path)
            except OSError:
                pass
            self._temp_file_path = None

    # ---- AI Fix ----

    def _fix_with_ai(self):
        api_key = config.get_gemini_api_key()
        if not api_key:
            QMessageBox.warning(
                self, "API Key Missing",
                "Please set your Gemini API key in Help -> Link to Gemini."
            )
            return

        code = self.code_editor.toPlainText()
        error = self._last_error_output

        if not error.strip():
            if self.code_editor.error_line > 0:
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    error = f"SyntaxError at line {e.lineno}: {e.msg}"

        if not error.strip():
            QMessageBox.information(
                self, "No Errors",
                "No errors detected. Run the code first to identify issues."
            )
            return

        self.ai_fix_action.setEnabled(False)
        self._status_message.setText("AI is analyzing code...")
        self._append_output("\n>>> Sending code to Gemini AI for analysis...\n", color="#bd93f9")

        self._ai_worker = GeminiFixWorker(code, error, self._on_ai_fix_result)
        self._ai_worker.start()

    def _on_ai_fix_result(self, fixed_code, error_msg):
        self._ai_result_signal.emit(fixed_code, error_msg)

    @Slot(str, str)
    def _handle_ai_result(self, fixed_code, error_msg):
        self.ai_fix_action.setEnabled(True)
        self._status_message.setText("Ready")

        if error_msg:
            self._append_output(f">>> AI Fix Error: {error_msg}\n", color="#ff5555")
            QMessageBox.warning(self, "AI Fix Failed", error_msg)
            return

        reply = QMessageBox.question(
            self, "Apply AI Fix?",
            "Gemini has suggested a fix. Replace the current code with the AI-corrected version?\n\n"
            "(Use Ctrl+Z in the editor to undo if needed.)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self.code_editor.setPlainText(fixed_code)
            self._append_output(">>> AI fix applied. Run the code again to verify.\n", color="#50fa7b")
            self._status_message.setText("AI fix applied")
        else:
            self._append_output(">>> AI fix rejected by user.\n", color="#ffb86c")

    # ---- Clipboard & Save ----

    def _copy_to_clipboard(self):
        QApplication.clipboard().setText(self.code_editor.toPlainText())
        self._status_message.setText("Copied to clipboard")

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Python Script", "", "Python Files (*.py)"
        )
        if path:
            if not path.endswith(".py"):
                path += ".py"
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.code_editor.toPlainText())
                QMessageBox.information(self, "Saved", f"Script saved to:\n{path}")
            except IOError as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    # ---- Status Bar ----

    def _update_cursor_pos(self):
        cursor = self.code_editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self._cursor_label.setText(f"Ln {line}, Col {col}")

    def _update_button_states(self):
        is_running = self._process is not None and self._process.state() != QProcess.NotRunning
        self.run_action.setEnabled(not is_running)
        self.stop_action.setEnabled(is_running)
        has_errors = bool(self._last_error_output.strip()) or self.code_editor.error_line > 0
        self.ai_fix_action.setEnabled(not is_running and has_errors)

    # ---- Cleanup ----

    def closeEvent(self, event):
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._process.waitForFinished(3000)
        self._cleanup_temp()
        super().closeEvent(event)
