"""Bazowa klasa dla wszystkich highlighterów składni"""

import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class SyntaxHighlighterBase(QSyntaxHighlighter):
    """Base class for all syntax highlighters"""
    
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.highlighting_rules = []
        self.update_highlighting_rules()
    
    def update_theme(self, theme):
        """Update theme and refresh highlighting"""
        self.theme = theme
        self.update_highlighting_rules()
        self.rehighlight()
    
    def update_highlighting_rules(self):
        """Setup highlighting rules - to be overridden by subclasses"""
        pass
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given text block"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


# Rejestr highlighterów
_HIGHLIGHTERS = {}
_EXTENSION_MAP = {}


def register_highlighter(language, highlighter_class, extensions=None):
    """
    Zarejestruj highlighter dla danego języka.
    
    Args:
        language: Nazwa języka (np. 'COBOL', 'Python')
        highlighter_class: Klasa highlightera dziedzicząca po SyntaxHighlighterBase
        extensions: Lista rozszerzeń (bez kropki) lub None
    """
    _HIGHLIGHTERS[language] = highlighter_class
    if extensions:
        for ext in extensions:
            _EXTENSION_MAP[ext.lower()] = language


def get_highlighter_for_extension(ext, theme=None):
    """
    Pobierz klasę highlightera dla danego rozszerzenia.
    
    Args:
        ext: Rozszerzenie pliku (z lub bez kropki)
        theme: Opcjonalnie słownik z kolorami motywu
    
    Returns:
        Klasa highlightera lub None
    """
    ext = ext.lower().lstrip('.')
    language = _EXTENSION_MAP.get(ext)
    if language:
        return _HIGHLIGHTERS.get(language)
    return None


def get_highlighter_for_language(language, theme=None):
    """
    Pobierz klasę highlightera dla danego języka.
    
    Args:
        language: Nazwa języka
        theme: Opcjonalnie słownik z kolorami motywu
    
    Returns:
        Klasa highlightera lub None
    """
    return _HIGHLIGHTERS.get(language)


def get_registered_languages():
    """Pobierz listę zarejestrowanych języków"""
    return list(_HIGHLIGHTERS.keys())


def get_registered_extensions():
    """Pobierz słownik rozszerzeń -> języków"""
    return _EXTENSION_MAP.copy()
