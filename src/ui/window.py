import sys
import os
import asyncio
import threading
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QToolBar, QMessageBox, QDockWidget
from PyQt5.QtCore import Qt
from src.ui.canvas.scene import NodeScene
from src.ui.canvas.view import NodeView
from src.ui.node_builder import NodeBuilderDialog
from src.ui.library_panel import LibraryPanel
from src.ui.log_panel import LogPanel
from src.core.models import WorkflowModel
from src.core.registry import NodeRegistry
from src.core.engine import NetworkExecutor

class MainWindow(QMainWindow):
    def __init__(self):
        print("MainWindow init started")
        super().__init__()
        self.setWindowTitle("Python Node-Based Pipeline Editor")
        self.resize(1200, 800)

        # Initialize Registry
        self.nodes_dir = os.path.abspath(os.path.join(os.getcwd(), 'nodes'))
        print(f"Loading nodes from {self.nodes_dir}")
        NodeRegistry.load_all(self.nodes_dir)
        print("Nodes loaded")

        # Setup Canvas
        self.scene = NodeScene(self)
        self.view = NodeView(self.scene, self)
        self.setCentralWidget(self.view)
        print("Canvas setup done")

        # Setup Library Panel
        self.library_panel = LibraryPanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_panel)
        print("Library panel setup done")

        # Setup Log Panel
        self.log_panel = LogPanel(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_panel)
        self.log_panel.log("Application started", "info")
        
        # Connect Library Signals
        self.library_panel.node_selected.connect(self._on_node_selected)
        self.library_panel.edit_requested.connect(self._on_edit_requested)
        self.library_panel.delete_requested.connect(self._on_delete_requested)

        # Setup Menu & Toolbars
        self._init_menu()
        self._init_toolbar()

    def _init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        
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

    def _init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        new_node_btn = QAction("New Node", self)
        new_node_btn.triggered.connect(self.open_node_builder)
        toolbar.addAction(new_node_btn)
        
        toolbar.addSeparator()
        
        self.execute_btn = QAction("Run Workflow", self)
        self.execute_btn.setShortcut('F5')
        self.execute_btn.triggered.connect(self.execute_pipeline)
        toolbar.addAction(self.execute_btn)

    def _on_node_selected(self, node_id):
        # Add node to scene at center or mouse pos
        self.scene.add_node_by_name(node_id, self.view.mapToScene(self.view.rect().center()))

    def _on_edit_requested(self, node_id):
        dialog = NodeBuilderDialog(self, editing_node_id=node_id)
        if dialog.exec_():
            self.library_panel.refresh()

    def _on_delete_requested(self, node_id):
        # Check if used in scene
        used = any(nw.node_definition.name == node_id for nw in self.scene.nodes)
        if used:
            res = QMessageBox.warning(self, "Warning", f"Node '{node_id}' is currently in use in the workflow. Deleting it will break the workflow. Continue?", 
                                     QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.No:
                return
        
        NodeRegistry.delete_node(node_id, self.nodes_dir)
        self.library_panel.refresh()

    def open_node_builder(self):
        dialog = NodeBuilderDialog(self)
        if dialog.exec_():
            self.library_panel.refresh()

    def save_workflow(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Workflow", "workflows", "Workflow Files (*.json)")
        if file_path:
            workflow_model = self.scene.to_workflow_model()
            with open(file_path, "w") as f:
                f.write(workflow_model.model_dump_json(indent=4))
            QMessageBox.information(self, "Success", "Workflow saved successfully!")

    def load_workflow(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Workflow", "workflows", "Workflow Files (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                json_data = f.read()
            workflow_model = WorkflowModel.model_validate_json(json_data)
            self.scene.from_workflow_model(workflow_model)
            QMessageBox.information(self, "Success", "Workflow loaded successfully!")

    def execute_pipeline(self):
        self.execute_btn.setEnabled(False)
        self.log_panel.log("Starting network execution...", "execution")
        workflow_model = self.scene.to_workflow_model()
        
        from src.core.graph import GraphManager
        gm = GraphManager()
        gm.from_model(workflow_model)
        
        # Store executor as instance variable to prevent GC
        self.current_executor = NetworkExecutor(gm)
        
        # Connect signals
        self.current_executor.node_started.connect(self._on_node_started)
        self.current_executor.node_finished.connect(self._on_node_finished)
        self.current_executor.node_error.connect(self._on_node_error)
        self.current_executor.node_output.connect(self._on_node_output)
        self.current_executor.execution_finished.connect(self._on_execution_finished)
        
        # Use threading to run asyncio loop
        def run_async_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.current_executor.run())
                loop.close()
            except Exception as e:
                print(f"Error in async loop: {e}")
                # We need to emit from a QObject. current_executor is one.
                self.current_executor.execution_finished.emit(False)

        thread = threading.Thread(target=run_async_loop, daemon=True)
        thread.start()

    def _on_execution_finished(self, success):
        self.execute_btn.setEnabled(True)
        status = "successfully" if success else "with errors"
        self.log_panel.log(f"Network execution finished {status}.", "info" if success else "error")

    def _on_node_started(self, node_instance_id):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        self.log_panel.log(f"Node '{name}' started ({node_instance_id})", "execution")
        if widget: widget.set_status("running")

    def _on_node_output(self, node_instance_id, results):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        res_str = ", ".join([f"{k}: {v}" for k, v in results.items()])
        self.log_panel.log(f"Node '{name}' output -> {res_str}", "success")

    def _on_node_finished(self, node_instance_id, status):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        level = "success" if status == "success" else "error"
        self.log_panel.log(f"Node '{name}' finished with status: {status}", level)
        if widget: widget.set_status(status)

    def _on_node_error(self, node_instance_id, error_msg):
        widget = self._find_node_widget(node_instance_id)
        name = widget.node_definition.name if widget else "Unknown"
        self.log_panel.log(f"Node '{name}' error: {error_msg}", "error")
        QMessageBox.critical(self, "Execution Error", f"Node {name} ({node_instance_id}) failed:\n{error_msg}")

    def _find_node_widget(self, instance_id):
        for widget in self.scene.nodes:
            if widget.instance_id == instance_id:
                return widget
        return None
