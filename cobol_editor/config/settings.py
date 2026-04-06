"""Ustawienia i konfiguracja aplikacji COBOL Editor"""

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor

from .constants import DEFAULT_FONT_SIZE, DEFAULT_FONT_FAMILY


class AppSettings:
    """Wrapper dla QSettings z domyślnymi wartościami"""
    
    def __init__(self):
        self._settings = QSettings('CobolEditor', 'CobolEditor')
    
    def get(self, key, default=None):
        """Pobierz wartość z ustawień"""
        value = self._settings.value(key, default)
        # Konwersja typów
        if isinstance(default, bool) and isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        if isinstance(default, int) and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Zapisz wartość w ustawieniach"""
        self._settings.setValue(key, value)
    
    def get_font_size(self):
        """Pobierz rozmiar czcionki"""
        return self.get('font_size', DEFAULT_FONT_SIZE)
    
    def set_font_size(self, size):
        """Zapisz rozmiar czcionki"""
        self.set('font_size', size)
    
    def get_font_family(self):
        """Pobierz rodzinę czcionek"""
        return self.get('font_family', DEFAULT_FONT_FAMILY)
    
    def set_font_family(self, family):
        """Zapisz rodzinę czcionek"""
        self.set('font_family', family)
    
    def get_theme(self):
        """Pobierz nazwę motywu"""
        return self.get('theme', 'Light')
    
    def set_theme(self, theme):
        """Zapisz nazwę motywu"""
        self.set('theme', theme)
    
    def get_working_directories(self):
        """Pobierz listę katalogów roboczych"""
        dirs = self._settings.value('working_directories', [])
        return dirs if isinstance(dirs, list) else [dirs] if dirs else []
    
    def set_working_directories(self, directories):
        """Zapisz listę katalogów roboczych"""
        self._settings.setValue('working_directories', directories)
    
    def get_syntax_mappings(self):
        """Pobierz mapowania składni"""
        from .constants import default_syntax_mappings
        mappings = self._settings.value('syntax_mappings')
        if mappings:
            return mappings
        return default_syntax_mappings.copy()
    
    def set_syntax_mappings(self, mappings):
        """Zapisz mapowania składni"""
        self._settings.setValue('syntax_mappings', mappings)


# Definicje motywów kolorystycznych
THEMES = {
    'Light': {
        'bg': '#FFFFFF',
        'fg': '#000000',
        'line_numbers_bg': '#E0E0E0',
        'line_numbers_fg': '#555555',
        'keyword': '#0000FF',
        'datatype': '#008080',
        'string': '#A31515',
        'comment': '#008000',
        'number': '#098658',
        'division': '#AF00DB',
        'section': '#AF00DB',
        'search_bg': '#FFFF00',
        'search_fg': '#000000'
    },
    'Dark': {
        'bg': '#1E1E1E',
        'fg': '#D4D4D4',
        'line_numbers_bg': '#252526',
        'line_numbers_fg': '#858585',
        'keyword': '#569CD6',
        'datatype': '#4EC9B0',
        'string': '#CE9178',
        'comment': '#6A9955',
        'number': '#B5CEA8',
        'division': '#C586C0',
        'section': '#C586C0',
        'search_bg': '#515C6A',
        'search_fg': '#FFFFFF'
    },
    'High Contrast': {
        'bg': '#000000',
        'fg': '#FFFFFF',
        'line_numbers_bg': '#1E1E1E',
        'line_numbers_fg': '#FFFFFF',
        'keyword': '#00FFFF',
        'datatype': '#00FF00',
        'string': '#FF00FF',
        'comment': '#7FFF00',
        'number': '#FFFF00',
        'division': '#FF8800',
        'section': '#FF8800',
        'search_bg': '#FFFF00',
        'search_fg': '#000000'
    },
    'Monokai': {
        'bg': '#272822',
        'fg': '#F8F8F2',
        'line_numbers_bg': '#3E3D32',
        'line_numbers_fg': '#90908A',
        'keyword': '#F92672',
        'datatype': '#66D9EF',
        'string': '#E6DB74',
        'comment': '#75715E',
        'number': '#AE81FF',
        'division': '#A6E22E',
        'section': '#A6E22E',
        'search_bg': '#49483E',
        'search_fg': '#FFFFFF'
    }
}


def get_theme_colors(theme_name):
    """Pobierz kolory dla danego motywu"""
    return THEMES.get(theme_name, THEMES['Light'])


def get_available_themes():
    """Pobierz listę dostępnych motywów"""
    return list(THEMES.keys())
