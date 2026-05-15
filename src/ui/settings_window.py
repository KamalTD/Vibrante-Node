import json
import os
import sys

from src.utils.qt_compat import QtWidgets, QtCore, QtGui
from src.utils.env_manager import env_manager

QDialog = QtWidgets.QDialog
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QLabel = QtWidgets.QLabel
QPushButton = QtWidgets.QPushButton
QListWidget = QtWidgets.QListWidget
QStackedWidget = QtWidgets.QStackedWidget
QPlainTextEdit = QtWidgets.QPlainTextEdit
QTableWidget = QtWidgets.QTableWidget
QTableWidgetItem = QtWidgets.QTableWidgetItem
QHeaderView = QtWidgets.QHeaderView
QAbstractItemView = QtWidgets.QAbstractItemView
QFileDialog = QtWidgets.QFileDialog
QMessageBox = QtWidgets.QMessageBox
QFrame = QtWidgets.QFrame
Qt = QtCore.Qt


# Known built-in Vibrante-Node environment variables displayed read-only.
# v_nodes_dir and v_scripts_path are managed on the Application Paths page.
# Each entry: (variable_name, description).
_VIBRANTE_BUILTIN_VARS = [
    ("VIBRANTE_NODE_APP",     "Path to the Vibrante-Node application root directory."),
    ("VIBRANTE_PYTHON_EXE",   "Path to the system Python executable used for subprocess launches."),
    ("VIBRANTE_HOUDINI_MODE", "Runtime mode: 'subprocess' (launched from Houdini) or 'direct'."),
    ("VIBRANTE_HOU_PORT",     "TCP port for the Houdini JSON-RPC bridge server (default: 18811)."),
    ("VIBRANTE_HIP_FILE",     "Path to the current Houdini scene (.hip) file."),
]


