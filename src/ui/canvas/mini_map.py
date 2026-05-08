from src.utils.qt_compat import QtWidgets, QtCore, QtGui

QGraphicsView = QtWidgets.QGraphicsView
Qt = QtCore.Qt
QRectF = QtCore.QRectF
QTimer = QtCore.QTimer
QPen = QtGui.QPen
QColor = QtGui.QColor
QBrush = QtGui.QBrush
QPainter = QtGui.QPainter

_W, _H = 200, 150   # fixed widget size in pixels
_PAD = 40            # extra scene-unit padding around items bounding rect


class MiniMap(QGraphicsView):
    """Thumbnail of the full canvas overlaid at the bottom-right of NodeView.

    Shares the same QGraphicsScene as the parent NodeView.
    Draws a blue semi-transparent rectangle showing the current viewport.
    Click or drag to pan the main view.
    """

    def __init__(self, main_view):
        super().__init__(main_view)   # child widget of NodeView
        self._main_view = main_view
        self._dragging = False

        self.setObjectName("MiniMapView")
        self.setFixedSize(_W, _H)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        # Debounce re-fit when scene items change rapidly
        self._fit_timer = QTimer(self)
        self._fit_timer.setSingleShot(True)
        self._fit_timer.setInterval(80)
        self._fit_timer.timeout.connect(self._do_fit)

        self.apply_theme(True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def attach_scene(self, scene):
        """Attach to a scene, disconnecting from any previous one."""
        old = self.scene()
        if old is not None:
            try:
                old.changed.disconnect(self._schedule_fit)
            except RuntimeError:
                pass
        self.setScene(scene)
        if scene is not None:
            scene.changed.connect(self._schedule_fit)
            self._do_fit()

    def refresh(self):
        """Redraw the viewport indicator without re-fitting (cheap)."""
        self.update()

    def reposition(self):
        """Pin to the bottom-right corner of the parent NodeView."""
        pv = self._main_view
        self.move(pv.width() - self.width() - 8,
                  pv.height() - self.height() - 8)

    def apply_theme(self, is_dark=True):
        border = "#555555" if is_dark else "#aaaaaa"
        self.setStyleSheet(
            f"QGraphicsView#MiniMapView {{ border: 1px solid {border};"
            f" border-radius: 4px; }}"
        )

    # ------------------------------------------------------------------
    # Internal — scene fit
    # ------------------------------------------------------------------

    def _schedule_fit(self, _rects=None):
        if not self._fit_timer.isActive():
            self._fit_timer.start()

    def _do_fit(self):
        scene = self.scene()
        if not scene:
            return
        r = scene.itemsBoundingRect()
        if r.isEmpty():
            r = QRectF(-200, -200, 400, 400)
        else:
            r.adjust(-_PAD, -_PAD, _PAD, _PAD)
        self.fitInView(r, Qt.KeepAspectRatio)
        self.update()

    # ------------------------------------------------------------------
    # Viewport indicator drawn over the scene thumbnail
    # ------------------------------------------------------------------

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        mv = self._main_view
        vp = mv.viewport().rect()
        scene_rect = QRectF(mv.mapToScene(vp.topLeft()),
                            mv.mapToScene(vp.bottomRight()))
        painter.save()
        painter.setBrush(QBrush(QColor(100, 180, 255, 35)))
        painter.setPen(QPen(QColor(100, 180, 255, 200), 1.5))
        painter.drawRect(scene_rect)
        painter.restore()

    # ------------------------------------------------------------------
    # Mouse — pan main view; do NOT propagate to scene items
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._pan_to(event.pos())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._pan_to(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self._main_view.setFocus()

    def _pan_to(self, mini_pos):
        scene_pos = self.mapToScene(mini_pos)
        self._main_view.centerOn(scene_pos)
        self.update()
