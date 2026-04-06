"""Stałe używane w aplikacji COBOL Editor"""

# Domyślne kodowania do próbowania przy odczycie pliku
DEFAULT_ENCODINGS = [
    'utf-8',
    'utf-8-sig',  # UTF-8 with BOM
    'latin-1',    # ISO-8859-1
    'cp1252',     # Windows-1252
    'cp1250',     # Polish/Central European
    'iso-8859-2', # Latin-2 (Central European)
]

# Katalogi do pominięcia podczas wyszukiwania
SKIP_DIRS = {
    '.git', '.svn', '.hg', '.bzr',  # Version control
    'node_modules', 'bower_components',  # JavaScript
    '__pycache__', '.pytest_cache', '.tox', 'venv', 'env', '.env',  # Python
    'bin', 'obj', '.vs', '.vscode',  # Build outputs and IDE
    'target', 'build', 'dist', '.gradle',  # Build systems
    '.idea', '.settings', '.eclipse',  # IDEs
    'vendor', 'packages'  # Dependencies
}

# Rozszerzenia plików przeszukiwanych podczas wyszukiwania
SEARCHABLE_EXTENSIONS = {
    '.cob', '.cbl', '.cobol', '.cpy',  # COBOL
    '.cs', '.csharp',  # C#
    '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
    '.py', '.pyw',  # Python
    '.xml', '.xaml', '.html', '.htm',  # Markup
    '.json', '.yaml', '.yml', '.toml',  # Config
    '.txt', '.md', '.rst',  # Documentation
    '.c', '.cpp', '.h', '.hpp',  # C/C++
    '.java', '.kt',  # JVM languages
    '.go', '.rs', '.rb', '.php',  # Other languages
    '.sql', '.sh', '.bat', '.ps1',  # Scripts
    '.css', '.scss', '.sass', '.less',  # Styles
    '.log', '.ini', '.cfg', '.conf'  # Config/logs
}

# Rozszerzenia plików Markdown
MARKDOWN_EXTENSIONS = {'.md', '.markdown', '.mdown', '.mkd'}

# Ikony dla rozszerzeń plików
FILE_ICONS = {
    '.cbl': "🧾",
    '.cob': "🧾",
    '.cobol': "🧾",
    '.py': "🐍",
    '.js': "🟨",
    '.ts': "🟦",
    '.json': "🧩",
    '.xml': "🧷",
    '.yml': "🗂️",
    '.yaml': "🗂️",
    '.cs': "♯",
    '.java': "☕",
    '.txt': "📄",
    '.md': "📝",
    '.html': "🌐",
    '.css': "🎨",
    '.sql': "🗃️",
    '.sh': "💻",
    '.bat': "💾",
    '.rb': "💎",
    '.go': "🐹",
}

# Domyślne mapowania składni (rozszerzenie -> język)
default_syntax_mappings = {
    'COBOL': ['cbl', 'cob', 'cobol'],
    'C#': ['cs', 'csharp'],
    'JavaScript': ['js', 'jsx', 'mjs'],
    'Python': ['py', 'pyw'],
    'XML': ['xml', 'xaml', 'svg'],
    'JSON': ['json'],
    'YAML': ['yaml', 'yml']
}

# Limity wyszukiwania
MAX_SEARCH_RESULTS = 1000
MAX_FILE_SIZE_MB = 10
BATCH_SIZE = 50

# Domyślne ustawienia aplikacji
DEFAULT_FONT_SIZE = 18
DEFAULT_FONT_FAMILY = 'Consolas'
MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 72
