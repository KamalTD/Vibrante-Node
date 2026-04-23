import sys
import os
import shutil
import asyncio
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QToolBar, QMessageBox, QDockWidget, QMenu, QStyle, QTabWidget, QStatusBar, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor
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


class _EventLoopRunner:
    """Drives the NetworkExecutor's asyncio event loop on the main Qt thread.

    A zero-delay QTimer pumps the asyncio loop so every signal the executor
    emits originates from the main thread.  No cross-thread machinery is
    ever needed, which makes QBasicTimer warnings structurally impossible.
    """

    def __init__(self, executor):
        self._executor = executor
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._task = None
        self._active = False
        self._timer = QTimer()
        self._timer.setInterval(0)
        self._timer.timeout.connect(self._step)

    def start(self):
        self._active = True
        self._task = self._loop.create_task(self._executor.run())
        self._timer.start()

    def _step(self):
        if not self._active:
            return
        # Process one round of ready asyncio callbacks without blocking.
        # call_soon(stop) ensures run_forever() returns after one _run_once().
        self._loop.call_soon(self._loop.stop)
        self._loop.run_forever()
        if self._task is not None and self._task.done():
            self._cleanup()

    def _cleanup(self):
        if not self._active:
            return
        self._active = False
        self._timer.stop()
        if not self._loop.is_closed():
            self._loop.close()

    def stop(self):
        """Request a graceful stop; the loop keeps pumping until the task finishes."""
        self._executor.stop()


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
        NodeRegistry.load_all(self.nodes_dir)

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

        save_as_action = QAction('Save Workflow &As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_workflow_as)
        file_menu.addAction(save_as_action)

        load_action = QAction('&Load Workflow', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_workflow)
        file_menu.addAction(load_action)

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
            f"<h3>Vibrante-Node v1.8.0</h3>"
            f"<p>{description}</p>"
            f"<hr>"
            f"<p><b>Copyright &copy; 2026 Mahmoud Kamal - KamalTD</b></p>"
            f"<p>GitHub: <a href='https://github.com/KamalTD'>https://github.com/KamalTD</a></p>"
            f"<p>Built with PyQt5, Asyncio, and ❤️</p>"
            f"<hr>"
            f"<p><small>{license_text}</small></p>")

    def _link_to_gemini(self):
        import webbrowser
        webbrowser.open("https://aistudio.google.com/app/api-keys?project=gen-lang-client-0761136562")
        dialog = GeminiApiDialog(self)
        dialog.exec_()

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

        # Stop Workflow
        self.stop_btn = QAction(self.style().standardIcon(QStyle.SP_MediaStop), "Stop Workflow", self)
        self.stop_btn.setToolTip("Stop the active pipeline (Shift+F5)")
        self.stop_btn.triggered.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        toolbar.addAction(self.stop_btn)

    def _delete_selected(self):
        scene = self.get_current_scene()
        if not scene: return
        from PyQt5.QtGui import QKeyEvent
        from PyQt5.QtCore import QEvent
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        scene.keyPressEvent(event)

    def _apply_dark_theme(self):
        self._is_dark_theme = True
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
        from PyQt5.QtWidgets import QApplication
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

    @staticmethod
    def _atomic_write(file_path: str, data: str):
        """Write to a temp file then rename so a crash never corrupts the target."""
        import tempfile
        dir_name = os.path.dirname(os.path.abspath(file_path))
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(data)
            os.replace(tmp_path, file_path)
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

    def save_workflow(self):
        scene = self.get_current_scene()
        if not scene: return

        file_path = scene.file_path
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Workflow", "workflows", "Workflow Files (*.json)")

        if file_path:
            if not file_path.endswith(".json"): file_path += ".json"
            workflow_model = scene.to_workflow_model()
            self._atomic_write(file_path, workflow_model.model_dump_json(indent=4))
            scene.file_path = file_path
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))
            self.log_panel.log(f"Workflow saved: {file_path}", "success")

    def save_workflow_as(self):
        """Save workflow to a new file, always prompting for location."""
        scene = self.get_current_scene()
        if not scene: return

        default_dir = os.path.dirname(scene.file_path) if scene.file_path else "workflows"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Workflow As", default_dir, "Workflow Files (*.json)")

        if file_path:
            if not file_path.endswith(".json"): file_path += ".json"
            workflow_model = scene.to_workflow_model()
            self._atomic_write(file_path, workflow_model.model_dump_json(indent=4))
            scene.file_path = file_path
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))
            self.log_panel.log(f"Workflow saved as: {file_path}", "success")

    def load_workflow(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Workflow", "workflows", "Workflow Files (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                json_data = f.read()
            if not json_data.strip():
                QMessageBox.critical(self, "Load Error", f"Workflow file is empty or corrupted:\n{file_path}")
                self.log_panel.log(f"Failed to load workflow — file is empty: {file_path}", "error")
                return
            try:
                workflow_model = WorkflowModel.model_validate_json(json_data)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Invalid workflow file:\n{e}")
                self.log_panel.log(f"Failed to load workflow: {e}", "error")
                return

            # Create a new tab for loaded workflow
            view = self.add_new_workflow(os.path.basename(file_path))
            scene = view.scene()
            scene.from_workflow_model(workflow_model)
            scene.file_path = file_path
            self.log_panel.log(f"Workflow loaded: {file_path}", "info")

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

        self._runner = _EventLoopRunner(self.current_executor)
        self._runner.start()

    def stop_execution(self):
        if hasattr(self, '_runner') and self._runner:
            self._runner.stop()
            self.status_label.setText("Stopping...")
            self.log_panel.log("Stop requested...", "warning")

    def _on_execution_finished(self, success):
        self._is_executing = False
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Ready")
        status = "successfully" if success else "or stopped"
        self.log_panel.log(f"Execution finished {status}.", "info" if success else "warning")

        # After a short delay, reset all nodes to 'idle' to clear status colors
        QTimer.singleShot(2000, self._reset_node_statuses)

    def _reset_node_statuses(self):
        scene = self.get_current_scene()
        if scene:
            for node in scene.nodes:
                node.set_status("idle")

    def _on_node_started(self, node_instance_id):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        self.log_panel.log(f"Node '{name}' started", "execution")
        if widget: widget.set_status("running")

    def _on_node_output(self, node_instance_id, results):
        widget = self._find_node_widget(node_instance_id)
        if widget:
            for name, val in results.items():
                widget.set_parameter(name, val, propagate=False)
                
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
