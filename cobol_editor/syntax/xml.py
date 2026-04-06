"""Highlighter składni XML/HTML"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class XMLSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for XML, HTML, XAML"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(theme['keyword']))
        tag_format.setFontWeight(QFont.Bold)
        # Opening tags
        self.highlighting_rules.append((re.compile(r'<[a-zA-Z_][a-zA-Z0-9_:\-]*'), tag_format))
        # Closing tags
        self.highlighting_rules.append((re.compile(r'</[a-zA-Z_][a-zA-Z0-9_:\-]*'), tag_format))
        # Tag endings
        self.highlighting_rules.append((re.compile(r'/>'), tag_format))
        self.highlighting_rules.append((re.compile(r'>'), tag_format))
        
        # Attributes
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor(theme['datatype']))
        self.highlighting_rules.append((re.compile(r'\s[a-zA-Z_][a-zA-Z0-9_:\-]*(?=\s*=)'), attr_format))
        
        # Attribute values
        attr_value_format = QTextCharFormat()
        attr_value_format.setForeground(QColor(theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"]*"'), attr_value_format))
        self.highlighting_rules.append((re.compile(r"'[^']*'"), attr_value_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(theme['comment']))
        comment_format.setFontItalic(True)
        # XML comments
        self.highlighting_rules.append((re.compile(r'<!--.*?-->', re.DOTALL), comment_format))
        # HTML doctype
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'<!DOCTYPE[^>]*>', re.IGNORECASE), doctype_format))
        self.highlighting_rules.append((re.compile(r'<!ENTITY[^>]*>', re.IGNORECASE), doctype_format))
        
        # Processing instructions
        pi_format = QTextCharFormat()
        pi_format.setForeground(QColor(theme['section']))
        self.highlighting_rules.append((re.compile(r'<\?.*?\?>'), pi_format))
        
        # CDATA sections
        cdata_format = QTextCharFormat()
        cdata_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'<!\[CDATA\[.*?\]\]>', re.DOTALL), cdata_format))
        
        # Entities
        entity_format = QTextCharFormat()
        entity_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'&[a-zA-Z][a-zA-Z0-9]*;'), entity_format))
        self.highlighting_rules.append((re.compile(r'&#[0-9]+;'), entity_format))
        self.highlighting_rules.append((re.compile(r'&#x[0-9a-fA-F]+;'), entity_format))


# Rejestracja highlightera
register_highlighter(
    'XML',
    XMLSyntaxHighlighter,
    extensions=['xml', 'xaml', 'svg', 'html', 'htm', 'xsd', 'xsl', 'xslt', 'wsdl', 'config']
)
