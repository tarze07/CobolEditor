"""Główny widget edytora kodu"""

from PySide6.QtWidgets import QPlainTextEdit, QTextEdit
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import (
    QPainter, QColor, QFont, QTextCursor, 
    QTextFormat, QAction, QPalette
)

from .line_numbers import LineNumberArea


class CodeEditor(QPlainTextEdit):
    """Code editor widget with line numbers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        # Set monospace font
        font = QFont("Consolas", 18)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        
        # Enable tab key
        self.setTabStopDistance(40)
        
        # Track highlighted line from search results
        self.search_highlight_color = QColor("#fff59d")
        self.highlighted_line_number = None
    
    def contextMenuEvent(self, event):
        """Create custom context menu with search in working directory option"""
        menu = self.createStandardContextMenu()
        
        # Get selected text
        cursor = self.textCursor()
        selected_text = cursor.selectedText().strip()
        
        # Add separator and custom search action if text is selected
        if selected_text:
            menu.addSeparator()
            search_action = QAction(f"Search '{selected_text}' in Working Directory", self)
            search_action.triggered.connect(lambda: self.search_in_working_directory(selected_text))
            menu.addAction(search_action)
        
        menu.exec(event.globalPos())
    
    def search_in_working_directory(self, text):
        """Search for selected text in working directory"""
        if self.main_window and hasattr(self.main_window, 'search_in_working_directory_for_text'):
            self.main_window.search_in_working_directory_for_text(text)
    
    def set_search_highlight_color(self, color):
        """Set the background color used when highlighting a search result line."""
        if isinstance(color, QColor):
            self.search_highlight_color = color
        else:
            self.search_highlight_color = QColor(color)
        
        if self.highlighted_line_number is not None:
            # Refresh highlight with new color
            self.highlight_line(self.highlighted_line_number)
    
    def clear_search_highlight(self):
        """Remove any active search line highlight."""
        self.highlighted_line_number = None
        self.setExtraSelections([])
    
    def highlight_line(self, line_number):
        """Highlight a specific 1-based line number in the editor."""
        if line_number is None or line_number <= 0:
            self.clear_search_highlight()
            return
        
        block = self.document().findBlockByLineNumber(line_number - 1)
        if not block.isValid():
            self.clear_search_highlight()
            return
        
        self.highlighted_line_number = line_number
        
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(self.search_highlight_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        
        cursor = QTextCursor(block)
        cursor.clearSelection()
        selection.cursor = cursor
        
        self.setExtraSelections([selection])
    
    def line_number_area_width(self):
        """Calculate the width needed for line numbers"""
        digits = len(str(max(1, self.blockCount())))
        
        # Determine how wide the current line number text can be
        digit_text_width = self.fontMetrics().horizontalAdvance('9' * digits)
        
        # Provide generous padding
        left_padding = 8
        right_padding = 15
        
        return left_padding + digit_text_width + right_padding
    
    def update_line_number_area_width(self, _):
        """Update the width of line number area"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update the line number area when scrolling"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                                  self.line_number_area_width(), cr.height()))
    
    def line_number_area_paint_event(self, event):
        """Paint the line numbers"""
        painter = QPainter(self.line_number_area)
        
        # Get colors from palette
        bg_color = self.palette().color(QPalette.Window)
        fg_color = self.palette().color(QPalette.WindowText)
        
        painter.fillRect(event.rect(), bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        # Add padding to align line numbers properly
        left_padding = 8
        right_padding = 10
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(fg_color)
                painter.drawText(left_padding, top,
                               self.line_number_area.width() - left_padding - right_padding,
                               self.fontMetrics().height(), Qt.AlignRight, number)
            
            block = block.next()
            block_number += 1
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
