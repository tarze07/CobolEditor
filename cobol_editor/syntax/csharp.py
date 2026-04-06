"""Highlighter składni C#"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class CSharpSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for C#"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'abstract', 'as', 'base', 'bool', 'break', 'byte', 'case', 'catch', 'char', 'checked',
            'class', 'const', 'continue', 'decimal', 'default', 'delegate', 'do', 'double', 'else',
            'enum', 'event', 'explicit', 'extern', 'false', 'finally', 'fixed', 'float', 'for',
            'foreach', 'goto', 'if', 'implicit', 'in', 'int', 'interface', 'internal', 'is', 'lock',
            'long', 'namespace', 'new', 'null', 'object', 'operator', 'out', 'override', 'params',
            'private', 'protected', 'public', 'readonly', 'ref', 'return', 'sbyte', 'sealed',
            'short', 'sizeof', 'stackalloc', 'static', 'string', 'struct', 'switch', 'this',
            'throw', 'true', 'try', 'typeof', 'uint', 'ulong', 'unchecked', 'unsafe', 'ushort',
            'using', 'virtual', 'void', 'volatile', 'while', 'async', 'await', 'var', 'record',
            'init', 'required', 'when', 'nameof', 'with', 'yield', 'get', 'set', 'add', 'remove',
            'where', 'partial', 'dynamic', 'let', 'from', 'select', 'group', 'into', 'orderby',
            'join', 'on', 'equals', 'by', 'ascending', 'descending'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern), keyword_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))
        # Multi-line comments
        self.highlighting_rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme['string']))
        # Regular strings
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        # Verbatim strings
        self.highlighting_rules.append((re.compile(r'@"(?:""|[^"])*"'), string_format))
        # Interpolated strings
        self.highlighting_rules.append((re.compile(r'\$"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        # Single-quoted chars
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+(\.\d+)?([eE][+-]?\d+)?[fFdDmM]?\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[bB][01]+\b'), number_format))
        
        # Preprocessor directives
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'^\s*#\s*(if|else|elif|endif|define|undef|warning|error|line|region|endregion|pragma)\b'), preprocessor_format))


# Rejestracja highlightera
register_highlighter(
    'C#',
    CSharpSyntaxHighlighter,
    extensions=['cs', 'csharp']
)
