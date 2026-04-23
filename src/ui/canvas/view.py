from src.utils.qt_compat import QtWidgets, QtCore, QtGui, exec_dialog
from src.ui.canvas.node_search_popup import NodeSearchPopup

QGraphicsView = QtWidgets.QGraphicsView
QGraphicsScene = QtWidgets.QGraphicsScene
Qt = QtCore.Qt
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
QEvent = QtCore.QEvent
QPainter = QtGui.QPainter
QWheelEvent = QtGui.QWheelEvent
QMouseEvent = QtGui.QMouseEvent
QKeyEvent = QtGui.QKeyEvent

class NodeView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Enable Drops
        self.setAcceptDrops(True)
        
        # Enable focus and prevent Tab from being used for navigation
        self.setFocusPolicy(Qt.StrongFocus)
        
        self._is_panning = False
        self._last_pan_pos = QPoint()
        self._search_popup = None
        self._last_mouse_scene_pos = QPointF(0, 0)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-node-id") or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-node-id") or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        node_id = None
        
        if mime.hasFormat("application/x-node-id"):
            node_id = bytes(mime.data("application/x-node-id")).decode("utf-8")
        elif mime.hasText():
            node_id = mime.text()
            
        if node_id:
            scene = self.scene()
            if scene:
                # Map drop position to scene coordinates
                pos = self.mapToScene(event.pos())
                result = scene.add_node_by_name(node_id, pos)
                if result:
                    scene.push_history()
                    event.acceptProposedAction()
                return
                
        super().dropEvent(event)

    def event(self, event):
        """Override to catch Tab key before it's used for focus navigation."""
        if event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Tab:
                self.show_node_search_popup()
                return True
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent):
        # Ensure view has focus for keyboard shortcuts
        self.setFocus()
        
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() == Qt.AltModifier):
            self._start_pan(event.pos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Track mouse position for spawning nodes
        self._last_mouse_scene_pos = self.mapToScene(event.pos())
        
        if self._is_panning:
            # Manually pan the view by shifting scrollbars
            delta = event.pos() - self._last_pan_pos
            self._last_pan_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            # Stop panning on any button release if we were panning
            self._stop_pan()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _start_pan(self, pos):
        self._is_panning = True
        self._last_pan_pos = pos
        self.setCursor(Qt.ClosedHandCursor)
        self.setDragMode(QGraphicsView.NoDrag)

    def _stop_pan(self):
        self._is_panning = False
        self.setCursor(Qt.ArrowCursor)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def keyPressEvent(self, event: QKeyEvent):
        from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit, QPlainTextEdit
        focus_widget = QApplication.focusWidget()
        if isinstance(focus_widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
            super().keyPressEvent(event)
            return
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.setCursor(Qt.OpenHandCursor)
            # We don't start panning yet, just show the cursor
            # Actual pan starts on mouse press + space
        elif event.key() == Qt.Key_F:
            self.focus_on_selection()
        elif event.key() == Qt.Key_B and event.modifiers() == Qt.ControlModifier:
            # Toggle Bypass on selection
            scene = self.scene()
            if scene:
                from src.ui.node_widget import NodeWidget
                selected_nodes = [i for i in scene.selectedItems() if isinstance(i, NodeWidget)]
                if selected_nodes:
                    scene.push_history()
                    # If any are NOT bypassed, bypass them all. Otherwise, unbypass all.
                    any_not_bypassed = any(not n.bypassed for n in selected_nodes)
                    for node in selected_nodes:
                        node.set_bypassed(any_not_bypassed)
        elif event.key() == Qt.Key_G and event.modifiers() == Qt.ControlModifier:
            # Wrap in Backdrop
            scene = self.scene()
            if scene:
                from src.ui.node_widget import NodeWidget
                selected_nodes = [i for i in scene.selectedItems() if isinstance(i, NodeWidget)]
                if selected_nodes:
                    # Trigger the wrap logic
                    # We can either duplicate the logic or call a method on scene
                    if hasattr(scene, '_wrap_selection_in_backdrop'):
                        scene._wrap_selection_in_backdrop()
                    else:
                        # Fallback to direct implementation if method doesn't exist yet
                        rect = selected_nodes[0].sceneBoundingRect()
                        for node in selected_nodes[1:]:
                            rect = rect.united(node.sceneBoundingRect())
                        padding = 40
                        box_pos = (rect.x() - padding, rect.y() - padding - 20)
                        box_size = (rect.width() + padding*2, rect.height() + padding*2 + 20)
                        scene.add_backdrop(title="Grouped Nodes", pos=box_pos, size=box_size)
        super().keyPressEvent(event)

    def focus_on_selection(self):
        scene = self.scene()
        if not scene: return
        
        selected_items = scene.selectedItems()
        target_rect = None

        if selected_items:
            # Focus on bounding rect of selected items
            target_rect = selected_items[0].sceneBoundingRect()
            for item in selected_items[1:]:
                target_rect = target_rect.united(item.sceneBoundingRect())
        else:
            # Focus on all nodes, notes, and backdrops specifically
            from src.ui.node_widget import NodeWidget
            from src.ui.canvas.sticky_note import StickyNote
            from src.ui.canvas.backdrop import Backdrop
            
            content_items = [i for i in scene.items() if isinstance(i, (NodeWidget, StickyNote, Backdrop))]
            
            if content_items:
                target_rect = content_items[0].sceneBoundingRect()
                for item in content_items[1:]:
                    target_rect = target_rect.united(item.sceneBoundingRect())
        
        if target_rect:
            # Add some padding (10%)
            padding = max(target_rect.width(), target_rect.height()) * 0.1
            target_rect.adjust(-padding, -padding, padding, padding)
            self.fitInView(target_rect, Qt.KeepAspectRatio)
        else:
            self.centerOn(0, 0)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._stop_pan()
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """
        Handle zoom in/out with Ctrl + Wheel.
        """
        if event.modifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor

            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor

            self.scale(zoom_factor, zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def show_node_search_popup(self, pos=None):
        """Show the node search popup at the current mouse position."""
        scene = self.scene()
        if not scene:
            return
        
        # Get spawn position in scene coordinates
        if pos is None:
            spawn_pos = self._last_mouse_scene_pos
        else:
            spawn_pos = pos
        
        # Create and show the popup
        popup = NodeSearchPopup(self)
        
        # Apply theme based on scene background
        is_dark = scene.backgroundBrush().color().lightness() < 128
        popup.apply_theme(is_dark)
        
        # Connect selection signal
        def on_node_selected(node_id):
            scene.push_history()
            scene.add_node_by_name(node_id, spawn_pos)
        
        popup.node_selected.connect(on_node_selected)
        
        # Position popup near the cursor
        cursor_pos = self.mapFromGlobal(self.cursor().pos())
        popup_pos = self.mapToGlobal(cursor_pos)
        popup.move(popup_pos)
        exec_dialog(popup)
