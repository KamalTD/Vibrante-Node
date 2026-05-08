import ast
import re
from src.utils.qt_compat import QtGui, QtCore, QtWidgets

QColor = QtGui.QColor
QFont = QtGui.QFont
Qt = QtCore.Qt
QPlainTextEdit = QtWidgets.QPlainTextEdit
QSyntaxHighlighter = QtGui.QSyntaxHighlighter
QTextCharFormat = QtGui.QTextCharFormat

# ── Try QScintilla; graceful fallback to QPlainTextEdit ───────────────────────

_QSCINTILLA_AVAILABLE = False
try:
    from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
    _QSCINTILLA_AVAILABLE = True
except ImportError:
    try:
        from PySide2.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
        _QSCINTILLA_AVAILABLE = True
    except ImportError:
        pass  # fallback implementation below

# ── Colour palettes ───────────────────────────────────────────────────────────

_DARK = {
    "BG":        "#282a36",
    "FG":        "#f8f8f2",
    "MARGIN_BG": "#2d2d2d",
    "MARGIN_FG": "#888888",
    "LINE_HL":   "#3c3c3c",
    "SEL_BG":    "#44475a",
    "COMMENT":   "#6272a4",
    "STRING":    "#f1fa8c",
    "KEYWORD":   "#ff79c6",
    "BUILTIN":   "#8be9fd",
    "NUMBER":    "#bd93f9",
    "OPERATOR":  "#ff79c6",
    "DECORATOR": "#ffb86c",
    "FUNCTION":  "#f1fa8c",
    "CLASS":     "#50fa7b",
    "ERROR_BG":  "#3d0000",
    "GUIDE":     "#3a3a4a",
    "UNMATCH_BG":"#ff5555",
}

_LIGHT = {
    "BG":        "#fafafa",
    "FG":        "#383a42",
    "MARGIN_BG": "#e8e8e8",
    "MARGIN_FG": "#999999",
    "LINE_HL":   "#f0f0f0",
    "SEL_BG":    "#bde3ff",
    "COMMENT":   "#a0a1a7",
    "STRING":    "#50a14f",
    "KEYWORD":   "#a626a4",
    "BUILTIN":   "#0184bc",
    "NUMBER":    "#986801",
    "OPERATOR":  "#383a42",
    "DECORATOR": "#4078f2",
    "FUNCTION":  "#4078f2",
    "CLASS":     "#c18401",
    "ERROR_BG":  "#fff0f0",
    "GUIDE":     "#dddddd",
    "UNMATCH_BG":"#ff9999",
}

_PYTHON_KEYWORDS = (
    "False None True and as assert async await break class continue def del "
    "elif else except finally for from global if import in is lambda nonlocal "
    "not or pass raise return try while with yield"
)

_PYTHON_BUILTINS = (
    "abs all any ascii bin bool breakpoint bytearray bytes callable chr "
    "classmethod compile complex delattr dict dir divmod enumerate eval exec "
    "filter float format frozenset getattr globals hasattr hash help hex id "
    "input int isinstance issubclass iter len list locals map max memoryview "
    "min next object oct open ord pow print property range repr reversed round "
    "set setattr slice sorted staticmethod str sum super tuple type vars zip "
    "self execute inputs add_input add_output BaseNode get_bridge "
    "is_available resolve_prism_core log_error log_info"
)


def _current_theme_is_dark() -> bool:
    try:
        from src.utils.config_manager import config
        return config.get("ui.theme", "dark") != "light"
    except Exception:
        return True


# =============================================================================
# FALLBACK: QPlainTextEdit-based editor (used when QScintilla is not installed)
# =============================================================================

