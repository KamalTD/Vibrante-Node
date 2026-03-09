from PyQt5.QtWidgets import QDockWidget, QListWidget, QVBoxLayout, QWidget, QMenu, QAction, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from src.core.registry import NodeRegistry

class LibraryPanel(QDockWidget):
    # Signals
    node_selected = pyqtSignal(str) # node_id
    edit_requested = pyqtSignal(str) # node_id
    delete_requested = pyqtSignal(str) # node_id

    def __init__(self, parent=None):
        super().__init__("Node Library", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        self.layout.addWidget(self.list_widget)
        self.setWidget(self.container)
        
        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for node_id in NodeRegistry.list_node_ids():
            item = QListWidgetItem(node_id)
            self.list_widget.addItem(item)

    def _on_item_double_clicked(self, item):
        self.node_selected.emit(item.text())

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        node_id = item.text()
        menu = QMenu()
        
        edit_action = QAction("Edit Node", self)
        edit_action.triggered.connect(lambda: self.edit_requested.emit(node_id))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Node", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(node_id))
        menu.addAction(delete_action)
        
        menu.exec_(self.list_widget.mapToGlobal(pos))
