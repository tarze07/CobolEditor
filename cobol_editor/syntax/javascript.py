"""Highlighter składni JavaScript/TypeScript"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class JavaScriptSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for JavaScript and TypeScript"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
            'if', 'import', 'in', 'instanceof', 'let', 'new', 'return', 'super', 'switch', 'this',
            'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'true', 'false',
            'null', 'undefined', 'static', 'get', 'set', 'of', 'from', 'as', 'interface', 'type',
            'implements', 'namespace', 'declare', 'abstract', 'readonly', 'private', 'protected',
            'public', 'constructor', 'enum', 'module', 'require', 'global', 'is', 'keyof',
            'infer', 'never', 'unknown', 'symbol', 'bigint', 'unique', 'satisfies', 'using'
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
        # JSDoc comments
        jsdoc_format = QTextCharFormat()
        jsdoc_format.setForeground(QColor(theme['comment']))
        jsdoc_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'/\*\*.*?\*/', re.DOTALL), jsdoc_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme['string']))
        # Double quoted
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        # Single quoted
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        # Template literals
        self.highlighting_rules.append((re.compile(r'`[^`\\]*(\\.[^`\\]*)*`'), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[oO]?[0-7]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[bB][01]+\b'), number_format))
        
        # Regex literals
        regex_format = QTextCharFormat()
        regex_format.setForeground(QColor(theme['string']))
        self.highlighting_rules.append((re.compile(r'/(?!/)(\\/|[^/])+/[gimuy]*'), regex_format))
        
        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(theme['datatype']))
        self.highlighting_rules.append((re.compile(r'\b[a-zA-Z_$][a-zA-Z0-9_$]*(?=\s*\()'), function_format))


# Rejestracja highlightera
register_highlighter(
    'JavaScript',
    JavaScriptSyntaxHighlighter,
    extensions=['js', 'jsx', 'mjs', 'ts', 'tsx']
)
