from src.utils.qt_compat import QtWidgets, QtCore, QtGui

QGraphicsPathItem = QtWidgets.QGraphicsPathItem
QGraphicsItem = QtWidgets.QGraphicsItem
Qt = QtCore.Qt
QPointF = QtCore.QPointF
QPainterPath = QtGui.QPainterPath
QPen = QtGui.QPen
QColor = QtGui.QColor
QPainterPathStroker = QtGui.QPainterPathStroker

class Edge(QGraphicsPathItem):
    def __init__(self, from_port, to_port=None, parent=None):
        super().__init__(parent)
        self.from_port = from_port
        self.to_port = to_port
        self.pos_end = QPointF(0, 0)
        self.is_dark = True
        self._live_value = None

        self.setZValue(-1) # Draw edges behind nodes
        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        self.apply_theme(True)
        
        self.update_path()

    def apply_theme(self, is_dark=True):
        self.is_dark = is_dark
        self._refresh_color()

    def _refresh_color(self):
        if self.from_port is not None:
            color = self.from_port.brush().color()
            # White exec wires are invisible on a light background.
            if not self.is_dark and color.lightness() > 200:
                color = QColor(Qt.black)
        else:
            color = QColor(Qt.white) if self.is_dark else QColor(Qt.black)
        self.setPen(QPen(color, 2))
        self.update()

    def update_path(self):
        """
        Updates the cubic path between from_port and to_port (or pos_end).
        """
        if not self.from_port: return

        pos_start = self.from_port.get_scene_pos()
        pos_end = self.to_port.get_scene_pos() if self.to_port else self.pos_end
        
        path = QPainterPath()
        path.moveTo(pos_start)
        
        # Calculate control points for a smooth curve
        dx = pos_end.x() - pos_start.x()
        dist = max(abs(dx) * 0.5, 20) # Ensure some curvature
        
        if self.from_port.is_input:
            # If from_port is input, it means it's actually the 'to' side in logic
            # but in Edge object it's the anchor.
            # This case is handled in mouseReleaseEvent by swapping.
            pass

        ctrl1 = QPointF(pos_start.x() + dist, pos_start.y())
        ctrl2 = QPointF(pos_end.x() - dist, pos_end.y())
        
        path.cubicTo(ctrl1, ctrl2, pos_end)
        self.setPath(path)
        self._refresh_color()

    def set_end_pos(self, pos):
        self.pos_end = pos
        self.update_path()

    def shape(self):
        """Widen the hit area to 12 px so hovering for tooltips is easy."""
        stroker = QPainterPathStroker()
        stroker.setWidth(12)
        return stroker.createStroke(self.path())

    def set_live_value(self, value):
        """Store a live execution value and show it as a hover tooltip."""
        self._live_value = value
        if value is None:
            self.setToolTip("")
            return
        port_name = ""
        if self.from_port is not None:
            port_name = getattr(getattr(self.from_port, 'port_definition', None), 'name', '') or ''
        s = repr(value)
        if len(s) > 300:
            s = s[:297] + "..."
        self.setToolTip(f"{port_name}: {s}" if port_name else s)

    def clear_live_value(self):
        """Remove the live value tooltip."""
        self._live_value = None
        self.setToolTip("")
