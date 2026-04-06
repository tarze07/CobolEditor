"""Highlighter składni YAML"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class YAMLSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for YAML"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Keys
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(theme['keyword']))
        key_format.setFontWeight(QFont.Bold)
        # Standard key
        self.highlighting_rules.append((re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(?=\s*:)'), key_format))
        # Quoted key
        self.highlighting_rules.append((re.compile(r'^"[^"]*"(?=\s*:)'), key_format))
        self.highlighting_rules.append((re.compile(r"^'[^']*'(?=\s*:)"), key_format))
        # Complex key with special chars
        self.highlighting_rules.append((re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\-]*(?=\s*:)'), key_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme['string']))
        # Double quoted
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        # Single quoted
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        # Unquoted strings (after colon or dash)
        self.highlighting_rules.append((re.compile(r'(?<=:\s)[^\s#\n][^#\n]*'), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b\d+\.\d+\b'), number_format))
        
        # Boolean and null values
        constant_format = QTextCharFormat()
        constant_format.setForeground(QColor(theme['datatype']))
        constants = ['true', 'false', 'yes', 'no', 'on', 'off', 'null', '~']
        constant_pattern = r'\b(' + '|'.join(constants) + r')\b'
        self.highlighting_rules.append((re.compile(constant_pattern, re.IGNORECASE), constant_format))
        
        # Directives
        directive_format = QTextCharFormat()
        directive_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'^%[A-Z]+'), directive_format))
        
        # Document separators
        docsep_format = QTextCharFormat()
        docsep_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'^---'), docsep_format))
        self.highlighting_rules.append((re.compile(r'^\.\.\.'), docsep_format))
        
        # Anchors and aliases
        anchor_format = QTextCharFormat()
        anchor_format.setForeground(QColor(theme['section']))
        self.highlighting_rules.append((re.compile(r'&[a-zA-Z_][a-zA-Z0-9_]*'), anchor_format))
        self.highlighting_rules.append((re.compile(r'\*[a-zA-Z_][a-zA-Z0-9_]*'), anchor_format))
        
        # Tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(theme['datatype']))
        self.highlighting_rules.append((re.compile(r'!![a-zA-Z]+'), tag_format))
        self.highlighting_rules.append((re.compile(r'![a-zA-Z_][a-zA-Z0-9_]*'), tag_format))
        
        # List items
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'^(\s*)-\s'), list_format))


# Rejestracja highlightera
register_highlighter(
    'YAML',
    YAMLSyntaxHighlighter,
    extensions=['yaml', 'yml']
)
