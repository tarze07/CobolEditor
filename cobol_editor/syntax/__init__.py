"""Moduł podświetlania składni dla COBOL Editor"""

from .base import (
    SyntaxHighlighterBase,
    register_highlighter,
    get_highlighter_for_extension,
    get_highlighter_for_language,
    get_registered_languages,
    get_registered_extensions,
)

# Import wszystkich highlighterów (rejestrują się automatycznie)
from .cobol import CobolSyntaxHighlighter
from .csharp import CSharpSyntaxHighlighter
from .javascript import JavaScriptSyntaxHighlighter
from .python import PythonSyntaxHighlighter
from .xml import XMLSyntaxHighlighter
from .json import JSONSyntaxHighlighter
from .yaml import YAMLSyntaxHighlighter

__all__ = [
    'SyntaxHighlighterBase',
    'register_highlighter',
    'get_highlighter_for_extension',
    'get_highlighter_for_language',
    'get_registered_languages',
    'get_registered_extensions',
    'CobolSyntaxHighlighter',
    'CSharpSyntaxHighlighter',
    'JavaScriptSyntaxHighlighter',
    'PythonSyntaxHighlighter',
    'XMLSyntaxHighlighter',
    'JSONSyntaxHighlighter',
    'YAMLSyntaxHighlighter',
]
