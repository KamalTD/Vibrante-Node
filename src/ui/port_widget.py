from src.utils.qt_compat import QtWidgets, QtCore, QtGui

QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem
QGraphicsItem = QtWidgets.QGraphicsItem
Qt = QtCore.Qt
QPointF = QtCore.QPointF
QRectF = QtCore.QRectF
QColor = QtGui.QColor
QBrush = QtGui.QBrush
QPen = QtGui.QPen
QPolygonF = QtGui.QPolygonF
QPainter = QtGui.QPainter

class PortWidget(QGraphicsEllipseItem):
    # Map data types to colors
    TYPE_COLORS = {
        "int": QColor(0, 255, 255),      # Cyan
        "float": QColor(255, 255, 0),    # Yellow
        "number": QColor(255, 255, 0),   # Yellow
        "string": QColor(189, 147, 249), # Purple
        "bool": QColor(80, 250, 123),    # Green
        "boolean": QColor(80, 250, 123), # Green
        "list": QColor(255, 184, 108),   # Orange
        "dict": QColor(255, 85, 85),     # Red
        "any": QColor(139, 233, 253),    # Light Blue/Cyan
        "exec": QColor(255, 255, 255),   # White
        "default": QColor(170, 170, 170) # Gray
    }

    def __init__(self, port_definition, is_input=True, parent=None):
        super().__init__(parent)
        self.port_definition = port_definition
        self.is_input = is_input
        self.radius = 6
        self.setRect(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
        
        # Determine if it's an execution port
        data_type = "any"
        if hasattr(self.port_definition, "type"):
            data_type = self.port_definition.type.lower()
        elif hasattr(self.port_definition, "data_type"):
            data_type = self.port_definition.data_type.lower()
        self.port_type = "exec" if data_type == "exec" else "data"
        
        self.setAcceptHoverEvents(True)
        self._init_ui()

    def _init_ui(self):
        # Color based on type
        data_type = "any"
        if hasattr(self.port_definition, "type"):
            data_type = self.port_definition.type.lower()
        elif hasattr(self.port_definition, "data_type"):
            data_type = self.port_definition.data_type.lower()
            
        color = self.TYPE_COLORS.get(data_type, self.TYPE_COLORS["default"])
        
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 1))
        
        # Tooltip showing name and type
        self.setToolTip(f"{self.port_definition.name}\nType: {data_type}")
        
    def paint(self, painter, option, widget):
        if self.port_type == "exec":
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(self.brush())
            painter.setPen(self.pen())
            
            # Draw a triangle (arrow head)
            r = self.radius
            poly = QPolygonF([QPointF(-r, -r), QPointF(r, 0), QPointF(-r, r)])
            painter.drawPolygon(poly)
        else:
            super().paint(painter, option, widget)

    def get_scene_pos(self) -> QPointF:
        return self.scenePos()
