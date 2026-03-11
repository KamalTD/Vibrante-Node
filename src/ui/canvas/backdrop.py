from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush
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
        
        # Title
        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setPos(5, 5)
        self.title_item.setDefaultTextColor(Qt.white)
        font = self.title_item.font()
        font.setBold(True)
        font.setPointSize(12)
        self.title_item.setFont(font)

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
        
        # Selection highlight
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(-2, -2, 2, 2), 10, 10)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            delta = value - self.pos()
            # Move all nodes inside the backdrop
            for item in self.scene().items():
                from src.ui.node_widget import NodeWidget
                if isinstance(item, NodeWidget) and self.sceneBoundingRect().contains(item.sceneBoundingRect()):
                    # Only move if the node is NOT also selected (to avoid double move)
                    if not item.isSelected():
                        item.setPos(item.pos() + delta)
        return super().itemChange(change, value)
