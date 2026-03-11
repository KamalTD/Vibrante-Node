from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QCursor
from uuid import uuid4

class Backdrop(QGraphicsRectItem):
    def __init__(self, title="Network Box", pos=(0, 0), size=(400, 300), color="#444444", instance_id=None):
        super().__init__(0, 0, size[0], size[1])
        self.instance_id = instance_id or uuid4()
        self.setPos(pos[0], pos[1])
        self.setZValue(-100) # Always behind nodes
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.bg_color = QColor(color)
        self.bg_color.setAlpha(100) # Semi-transparent
        self.setBrush(QBrush(self.bg_color))
        self.setPen(QPen(QColor(255, 255, 255, 50), 2))
        
        # Title Item
        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setPos(5, 5)
        self.title_item.setDefaultTextColor(Qt.white)
        font = self.title_item.font()
        font.setBold(True)
        font.setPointSize(12)
        self.title_item.setFont(font)
        self.title_item.setTextInteractionFlags(Qt.TextEditorInteraction)

        # Resize State
        self.resizing = False
        self.resize_handle_size = 20
        self.setAcceptHoverEvents(True)

    def hoverMoveEvent(self, event):
        if self._is_on_handle(event.pos()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def _is_on_handle(self, pos):
        return pos.x() > self.rect().width() - self.resize_handle_size and \
               pos.y() > self.rect().height() - self.resize_handle_size

    def mousePressEvent(self, event):
        if self.title_item.boundingRect().contains(event.pos()):
            pass
            
        if event.button() == Qt.LeftButton and self._is_on_handle(event.pos()):
            self.resizing = True
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_width = max(100, event.pos().x())
            new_height = max(100, event.pos().y())
            self.setRect(0, 0, new_width, new_height)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        # Draw background
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # Draw header area
        header_rect = QRectF(self.rect().x(), self.rect().y(), self.rect().width(), 35)
        painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(header_rect, 10, 10)
        
        # Resize Handle (bottom right)
        painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
        handle_rect = QRectF(self.rect().width() - 15, self.rect().height() - 15, 10, 10)
        painter.drawRect(handle_rect)

        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(-2, -2, 2, 2), 10, 10)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Calculate delta based on new value (which is the proposed new position)
            delta = value - self.pos()
            
            # Find nodes that were INSIDE before we moved
            # Use current pos for check
            current_bounds = self.sceneBoundingRect()
            
            for item in self.scene().items():
                # Avoid circular dependencies and only move specific types
                from src.ui.node_widget import NodeWidget
                from src.ui.canvas.sticky_note import StickyNote
                
                if isinstance(item, (NodeWidget, StickyNote)):
                    if current_bounds.contains(item.sceneBoundingRect()):
                        # Only move child if it's NOT also selected (prevent double move)
                        if not item.isSelected():
                            item.setPos(item.pos() + delta)
                            
        return super().itemChange(change, value)
