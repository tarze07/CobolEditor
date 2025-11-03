#!/usr/bin/env python3
"""
COBOL Editor with Syntax Highlighting and Search
Migrated to PySide6
"""

import sys
import os
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QLabel, QFrame,
    QFileDialog, QMessageBox, QInputDialog, QDialog, QListWidget,
    QScrollBar, QSplitter, QStatusBar, QMenuBar, QMenu, QTabWidget
)
from PySide6.QtCore import Qt, QRect, QSize, Signal, Slot, QSettings
from PySide6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QTextCharFormat,
    QSyntaxHighlighter, QTextCursor, QTextDocument, QKeySequence,
    QAction, QPalette
)


class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CobolSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for COBOL"""
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
        """Setup highlighting rules based on current theme"""
        self.highlighting_rules = []

        # Division headers
        division_format = QTextCharFormat()
        division_format.setForeground(QColor(self.theme['division']))
        division_format.setFontWeight(QFont.Bold)
        division_pattern = r'\b(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION\b'
        self.highlighting_rules.append((re.compile(division_pattern, re.IGNORECASE), division_format))

        # Section headers
        section_format = QTextCharFormat()
        section_format.setForeground(QColor(self.theme['section']))
        section_pattern = r'\b(CONFIGURATION|INPUT-OUTPUT|FILE|WORKING-STORAGE|LINKAGE|LOCAL-STORAGE)\s+SECTION\b'
        self.highlighting_rules.append((re.compile(section_pattern, re.IGNORECASE), section_format))

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'ACCEPT', 'ACCESS', 'ADD', 'ADDRESS', 'ADVANCING', 'AFTER', 'ALL', 'ALPHABET', 'ALPHABETIC',
            'ALPHABETIC-LOWER', 'ALPHABETIC-UPPER', 'ALPHANUMERIC', 'ALPHANUMERIC-EDITED',
            'ALSO', 'ALTER', 'ALTERNATE', 'AND', 'ANY', 'ARE', 'AREA', 'AREAS', 'ASCENDING', 'ASSIGN', 'AT',
            'AUTHOR', 'BEFORE', 'BINARY', 'BLANK', 'BLOCK', 'BOTTOM', 'BY', 'CALL', 'CANCEL', 'CD', 'CF', 'CH',
            'CHARACTER', 'CHARACTERS', 'CLASS', 'CLOCK-UNITS', 'CLOSE', 'COBOL', 'CODE', 'CODE-SET',
            'COLLATING', 'COLUMN', 'COMMA', 'COMMON', 'COMMUNICATION', 'COMP', 'COMPUTE',
            'COMPUTATIONAL', 'CONFIGURATION', 'CONTAINS', 'CONTENT', 'CONTINUE', 'CONTROL',
            'CONTROLS', 'CONVERTING', 'COPY', 'CORR', 'CORRESPONDING', 'COUNT', 'CURRENCY', 'DATE',
            'DATE-COMPILED', 'DATE-WRITTEN', 'DAY', 'DAY-OF-WEEK', 'DE', 'DEBUG-CONTENTS',
            'DEBUG-ITEM', 'DEBUG-LINE', 'DEBUG-NAME', 'DEBUG-SUB-1', 'DEBUG-SUB-2',
            'DEBUG-SUB-3', 'DEBUGGING', 'DECIMAL-POINT', 'DECLARATIVES', 'DELETE', 'DELIMITED',
            'DELIMITER', 'DEPENDING', 'DESCENDING', 'DESTINATION', 'DETAIL', 'DISABLE', 'DISPLAY',
            'DIVIDE', 'DOWN', 'DUPLICATES', 'DYNAMIC', 'EGI', 'ELSE', 'EMI', 'ENABLE', 'END', 'END-ADD',
            'END-CALL', 'END-COMPUTE', 'END-DELETE', 'END-DIVIDE', 'END-EVALUATE', 'END-IF',
            'END-MULTIPLY', 'END-OF-PAGE', 'END-PERFORM', 'END-READ', 'END-RECEIVE',
            'END-RETURN', 'END-REWRITE', 'END-SEARCH', 'END-START', 'END-STRING', 'END-SUBTRACT',
            'END-UNSTRING', 'END-WRITE', 'ENTER', 'ENTRY', 'ENVIRONMENT', 'EOP', 'EQUAL', 'ERROR', 'ESI',
            'EVALUATE', 'EVERY', 'EXCEPTION', 'EXIT', 'EXTEND', 'EXTERNAL', 'FALSE', 'FD', 'FILE',
            'FILE-CONTROL', 'FILLER', 'FINAL', 'FIRST', 'FOOTING', 'FOR', 'FROM', 'FUNCTION', 'GENERATE',
            'GIVING', 'GLOBAL', 'GO', 'GOBACK', 'GREATER', 'GROUP', 'HEADING', 'HIGH-VALUE', 'HIGH-VALUES',
            'I-O', 'I-O-CONTROL', 'IF', 'IN', 'INDEX', 'INDEXED', 'INDICATE', 'INITIAL', 'INITIALIZE',
            'INITIATE', 'INPUT', 'INPUT-OUTPUT', 'INSPECT', 'INSTALLATION', 'INTO', 'INVALID', 'IS',
            'JUST', 'JUSTIFIED', 'KEY', 'LABEL', 'LAST', 'LEADING', 'LEFT', 'LENGTH', 'LESS', 'LIMIT', 'LIMITS',
            'LINAGE', 'LINAGE-COUNTER', 'LINE', 'LINE-COUNTER', 'LINES', 'LINKAGE', 'LOCK',
            'LOW-VALUE', 'LOW-VALUES', 'MEMORY', 'MERGE', 'MESSAGE', 'MODE', 'MODULES', 'MOVE', 'MULTIPLE',
            'MULTIPLY', 'NATIVE', 'NEGATIVE', 'NEXT', 'NO', 'NOT', 'NUMBER', 'NUMERIC', 'NUMERIC-EDITED',
            'OBJECT-COMPUTER', 'OCCURS', 'OF', 'OFF', 'OMITTED', 'ON', 'OPEN', 'OPTIONAL', 'OR', 'ORDER',
            'ORGANIZATION', 'OTHER', 'OUTPUT', 'OVERFLOW', 'PACKED-DECIMAL', 'PADDING', 'PAGE',
            'PAGE-COUNTER', 'PERFORM', 'PF', 'PH', 'PICTURE', 'PIC', 'PLUS', 'POINTER', 'POSITION', 'POSITIVE',
            'PRINTING', 'PROCEDURE', 'PROCEDURES', 'PROCEED', 'PROGRAM', 'PROGRAM-ID', 'PURGE', 'QUEUE',
            'QUOTE', 'QUOTES', 'RANDOM', 'RD', 'READ', 'RECEIVE', 'RECORD', 'RECORDS', 'REDEFINES', 'REEL',
            'REFERENCE', 'REFERENCES', 'RELATIVE', 'RELEASE', 'REMAINDER', 'REMOVAL', 'RENAMES',
            'REPLACE', 'REPLACING', 'REPORT', 'REPORTING', 'REPORTS', 'RERUN', 'RESERVE', 'RESET',
            'RETURN', 'REVERSED', 'REWIND', 'REWRITE', 'RF', 'RH', 'RIGHT', 'ROUNDED', 'RUN', 'SAME', 'SD',
            'SEARCH', 'SECTION', 'SECURITY', 'SEGMENT', 'SEGMENT-LIMIT', 'SELECT', 'SEND', 'SENTENCE',
            'SEPARATE', 'SEQUENCE', 'SEQUENTIAL', 'SET', 'SIGN', 'SIZE', 'SORT', 'SORT-MERGE', 'SOURCE',
            'SOURCE-COMPUTER', 'SPACE', 'SPACES', 'SPECIAL-NAMES', 'STANDARD', 'STANDARD-1',
            'STANDARD-2', 'START', 'STATUS', 'STOP', 'STRING', 'SUB-QUEUE-1', 'SUB-QUEUE-2',
            'SUB-QUEUE-3', 'SUBTRACT', 'SUM', 'SUPPRESS', 'SYMBOLIC', 'SYNC', 'SYNCHRONIZED', 'TABLE',
            'TALLYING', 'TAPE', 'TERMINAL', 'TERMINATE', 'TEST', 'TEXT', 'THAN', 'THEN', 'THROUGH', 'THRU',
            'TIME', 'TIMES', 'TO', 'TOP', 'TRAILING', 'TRUE', 'TYPE', 'UNIT', 'UNSTRING', 'UNTIL', 'UP', 'UPON',
            'USAGE', 'USE', 'USING', 'VALUE', 'VALUES', 'VARYING', 'WHEN', 'WITH', 'WORDS',
            'WORKING-STORAGE', 'WRITE', 'ZERO', 'ZEROES', 'ZEROS'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern, re.IGNORECASE), keyword_format))

        # Data types (PIC clause)
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(self.theme['datatype']))
        datatype_format.setFontWeight(QFont.Bold)
        datatype_pattern = r'\bPIC\s+[X9A\(\)V\-\+\*\$\,\.ZS]+'
        self.highlighting_rules.append((re.compile(datatype_pattern, re.IGNORECASE), datatype_format))

        # Comments (lines starting with *)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        comment_pattern = r'^\s*\*.*$'
        self.highlighting_rules.append((re.compile(comment_pattern, re.MULTILINE), comment_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        string_pattern = r'["\']([^"\']*)["\']'
        self.highlighting_rules.append((re.compile(string_pattern), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        number_pattern = r'\b\d+(\.\d+)?\b'
        self.highlighting_rules.append((re.compile(number_pattern), number_format))

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given text block"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


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

    def line_number_area_width(self):
        """Calculate the width needed for line numbers"""
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

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

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(fg_color)
                painter.drawText(0, top, self.line_number_area.width() - 5,
                               self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class CobolEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.working_directory = None
        self.search_text = ""
        self.last_search_position = 0

        # Track open files: {tab_index: {'path': file_path, 'modified': bool}}
        self.open_files = {}

        # Initialize settings
        self.settings = QSettings('CobolEditor', 'CobolEditor')

        # Default values
        self.font_size = 18
        self.font_family = 'Consolas'
        self.current_theme = 'Light'

        # Define color themes
        self.themes = {
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

        self.init_ui()
        self.load_settings()
        self.apply_theme(self.current_theme)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("COBOL Editor")
        self.setGeometry(100, 100, 900, 700)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Create file tree panel
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)

        self.tree_label = QLabel("Workspace")
        self.tree_label.setAlignment(Qt.AlignCenter)
        self.tree_label.setMaximumHeight(25)
        tree_layout.addWidget(self.tree_label)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setMaximumWidth(300)
        self.file_tree.setMinimumWidth(150)
        self.file_tree.itemDoubleClicked.connect(self.on_tree_double_click)
        tree_layout.addWidget(self.file_tree)

        splitter.addWidget(tree_container)

        # Create vertical splitter for editor and search panel
        vertical_splitter = QSplitter(Qt.Vertical)

        # Create tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        vertical_splitter.addWidget(self.tab_widget)

        # Create search results panel
        self.search_panel = QWidget()
        search_panel_layout = QVBoxLayout(self.search_panel)
        search_panel_layout.setContentsMargins(0, 0, 0, 0)
        search_panel_layout.setSpacing(0)

        # Search panel header
        self.search_panel_label = QLabel("Search Results")
        self.search_panel_label.setAlignment(Qt.AlignCenter)
        self.search_panel_label.setMaximumHeight(25)
        search_panel_layout.addWidget(self.search_panel_label)

        # Search results list
        self.search_results_list = QListWidget()
        search_panel_layout.addWidget(self.search_results_list)

        # Search status label
        self.search_status_label = QLabel("")
        self.search_status_label.setMaximumHeight(20)
        search_panel_layout.addWidget(self.search_status_label)

        # Initially hide search panel
        self.search_panel.hide()

        vertical_splitter.addWidget(self.search_panel)

        # Set initial sizes (give more space to editor)
        vertical_splitter.setSizes([500, 200])

        splitter.addWidget(vertical_splitter)

        # Create initial empty tab
        self.create_new_tab()

        # Set splitter sizes (200px for tree, rest for editor)
        splitter.setSizes([200, 700])

        # Create menu bar
        self.create_menu()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        select_dir_action = QAction("Select Working Directory...", self)
        select_dir_action.triggered.connect(self.select_working_directory)
        file_menu.addAction(select_dir_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)

        find_next_action = QAction("Find Next", self)
        find_next_action.setShortcut(QKeySequence.FindNext)
        find_next_action.triggered.connect(self.find_next)
        edit_menu.addAction(find_next_action)

        find_in_files_action = QAction("Find in Files...", self)
        find_in_files_action.setShortcut("Ctrl+Shift+F")
        find_in_files_action.triggered.connect(self.find_in_files)
        edit_menu.addAction(find_in_files_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.select_all_text)
        edit_menu.addAction(select_all_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Theme submenu
        theme_menu = view_menu.addMenu("Color Theme")

        for theme_name in self.themes.keys():
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, t=theme_name: self.apply_theme(t))
            theme_menu.addAction(theme_action)

        view_menu.addSeparator()

        increase_font_action = QAction("Increase Font Size", self)
        increase_font_action.setShortcut(QKeySequence.ZoomIn)
        increase_font_action.triggered.connect(self.increase_font_size)
        view_menu.addAction(increase_font_action)

        decrease_font_action = QAction("Decrease Font Size", self)
        decrease_font_action.setShortcut(QKeySequence.ZoomOut)
        decrease_font_action.triggered.connect(self.decrease_font_size)
        view_menu.addAction(decrease_font_action)

        reset_font_action = QAction("Reset Font Size", self)
        reset_font_action.triggered.connect(self.reset_font_size)
        view_menu.addAction(reset_font_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_new_tab(self, file_path=None, content=""):
        """Create a new tab with a code editor"""
        editor = CodeEditor(self)
        highlighter = CobolSyntaxHighlighter(editor.document(), self.themes[self.current_theme])
        editor.textChanged.connect(lambda: self.on_text_changed(editor))

        # Apply current font settings
        font = QFont(self.font_family, self.font_size)
        font.setStyleHint(QFont.Monospace)
        editor.setFont(font)

        # Apply current theme
        theme = self.themes[self.current_theme]
        palette = editor.palette()
        palette.setColor(QPalette.Base, QColor(theme['bg']))
        palette.setColor(QPalette.Text, QColor(theme['fg']))
        editor.setPalette(palette)

        # Update line number area colors
        line_palette = editor.line_number_area.palette()
        line_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
        line_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
        editor.line_number_area.setPalette(line_palette)

        # Set content
        if content:
            editor.setPlainText(content)

        # Determine tab title
        if file_path:
            tab_title = os.path.basename(file_path)
        else:
            tab_title = "Untitled"

        # Add tab
        tab_index = self.tab_widget.addTab(editor, tab_title)

        # Track the file
        self.open_files[tab_index] = {
            'path': file_path,
            'modified': False,
            'highlighter': highlighter
        }

        # Switch to new tab
        self.tab_widget.setCurrentIndex(tab_index)

        return tab_index

    def close_tab(self, index):
        """Close a tab with save confirmation if modified"""
        if index < 0 or index >= self.tab_widget.count():
            return

        editor = self.tab_widget.widget(index)
        file_info = self.open_files.get(index, {})

        # Check if modified
        if file_info.get('modified', False) or (not file_info.get('path') and editor.toPlainText()):
            file_name = file_info.get('path', 'Untitled')
            if file_info.get('path'):
                file_name = os.path.basename(file_name)

            reply = QMessageBox.question(
                self, "Close Tab",
                f"Save changes to '{file_name}' before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                # Save before closing
                current_index = self.tab_widget.currentIndex()
                self.tab_widget.setCurrentIndex(index)
                self.save_file()
                self.tab_widget.setCurrentIndex(current_index)
            elif reply == QMessageBox.Cancel:
                return

        # Remove tab and cleanup
        self.tab_widget.removeTab(index)
        if index in self.open_files:
            del self.open_files[index]

        # Reindex open_files dictionary
        new_open_files = {}
        for i in range(self.tab_widget.count()):
            old_index = list(self.open_files.keys())[i] if i < len(self.open_files) else i
            if old_index in self.open_files:
                new_open_files[i] = self.open_files[old_index]
        self.open_files = new_open_files

        # Create new tab if all tabs are closed
        if self.tab_widget.count() == 0:
            self.create_new_tab()

    def get_current_editor(self):
        """Get the current active editor widget"""
        return self.tab_widget.currentWidget()

    def on_tab_changed(self, index):
        """Handle tab change event"""
        if index >= 0:
            file_info = self.open_files.get(index, {})
            file_path = file_info.get('path')

            if file_path:
                self.setWindowTitle(f"COBOL Editor - {os.path.basename(file_path)}")
            else:
                self.setWindowTitle("COBOL Editor - Untitled")

    def load_settings(self):
        """Load user settings from QSettings"""
        # Load font settings
        self.font_size = self.settings.value('font_size', 18, type=int)
        self.font_family = self.settings.value('font_family', 'Consolas', type=str)

        # Load theme
        self.current_theme = self.settings.value('theme', 'Light', type=str)

        # Load working directory
        working_dir = self.settings.value('working_directory', '', type=str)
        if working_dir and os.path.exists(working_dir):
            self.working_directory = working_dir
            # Only populate tree if file_tree widget exists
            if hasattr(self, 'file_tree'):
                self.populate_tree()

        # Load window geometry
        geometry = self.settings.value('window_geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.setGeometry(100, 100, 900, 700)

        # Load splitter state
        splitter_state = self.settings.value('splitter_state')
        if splitter_state:
            # Find the splitter widget
            splitter = self.centralWidget().findChild(QSplitter)
            if splitter:
                splitter.restoreState(splitter_state)

        # Apply font settings if tab_widget exists
        if hasattr(self, 'tab_widget'):
            self.update_font()

    def save_settings(self):
        """Save user settings to QSettings"""
        # Save font settings
        self.settings.setValue('font_size', self.font_size)
        self.settings.setValue('font_family', self.font_family)

        # Save theme
        self.settings.setValue('theme', self.current_theme)

        # Save working directory
        if self.working_directory:
            self.settings.setValue('working_directory', self.working_directory)

        # Save window geometry
        self.settings.setValue('window_geometry', self.saveGeometry())

        # Save splitter state
        splitter = self.centralWidget().findChild(QSplitter)
        if splitter:
            self.settings.setValue('splitter_state', splitter.saveState())

        # Ensure settings are written to disk
        self.settings.sync()

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()

    def on_text_changed(self, editor):
        """Handle text changes - triggers syntax highlighting automatically"""
        # Mark current tab as modified
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0 and current_index in self.open_files:
            if not self.open_files[current_index]['modified']:
                self.open_files[current_index]['modified'] = True
                # Add asterisk to tab title
                current_title = self.tab_widget.tabText(current_index)
                if not current_title.endswith('*'):
                    self.tab_widget.setTabText(current_index, current_title + '*')

    def new_file(self):
        """Create a new file in a new tab"""
        self.create_new_tab()

    def open_file(self):
        """Open a file in a new tab or switch to existing tab"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "COBOL Files (*.cbl *.cob *.cobol);;All Files (*.*)"
        )

        if file_path:
            # Check if file is already open
            for tab_index, file_info in self.open_files.items():
                if file_info.get('path') == file_path:
                    # File already open, switch to that tab
                    self.tab_widget.setCurrentIndex(tab_index)
                    self.status_bar.showMessage(f"Switched to: {file_path}")
                    return

            # Open file in new tab
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.create_new_tab(file_path, content)
                    self.status_bar.showMessage(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save the current file in current tab"""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return

        editor = self.get_current_editor()
        if not editor:
            return

        file_info = self.open_files.get(current_index, {})
        file_path = file_info.get('path')

        if file_path:
            try:
                content = editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

                # Mark as not modified
                self.open_files[current_index]['modified'] = False

                # Remove asterisk from tab title
                tab_title = os.path.basename(file_path)
                self.tab_widget.setTabText(current_index, tab_title)

                self.status_bar.showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save the file with a new name in current tab"""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return

        editor = self.get_current_editor()
        if not editor:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "COBOL Files (*.cbl);;All Files (*.*)"
        )

        if file_path:
            try:
                content = editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

                # Update file info
                self.open_files[current_index]['path'] = file_path
                self.open_files[current_index]['modified'] = False

                # Update tab title
                tab_title = os.path.basename(file_path)
                self.tab_widget.setTabText(current_index, tab_title)

                # Update window title
                self.setWindowTitle(f"COBOL Editor - {os.path.basename(file_path)}")
                self.status_bar.showMessage(f"Saved as: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def select_all_text(self):
        """Select all text in current tab"""
        editor = self.get_current_editor()
        if editor:
            editor.selectAll()

    def find_text(self):
        """Open find dialog"""
        text, ok = QInputDialog.getText(self, "Find", "Enter text to find:")
        if ok and text:
            self.search_text = text
            self.last_search_position = 0
            self.find_next()

    def find_next(self):
        """Find next occurrence of search text in current tab"""
        if not self.search_text:
            self.find_text()
            return

        editor = self.get_current_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        document = editor.document()

        # Search from current position
        found_cursor = document.find(self.search_text, cursor,
                                     QTextDocument.FindCaseSensitively)

        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
            self.status_bar.showMessage(f"Found: {self.search_text}")
        else:
            # Wrap around to beginning
            found_cursor = document.find(self.search_text, 0)
            if not found_cursor.isNull():
                editor.setTextCursor(found_cursor)
                self.status_bar.showMessage(f"Found: {self.search_text} (wrapped)")
            else:
                QMessageBox.information(self, "Find",
                                       f"Text '{self.search_text}' not found")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(self, "About",
            "COBOL Editor\n\n"
            "A COBOL editor with syntax highlighting, search,\n"
            "multi-file search, and adjustable font size.\n\n"
            "Shortcuts:\n"
            "Ctrl+N - New File\n"
            "Ctrl+O - Open File\n"
            "Ctrl+S - Save File\n"
            "Ctrl+F - Find\n"
            "F3 - Find Next\n"
            "Ctrl+Shift+F - Find in Files\n"
            "Ctrl++ - Increase Font Size\n"
            "Ctrl+- - Decrease Font Size"
        )

    def increase_font_size(self):
        """Increase font size"""
        if self.font_size < 72:
            self.font_size += 2
            self.update_font()
            self.save_settings()
            self.status_bar.showMessage(f"Font size: {self.font_size}")

    def decrease_font_size(self):
        """Decrease font size"""
        if self.font_size > 6:
            self.font_size -= 2
            self.update_font()
            self.save_settings()
            self.status_bar.showMessage(f"Font size: {self.font_size}")

    def reset_font_size(self):
        """Reset font size to default"""
        self.font_size = 18
        self.update_font()
        self.save_settings()
        self.status_bar.showMessage(f"Font size reset to: {self.font_size}")

    def update_font(self):
        """Update font for all tabs"""
        font = QFont(self.font_family, self.font_size)
        font.setStyleHint(QFont.Monospace)

        # Update all open tabs
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if editor:
                editor.setFont(font)
                editor.update_line_number_area_width(0)

    def apply_theme(self, theme_name):
        """Apply a color theme to all editors"""
        if theme_name not in self.themes:
            QMessageBox.critical(self, "Error", f"Theme '{theme_name}' not found")
            return

        self.current_theme = theme_name
        theme = self.themes[theme_name]

        # Update all tabs
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if editor:
                # Update text area colors
                palette = editor.palette()
                palette.setColor(QPalette.Base, QColor(theme['bg']))
                palette.setColor(QPalette.Text, QColor(theme['fg']))
                editor.setPalette(palette)

                # Update line number area colors
                line_palette = editor.line_number_area.palette()
                line_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
                line_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
                editor.line_number_area.setPalette(line_palette)

                # Update syntax highlighter for this tab
                if i in self.open_files and 'highlighter' in self.open_files[i]:
                    self.open_files[i]['highlighter'].update_theme(theme)

                # Force redraw
                editor.line_number_area.update()

        # Update tree colors
        tree_palette = self.file_tree.palette()
        tree_palette.setColor(QPalette.Base, QColor(theme['bg']))
        tree_palette.setColor(QPalette.Text, QColor(theme['fg']))
        self.file_tree.setPalette(tree_palette)

        # Update tree label colors
        label_palette = self.tree_label.palette()
        label_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
        label_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
        self.tree_label.setPalette(label_palette)
        self.tree_label.setAutoFillBackground(True)

        # Update search panel colors
        search_results_palette = self.search_results_list.palette()
        search_results_palette.setColor(QPalette.Base, QColor(theme['bg']))
        search_results_palette.setColor(QPalette.Text, QColor(theme['fg']))
        self.search_results_list.setPalette(search_results_palette)

        search_label_palette = self.search_panel_label.palette()
        search_label_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
        search_label_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
        self.search_panel_label.setPalette(search_label_palette)
        self.search_panel_label.setAutoFillBackground(True)

        self.save_settings()
        self.status_bar.showMessage(f"Theme changed to: {theme_name}")

    def find_in_files(self):
        """Open multi-file search dialog"""
        directory = QFileDialog.getExistingDirectory(self, "Select directory to search in")
        if not directory:
            return

        text, ok = QInputDialog.getText(self, "Find in Files", "Enter text to find:")
        if not ok or not text:
            return

        # Search in files
        results = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if text.lower() in line.lower():
                                results.append((file_path, line_num, line.strip()))
                except Exception:
                    continue

        # Display results
        if results:
            self.show_search_results(text, results)
        else:
            QMessageBox.information(self, "Find in Files",
                                   f"No matches found for '{text}'")

    def search_in_working_directory_for_text(self, text):
        """Search for given text in working directory"""
        if not self.working_directory:
            QMessageBox.warning(self, "No Working Directory",
                              "Please select a working directory first using File > Select Working Directory")
            return

        if not text:
            return

        # Search in files within working directory
        results = []
        for root, dirs, files in os.walk(self.working_directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if text.lower() in line.lower():
                                results.append((file_path, line_num, line.strip()))
                except Exception:
                    continue

        # Display results
        if results:
            self.show_search_results(text, results)
        else:
            QMessageBox.information(self, "Search in Working Directory",
                                   f"No matches found for '{text}' in working directory")

    def show_search_results(self, search_text, results):
        """Show search results in embedded panel"""
        # Store results for double-click handler
        self.current_search_results = results

        # Update panel label
        self.search_panel_label.setText(f"Search Results: '{search_text}' ({len(results)} matches)")

        # Clear and populate results list
        self.search_results_list.clear()
        for file_path, line_num, line_text in results:
            display_text = f"{file_path}:{line_num}: {line_text}"
            self.search_results_list.addItem(display_text)

        # Update status label
        self.search_status_label.setText(f"Found {len(results)} matches. Double-click to open file.")

        # Show the search panel
        self.search_panel.show()

        # Connect double-click handler (disconnect first to avoid multiple connections)
        try:
            self.search_results_list.itemDoubleClicked.disconnect()
        except:
            pass
        self.search_results_list.itemDoubleClicked.connect(self.on_search_result_double_clicked)

    def on_search_result_double_clicked(self, item):
        """Handle double-click on search result"""
        index = self.search_results_list.row(item)
        if hasattr(self, 'current_search_results') and index < len(self.current_search_results):
            file_path, line_num, _ = self.current_search_results[index]
            self.open_file_at_line(file_path, line_num)

    def open_file_at_line(self, file_path, line_num):
        """Open a file in a tab and jump to specific line"""
        # Check if file is already open
        for tab_index, file_info in self.open_files.items():
            if file_info.get('path') == file_path:
                # File already open, switch to that tab
                self.tab_widget.setCurrentIndex(tab_index)
                editor = self.get_current_editor()
                if editor:
                    # Jump to line
                    cursor = editor.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num - 1)
                    editor.setTextCursor(cursor)
                    editor.centerCursor()
                    self.status_bar.showMessage(f"Jumped to line {line_num} in {file_path}")
                return

        # Open file in new tab
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                tab_index = self.create_new_tab(file_path, content)

                # Jump to line
                editor = self.get_current_editor()
                if editor:
                    cursor = editor.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num - 1)
                    editor.setTextCursor(cursor)
                    editor.centerCursor()

                self.status_bar.showMessage(f"Opened: {file_path} at line {line_num}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def select_working_directory(self):
        """Select a working directory to browse"""
        directory = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if directory:
            self.working_directory = directory
            self.populate_tree()
            self.save_settings()
            self.status_bar.showMessage(f"Working directory: {directory}")

    def populate_tree(self):
        """Populate the tree view with files and directories"""
        self.file_tree.clear()

        if not self.working_directory or not os.path.exists(self.working_directory):
            return

        # Add root directory
        root_name = os.path.basename(self.working_directory) or self.working_directory
        root_item = QTreeWidgetItem(self.file_tree, [root_name])
        root_item.setData(0, Qt.UserRole, self.working_directory)

        # Populate tree recursively
        self.add_tree_nodes(root_item, self.working_directory)
        root_item.setExpanded(True)

    def add_tree_nodes(self, parent_item, path):
        """Recursively add nodes to the tree"""
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))

            for item in items:
                if item.startswith('.'):
                    continue

                full_path = os.path.join(path, item)

                if os.path.isdir(full_path):
                    # Add directory
                    tree_item = QTreeWidgetItem(parent_item, [f"📁 {item}"])
                    tree_item.setData(0, Qt.UserRole, full_path)
                    self.add_tree_nodes(tree_item, full_path)
                else:
                    # Add file
                    if item.endswith(('.cbl', '.cob', '.cobol')):
                        icon = "📄"
                    else:
                        icon = "📋"
                    tree_item = QTreeWidgetItem(parent_item, [f"{icon} {item}"])
                    tree_item.setData(0, Qt.UserRole, full_path)
        except PermissionError:
            pass

    def on_tree_double_click(self, item, column):
        """Handle double-click on tree item - open file in tab"""
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            # Check if file is already open
            for tab_index, file_info in self.open_files.items():
                if file_info.get('path') == file_path:
                    # File already open, switch to that tab
                    self.tab_widget.setCurrentIndex(tab_index)
                    self.status_bar.showMessage(f"Switched to: {file_path}")
                    return

            # Open file in new tab
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.create_new_tab(file_path, content)
                    self.status_bar.showMessage(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    editor = CobolEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
