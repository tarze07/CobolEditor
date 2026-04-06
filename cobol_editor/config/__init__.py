"""Konfiguracja aplikacji COBOL Editor"""

from .constants import (
    DEFAULT_ENCODINGS,
    SKIP_DIRS,
    SEARCHABLE_EXTENSIONS,
    MARKDOWN_EXTENSIONS,
    FILE_ICONS,
    MAX_SEARCH_RESULTS,
    MAX_FILE_SIZE_MB,
    BATCH_SIZE,
    DEFAULT_FONT_SIZE,
    DEFAULT_FONT_FAMILY,
    MIN_FONT_SIZE,
    MAX_FONT_SIZE,
)
from .settings import AppSettings, THEMES, get_theme_colors, get_available_themes

__all__ = [
    'DEFAULT_ENCODINGS',
    'SKIP_DIRS',
    'SEARCHABLE_EXTENSIONS',
    'MARKDOWN_EXTENSIONS',
    'FILE_ICONS',
    'MAX_SEARCH_RESULTS',
    'MAX_FILE_SIZE_MB',
    'BATCH_SIZE',
    'DEFAULT_FONT_SIZE',
    'DEFAULT_FONT_FAMILY',
    'MIN_FONT_SIZE',
    'MAX_FONT_SIZE',
    'AppSettings',
    'THEMES',
    'get_theme_colors',
    'get_available_themes',
]
