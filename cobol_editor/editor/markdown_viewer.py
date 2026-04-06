"""Widget z podglądem Markdown"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont

from .code_editor import CodeEditor


class MarkdownPreviewWidget(QWidget):
    """Composite widget with a code editor and live Markdown preview."""
    
    def __init__(self, main_window, theme, font, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)
        
        # Create the code editor portion for raw Markdown
        self.editor = CodeEditor(self)
        self.editor.main_window = main_window
        self.splitter.addWidget(self.editor)
        
        # Create the preview pane
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setAcceptRichText(True)
        self.preview.setPlaceholderText("Markdown preview")
        self.splitter.addWidget(self.preview)
        
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        # Apply initial font and theme
        self.apply_font(font)
        self.apply_theme(theme)
        
        # Update preview whenever markdown changes
        self.editor.textChanged.connect(self.update_preview)
    
    def update_preview(self):
        """Render the current Markdown content in the preview pane."""
        markdown_text = self.editor.toPlainText()
        # QTextEdit supports Markdown rendering via setMarkdown
        self.preview.setMarkdown(markdown_text)
    
    def apply_font(self, font):
        """Apply font settings to both editor and preview."""
        self.editor.setFont(font)
        self.editor.update_line_number_area_width(0)
        self.preview.document().setDefaultFont(font)
    
    def apply_theme(self, theme):
        """Apply color theme to editor and preview."""
        palette = self.editor.palette()
        palette.setColor(QPalette.Base, QColor(theme['bg']))
        palette.setColor(QPalette.Text, QColor(theme['fg']))
        self.editor.setPalette(palette)
        
        line_palette = self.editor.line_number_area.palette()
        line_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
        line_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
        self.editor.line_number_area.setPalette(line_palette)
        self.editor.line_number_area.update()
        
        self.editor.set_search_highlight_color(QColor(theme['search_bg']))
        
        preview_palette = self.preview.palette()
        preview_palette.setColor(QPalette.Base, QColor(theme['bg']))
        preview_palette.setColor(QPalette.Text, QColor(theme['fg']))
        self.preview.setPalette(preview_palette)
    
    def setPlainText(self, text):
        """Proxy to set the Markdown text in the editor."""
        self.editor.setPlainText(text)
    
    def toPlainText(self):
        """Proxy to access the raw Markdown text."""
        return self.editor.toPlainText()
