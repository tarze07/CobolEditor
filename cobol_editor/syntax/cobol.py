"""Highlighter składni COBOL"""

import re
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from .base import SyntaxHighlighterBase, register_highlighter


class CobolSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for COBOL"""
    
    def update_highlighting_rules(self):
        self.highlighting_rules = []
        theme = self.theme
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'ACCEPT', 'ADD', 'ALTER', 'CALL', 'CANCEL', 'CLOSE', 'COMPUTE',
            'CONTINUE', 'DELETE', 'DISPLAY', 'DIVIDE', 'ELSE', 'END-IF',
            'END-PERFORM', 'END-READ', 'EVALUATE', 'EXIT', 'EXIT PROGRAM',
            'GOBACK', 'GO', 'IF', 'INITIALIZE', 'INSPECT', 'INVOKE', 'MERGE',
            'MOVE', 'MULTIPLY', 'OPEN', 'PERFORM', 'READ', 'RELEASE', 'RETURN',
            'REWRITE', 'SEARCH', 'SET', 'SORT', 'START', 'STOP', 'STOP RUN',
            'STRING', 'SUBTRACT', 'UNSTRING', 'WRITE', 'END-WRITE', 'END-CALL',
            'END-COMPUTE', 'END-DELETE', 'END-DIVIDE', 'END-EVALUATE', 'END-MULTIPLY',
            'END-SEARCH', 'END-STRING', 'END-SUBTRACT', 'END-UNSTRING',
            'END-ADD', 'THEN', 'THRU', 'THROUGH', 'VARYING', 'UNTIL', 'TIMES',
            'GIVING', 'REMAINDER', 'ROUNDED', 'ON', 'SIZE', 'ERROR', 'NOT',
            'AT', 'END', 'INVALID', 'KEY', 'FROM', 'INTO', 'BY', 'TO', 'WITH',
            'USING', 'GIVING', 'REPLACING', 'TALLYING', 'FOR', 'IS', 'ARE',
            'ASCENDING', 'DESCENDING', 'SEQUENCE', 'INPUT', 'OUTPUT', 'I-O',
            'EXTEND', 'ALL', 'LEADING', 'TRAILING', 'FIRST', 'DELIMITED',
            'CHARACTERS', 'REFERENCE', 'VALUE', 'RETURNING', 'RAISING',
            'EXCEPTION', 'OVERFLOW', 'EGI', 'EMI', 'ESI', 'ENABLE', 'DISABLE',
            'SEND', 'RECEIVE', 'PASS', 'BEFORE', 'AFTER', 'ADVANCING',
            'PAGE', 'LINES', 'UNIT', 'CD', 'REPORT', 'INITIATE', 'GENERATE',
            'TERMINATE', 'SUPPRESS', 'USE', 'GLOBAL', 'EXTERNAL', 'INTRINSIC'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern, re.IGNORECASE), keyword_format))
        
        # Divisions
        division_format = QTextCharFormat()
        division_format.setForeground(QColor(theme['division']))
        division_format.setFontWeight(QFont.Bold)
        divisions = [
            'IDENTIFICATION', 'ENVIRONMENT', 'DATA', 'PROCEDURE',
            'DIVISION'
        ]
        division_pattern = r'\b(' + '|'.join(divisions) + r')\b'
        self.highlighting_rules.append((re.compile(division_pattern, re.IGNORECASE), division_format))
        
        # Sections
        section_format = QTextCharFormat()
        section_format.setForeground(QColor(theme['section']))
        sections = [
            'WORKING-STORAGE', 'LOCAL-STORAGE', 'LINKAGE', 'FILE', 'REPORT',
            'COMMUNICATION', 'SCREEN', 'CONFIGURATION', 'INPUT-OUTPUT',
            'FILE-CONTROL', 'I-O-CONTROL', 'SPECIAL-NAMES', 'REPOSITORY',
            'SECTION'
        ]
        section_pattern = r'\b(' + '|'.join(sections) + r')\b'
        self.highlighting_rules.append((re.compile(section_pattern, re.IGNORECASE), section_format))
        
        # Data types (PIC clauses)
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(theme['datatype']))
        self.highlighting_rules.append((re.compile(r'\bPIC\s+[A-Z9XSV]+\(?[\d,]+\)?', re.IGNORECASE), datatype_format))
        self.highlighting_rules.append((re.compile(r'\bPIC\s+[A-Z9XSV]+', re.IGNORECASE), datatype_format))
        
        # Comments (lines starting with * in column 7)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'^\s{6}\*.*$'), comment_format))
        self.highlighting_rules.append((re.compile(r'(^|\s)\*\*\*.*$', re.IGNORECASE), comment_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"]*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^']*'"), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b\d+\.\d+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b[+-]?\d+\b'), number_format))
        
        # Paragraph names (labels ending with period at start of area B)
        label_format = QTextCharFormat()
        label_format.setForeground(QColor(theme['division']))
        self.highlighting_rules.append((re.compile(r'^\s{8,11}[A-Z][A-Z0-9-]*\.', re.IGNORECASE), label_format))
        
        # Level numbers
        level_format = QTextCharFormat()
        level_format.setForeground(QColor(theme['number']))
        self.highlighting_rules.append((re.compile(r'^\s+\d{1,2}\s'), level_format))
        
        # COPY statement
        copy_format = QTextCharFormat()
        copy_format.setForeground(QColor(theme['keyword']))
        copy_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'\bCOPY\s+', re.IGNORECASE), copy_format))
        
        # 88 level condition names
        condition_format = QTextCharFormat()
        condition_format.setForeground(QColor(theme['datatype']))
        self.highlighting_rules.append((re.compile(r'\b88\s+'), condition_format))


# Rejestracja highlightera
register_highlighter(
    'COBOL',
    CobolSyntaxHighlighter,
    extensions=['cbl', 'cob', 'cobol', 'cpy']
)