class SettingsWindow(QDialog):
    """Application settings and preferences dialog.

    Sidebar navigation with stacked pages:
      - Python Runtime      (VIBRANTE_PYTHONPATH editor)
      - Application Paths   (v_nodes_dir and v_scripts_path editors)
      - Environment Vars    (custom user variables table)
      - Vibrante Variables  (read-only display of built-in runtime variables)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings — Vibrante-Node")
        self.setMinimumSize(720, 480)
        self.resize(760, 520)
        self._init_ui()
        self._load_settings()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Sidebar ----
        self._sidebar = QListWidget()
        self._sidebar.setFixedWidth(170)
        self._sidebar.setFrameShape(QFrame.NoFrame)
        self._sidebar.setSpacing(2)
        self._sidebar.addItem("Python Runtime")
        self._sidebar.addItem("Application Paths")
        self._sidebar.addItem("Environment Variables")
        self._sidebar.addItem("Vibrante Variables")
        self._sidebar.setCurrentRow(0)
        root.addWidget(self._sidebar)

        # Vertical divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        root.addWidget(divider)

        # ---- Right panel ----
        right = QVBoxLayout()
        right.setContentsMargins(16, 16, 16, 12)
        right.setSpacing(8)

        self._pages = QStackedWidget()
        self._pages.addWidget(self._build_python_runtime_page())     # index 0
        self._pages.addWidget(self._build_app_paths_page())          # index 1
        self._pages.addWidget(self._build_env_vars_page())           # index 2
        self._pages.addWidget(self._build_vibrante_vars_page())      # index 3
        right.addWidget(self._pages, 1)

        # ---- Buttons row ----
        btn_row = QHBoxLayout()
        self._import_btn = QPushButton("Import Settings…")
        self._import_btn.setToolTip("Load settings from a JSON file into this dialog")
        self._export_btn = QPushButton("Export Settings…")
        self._export_btn.setToolTip("Save current settings to a JSON file")
        btn_row.addWidget(self._import_btn)
        btn_row.addWidget(self._export_btn)
        btn_row.addStretch()
        self._ok_btn = QPushButton("OK")
        self._ok_btn.setFixedWidth(88)
        self._ok_btn.setDefault(True)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setFixedWidth(88)
        btn_row.addWidget(self._ok_btn)
        btn_row.addWidget(self._cancel_btn)
        right.addLayout(btn_row)

        right_widget = QWidget()
        right_widget.setLayout(right)
        root.addWidget(right_widget, 1)

        # ---- Connections ----
        self._sidebar.currentRowChanged.connect(self._pages.setCurrentIndex)
        self._ok_btn.clicked.connect(self._save_and_accept)
        self._cancel_btn.clicked.connect(self.reject)
        self._import_btn.clicked.connect(self._import_settings)
        self._export_btn.clicked.connect(self._export_settings)

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def _build_general_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("<b>General</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        note = QLabel(
            "General application preferences will be available here in a future release.\n\n"
            "Current settings such as theme can be changed via the Themes menu."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def _build_python_runtime_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("<b>Python Runtime</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        layout.addWidget(QLabel("<b>VIBRANTE_PYTHONPATH</b>"))
        desc = QLabel(
            "Extra Python package/library directories injected into sys.path at startup. "
            "Enter one absolute path per line. Paths that do not exist are ignored."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._pythonpath_edit = QPlainTextEdit()
        self._pythonpath_edit.setPlaceholderText(
            "C:\\MyLibs\\python\nD:\\studio\\tools\\python"
        )
        self._pythonpath_edit.setMinimumHeight(120)
        layout.addWidget(self._pythonpath_edit)

        browse_btn = QPushButton("Browse && Add Directory…")
        browse_btn.clicked.connect(self._browse_pythonpath)
        layout.addWidget(browse_btn)

        layout.addSpacing(8)
        layout.addWidget(QLabel("<b>Current sys.path preview</b> (VIBRANTE_PYTHONPATH entries only):"))
        self._syspath_preview = QPlainTextEdit()
        self._syspath_preview.setReadOnly(True)
        self._syspath_preview.setMaximumHeight(80)
        self._syspath_preview.setPlaceholderText("(none yet applied)")
        layout.addWidget(self._syspath_preview)

        layout.addStretch()
        return page

    def _build_app_paths_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("<b>Application Paths</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        # v_nodes_dir
        layout.addWidget(QLabel("<b>v_nodes_dir</b> — Extra Node Directories"))
        nodes_desc = QLabel(
            "Additional directories scanned for .json node definitions at startup. "
            "One absolute path per line. Changes take effect after restarting the application."
        )
        nodes_desc.setWordWrap(True)
        layout.addWidget(nodes_desc)

        self._v_nodes_dir_edit = QPlainTextEdit()
        self._v_nodes_dir_edit.setPlaceholderText(
            "C:\\MyStudio\\nodes\nD:\\pipeline\\vibrante_nodes"
        )
        self._v_nodes_dir_edit.setMinimumHeight(80)
        self._v_nodes_dir_edit.setMaximumHeight(110)
        layout.addWidget(self._v_nodes_dir_edit)

        nodes_browse_btn = QPushButton("Browse && Add Directory…")
        nodes_browse_btn.clicked.connect(self._browse_v_nodes_dir)
        layout.addWidget(nodes_browse_btn)

        layout.addSpacing(8)

        # v_scripts_path
        layout.addWidget(QLabel("<b>v_scripts_path</b> — Extra Script Directories"))
        scripts_desc = QLabel(
            "Additional directories scanned for .py scripts in the Scripts menu. "
            "One absolute path per line. Use Scripts → Refresh Scripts to apply without restarting."
        )
        scripts_desc.setWordWrap(True)
        layout.addWidget(scripts_desc)

        self._v_scripts_path_edit = QPlainTextEdit()
        self._v_scripts_path_edit.setPlaceholderText(
            "C:\\MyStudio\\scripts\nD:\\pipeline\\vibrante_scripts"
        )
        self._v_scripts_path_edit.setMinimumHeight(80)
        self._v_scripts_path_edit.setMaximumHeight(110)
        layout.addWidget(self._v_scripts_path_edit)

        scripts_browse_btn = QPushButton("Browse && Add Directory…")
        scripts_browse_btn.clicked.connect(self._browse_v_scripts_path)
        layout.addWidget(scripts_browse_btn)

        layout.addStretch()
        return page

    def _build_env_vars_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("<b>Environment Variables</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        desc = QLabel(
            "Custom variables set in the current process environment (os.environ). "
            "These are accessible inside nodes and workflows via os.environ.get()."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._var_table = QTableWidget(0, 2)
        self._var_table.setHorizontalHeaderLabels(["Variable Name", "Value"])
        self._var_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._var_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._var_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._var_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._var_table.verticalHeader().setVisible(False)
        layout.addWidget(self._var_table, 1)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Variable")
        add_btn.clicked.connect(self._add_variable_row)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_variable_row)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return page

    def _build_vibrante_vars_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("<b>Vibrante-Node Variables</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        desc = QLabel(
            "Built-in environment variables used by the Vibrante-Node runtime. "
            "Values are read-only — set them via your Houdini package JSON or system environment."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._vibrante_vars_table = QTableWidget(0, 3)
        self._vibrante_vars_table.setHorizontalHeaderLabels(["Variable", "Current Value", "Description"])
        hh = self._vibrante_vars_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        self._vibrante_vars_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._vibrante_vars_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._vibrante_vars_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._vibrante_vars_table.verticalHeader().setVisible(False)
        self._vibrante_vars_table.setAlternatingRowColors(True)
        layout.addWidget(self._vibrante_vars_table, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Re-read current runtime values from os.environ")
        refresh_btn.clicked.connect(self._load_vibrante_vars)
        btn_row = QHBoxLayout()
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return page

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def _load_settings(self):
        # Python Runtime page
        paths = env_manager.get_vibrante_pythonpath()
        self._pythonpath_edit.setPlainText("\n".join(paths))
        self._refresh_syspath_preview()

        # Application Paths page
        self._v_nodes_dir_edit.setPlainText("\n".join(env_manager.get_v_nodes_dir()))
        self._v_scripts_path_edit.setPlainText("\n".join(env_manager.get_v_scripts_path()))

        # Environment Variables page
        custom = env_manager.get_custom_variables()
        self._var_table.setRowCount(0)
        for name, value in custom.items():
            self._append_var_row(name, value)

        # Vibrante Variables page
        self._load_vibrante_vars()

    def _load_vibrante_vars(self):
        """Populate the Vibrante Variables table from current os.environ values."""
        self._vibrante_vars_table.setRowCount(0)
        for var_name, description in _VIBRANTE_BUILTIN_VARS:
            row = self._vibrante_vars_table.rowCount()
            self._vibrante_vars_table.insertRow(row)

            name_item = QTableWidgetItem(var_name)
            value = os.environ.get(var_name, "")
            value_item = QTableWidgetItem(value if value else "(not set)")
            desc_item = QTableWidgetItem(description)

            if not value:
                gray = QtGui.QColor(128, 128, 128)
                value_item.setForeground(gray)

            self._vibrante_vars_table.setItem(row, 0, name_item)
            self._vibrante_vars_table.setItem(row, 1, value_item)
            self._vibrante_vars_table.setItem(row, 2, desc_item)
        self._vibrante_vars_table.resizeColumnsToContents()
        self._vibrante_vars_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def _refresh_syspath_preview(self):
        configured = set(env_manager.get_vibrante_pythonpath())
        applied = [p for p in configured if p in sys.path]
        self._syspath_preview.setPlainText("\n".join(applied) if applied else "")

    def _save_and_accept(self):
        # Collect VIBRANTE_PYTHONPATH
        raw_paths = self._pythonpath_edit.toPlainText()
        paths = [p.strip() for p in raw_paths.splitlines() if p.strip()]

        # Validate paths — warn but don't block
        missing = [p for p in paths if not os.path.isdir(p)]
        if missing:
            msg = "The following paths do not exist and will be ignored at runtime:\n\n"
            msg += "\n".join(missing)
            msg += "\n\nSave anyway?"
            reply = QMessageBox.question(
                self, "Path Warning", msg,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply == QMessageBox.No:
                return

        # Collect custom variables
        variables = {}
        for row in range(self._var_table.rowCount()):
            name_item = self._var_table.item(row, 0)
            value_item = self._var_table.item(row, 1)
            name = (name_item.text().strip() if name_item else "")
            value = (value_item.text().strip() if value_item else "")
            if name:
                variables[name] = value

        # Validate variable names
        invalid = [n for n in variables if not n.replace("_", "").isalnum()]
        if invalid:
            QMessageBox.warning(
                self, "Invalid Variable Names",
                "Variable names must be alphanumeric (underscores allowed):\n" + "\n".join(invalid)
            )
            return

        # Collect Application Paths
        v_nodes_dir = [
            p.strip()
            for p in self._v_nodes_dir_edit.toPlainText().splitlines()
            if p.strip()
        ]
        v_scripts_path = [
            p.strip()
            for p in self._v_scripts_path_edit.toPlainText().splitlines()
            if p.strip()
        ]

        # Persist and apply
        env_manager.set_vibrante_pythonpath(paths)
        env_manager.set_v_nodes_dir(v_nodes_dir)
        env_manager.set_v_scripts_path(v_scripts_path)
        env_manager.set_custom_variables(variables)
        env_manager.reinitialize()

        self.accept()

    # ------------------------------------------------------------------
    # Table helpers
    # ------------------------------------------------------------------

    def _append_var_row(self, name: str = "", value: str = ""):
        row = self._var_table.rowCount()
        self._var_table.insertRow(row)
        self._var_table.setItem(row, 0, QTableWidgetItem(name))
        self._var_table.setItem(row, 1, QTableWidgetItem(value))

    def _add_variable_row(self):
        self._append_var_row()
        self._var_table.scrollToBottom()
        row = self._var_table.rowCount() - 1
        self._var_table.editItem(self._var_table.item(row, 0))

    def _remove_variable_row(self):
        rows = self._var_table.selectedItems()
        if rows:
            self._var_table.removeRow(self._var_table.currentRow())

    def _import_settings(self):
        """Load settings from a JSON file and populate the UI widgets."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "", "Vibrante Settings (*.json);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", f"Could not read settings file:\n{exc}")
            return
        if not isinstance(data, dict):
            QMessageBox.critical(self, "Import Failed", "Settings file format is invalid (expected a JSON object).")
            return

        # Populate UI widgets — user still clicks OK to persist
        if "vibrante_pythonpath" in data and isinstance(data["vibrante_pythonpath"], list):
            self._pythonpath_edit.setPlainText("\n".join(data["vibrante_pythonpath"]))
        if "v_nodes_dir" in data and isinstance(data["v_nodes_dir"], list):
            self._v_nodes_dir_edit.setPlainText("\n".join(data["v_nodes_dir"]))
        if "v_scripts_path" in data and isinstance(data["v_scripts_path"], list):
            self._v_scripts_path_edit.setPlainText("\n".join(data["v_scripts_path"]))
        if "custom_variables" in data and isinstance(data["custom_variables"], dict):
            self._var_table.setRowCount(0)
            for name, value in data["custom_variables"].items():
                self._append_var_row(str(name), str(value))

        print(f"[Settings] Imported settings from: {path}")

    def _export_settings(self):
        """Save the current UI state to a JSON file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "vibrante_settings.json",
            "Vibrante Settings (*.json);;All Files (*)"
        )
        if not path:
            return

        # Read current UI state (not necessarily saved to config yet)
        data = {
            "vibrante_pythonpath": [
                p.strip()
                for p in self._pythonpath_edit.toPlainText().splitlines()
                if p.strip()
            ],
            "v_nodes_dir": [
                p.strip()
                for p in self._v_nodes_dir_edit.toPlainText().splitlines()
                if p.strip()
            ],
            "v_scripts_path": [
                p.strip()
                for p in self._v_scripts_path_edit.toPlainText().splitlines()
                if p.strip()
            ],
            "custom_variables": {
                self._var_table.item(r, 0).text().strip(): self._var_table.item(r, 1).text().strip()
                for r in range(self._var_table.rowCount())
                if self._var_table.item(r, 0) and self._var_table.item(r, 0).text().strip()
            },
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", f"Could not write settings file:\n{exc}")
            return

        print(f"[Settings] Exported settings to: {path}")

    def _browse_pythonpath(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Python Library Directory")
        if directory:
            current = self._pythonpath_edit.toPlainText().strip()
            if current:
                self._pythonpath_edit.setPlainText(current + "\n" + directory)
            else:
                self._pythonpath_edit.setPlainText(directory)

    def _browse_v_nodes_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Node Directory")
        if directory:
            current = self._v_nodes_dir_edit.toPlainText().strip()
            if current:
                self._v_nodes_dir_edit.setPlainText(current + "\n" + directory)
            else:
                self._v_nodes_dir_edit.setPlainText(directory)

    def _browse_v_scripts_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Script Directory")
        if directory:
            current = self._v_scripts_path_edit.toPlainText().strip()
            if current:
                self._v_scripts_path_edit.setPlainText(current + "\n" + directory)
            else:
                self._v_scripts_path_edit.setPlainText(directory)


