"""Core module - główna logika aplikacji"""

from .file_manager import FileManager
from .workspace import Workspace
from .app import CobolEditor

__all__ = [
    'FileManager',
    'Workspace',
    'CobolEditor',
]