if not _QSCINTILLA_AVAILABLE:

    class _PythonHighlighter(QSyntaxHighlighter):
        """Minimal regex-based Python syntax highlighter."""

        def __init__(self, document, palette):
            super().__init__(document)
            self._rules = []
            self._build_rules(palette)

        def _fmt(self, color_hex, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color_hex))
            if bold:
                fmt.setFontWeight(QtGui.QFont.Bold)
            return fmt

        def _build_rules(self, p):
            kw_fmt = self._fmt(p["KEYWORD"], bold=True)
            for kw in _PYTHON_KEYWORDS.split():
                self._rules.append((re.compile(rf"\b{kw}\b"), kw_fmt))

            bi_fmt = self._fmt(p["BUILTIN"])
            for bi in _PYTHON_BUILTINS.split():
                self._rules.append((re.compile(rf"\b{bi}\b"), bi_fmt))

            self._rules += [
                (re.compile(r"\bclass\s+(\w+)"),      self._fmt(p["CLASS"], bold=True)),
                (re.compile(r"\bdef\s+(\w+)"),        self._fmt(p["FUNCTION"])),
                (re.compile(r"@\w+"),                 self._fmt(p["DECORATOR"])),
                (re.compile(r"\b\d+(\.\d+)?\b"),      self._fmt(p["NUMBER"])),
                (re.compile(r"#[^\n]*"),               self._fmt(p["COMMENT"])),
                (re.compile(r"\"\"\"[\s\S]*?\"\"\""),  self._fmt(p["STRING"])),
                (re.compile(r"'''[\s\S]*?'''"),        self._fmt(p["STRING"])),
                (re.compile(r'"[^"\n]*"'),             self._fmt(p["STRING"])),
                (re.compile(r"'[^'\n]*'"),             self._fmt(p["STRING"])),
            ]

        def highlightBlock(self, text):
            for pattern, fmt in self._rules:
                for m in pattern.finditer(text):
                    self.setFormat(m.start(), m.end() - m.start(), fmt)

        def update_palette(self, palette):
            self._rules = []
            self._build_rules(palette)
            self.rehighlight()

    class _NoopMarginArea:
        def hide(self): pass
        def show(self): pass

    class CodeEditor(QPlainTextEdit):
        """Plain-text fallback editor used when QScintilla is not installed."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.error_line = -1
            self._is_dark = _current_theme_is_dark()
            self.lineNumberArea = _NoopMarginArea()
            self._highlighter = None
            self._setup()

        def _setup(self):
            font = QFont("Consolas", 11)
            font.setStyleHint(QFont.Monospace)
            self.setFont(font)
            self.setTabStopDistance(4 * QtGui.QFontMetricsF(font).horizontalAdvance(" "))
            p = _DARK if self._is_dark else _LIGHT
            self._highlighter = _PythonHighlighter(self.document(), p)
            self._apply_stylesheet(p)
            self.textChanged.connect(self._run_lint)

        def _apply_stylesheet(self, p):
            self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: {p['BG']};
                    color: {p['FG']};
                    border: 1px solid #3a3a4a;
                    selection-background-color: {p['SEL_BG']};
                }}
            """)

        def apply_theme(self, is_dark: bool):
            self._is_dark = is_dark
            p = _DARK if is_dark else _LIGHT
            self._highlighter.update_palette(p)
            self._apply_stylesheet(p)

        def _run_lint(self):
            try:
                ast.parse(self.toPlainText())
                self.error_line = -1
            except SyntaxError as e:
                self.error_line = e.lineno if e.lineno else -1

        def setViewportMargins(self, left, top, right, bottom):
            pass

        def setPlaceholderText(self, text):
            super().setPlaceholderText(text)

        def set_completer_list(self, words):
            pass

        def append_completer_list(self, words):
            pass

        def wheelEvent(self, event):
            if event.modifiers() == Qt.ControlModifier:
                font = self.font()
                delta = 1 if event.angleDelta().y() > 0 else -1
                font.setPointSize(max(6, font.pointSize() + delta))
                self.setFont(font)
            else:
                super().wheelEvent(event)


# =============================================================================
# FULL QSCINTILLA IMPLEMENTATION
# =============================================================================

