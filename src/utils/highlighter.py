import re
from src.utils.qt_compat import QtCore, QtGui

QSyntaxHighlighter = QtGui.QSyntaxHighlighter
QTextCharFormat = QtGui.QTextCharFormat
QFont = QtGui.QFont
QColor = QtGui.QColor
Qt = QtCore.Qt

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Keywords (Dracula Pink)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#ff79c6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield", "self"
        ]
        for word in keywords:
            self.highlighting_rules.append((re.compile(rf"\b{word}\b"), keyword_format))

        # Builtins (Dracula Cyan)
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#8be9fd"))
        builtins = [
            "abs", "all", "any", "ascii", "bin", "bool", "breakpoint", "bytearray",
            "bytes", "callable", "chr", "classmethod", "compile", "complex",
            "delattr", "dict", "dir", "divmod", "enumerate", "eval", "exec",
            "filter", "float", "format", "frozenset", "getattr", "globals",
            "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance",
            "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
            "min", "next", "object", "oct", "open", "ord", "pow", "print",
            "property", "range", "repr", "reversed", "round", "set", "setattr",
            "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple",
            "type", "vars", "zip"
        ]
        for word in builtins:
            self.highlighting_rules.append((re.compile(rf"\b{word}\b"), builtin_format))

        # Classes (Dracula Green)
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#50fa7b"))
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r"\bclass\s+\w+"), class_format))

        # Functions (Dracula Yellow)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#f1fa8c"))
        self.highlighting_rules.append((re.compile(r"\bdef\s+\w+"), function_format))

        # Decorators (Dracula Orange)
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#ffb86c"))
        self.highlighting_rules.append((re.compile(r"@\w+"), decorator_format))

        # Numbers (Dracula Purple)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#bd93f9"))
        self.highlighting_rules.append((re.compile(r"\b[0-9]+L?\b"), number_format))
        self.highlighting_rules.append((re.compile(r"\b0x[0-9A-Fa-f]+L?\b"), number_format))
        self.highlighting_rules.append((re.compile(r"\b[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?\b"), number_format))

        # Comments (Dracula Muted Blue)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6272a4"))
        self.highlighting_rules.append((re.compile(r"#.*"), self.comment_format))

        # Strings (Dracula Orange/Yellow)
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#f1fa8c"))
        self.highlighting_rules.append((re.compile(r'".*?"'), self.string_format))
        self.highlighting_rules.append((re.compile(r"'.*?'"), self.string_format))

        self.triple_double_re = re.compile(r'"""')
        self.triple_single_re = re.compile(r"'''")

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)

        self.setCurrentBlockState(0)

        # Multi-line strings
        start_index = 0
        if self.previousBlockState() != 1:
            m = self.triple_double_re.search(text)
            start_index = m.start() if m else -1

        while start_index >= 0:
            m = self.triple_double_re.search(text, start_index + 3)
            if m is None:
                self.setCurrentBlockState(1)
                comment_len = len(text) - start_index
            else:
                end_index = m.start()
                comment_len = end_index - start_index + 3

            self.setFormat(start_index, comment_len, self.string_format)
            m2 = self.triple_double_re.search(text, start_index + comment_len)
            start_index = m2.start() if m2 else -1
