from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QBrush, QPen

class PortWidget(QGraphicsEllipseItem):
    def __init__(self, port_definition, is_input=True, parent=None):
        super().__init__(parent)
        self.port_definition = port_definition
        self.is_input = is_input
        self.radius = 6
        self.setRect(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
        
        self._init_ui()

    def _init_ui(self):
        self.setBrush(QBrush(QColor(100, 255, 100) if self.is_input else QColor(255, 100, 100)))
        self.setPen(QPen(Qt.black, 1))
        
        # Position within parent (NodeWidget)
        if self.is_input:
            self.setPos(0, 50)  # Simple placeholder position
        else:
            self.setPos(150, 50) # Simple placeholder position

    def get_scene_pos(self) -> QPointF:
        return self.scenePos()
