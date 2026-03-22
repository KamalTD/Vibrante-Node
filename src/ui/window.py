import sys
import os
import shutil
import asyncio
import threading
from src.utils.qt_compat import QtWidgets, QtCore, QtGui, exec_dialog

QMainWindow = QtWidgets.QMainWindow
QAction = QtWidgets.QAction
QFileDialog = QtWidgets.QFileDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QWidget = QtWidgets.QWidget
QGraphicsView = QtWidgets.QGraphicsView
QGraphicsScene = QtWidgets.QGraphicsScene
QToolBar = QtWidgets.QToolBar
QMessageBox = QtWidgets.QMessageBox
QDockWidget = QtWidgets.QDockWidget
QMenu = QtWidgets.QMenu
QStyle = QtWidgets.QStyle
QTabWidget = QtWidgets.QTabWidget
QStatusBar = QtWidgets.QStatusBar
QLabel = QtWidgets.QLabel
Qt = QtCore.Qt
QCursor = QtGui.QCursor
from src.ui.canvas.scene import NodeScene
from src.ui.canvas.view import NodeView
from src.ui.node_builder import NodeBuilderDialog
from src.ui.library_panel import LibraryPanel
from src.ui.log_panel import LogPanel
from src.ui.scripting_console import ScriptingConsole
from src.core.models import WorkflowModel
from src.core.registry import NodeRegistry
from src.core.engine import NetworkExecutor
from src.ui.node_widget import NodeWidget

from src.ui.gemini_api_dialog import GeminiApiDialog

