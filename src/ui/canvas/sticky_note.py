from src.utils.qt_compat import QtWidgets, QtCore, QtGui
from uuid import uuid4

QGraphicsRectItem = QtWidgets.QGraphicsRectItem
QGraphicsTextItem = QtWidgets.QGraphicsTextItem
QGraphicsItem = QtWidgets.QGraphicsItem
Qt = QtCore.Qt
QRectF = QtCore.QRectF
QColor = QtGui.QColor
QPen = QtGui.QPen
QBrush = QtGui.QBrush
QFont = QtGui.QFont

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
        # Enable text editing
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)

        # Resize State
        self.resizing = False
        self.resize_handle_size = 15
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
        if self.text_item.boundingRect().contains(event.pos()):
            pass # Let text item handle it
            
        if event.button() == Qt.LeftButton and self._is_on_handle(event.pos()):
            self.resizing = True
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_width = max(50, event.pos().x())
            new_height = max(50, event.pos().y())
            self.setRect(0, 0, new_width, new_height)
            self.text_item.setTextWidth(new_width - 10)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())
        
        # Resize Handle
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        handle_rect = QRectF(self.rect().width() - 10, self.rect().height() - 10, 10, 10)
        painter.drawRect(handle_rect)

        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect().adjusted(-2, -2, 2, 2))

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()

        color_act = menu.addAction("Change Color")
        color_act.triggered.connect(self._pick_color)

        menu.addSeparator()

        delete_act = menu.addAction("Delete Sticky Note")
        def delete_self():
            if self.scene():
                self.setSelected(True)
                from src.utils.qt_compat import QtGui
                QKeyEvent = QtGui.QKeyEvent
                QEvent = QtCore.QEvent
                ev = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
                self.scene().keyPressEvent(ev)
        delete_act.triggered.connect(delete_self)

        menu.exec_(event.screenPos())

    def _pick_color(self):
        color = QtWidgets.QColorDialog.getColor(self.bg_color, None, "Choose Sticky Note Color")
        if color.isValid():
            self.bg_color = color
            self.setBrush(QBrush(self.bg_color))
            self.update()

    def get_text(self):
        return self.text_item.toPlainText()

    def set_text(self, text):
        self.text_item.setPlainText(text)
