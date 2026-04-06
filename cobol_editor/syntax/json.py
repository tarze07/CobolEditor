"""Highlighter składni JSON"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class JSONSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for JSON"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Keys (strings before colon)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(theme['keyword']))
        key_format.setFontWeight(QFont.Bold)
        # Double quoted key
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"(?=\s*:)'), key_format))
        
        # String values
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'-?\b\d+(\.\d+)?([eE][+-]?\d+)?\b'), number_format))
        
        # Constants
        constant_format = QTextCharFormat()
        constant_format.setForeground(QColor(theme['datatype']))
        self.highlighting_rules.append((re.compile(r'\b(true|false|null)\b'), constant_format))
        
        # Brackets and braces
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'[\{\}\[\]]'), bracket_format))
        
        # Colons and commas
        punctuation_format = QTextCharFormat()
        punctuation_format.setForeground(QColor(theme['fg']))
        self.highlighting_rules.append((re.compile(r'[,:]'), punctuation_format))


# Rejestracja highlightera
register_highlighter(
    'JSON',
    JSONSyntaxHighlighter,
    extensions=['json']
)
