"""Highlighter składni Python"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class PythonSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for Python"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class',
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield', 'match', 'case'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern), keyword_format))
        
        # Built-in functions
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor(theme['datatype']))
        builtins = [
            'abs', 'aiter', 'all', 'anext', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray',
            'bytes', 'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict',
            'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int',
            'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview',
            'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property', 'range',
            'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__'
        ]
        builtin_pattern = r'\b(' + '|'.join(builtins) + r')\b'
        self.highlighting_rules.append((re.compile(builtin_pattern), builtin_format))
        
        # Decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'^\s*@[a-zA-Z_][a-zA-Z0-9_]*'), decorator_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))
        
        # Docstrings
        docstring_format = QTextCharFormat()
        docstring_format.setForeground(QColor(theme['string']))
        docstring_format.setFontItalic(True)
        # Triple double quotes
        self.highlighting_rules.append((re.compile(r'"""[^"]*"""', re.DOTALL), docstring_format))
        # Triple single quotes
        self.highlighting_rules.append((re.compile(r"'''[^']*'''", re.DOTALL), docstring_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme['string']))
        # Double quoted
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        # Single quoted
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        # f-strings
        fstring_format = QTextCharFormat()
        fstring_format.setForeground(QColor(theme['string']))
        self.highlighting_rules.append((re.compile(r'f"[^"\\]*(\\.[^"\\]*)*"'), fstring_format))
        self.highlighting_rules.append((re.compile(r"f'[^'\\]*(\\.[^'\\]*)*'"), fstring_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b\d+\.\d+([eE][+-]?\d+)?\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[oO][0-7]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[bB][01]+\b'), number_format))
        
        # Self and cls
        self_format = QTextCharFormat()
        self_format.setForeground(QColor(theme['keyword']))
        self_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'\b(self|cls)\b'), self_format))
        
        # Class definitions
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(theme['datatype']))
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)'), class_format))
        
        # Function definitions
        func_format = QTextCharFormat()
        func_format.setForeground(QColor(theme['datatype'])
        )
        self.highlighting_rules.append((re.compile(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)'), func_format))


# Rejestracja highlightera
register_highlighter(
    'Python',
    PythonSyntaxHighlighter,
    extensions=['py', 'pyw']
)
