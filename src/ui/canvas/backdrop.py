from src.utils.qt_compat import QtWidgets, QtCore, QtGui
from uuid import uuid4

QGraphicsRectItem = QtWidgets.QGraphicsRectItem
QGraphicsTextItem = QtWidgets.QGraphicsTextItem
QGraphicsItem = QtWidgets.QGraphicsItem
Qt = QtCore.Qt
QRectF = QtCore.QRectF
QPointF = QtCore.QPointF
QColor = QtGui.QColor
QPen = QtGui.QPen
QBrush = QtGui.QBrush
QCursor = QtGui.QCursor

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
        # 1. Title item interaction
        if self.title_item.boundingRect().contains(event.pos()):
            super().mousePressEvent(event)
            return
            
        # 2. Resize handle interaction
        if event.button() == Qt.LeftButton and self._is_on_handle(event.pos()):
            self.resizing = True
            event.accept()
            return
            
        # 3. Header interaction (Move & Select)
        if event.pos().y() < 35:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            super().mousePressEvent(event)
        else:
            # 4. Body interaction (Select, but allow RubberBand selection through to the View)
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setSelected(True)
            # By ignoring the event, we allow the QGraphicsView to receive it 
            # and start its RubberBandDrag logic if the user drags.
            event.ignore()

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

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()

        color_act = menu.addAction("Change Color")
        color_act.triggered.connect(self._pick_color)

        menu.addSeparator()

        fit_act = menu.addAction("Fit to Contained Nodes")
        fit_act.triggered.connect(self.fit_to_nodes)

        select_act = menu.addAction("Select Contained Nodes")
        select_act.triggered.connect(self.select_contained_nodes)

        menu.addSeparator()

        delete_act = menu.addAction("Delete Network Box")
        def delete_self():
            if self.scene():
                # NodeScene handles the actual removal from its internal lists if we use its logic,
                # but for simple UI triggered delete, we can just send a Delete key event to the scene
                # or call scene method.
                self.setSelected(True)
                from src.utils.qt_compat import QtGui
                QKeyEvent = QtGui.QKeyEvent
                QEvent = QtCore.QEvent
                ev = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
                self.scene().keyPressEvent(ev)
        delete_act.triggered.connect(delete_self)
        
        menu.exec_(event.screenPos())

    def _pick_color(self):
        opaque = QColor(self.bg_color)
        opaque.setAlpha(255)
        color = QtWidgets.QColorDialog.getColor(opaque, None, "Choose Network Box Color")
        if color.isValid():
            self.bg_color = QColor(color)
            self.bg_color.setAlpha(100)
            self.setBrush(QBrush(self.bg_color))
            self.update()

    def fit_to_nodes(self):
        """Resizes the backdrop to fit all nodes currently inside or partially inside it."""
        if not self.scene(): return
        
        contained_items = []
        from src.ui.node_widget import NodeWidget
        from src.ui.canvas.sticky_note import StickyNote
        
        # Find all nodes/notes in the scene that overlap with this backdrop
        for item in self.scene().items():
            if item == self: continue
            if isinstance(item, (NodeWidget, StickyNote)):
                if self.sceneBoundingRect().intersects(item.sceneBoundingRect()):
                    contained_items.append(item)
        
        if not contained_items:
            return
            
        # Calculate new bounding rect
        rect = contained_items[0].sceneBoundingRect()
        for item in contained_items[1:]:
            rect = rect.united(item.sceneBoundingRect())
            
        # Add padding
        padding = 40
        new_pos = QtCore.QPointF(rect.x() - padding, rect.y() - padding - 20)
        new_size = (rect.width() + padding*2, rect.height() + padding*2 + 20)
        
        self.prepareGeometryChange()
        self.setPos(new_pos)
        self.setRect(0, 0, new_size[0], new_size[1])

    def select_contained_nodes(self):
        if not self.scene(): return
        self.scene().clearSelection()
        
        from src.ui.node_widget import NodeWidget
        from src.ui.canvas.sticky_note import StickyNote
        
        bounds = self.sceneBoundingRect()
        for item in self.scene().items():
            if isinstance(item, (NodeWidget, StickyNote)):
                if bounds.contains(item.sceneBoundingRect().center()):
                    item.setSelected(True)

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
