from src.utils.qt_compat import QtWidgets, QtCore, QtGui, Signal

QPlainTextEdit = QtWidgets.QPlainTextEdit
QWidget = QtWidgets.QWidget
QTextEdit = QtWidgets.QTextEdit
QCompleter = QtWidgets.QCompleter
Qt = QtCore.Qt
QRect = QtCore.QRect
QSize = QtCore.QSize
QStringListModel = QtCore.QStringListModel
QColor = QtGui.QColor
QPainter = QtGui.QPainter
QTextFormat = QtGui.QTextFormat
QFont = QtGui.QFont
QCursor = QtGui.QCursor
QTextCursor = QtGui.QTextCursor
import ast

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self.match_brackets)
        self.textChanged.connect(self.run_lint)

        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
        # Professional Look
        self.base_font_size = 11
        font = QFont("Consolas", self.base_font_size)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Completer Setup
        self.completer = QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        python_keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield", "self", "execute", "inputs", "add_input", "add_output"
        ]
        self.completer.setModel(QStringListModel(python_keywords, self.completer))
        self.completer.activated.connect(self.insert_completion)

        self.error_line = -1

    def insert_completion(self, completion):
        if self.completer.widget() != self:
            return
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def run_lint(self):
        code = self.toPlainText()
        try:
            ast.parse(code)
            self.error_line = -1
        except SyntaxError as e:
            self.error_line = e.lineno
        self.update() # Redraw line numbers to show error

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        extraSelections = getattr(self, '_extra_selections_brackets', [])
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(60, 60, 60) if self.palette().base().color().lightness() < 128 else QColor(Qt.yellow).lighter(160)
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def match_brackets(self):
        self._extra_selections_brackets = []
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()
        if pos == 0: return

        char_before = text[pos-1]
        pairs = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}
        if char_before in pairs:
            target = pairs[char_before]
            direction = 1 if char_before in '([{' else -1
            counter = 1
            check_pos = pos - 1 + direction
            while 0 <= check_pos < len(text):
                if text[check_pos] == char_before: counter += 1
                elif text[check_pos] == target: counter -= 1
                if counter == 0:
                    for p in [pos-1, check_pos]:
                        sel = QTextEdit.ExtraSelection()
                        sel.format.setBackground(QColor("#44475a"))
                        sel.format.setForeground(QColor("#ff79c6"))
                        sel.format.setFontWeight(QFont.Bold)
                        sel.cursor = self.textCursor()
                        sel.cursor.setPosition(p)
                        sel.cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                        self._extra_selections_brackets.append(sel)
                    break
                check_pos += direction
        self.highlight_current_line()

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        is_dark = self.palette().base().color().lightness() < 128
        bg_color = QColor(45, 45, 45) if is_dark else QColor(240, 240, 240)
        painter.fillRect(event.rect(), bg_color)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                # Highlight error line in red
                if blockNumber + 1 == self.error_line:
                    painter.setPen(Qt.red)
                    painter.setBrush(QColor(255, 0, 0, 50))
                    painter.drawRect(0, top, self.lineNumberArea.width(), self.fontMetrics().height())
                else:
                    painter.setPen(Qt.gray)
                
                painter.drawText(0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return

        # Smart Indentation on Enter
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text().rstrip()
            indent = ""
            for char in text:
                if char == ' ': indent += " "
                elif char == '\t': indent += "\t"
                else: break
            
            if text.endswith(":"):
                indent += "    "
            
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        cursor = self.textCursor()
        
        # Block Indent
        if event.key() == Qt.Key_Tab:
            if cursor.hasSelection():
                # Block indent logic
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.StartOfLine)
                while cursor.position() < end:
                    cursor.insertText("    ")
                    cursor.movePosition(QTextCursor.EndOfLine)
                    if not cursor.movePosition(QTextCursor.NextBlock): break
                    end += 4
                return
            elif event.modifiers() == Qt.NoModifier:
                self.insertPlainText("    ") # Soft tab
                return

        # Auto-closing
        auto_closes = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        if event.text() in auto_closes:
            self.insertPlainText(event.text() + auto_closes[event.text()])
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            return

        super().keyPressEvent(event)

        # Trigger Completer
        ctrl_space = (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Space)
        completion_prefix = self.text_under_cursor()
        
        if (not event.text() and not ctrl_space) or (len(completion_prefix) < 1 and not ctrl_space):
            self.completer.popup().hide()
            return

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def set_completer_list(self, words):
        self.completer.setModel(QStringListModel(words, self.completer))

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0: self.base_font_size += 1
            else: self.base_font_size = max(6, self.base_font_size - 1)
            f = self.font()
            f.setPointSize(self.base_font_size)
            self.setFont(f)
        else:
            super().wheelEvent(event)