else:

    class _DraculaPythonLexer(QsciLexerPython):
        def keywords(self, keyset):
            if keyset == 2:
                return _PYTHON_BUILTINS
            return super().keywords(keyset)

    class _MarginCompat:
        """Shim matching the old `.lineNumberArea` hide/show API."""

        def __init__(self, editor):
            self._e = editor

        def hide(self):
            for i in range(4):
                self._e.setMarginWidth(i, 0)

        def show(self):
            self._e._restore_margins()

    class CodeEditor(QsciScintilla):
        """
        Professional Python code editor (QScintilla) with Dracula-dark / One-Light
        palettes that switch via apply_theme(is_dark).

        API surface is backward-compatible with the old QPlainTextEdit-based editor:
        setPlainText / toPlainText / textChanged / lineNumberArea.hide() all work.
        """

        def __init__(self, parent=None):
            super().__init__(parent)
            self.error_line = -1
            self._base_font_size = 11
            self._is_dark = True
            self.lineNumberArea = _MarginCompat(self)
            self._setup()

        def _setup(self):
            is_dark = _current_theme_is_dark()
            self._is_dark = is_dark
            p = _DARK if is_dark else _LIGHT

            font = QFont("Consolas", self._base_font_size)
            font.setStyleHint(QFont.Monospace)
            self.setFont(font)
            self.setMarginsFont(font)

            self.setMarginType(0, QsciScintilla.NumberMargin)
            self.setMarginWidth(0, "00000")

            self.setMarginType(1, QsciScintilla.SymbolMargin)
            self.setMarginWidth(1, 14)
            self.setMarginSensitivity(1, False)
            self._error_marker = self.markerDefine(QsciScintilla.Background, 0)

            self.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)

            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
            self.setAutoIndent(True)
            self.setIndentationGuides(True)
            self.setIndentationsUseTabs(False)
            self.setTabWidth(4)
            self.setBackspaceUnindents(True)
            self.setWrapMode(QsciScintilla.WrapNone)
            self.setScrollWidth(1)
            self.setScrollWidthTracking(True)
            self.setCaretLineVisible(True)

            self._setup_lexer(p)
            self._setup_autocomplete()
            self._apply_widget_colors(p)

            self.textChanged.connect(self._run_lint)

        def _setup_lexer(self, p):
            font = QFont("Consolas", self._base_font_size)
            font.setStyleHint(QFont.Monospace)

            lexer = _DraculaPythonLexer(self)
            lexer.setDefaultFont(font)
            lexer.setFont(font)
            self._apply_lexer_colors_to(lexer, p)
            self.setLexer(lexer)
            self._lexer = lexer

        def _setup_autocomplete(self):
            self._api = QsciAPIs(self._lexer)
            for word in (_PYTHON_KEYWORDS + " " + _PYTHON_BUILTINS).split():
                self._api.add(word)
            self._api.prepare()

            self.setAutoCompletionSource(QsciScintilla.AcsAll)
            self.setAutoCompletionThreshold(2)
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionReplaceWord(False)
            self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        def apply_theme(self, is_dark: bool):
            self._is_dark = is_dark
            p = _DARK if is_dark else _LIGHT
            self._apply_lexer_colors_to(self._lexer, p)
            self._apply_widget_colors(p)

        def _apply_lexer_colors_to(self, lexer, p):
            font = QFont("Consolas", self._base_font_size)
            font.setStyleHint(QFont.Monospace)
            bold = QFont("Consolas", self._base_font_size)
            bold.setBold(True)
            bold.setStyleHint(QFont.Monospace)

            bg = QColor(p["BG"])
            for style in range(32):
                lexer.setPaper(bg, style)

            lexer.setColor(QColor(p["FG"]),        QsciLexerPython.Default)
            lexer.setColor(QColor(p["COMMENT"]),   QsciLexerPython.Comment)
            lexer.setColor(QColor(p["COMMENT"]),   QsciLexerPython.CommentBlock)

            for style in (
                QsciLexerPython.SingleQuotedString,
                QsciLexerPython.DoubleQuotedString,
                QsciLexerPython.TripleSingleQuotedString,
                QsciLexerPython.TripleDoubleQuotedString,
                QsciLexerPython.UnclosedString,
                QsciLexerPython.SingleQuotedFString,
                QsciLexerPython.DoubleQuotedFString,
                QsciLexerPython.TripleSingleQuotedFString,
                QsciLexerPython.TripleDoubleQuotedFString,
            ):
                lexer.setColor(QColor(p["STRING"]), style)

            lexer.setColor(QColor(p["KEYWORD"]),   QsciLexerPython.Keyword)
            lexer.setFont(bold,                    QsciLexerPython.Keyword)
            lexer.setColor(QColor(p["FG"]),        QsciLexerPython.Identifier)
            lexer.setColor(QColor(p["BUILTIN"]),   QsciLexerPython.HighlightedIdentifier)
            lexer.setColor(QColor(p["NUMBER"]),    QsciLexerPython.Number)
            lexer.setColor(QColor(p["OPERATOR"]),  QsciLexerPython.Operator)
            lexer.setColor(QColor(p["DECORATOR"]), QsciLexerPython.Decorator)
            lexer.setColor(QColor(p["FUNCTION"]),  QsciLexerPython.FunctionMethodName)
            lexer.setColor(QColor(p["CLASS"]),     QsciLexerPython.ClassName)
            lexer.setFont(bold,                    QsciLexerPython.ClassName)

        def _apply_widget_colors(self, p):
            self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, 32, QColor(p["BG"]))
            self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, 32, QColor(p["FG"]))

            self.setMarginsBackgroundColor(QColor(p["MARGIN_BG"]))
            self.setMarginsForegroundColor(QColor(p["MARGIN_FG"]))
            self.setFoldMarginColors(QColor(p["MARGIN_BG"]), QColor(p["MARGIN_BG"]))

            self.setMarkerBackgroundColor(QColor(p["ERROR_BG"]), self._error_marker)

            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QColor(p["LINE_HL"]))
            self.setCaretForegroundColor(QColor(p["FG"]))

            self.setSelectionBackgroundColor(QColor(p["SEL_BG"]))
            self.setSelectionForegroundColor(QColor(p["FG"]))

            self.setMatchedBraceBackgroundColor(QColor(p["SEL_BG"]))
            self.setMatchedBraceForegroundColor(QColor(p["KEYWORD"]))
            self.setUnmatchedBraceBackgroundColor(QColor(p["UNMATCH_BG"]))
            self.setUnmatchedBraceForegroundColor(QColor(p["FG"]))

            self.setIndentationGuidesBackgroundColor(QColor(p["BG"]))
            self.setIndentationGuidesForegroundColor(QColor(p["GUIDE"]))

        def _run_lint(self):
            self.markerDeleteAll(self._error_marker)
            try:
                ast.parse(self.text())
                self.error_line = -1
            except SyntaxError as e:
                self.error_line = e.lineno if e.lineno else -1
                if self.error_line > 0:
                    self.markerAdd(self.error_line - 1, self._error_marker)

        def _restore_margins(self):
            self.setMarginWidth(0, "00000")
            self.setMarginWidth(1, 14)

        def setPlainText(self, text):
            self.setText(text or "")

        def toPlainText(self):
            return self.text()

        def setViewportMargins(self, left, top, right, bottom):
            if left == 0 and top == 0 and right == 0 and bottom == 0:
                for i in range(4):
                    self.setMarginWidth(i, 0)

        def setPlaceholderText(self, _text):
            pass

        def set_completer_list(self, words):
            self._api.clear()
            for w in words:
                self._api.add(w)
            self._api.prepare()

        def append_completer_list(self, words):
            for w in words:
                self._api.add(w)
            self._api.prepare()

        def wheelEvent(self, event):
            if event.modifiers() == Qt.ControlModifier:
                if event.angleDelta().y() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()
            else:
                super().wheelEvent(event)
