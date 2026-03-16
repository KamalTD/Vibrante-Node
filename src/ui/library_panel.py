from PyQt5.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QMenu, QAction, QMessageBox, QStyle, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QByteArray
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter
from src.core.registry import NodeRegistry
import os
import re

class LibraryPanel(QDockWidget):
    # Signals
    node_selected = pyqtSignal(str) # node_id
    edit_requested = pyqtSignal(str) # node_id
    delete_requested = pyqtSignal(str) # node_id

    def __init__(self, parent=None):
        super().__init__("Node Library", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self._is_dark_theme = True  # Track current theme
        
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
        self.apply_theme(is_dark=True) # Default to dark theme as MainWindow does

    def _load_svg_icon_with_color(self, svg_path, color):
        """Load an SVG file and replace stroke color, return QIcon."""
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Replace stroke color (handles stroke="..." patterns)
            svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', svg_content)
            
            # Create QIcon from modified SVG
            svg_bytes = QByteArray(svg_content.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            if renderer.isValid():
                pixmap = QPixmap(24, 24)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                return QIcon(pixmap)
        except Exception as e:
            print(f"[ICON] Error loading SVG {svg_path}: {e}")
        
        return None

    def apply_theme(self, is_dark=True):
        self._is_dark_theme = is_dark
        if is_dark:
            # Dark theme: background #2b2b2b (matches window background) or #3c3f41 (dark gray)
            # Text: white/light-gray
            self.container.setStyleSheet("background-color: #2b2b2b; color: white;")
            self.tree_widget.setStyleSheet("""
                QTreeWidget { background-color: #3c3f41; color: #ffffff; border: 1px solid #2b2b2b; }
                QTreeWidget::item:hover { background-color: #4b4d4d; }
                QTreeWidget::item:selected { background-color: #5c5e5e; }
            """)
            self.search_bar.setStyleSheet("background-color: #3c3f41; color: white; border: 1px solid #2b2b2b;")
        else:
            # Light theme: background light gray (#f0f0f0), text black
            self.container.setStyleSheet("background-color: #f0f0f0; color: black;")
            self.tree_widget.setStyleSheet("""
                QTreeWidget { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; }
                QTreeWidget::item:hover { background-color: #e0e0e0; }
                QTreeWidget::item:selected { background-color: #d0d0d0; }
            """)
            self.search_bar.setStyleSheet("background-color: #ffffff; color: black; border: 1px solid #cccccc;")
        
        # Refresh icons with new theme color
        self.refresh()

    def refresh(self):
        self.tree_widget.clear()
        search_text = self.search_bar.text().lower()
        node_ids = NodeRegistry.list_node_ids()
        
        # Determine icon color based on theme
        icon_color = "white" if self._is_dark_theme else "black"
        
        categories = {} # category_name -> List of (node_id, icon)
        
        for node_id in node_ids:
            if search_text and search_text not in node_id.lower():
                continue
                
            defn = NodeRegistry.get_definition(node_id)
            category = defn.category if defn else "General"
            
            if category not in categories:
                categories[category] = []
                
            # Icon logic - use theme-appropriate color for SVG icons
            icon = self.style().standardIcon(QStyle.SP_FileIcon)
            if defn and defn.icon_path:
                # Try relative to cwd first, then absolute
                cwd_path = os.path.join(os.getcwd(), defn.icon_path)
                abs_path = os.path.abspath(defn.icon_path)
                
                icon_file = None
                if os.path.exists(cwd_path):
                    icon_file = cwd_path
                elif os.path.exists(abs_path):
                    icon_file = abs_path
                
                if icon_file:
                    # For SVG files, load with theme-appropriate color
                    if icon_file.lower().endswith('.svg'):
                        custom_icon = self._load_svg_icon_with_color(icon_file, icon_color)
                        if custom_icon:
                            icon = custom_icon
                    else:
                        custom_icon = QIcon(icon_file)
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
                # Display the human-friendly name when available, and show description as tooltip
                defn = NodeRegistry.get_definition(node_id)
                # Normalize display name to Title Case for consistency
                display_name = defn.name.title() if defn and getattr(defn, 'name', None) else node_id.title()
                node_item.setText(0, display_name)
                node_item.setIcon(0, icon)
                node_item.setData(0, Qt.UserRole, node_id)
                if defn and getattr(defn, 'description', None):
                    node_item.setToolTip(0, defn.description)

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
