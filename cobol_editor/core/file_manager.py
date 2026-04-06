"""Manager plików - operacje odczytu/zapisu z obsługą kodowań"""

import os
from ..config.constants import DEFAULT_ENCODINGS, MARKDOWN_EXTENSIONS


class FileManager:
    """Odpowiedzialny za odczyt/zapis plików z obsługą kodowań"""
    
    def __init__(self, encodings=None):
        self.encodings = encodings or DEFAULT_ENCODINGS.copy()
    
    def read_file(self, file_path):
        """
        Przeczytaj plik próbując różnych kodowań.
        
        Returns:
            tuple: (content, encoding_used)
        
        Raises:
            Exception: Jeśli nie uda się odczytać pliku
        """
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    return content, encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        # If all encodings fail, try with error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                return content, 'utf-8 (with replacements)'
        except Exception as e:
            raise Exception(f"Could not read file with any encoding: {str(e)}")
    
    def save_file(self, file_path, content, encoding='utf-8'):
        """
        Zapisz plik z podanym kodowaniem.
        
        Args:
            file_path: Ścieżka do pliku
            content: Zawartość do zapisania
            encoding: Kodowanie (domyślnie utf-8)
        
        Raises:
            Exception: Jeśli nie uda się zapisać pliku
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")
    
    def is_markdown(self, file_path):
        """Sprawdź czy plik jest Markdown"""
        if not file_path:
            return False
        ext = os.path.splitext(file_path)[1].lower()
        return ext in MARKDOWN_EXTENSIONS
    
    def get_file_icon(self, file_name):
        """Pobierz ikonę dla pliku na podstawie rozszerzenia"""
        from ..config.constants import FILE_ICONS
        _, extension = os.path.splitext(file_name.lower())
        return FILE_ICONS.get(extension, "📄")
    
    def get_extension(self, file_path):
        """Pobierz rozszerzenie pliku (bez kropki, lowercase)"""
        if not file_path:
            return ''
        return os.path.splitext(file_path)[1].lstrip('.').lower()
