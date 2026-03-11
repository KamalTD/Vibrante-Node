from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QWheelEvent, QMouseEvent, QKeyEvent

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
        
        self._is_panning = False
        self._last_pan_pos = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() == Qt.AltModifier):
            self._start_pan(event.pos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
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
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.setCursor(Qt.OpenHandCursor)
            # We don't start panning yet, just show the cursor
            # Actual pan starts on mouse press + space
        elif event.key() == Qt.Key_F:
            self.focus_on_selection()
        super().keyPressEvent(event)

    def focus_on_selection(self):
        scene = self.scene()
        if not scene: return
        
        selected_items = scene.selectedItems()
        if selected_items:
            # Focus on bounding rect of selected items
            rect = selected_items[0].sceneBoundingRect()
            for item in selected_items[1:]:
                rect = rect.united(item.sceneBoundingRect())
            self.centerOn(rect.center())
        else:
            # Focus on all items if any, otherwise origin
            items_rect = scene.itemsBoundingRect()
            if items_rect.width() > 0 and items_rect.height() > 0:
                self.centerOn(items_rect.center())
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
