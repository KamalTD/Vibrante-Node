from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(200, 120, 50))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield", "self"
        ]
        for word in keywords:
            pattern = QRegExp(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        class_format = QTextCharFormat()
        class_format.setForeground(QColor(255, 215, 0))
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("\\bclass\\s+\\w+"), class_format))

        function_format = QTextCharFormat()
        function_format.setForeground(QColor(100, 149, 237))
        self.highlighting_rules.append((QRegExp("\\bdef\\s+\\w+"), function_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))
        self.highlighting_rules.append((QRegExp("#.*"), comment_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(106, 171, 115))
        self.highlighting_rules.append((QRegExp("\".*\""), string_format))
        self.highlighting_rules.append((QRegExp("'.*'"), string_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)