class MainWindow(QMainWindow):
    def __init__(self):
        print("MainWindow init started")
        super().__init__()
        self._is_executing = False # Execution guard
        self._is_dark_theme = True # Track theme state
        self.setWindowTitle("Vibrante-Node Pipeline Editor")
        self.resize(1200, 800)
        
        self._apply_dark_theme()

        # Initialize Registry
        self.nodes_dir = os.path.abspath(os.path.join(os.getcwd(), 'nodes'))
        NodeRegistry.load_all_with_extras(self.nodes_dir)

        # Setup Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Setup Panels
        self.library_panel = LibraryPanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_panel)
        
        self.log_panel = LogPanel(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_panel)
        self.log_panel.log("Application started", "info")
        
        self.scripting_console = ScriptingConsole(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.scripting_console)

        # Enrich autocomplete with PYTHONPATH module names
        self._enrich_autocomplete_from_pythonpath()
        
        # Connect Library Signals
        self.library_panel.node_selected.connect(self._on_node_selected)
        self.library_panel.edit_requested.connect(self._on_edit_requested)
        self.library_panel.delete_requested.connect(self._on_delete_requested)

        # Setup Menu & Toolbars
        self._init_menu()
        self._init_toolbar()
        self._init_statusbar()

        # Create initial tab
        self.add_new_workflow()

    def _init_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setFixedWidth(120)
        self.statusbar.addWidget(self.status_label)
        
        self.node_desc_label = QLabel("")
        self.node_desc_label.setStyleSheet("color: #aaa; margin-left: 20px;")
        self.statusbar.addPermanentWidget(self.node_desc_label, 1) # Description spans most of the space

    def add_new_workflow(self, name="New Workflow"):
        scene = NodeScene(self)
        view = NodeView(scene, self)
        index = self.tabs.addTab(view, name)
        self.tabs.setCurrentIndex(index)
        
        # Connect selection signal
        scene.selectionChanged.connect(self._on_selection_changed)
        
        # Apply current theme
        scene.apply_theme(is_dark=self._is_dark_theme)
        
        return view

    def _on_selection_changed(self):
        scene = self.get_current_scene()
        if not scene: return
        
        selected_items = scene.selectedItems()
        if len(selected_items) == 1 and isinstance(selected_items[0], NodeWidget):
            node = selected_items[0]
            desc = getattr(node.node_definition, 'description', "No description available.")
            self.node_desc_label.setText(f"Selected Node: {node.node_definition.name} - {desc}")
        else:
            self.node_desc_label.setText("")

    def _on_tab_changed(self, index):
        # Refresh description for new tab's selection
        self._on_selection_changed()

    def _close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            QMessageBox.information(self, "Info", "Cannot close the last workflow.")

    def get_current_view(self) -> NodeView:
        return self.tabs.currentWidget()

    def get_current_scene(self) -> NodeScene:
        view = self.get_current_view()
        return view.scene() if view else None

    def _init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New Workflow', self)
        new_action.setShortcut('Ctrl+T')
        new_action.triggered.connect(lambda: self.add_new_workflow())
        file_menu.addAction(new_action)

        save_action = QAction('&Save Workflow', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(save_action)

        load_action = QAction('&Load Workflow', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_workflow)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_python_action = QAction('Export Workflow as &Python...', self)
        export_python_action.setShortcut('Ctrl+Shift+E')
        export_python_action.triggered.connect(self._export_as_python)
        file_menu.addAction(export_python_action)

        import_python_action = QAction('&Import Python as Workflow...', self)
        import_python_action.setShortcut('Ctrl+Shift+I')
        import_python_action.triggered.connect(self._import_from_python)
        file_menu.addAction(import_python_action)

        # Edit Menu
        edit_menu = menubar.addMenu('&Edit')
        
        undo_action = QAction('&Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('&Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()

        copy_action = QAction('&Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self._copy_selection)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('&Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self._paste_selection)
        edit_menu.addAction(paste_action)

        node_menu = menubar.addMenu('&Nodes')
        new_node_action = QAction('&New Node Builder...', self)
        new_node_action.setShortcut('Ctrl+N')
        new_node_action.triggered.connect(self.open_node_builder)
        node_menu.addAction(new_node_action)

        load_node_action = QAction('&Load Node from JSON...', self)
        load_node_action.triggered.connect(self.load_node_json)
        node_menu.addAction(load_node_action)

        # Window Menu
        window_menu = menubar.addMenu('&Window')
        
        toggle_library = self.library_panel.toggleViewAction()
        toggle_library.setText("Show/Hide Library")
        window_menu.addAction(toggle_library)
        
        toggle_log = self.log_panel.toggleViewAction()
        toggle_log.setText("Show/Hide Event Log")
        window_menu.addAction(toggle_log)
        
        toggle_script = self.scripting_console.toggleViewAction()
        toggle_script.setText("Show/Hide Scripting Console")
        window_menu.addAction(toggle_script)

        # Themes Menu
        theme_menu = menubar.addMenu('&Themes')
        dark_act = QAction("Dark Theme", self)
        dark_act.triggered.connect(self._apply_dark_theme)
        theme_menu.addAction(dark_act)
        
        light_act = QAction("Light Theme", self)
        light_act.triggered.connect(self._apply_light_theme)
        theme_menu.addAction(light_act)

        # Scripts Menu
        self._init_scripts_menu(menubar)

        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        user_guide_act = QAction('User Guide', self)
        user_guide_act.triggered.connect(lambda: self._open_doc("USER_GUIDE.md"))
        help_menu.addAction(user_guide_act)
        
        node_builder_act = QAction('Node Builder API', self)
        node_builder_act.triggered.connect(lambda: self._open_doc("NODE_BUILDER_API.md"))
        help_menu.addAction(node_builder_act)
        
        automation_act = QAction('Automation API', self)
        automation_act.triggered.connect(lambda: self._open_doc("AUTOMATION_API.md"))
        help_menu.addAction(automation_act)
        
        dev_doc_act = QAction('Developer Documentation', self)
        dev_doc_act.triggered.connect(lambda: self._open_doc("DEVELOPER.md"))
        help_menu.addAction(dev_doc_act)
        
        feature_list_act = QAction('Technical Feature List', self)
        feature_list_act.triggered.connect(lambda: self._open_doc("DOCUMENTATION.md"))
        help_menu.addAction(feature_list_act)

        env_vars_act = QAction('Environment Variables', self)
        env_vars_act.triggered.connect(self._show_env_vars_help)
        help_menu.addAction(env_vars_act)

        help_menu.addSeparator()

        gemini_act = QAction('Link to Gemini', self)
        gemini_act.triggered.connect(self._link_to_gemini)
        help_menu.addAction(gemini_act)
        
        help_menu.addSeparator()
        
        about_act = QAction('About Vibrante-Node', self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _open_doc(self, filename):
        import webbrowser
        path = os.path.abspath(os.path.join(os.getcwd(), filename))
        if os.path.exists(path):
            webbrowser.open(path)
        else:
            QMessageBox.critical(self, "Error", f"Documentation file not found: {filename}")

    def _init_scripts_menu(self, menubar):
        """Build the Scripts menu from v_scripts/ and v_scripts_path directories."""
        self.scripts_menu = menubar.addMenu('&Scripts')
        self._populate_scripts_menu()

    def _get_script_dirs(self):
        """Collect all script directories (default + env var)."""
        script_dirs = []

        # Default: v_scripts/ in the app folder
        self._default_scripts_dir = os.path.abspath(os.path.join(os.getcwd(), 'v_scripts'))
        if not os.path.exists(self._default_scripts_dir):
            os.makedirs(self._default_scripts_dir)
        script_dirs.append(self._default_scripts_dir)

        # Extra directories from v_scripts_path env var
        extra_paths = os.environ.get('v_scripts_path', '')
        if extra_paths:
            for p in extra_paths.split(os.pathsep):
                p = p.strip()
                if p and os.path.isdir(p) and p not in script_dirs:
                    script_dirs.append(p)

        return script_dirs

    def _populate_scripts_menu(self):
        """Scan script directories and populate the Scripts menu."""
        self.scripts_menu.clear()

        script_dirs = self._get_script_dirs()

        # Scan for .py files
        scripts_found = []
        for dir_path in script_dirs:
            if not os.path.isdir(dir_path):
                continue
            for filename in sorted(os.listdir(dir_path)):
                if filename.endswith('.py'):
                    full_path = os.path.join(dir_path, filename)
                    scripts_found.append((filename, full_path))

        if not scripts_found:
            no_scripts_action = QAction('(No scripts found)', self)
            no_scripts_action.setEnabled(False)
            self.scripts_menu.addAction(no_scripts_action)
        else:
            for name, path in scripts_found:
                action = QAction(name, self)
                action.setToolTip(path)
                action.triggered.connect(lambda checked, p=path: self._run_user_script(p))
                self.scripts_menu.addAction(action)

        self.scripts_menu.addSeparator()

        refresh_action = QAction('Refresh Scripts', self)
        refresh_action.triggered.connect(self._populate_scripts_menu)
        self.scripts_menu.addAction(refresh_action)

        open_folder_action = QAction('Open Scripts Folder', self)
        open_folder_action.triggered.connect(self._open_scripts_folder)
        self.scripts_menu.addAction(open_folder_action)

    def _open_scripts_folder(self):
        """Open the default scripts folder in the file manager."""
        import subprocess
        folder = getattr(self, '_default_scripts_dir', os.path.abspath(os.path.join(os.getcwd(), 'v_scripts')))
        if sys.platform == 'win32':
            os.startfile(folder)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folder])
        else:
            subprocess.Popen(['xdg-open', folder])

    def _run_user_script(self, script_path):
        """Execute a user script in the scripting console context."""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()

            context = {
                "app": self,
                "scene": self.get_current_scene(),
                "registry": NodeRegistry,
                "print": self.scripting_console.console_print,
            }

            exec(script_code, context)
            self.log_panel.log(f"Script '{os.path.basename(script_path)}' executed successfully.", "success")
        except Exception:
            import traceback
            error_msg = traceback.format_exc()
            self.log_panel.log(f"Script Error in '{os.path.basename(script_path)}':\n{error_msg}", "error")
            QMessageBox.critical(self, "Script Error", f"Error running script:\n{error_msg}")

    def _enrich_autocomplete_from_pythonpath(self):
        """Scan PYTHONPATH directories for top-level module/package names
        and add them to the scripting console's autocomplete."""
        extra_words = set()
        pythonpath = os.environ.get('PYTHONPATH', '')
        if pythonpath:
            for p in pythonpath.split(os.pathsep):
                p = p.strip()
                if not p or not os.path.isdir(p):
                    continue
                for entry in os.listdir(p):
                    full = os.path.join(p, entry)
                    # Python packages (directories with __init__.py)
                    if os.path.isdir(full) and os.path.exists(os.path.join(full, '__init__.py')):
                        extra_words.add(entry)
                    # Python modules (.py files)
                    elif entry.endswith('.py') and entry != '__init__.py':
                        extra_words.add(entry[:-3])
                    # Compiled extensions (.pyd on Windows, .so on Unix)
                    elif entry.endswith(('.pyd', '.so')):
                        mod_name = entry.split('.')[0]
                        extra_words.add(mod_name)

        if extra_words:
            existing = [
                "app", "scene", "registry", "print",
                "add_node_by_name", "connect_nodes", "find_node_by_name", "set_parameter",
                "NodeWidget", "Edge", "NodeRegistry", "execute"
            ]
            combined = sorted(set(existing) | extra_words)
            self.scripting_console.editor.set_completer_list(combined)

    def _show_env_vars_help(self):
        current_nodes_dir = os.environ.get('v_nodes_dir', '(not set)')
        current_scripts_path = os.environ.get('v_scripts_path', '(not set)')
        current_pythonpath = os.environ.get('PYTHONPATH', '(not set)')

        QMessageBox.information(self, "Environment Variables",
            "<h3>Environment Variables</h3>"
            "<p>Vibrante-Node supports the following environment variables to extend "
            "the application with external resources. All variables support multiple "
            "paths separated by <code>;</code> (Windows) or <code>:</code> (Linux/macOS).</p>"
            "<hr>"
            "<h4>v_nodes_dir</h4>"
            "<p>Append extra directories containing node definition JSON files. "
            "Nodes found in these paths will be loaded into the Library panel alongside built-in nodes.</p>"
            "<p><b>Example (Windows):</b><br>"
            "<code>set v_nodes_dir=C:\\my_nodes;D:\\shared_nodes</code></p>"
            "<p><b>Example (PowerShell):</b><br>"
            "<code>$env:v_nodes_dir = \"C:\\my_nodes;D:\\shared_nodes\"</code></p>"
            "<hr>"
            "<h4>v_scripts_path</h4>"
            "<p>Append extra directories containing Python scripts. Scripts found in these paths "
            "will appear in the <b>Scripts</b> menu. "
            "By default, the <code>v_scripts/</code> folder in the app directory is always included.</p>"
            "<p><b>Example (Windows):</b><br>"
            "<code>set v_scripts_path=%v_scripts_path%;C:\\my_scripts</code></p>"
            "<p><b>Example (PowerShell):</b><br>"
            "<code>$env:v_scripts_path = \"$env:v_scripts_path;C:\\my_scripts\"</code></p>"
            "<hr>"
            "<h4>PYTHONPATH</h4>"
            "<p>Append extra directories containing Python libraries/packages. "
            "These paths are added to <code>sys.path</code> at startup, making external libraries "
            "available for <code>import</code> in node scripts and the scripting console. "
            "Discovered module names are also added to the code editor autocomplete.</p>"
            "<p><b>Example (Windows):</b><br>"
            "<code>set PYTHONPATH=%PYTHONPATH%;C:\\my_libs</code></p>"
            "<p><b>Example (PowerShell):</b><br>"
            "<code>$env:PYTHONPATH = \"$env:PYTHONPATH;C:\\my_libs\"</code></p>"
            "<hr>"
            "<h4>Current Values</h4>"
            f"<p><b>v_nodes_dir:</b> <code>{current_nodes_dir}</code></p>"
            f"<p><b>v_scripts_path:</b> <code>{current_scripts_path}</code></p>"
            f"<p><b>PYTHONPATH:</b> <code>{current_pythonpath}</code></p>"
        )

    def _show_about(self):
        description = (
            "Vibrante-Node is a Python-node-based visual framework for building modular systems "
            "through connected nodes and data flows. It provides an intuitive graph interface "
            "where complex logic can be constructed visually by linking nodes together.<br><br>"
            "The project focuses on flexibility, extensibility, and developer productivity, "
            "making it suitable for building tools such as visual pipelines, automation workflows, "
            "and data-processing graphs."
        )
        
        license_text = (
            "Permission is granted to use, modify, and test this software for personal and non-commercial purposes.<br><br>"
            "Commercial use, redistribution in commercial products, or use within commercial services requires "
            "written permission from the author."
        )
        
        QMessageBox.about(self, "About Vibrante-Node",
            f"<h3>Vibrante-Node v1.1.5</h3>"
            f"<p>{description}</p>"
            f"<hr>"
            f"<p><b>Copyright &copy; 2026 Mahmoud Kamal - KamalTD</b></p>"
            f"<p>GitHub: <a href='https://github.com/KamalTD'>https://github.com/KamalTD</a></p>"
            f"<p>Built with PyQt5, Asyncio, and ❤️</p>"
            f"<hr>"
            f"<p><small>{license_text}</small></p>")

    def _link_to_gemini(self):
        import webbrowser
        webbrowser.open("https://aistudio.google.com/app/")
        dialog = GeminiApiDialog(self)
        exec_dialog(dialog)

    def _init_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        # New Tab
        new_act = QAction(self.style().standardIcon(QStyle.SP_FileIcon), "New Workflow", self)
        new_act.setToolTip("Create new workflow tab (Ctrl+T)")
        new_act.triggered.connect(lambda: self.add_new_workflow())
        toolbar.addAction(new_act)

        toolbar.addSeparator()

        # New Node Builder
        new_node_act = QAction(self.style().standardIcon(QStyle.SP_FileDialogNewFolder), "New Node Builder", self)
        new_node_act.setToolTip("Open Node Builder Dialog (Ctrl+N)")
        new_node_act.triggered.connect(self.open_node_builder)
        toolbar.addAction(new_node_act)
        
        toolbar.addSeparator()
        
        # Save Workflow
        save_act = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Save Workflow", self)
        save_act.setToolTip("Save current workflow to JSON (Ctrl+S)")
        save_act.triggered.connect(self.save_workflow)
        toolbar.addAction(save_act)
        
        # Load Workflow
        load_act = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "Load Workflow", self)
        load_act.setToolTip("Load workflow from JSON (Ctrl+O)")
        load_act.triggered.connect(self.load_workflow)
        toolbar.addAction(load_act)
        
        toolbar.addSeparator()
        
        # Delete Selected
        self.delete_btn = QAction(self.style().standardIcon(QStyle.SP_TrashIcon), "Delete Selected", self)
        self.delete_btn.setToolTip("Delete selected nodes or wires (Del)")
        self.delete_btn.triggered.connect(self._delete_selected)
        toolbar.addAction(self.delete_btn)
        
        toolbar.addSeparator()
        
        # Run Workflow
        self.execute_btn = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), "Run Workflow", self)
        self.execute_btn.setShortcut("F5")
        self.execute_btn.setToolTip("Execute the active pipeline (F5)")
        self.execute_btn.triggered.connect(self.execute_pipeline)
        toolbar.addAction(self.execute_btn)

        # Stop Workflow
        self.stop_btn = QAction(self.style().standardIcon(QStyle.SP_MediaStop), "Stop Workflow", self)
        self.stop_btn.setShortcut("Shift+F5")
        self.stop_btn.setToolTip("Stop the active pipeline (Shift+F5)")
        self.stop_btn.triggered.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        toolbar.addAction(self.stop_btn)

    def _delete_selected(self):
        scene = self.get_current_scene()
        if not scene: return
        QKeyEvent = QtGui.QKeyEvent
        QEvent = QtCore.QEvent
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        scene.keyPressEvent(event)

    def _apply_dark_theme(self):
        self._is_dark_theme = True
        QApplication = QtWidgets.QApplication
        app = QApplication.instance()
        app.setStyleSheet("""
            QMainWindow, QDialog { background-color: #2b2b2b; color: #ffffff; }
            QDockWidget { color: #ffffff; }
            QDockWidget::title { background: #3c3f41; padding-left: 5px; }
            QMenuBar { background-color: #3c3f41; color: #ffffff; }
            QMenuBar::item:selected { background-color: #4b4d4d; }
            QMenu { background-color: #3c3f41; color: #ffffff; border: 1px solid #2b2b2b; }
            QMenu::item:selected { background-color: #4b4d4d; }
            QToolBar { background-color: #3c3f41; border: none; }
            QToolTip { background-color: #4b4d4d; color: #ffffff; border: 1px solid #2b2b2b; }
            QPushButton { background-color: #4b4d4d; color: white; border: 1px solid #3c3f41; padding: 5px; }
            QPushButton:hover { background-color: #5c5e5e; }
            QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QHeaderView { background-color: #2b2b2b; color: #d4d4d4; border: 1px solid #3c3f41; }
            QHeaderView::section { background-color: #3c3f41; color: white; }
            QLabel { color: #ffffff; }
            QComboBox, QSpinBox, QDoubleSpinBox { background-color: #3c3f41; color: white; border: 1px solid #2b2b2b; }
            QTabBar::tab { background: #3c3f41; color: #ffffff; padding: 8px; border: 1px solid #2b2b2b; }
            QTabBar::tab:selected { background: #4b4d4d; border-bottom: 2px solid #50fa7b; }
        """)
        if hasattr(self, 'library_panel'):
            self.library_panel.apply_theme(is_dark=True)
        if hasattr(self, 'log_panel'):
            self.log_panel.apply_theme(is_dark=True)
            
        # Apply to all workflow scenes
        if hasattr(self, 'tabs'):
            for i in range(self.tabs.count()):
                view = self.tabs.widget(i)
                if isinstance(view, NodeView):
                    view.scene().apply_theme(is_dark=True)

    def _apply_light_theme(self):
        self._is_dark_theme = False
        QApplication = QtWidgets.QApplication
        app = QApplication.instance()
        app.setStyleSheet("") # Reset to default
        if hasattr(self, 'library_panel'):
            self.library_panel.apply_theme(is_dark=False)
        if hasattr(self, 'log_panel'):
            self.log_panel.apply_theme(is_dark=False)
            
        # Apply to all workflow scenes
        if hasattr(self, 'tabs'):
            for i in range(self.tabs.count()):
                view = self.tabs.widget(i)
                if isinstance(view, NodeView):
                    view.scene().apply_theme(is_dark=False)

    def _on_node_selected(self, node_id):
        scene = self.get_current_scene()
        view = self.get_current_view()
        if scene and view:
            scene.add_node_by_name(node_id, view.mapToScene(view.rect().center()))

    def _on_edit_requested(self, node_id):
        dialog = NodeBuilderDialog(self, editing_node_id=node_id)
        if exec_dialog(dialog):
            self.library_panel.refresh()

    def _on_delete_requested(self, node_id):
        # Check if used in ANY scene
        for i in range(self.tabs.count()):
            view = self.tabs.widget(i)
            if any(nw.node_definition.name == node_id for nw in view.scene().nodes):
                res = QMessageBox.warning(self, "Warning", f"Node '{node_id}' is in use in tab '{self.tabs.tabText(i)}'. Continue?", 
                                         QMessageBox.Yes | QMessageBox.No)
                if res == QMessageBox.No: return
        
        NodeRegistry.delete_node(node_id, self.nodes_dir)
        self.library_panel.refresh()

    def open_node_builder(self):
        dialog = NodeBuilderDialog(self)
        if exec_dialog(dialog):
            self.library_panel.refresh()

    def load_node_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Node JSON", "", "Node Files (*.json)")
        if not file_path:
            return

        try:
            # Validate the JSON content first using the registry
            success = NodeRegistry.load_node(file_path)
            if not success:
                err = NodeRegistry.last_error or "Unknown validation error"
                QMessageBox.critical(self, "Error", f"Invalid node definition JSON:\n\n{err}")
                return

            # If valid, copy it to the permanent nodes directory
            node_id = os.path.splitext(os.path.basename(file_path))[0]
            # Get actual node_id from definition if possible to ensure consistency
            defn = NodeRegistry.get_definition(node_id)
            if defn:
                node_id = defn.node_id
            
            dest_path = os.path.join(self.nodes_dir, f"{node_id}.json")
            
            if os.path.exists(dest_path):
                res = QMessageBox.question(self, "Overwrite", f"Node '{node_id}' already exists. Overwrite?", 
                                         QMessageBox.Yes | QMessageBox.No)
                if res == QMessageBox.No: return

            shutil.copy2(file_path, dest_path)
            self.library_panel.refresh()
            self.log_panel.log(f"Node '{node_id}' added to library from {file_path}", "success")
            QMessageBox.information(self, "Success", f"Node '{node_id}' has been added to your library.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load node: {str(e)}")

    def save_workflow(self):
        scene = self.get_current_scene()
        if not scene: return
        
        file_path = scene.file_path
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Workflow", "workflows", "Workflow Files (*.json)")
        
        if file_path:
            if not file_path.endswith(".json"): file_path += ".json"
            workflow_model = scene.to_workflow_model()
            with open(file_path, "w") as f:
                f.write(workflow_model.model_dump_json(indent=4))
            
            scene.file_path = file_path
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))
            self.log_panel.log(f"Workflow saved: {file_path}", "success")

    def load_workflow(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Workflow", "workflows", "Workflow Files (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                json_data = f.read()
            workflow_model = WorkflowModel.model_validate_json(json_data)
            
            # Create a new tab for loaded workflow
            view = self.add_new_workflow(os.path.basename(file_path))
            scene = view.scene()
            scene.from_workflow_model(workflow_model)
            scene.file_path = file_path # Track path for smart save
            self.log_panel.log(f"Workflow loaded: {file_path}", "info")

    def _export_as_python(self):
        scene = self.get_current_scene()
        if not scene:
            return
        workflow_model = scene.to_workflow_model()
        if not workflow_model.nodes:
            QMessageBox.information(self, "Export", "No nodes in the current workflow.")
            return
        from src.ui.export_python_dialog import ExportPythonDialog
        dialog = ExportPythonDialog(workflow_model, self)
        exec_dialog(dialog)

    def _import_from_python(self):
        from src.ui.import_python_dialog import ImportPythonDialog
        dialog = ImportPythonDialog(self)
        if exec_dialog(dialog):
            workflow_model = dialog.get_workflow_model()
            if workflow_model:
                view = self.add_new_workflow("Imported from Python")
                scene = view.scene()
                scene.from_workflow_model(workflow_model)
                self.log_panel.log("Workflow imported from Python code.", "success")

    def execute_pipeline(self):
        if self._is_executing:
            return
        self._is_executing = True
            
        scene = self.get_current_scene()
        if not scene: 
            self._is_executing = False
            return
        
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Running...")
        tab_name = self.tabs.tabText(self.tabs.currentIndex())
        self.log_panel.log(f"Starting execution for [{tab_name}]...", "execution")

        # Build node widget cache for fast lookup during execution
        self._node_widget_cache = {}
        for widget in scene.nodes:
            self._node_widget_cache[widget.instance_id] = widget

        workflow_model = scene.to_workflow_model()
        
        from src.core.graph import GraphManager
        gm = GraphManager()
        gm.from_model(workflow_model)
        
        self.current_executor = NetworkExecutor(gm)
        self.current_executor.node_started.connect(self._on_node_started)
        self.current_executor.node_finished.connect(self._on_node_finished)
        self.current_executor.node_error.connect(self._on_node_error)
        self.current_executor.node_output.connect(self._on_node_output)
        self.current_executor.node_log.connect(self._on_node_log)
        self.current_executor.execution_finished.connect(self._on_execution_finished)
        
        def run_async_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.current_executor.run())
                loop.close()
            except Exception as e:
                self.current_executor.execution_finished.emit(False)

        threading.Thread(target=run_async_loop, daemon=True).start()

    def stop_execution(self):
        if hasattr(self, 'current_executor') and self.current_executor:
            self.current_executor.stop()
            self.status_label.setText("Stopping...")
            self.log_panel.log("Stop requested...", "warning")

    def _on_execution_finished(self, success):
        self._is_executing = False
        self._node_widget_cache = None
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Ready")
        status = "successfully" if success else "or stopped"
        self.log_panel.log(f"Execution finished {status}.", "info" if success else "warning")

        # After a short delay, reset all nodes to 'idle' to clear status colors
        QTimer = QtCore.QTimer
        QTimer.singleShot(2000, self._reset_node_statuses)

    def _reset_node_statuses(self):
        scene = self.get_current_scene()
        if scene:
            for node in scene.nodes:
                node.set_status("idle")

    def _on_node_started(self, node_instance_id):
        widget = self._find_node_widget(node_instance_id)
        if widget:
            widget.set_status("running")
            if not self.log_panel.silent_mode.isChecked():
                self.log_panel.log(f"Node '{widget.node_definition.name}' started", "execution")

    def _on_node_output(self, node_instance_id, results):
        widget = self._find_node_widget(node_instance_id)
        if widget:
            for name, val in results.items():
                widget.set_parameter(name, val, propagate=False)
            if not self.log_panel.silent_mode.isChecked():
                res_str = ", ".join([f"{k}: {v}" for k, v in results.items()])
                self.log_panel.log(f"Node '{widget.node_definition.name}' output -> {res_str}", "success")

    def _on_node_log(self, node_instance_id, message, level):
        if self.log_panel.silent_mode.isChecked() and level not in ("error", "warning"):
            return
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        self.log_panel.log(f"[{name}] {message}", level)

    def _on_node_finished(self, node_instance_id, status):
        widget = self._find_node_widget(node_instance_id)
        if widget: widget.set_status(status)

    def _on_node_error(self, node_instance_id, error_msg):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        self.log_panel.log(f"Node '{name}' error: {error_msg}", "error")
        QMessageBox.critical(self, "Execution Error", f"Node {name} failed:\n{error_msg}")

    def _find_node_widget(self, instance_id):
        # Build lookup cache on first call per execution
        if not hasattr(self, '_node_widget_cache') or self._node_widget_cache is None:
            self._node_widget_cache = {}
            scene = self.get_current_scene()
            if scene:
                for widget in scene.nodes:
                    self._node_widget_cache[widget.instance_id] = widget
        return self._node_widget_cache.get(instance_id)

    def _copy_selection(self):
        scene = self.get_current_scene()
        if scene:
            scene.copy_selection()

    def _paste_selection(self):
        scene = self.get_current_scene()
        view = self.get_current_view()
        if scene and view:
            # Map mouse position to scene coordinates
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            scene_pos = view.mapToScene(mouse_pos)
            scene.paste_selection(target_pos=scene_pos)

    def _undo(self):
        scene = self.get_current_scene()
        if scene:
            self.log_panel.log("Undoing...", "info")
            scene.undo()

    def _redo(self):
        scene = self.get_current_scene()
        if scene:
            self.log_panel.log("Redoing...", "info")
            scene.redo()
