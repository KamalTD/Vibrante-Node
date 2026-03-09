import sys
import os
import asyncio
import threading
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QToolBar, QMessageBox, QDockWidget, QMenu, QStyle, QTabWidget
from PyQt5.QtCore import Qt
from src.ui.canvas.scene import NodeScene
from src.ui.canvas.view import NodeView
from src.ui.node_builder import NodeBuilderDialog
from src.ui.library_panel import LibraryPanel
from src.ui.log_panel import LogPanel
from src.ui.scripting_console import ScriptingConsole
from src.core.models import WorkflowModel
from src.core.registry import NodeRegistry
from src.core.engine import NetworkExecutor

class MainWindow(QMainWindow):
    def __init__(self):
        print("MainWindow init started")
        super().__init__()
        self.setWindowTitle("Vibrante-Node Pipeline Editor")
        self.resize(1200, 800)
        
        self._apply_dark_theme()

        # Initialize Registry
        self.nodes_dir = os.path.abspath(os.path.join(os.getcwd(), 'nodes'))
        NodeRegistry.load_all(self.nodes_dir)

        # Setup Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabs)

        # Setup Panels
        self.library_panel = LibraryPanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_panel)
        
        self.log_panel = LogPanel(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_panel)
        self.log_panel.log("Application started", "info")
        
        self.scripting_console = ScriptingConsole(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.scripting_console)
        self.scripting_console.hide() # Hidden by default
        
        # Connect Library Signals
        self.library_panel.node_selected.connect(self._on_node_selected)
        self.library_panel.edit_requested.connect(self._on_edit_requested)
        self.library_panel.delete_requested.connect(self._on_delete_requested)

        # Setup Menu & Toolbars
        self._init_menu()
        self._init_toolbar()

        # Create initial tab
        self.add_new_workflow()

    def add_new_workflow(self, name="New Workflow"):
        scene = NodeScene(self)
        view = NodeView(scene, self)
        index = self.tabs.addTab(view, name)
        self.tabs.setCurrentIndex(index)
        return view

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

        node_menu = menubar.addMenu('&Nodes')
        new_node_action = QAction('&New Node Builder...', self)
        new_node_action.setShortcut('Ctrl+N')
        new_node_action.triggered.connect(self.open_node_builder)
        node_menu.addAction(new_node_action)

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

        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        user_guide_act = QAction('User Guide', self)
        user_guide_act.triggered.connect(lambda: self._open_doc("USER_GUIDE.md"))
        help_menu.addAction(user_guide_act)
        
        dev_doc_act = QAction('Developer Documentation', self)
        dev_doc_act.triggered.connect(lambda: self._open_doc("DEVELOPER.md"))
        help_menu.addAction(dev_doc_act)
        
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

    def _show_about(self):
        QMessageBox.about(self, "About Vibrante-Node",
            "<h3>Vibrante-Node v1.0</h3>"
            "<p>A professional node-based visual workflow editor for Python.</p>"
            "<p><b>Copyright &copy; 2026 KamalTD</b></p>"
            "<p>Built with PyQt5, Asyncio, and ❤️</p>")

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
        self.execute_btn.setToolTip("Execute the active pipeline (F5)")
        self.execute_btn.triggered.connect(self.execute_pipeline)
        toolbar.addAction(self.execute_btn)

    def _delete_selected(self):
        scene = self.get_current_scene()
        if not scene: return
        from PyQt5.QtGui import QKeyEvent
        from PyQt5.QtCore import QEvent
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        scene.keyPressEvent(event)

    def _apply_dark_theme(self):
        from PyQt5.QtWidgets import QApplication
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

    def _apply_light_theme(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        app.setStyleSheet("") # Reset to default

    def _on_node_selected(self, node_id):
        scene = self.get_current_scene()
        view = self.get_current_view()
        if scene and view:
            scene.add_node_by_name(node_id, view.mapToScene(view.rect().center()))

    def _on_edit_requested(self, node_id):
        dialog = NodeBuilderDialog(self, editing_node_id=node_id)
        if dialog.exec_():
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
        if dialog.exec_():
            self.library_panel.refresh()

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

    def execute_pipeline(self):
        scene = self.get_current_scene()
        if not scene: return
        
        self.execute_btn.setEnabled(False)
        tab_name = self.tabs.tabText(self.tabs.currentIndex())
        self.log_panel.log(f"Starting execution for [{tab_name}]...", "execution")
        
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

    def _on_execution_finished(self, success):
        self.execute_btn.setEnabled(True)
        status = "successfully" if success else "with errors"
        self.log_panel.log(f"Execution finished {status}.", "info" if success else "error")

    def _on_node_started(self, node_instance_id):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        self.log_panel.log(f"Node '{name}' started", "execution")
        if widget: widget.set_status("running")

    def _on_node_output(self, node_instance_id, results):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        res_str = ", ".join([f"{k}: {v}" for k, v in results.items()])
        self.log_panel.log(f"Node '{name}' output -> {res_str}", "success")

    def _on_node_log(self, node_instance_id, message, level):
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
        scene = self.get_current_scene()
        if not scene: return None
        for widget in scene.nodes:
            if widget.instance_id == instance_id:
                return widget
        return None
