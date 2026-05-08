from src.utils.qt_compat import QtWidgets, QtCore, QtGui

QFrame = QtWidgets.QFrame
QHBoxLayout = QtWidgets.QHBoxLayout
QLineEdit = QtWidgets.QLineEdit
QLabel = QtWidgets.QLabel
QToolButton = QtWidgets.QToolButton
Qt = QtCore.Qt
QKeyEvent = QtGui.QKeyEvent


class CanvasSearchBar(QFrame):
    """Floating search bar overlaid on NodeView.

    Press Ctrl+F to open. Type to filter nodes by name. Enter/▼ cycles
    forward through matches; Shift+Enter/▲ cycles backward. Escape closes.
    The matched node is selected and the view pans to it.
    """

    def __init__(self, view):
        super().__init__(view)
        self._view = view
        self._matches = []
        self._current_idx = -1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search nodes…")
        self._input.setFixedWidth(200)
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        self._label = QLabel("0 / 0")
        self._label.setFixedWidth(46)
        self._label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label)

        self._prev_btn = QToolButton()
        self._prev_btn.setText("▲")
        self._prev_btn.setToolTip("Previous match (Shift+Enter)")
        self._prev_btn.clicked.connect(self._go_prev)
        layout.addWidget(self._prev_btn)

        self._next_btn = QToolButton()
        self._next_btn.setText("▼")
        self._next_btn.setToolTip("Next match (Enter)")
        self._next_btn.clicked.connect(self._go_next)
        layout.addWidget(self._next_btn)

        close_btn = QToolButton()
        close_btn.setText("✕")
        close_btn.setToolTip("Close (Escape)")
        close_btn.clicked.connect(self.hide_bar)
        layout.addWidget(close_btn)

        self.adjustSize()
        self.hide()
        self.apply_theme(True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_bar(self):
        scene = self._view.scene()
        if scene:
            is_dark = scene.backgroundBrush().color().lightness() < 128
            self.apply_theme(is_dark)
        self._reposition()
        self.show()
        self.raise_()
        self._input.setFocus()
        self._input.selectAll()
        self._on_text_changed(self._input.text())

    def hide_bar(self):
        self.hide()
        self._clear_state()
        self._view.setFocus()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reposition(self):
        self.adjustSize()
        x = max(0, (self._view.width() - self.width()) // 2)
        self.move(x, 8)

    def _on_text_changed(self, text):
        scene = self._view.scene()
        if not scene:
            return
        t = text.strip().lower()
        if t:
            self._matches = [
                w for w in scene.nodes
                if t in w.node_definition.name.lower()
                or t in getattr(w.node_definition, 'node_id', '').lower()
            ]
        else:
            self._matches = []
        self._current_idx = 0 if self._matches else -1
        self._update_label()
        self._pan_to_current()

    def _go_next(self):
        if not self._matches:
            return
        self._current_idx = (self._current_idx + 1) % len(self._matches)
        self._update_label()
        self._pan_to_current()

    def _go_prev(self):
        if not self._matches:
            return
        self._current_idx = (self._current_idx - 1) % len(self._matches)
        self._update_label()
        self._pan_to_current()

    def _update_label(self):
        total = len(self._matches)
        if total:
            self._label.setText(f"{self._current_idx + 1} / {total}")
        else:
            self._label.setText("0 / 0")

    def _pan_to_current(self):
        scene = self._view.scene()
        if not scene or self._current_idx < 0 or not self._matches:
            if scene:
                scene.clearSelection()
            return
        node = self._matches[self._current_idx]
        scene.clearSelection()
        node.setSelected(True)
        self._view.centerOn(node)

    def _clear_state(self):
        scene = self._view.scene()
        if scene:
            scene.clearSelection()
        self._matches = []
        self._current_idx = -1
        self._label.setText("0 / 0")
        self._input.clear()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.hide_bar()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                self._go_prev()
            else:
                self._go_next()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, is_dark=True):
        if is_dark:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                    border-radius: 6px;
                }
                QLineEdit {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 4px 6px;
                    font-size: 12px;
                }
                QLineEdit:focus { border: 1px solid #6699cc; }
                QLabel { color: #aaaaaa; font-size: 11px; min-width: 46px; }
                QToolButton {
                    color: #cccccc;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                    padding: 2px 6px;
                }
                QToolButton:hover { color: #ffffff; background: #4b4d4d; border-radius: 3px; }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px 6px;
                    font-size: 12px;
                }
                QLineEdit:focus { border: 1px solid #4a90d9; }
                QLabel { color: #666666; font-size: 11px; min-width: 46px; }
                QToolButton {
                    color: #333333;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                    padding: 2px 6px;
                }
                QToolButton:hover { color: #000000; background: #e0e0e0; border-radius: 3px; }
            """)
