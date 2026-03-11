from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush, QFont
from uuid import uuid4

class StickyNote(QGraphicsRectItem):
    def __init__(self, text="New Note", pos=(0, 0), size=(200, 150), color="#ffffcc", instance_id=None):
        super().__init__(0, 0, size[0], size[1])
        self.instance_id = instance_id or uuid4()
        self.setPos(pos[0], pos[1])
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.bg_color = QColor(color)
        self.setBrush(QBrush(self.bg_color))
        self.setPen(QPen(Qt.black, 1))
        
        # Text Item
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setPos(5, 5)
        self.text_item.setTextWidth(size[0] - 10)
        self.text_item.setDefaultTextColor(Qt.black)
        
        # Make text editable on double click
        self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        
    def mouseDoubleClickEvent(self, event):
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def paint(self, painter, option, widget):
        # Draw background
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())
        
        # Draw selection highlight
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect().adjusted(-2, -2, 2, 2))

    def get_text(self):
        return self.text_item.toPlainText()

    def set_text(self, text):
        self.text_item.setPlainText(text)
