from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget, 
                             QListWidgetItem, QHBoxLayout, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QFont
from src.core.registry import NodeRegistry


class NodeSearchPopup(QDialog):
    """A searchable popup menu for quickly adding nodes."""
    
    node_selected = pyqtSignal(str)  # Emits node_id when user selects a node
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Node")
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setMinimumSize(350, 400)
        self._is_dark_theme = True
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header
        header = QLabel("Search Nodes")
        header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(header)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search nodes...")
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.results_list.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self.results_list)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.status_label)
        
        # Populate initial list
        self._all_nodes = self._get_all_nodes()
        self._populate_list(self._all_nodes)
        
        # Apply theme
        self.apply_theme(is_dark=True)
        
    def _get_all_nodes(self):
        """Get all available nodes grouped by category."""
        nodes = []
        for node_id in NodeRegistry.list_node_ids():
            defn = NodeRegistry.get_definition(node_id)
            category = defn.category if defn else "General"
            name = defn.name if defn and defn.name else node_id
            description = defn.description if defn and defn.description else ""
            nodes.append({
                "id": node_id,
                "name": name,
                "category": category,
                "description": description
            })
        # Sort by category then name
        nodes.sort(key=lambda x: (x["category"], x["name"]))
        return nodes
    
    def _populate_list(self, nodes):
        """Populate the results list with nodes."""
        self.results_list.clear()
        current_category = None
        
        for node in nodes:
            # Add category header if changed
            if node["category"] != current_category:
                current_category = node["category"]
                header_item = QListWidgetItem(f"── {current_category} ──")
                header_item.setFlags(Qt.NoItemFlags)  # Not selectable
                header_item.setForeground(Qt.gray)
                font = header_item.font()
                font.setItalic(True)
                header_item.setFont(font)
                self.results_list.addItem(header_item)
            
            # Add node item
            item = QListWidgetItem(f"  {node['name']}")
            item.setData(Qt.UserRole, node["id"])
            if node["description"]:
                item.setToolTip(node["description"])
            self.results_list.addItem(item)
        
        # Update status
        node_count = len([n for n in nodes])
        self.status_label.setText(f"{node_count} nodes found  |  Enter: Add  |  Esc: Close")
        
        # Select first selectable item
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item.flags() & Qt.ItemIsSelectable:
                self.results_list.setCurrentItem(item)
                break
    
    def _on_search_changed(self, text):
        """Filter nodes based on search text."""
        search_text = text.lower().strip()
        
        if not search_text:
            self._populate_list(self._all_nodes)
            return
        
        # Filter nodes by name, category, or description
        filtered = []
        for node in self._all_nodes:
            if (search_text in node["name"].lower() or 
                search_text in node["category"].lower() or
                search_text in node["description"].lower()):
                filtered.append(node)
        
        self._populate_list(filtered)
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on item."""
        node_id = item.data(Qt.UserRole)
        if node_id:
            self.node_selected.emit(node_id)
            self.accept()
    
    def _on_item_activated(self, item):
        """Handle Enter key on item."""
        node_id = item.data(Qt.UserRole)
        if node_id:
            self.node_selected.emit(node_id)
            self.accept()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard navigation."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            current = self.results_list.currentItem()
            if current:
                node_id = current.data(Qt.UserRole)
                if node_id:
                    self.node_selected.emit(node_id)
                    self.accept()
        elif event.key() == Qt.Key_Down:
            # Move selection down
            current_row = self.results_list.currentRow()
            for i in range(current_row + 1, self.results_list.count()):
                item = self.results_list.item(i)
                if item.flags() & Qt.ItemIsSelectable:
                    self.results_list.setCurrentRow(i)
                    break
        elif event.key() == Qt.Key_Up:
            # Move selection up
            current_row = self.results_list.currentRow()
            for i in range(current_row - 1, -1, -1):
                item = self.results_list.item(i)
                if item.flags() & Qt.ItemIsSelectable:
                    self.results_list.setCurrentRow(i)
                    break
        else:
            super().keyPressEvent(event)
    
    def showEvent(self, event):
        """Focus the search input when shown."""
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def apply_theme(self, is_dark=True):
        """Apply theme colors."""
        self._is_dark_theme = is_dark
        
        if is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                    border-radius: 8px;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1px solid #6699cc;
                }
                QListWidget {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                QListWidget::item {
                    padding: 4px 8px;
                }
                QListWidget::item:selected {
                    background-color: #4a6fa5;
                }
                QListWidget::item:hover {
                    background-color: #4b4d4d;
                }
                QFrame {
                    color: #555;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                }
                QLabel {
                    color: #000000;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1px solid #4a90d9;
                }
                QListWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
                QListWidget::item {
                    padding: 4px 8px;
                }
                QListWidget::item:selected {
                    background-color: #0078d7;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #e0e0e0;
                }
                QFrame {
                    color: #ccc;
                }
            """)
