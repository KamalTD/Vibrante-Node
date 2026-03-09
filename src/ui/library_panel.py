from PyQt5.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QMenu, QAction, QMessageBox, QStyle, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from src.core.registry import NodeRegistry
import os

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
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search nodes...")
        self.search_bar.textChanged.connect(self.refresh)
        self.layout.addWidget(self.search_bar)
        
        # Tree Widget for Categories
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIconSize(QSize(24, 24))
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        self.layout.addWidget(self.tree_widget)
        self.setWidget(self.container)
        
        self.refresh()

    def refresh(self):
        self.tree_widget.clear()
        search_text = self.search_bar.text().lower()
        node_ids = NodeRegistry.list_node_ids()
        
        categories = {} # category_name -> List of (node_id, icon)
        
        for node_id in node_ids:
            if search_text and search_text not in node_id.lower():
                continue
                
            defn = NodeRegistry.get_definition(node_id)
            category = defn.category if defn else "General"
            
            if category not in categories:
                categories[category] = []
                
            # Icon logic
            icon = self.style().standardIcon(QStyle.SP_FileIcon)
            if defn and defn.icon_path:
                abs_path = os.path.abspath(defn.icon_path)
                if not os.path.exists(abs_path):
                    abs_path = os.path.join(os.getcwd(), defn.icon_path)
                
                if os.path.exists(abs_path):
                    custom_icon = QIcon(abs_path)
                    if not custom_icon.isNull():
                        icon = custom_icon
            
            categories[category].append((node_id, icon))

        # Build Tree
        for cat_name, nodes in sorted(categories.items()):
            cat_item = QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat_name)
            cat_item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
            cat_item.setExpanded(True)
            
            for node_id, icon in sorted(nodes):
                node_item = QTreeWidgetItem(cat_item)
                node_item.setText(0, node_id)
                node_item.setIcon(0, icon)
                node_item.setData(0, Qt.UserRole, node_id)

    def _on_item_double_clicked(self, item, column):
        node_id = item.data(0, Qt.UserRole)
        if node_id:
            self.node_selected.emit(node_id)

    def _show_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        if not item:
            return
            
        node_id = item.data(0, Qt.UserRole)
        if not node_id:
            return
            
        menu = QMenu()
        edit_action = QAction("Edit Node", self)
        edit_action.triggered.connect(lambda: self.edit_requested.emit(node_id))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Node", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(node_id))
        menu.addAction(delete_action)
        
        menu.exec_(self.tree_widget.mapToGlobal(pos))
