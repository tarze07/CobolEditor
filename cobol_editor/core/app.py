"""Główne okno aplikacji COBOL Editor"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QLabel, QFrame,
    QFileDialog, QMessageBox, QInputDialog, QDialog, QListWidget,
    QScrollBar, QSplitter, QStatusBar, QMenuBar, QMenu, QTabWidget,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QFormLayout, QDialogButtonBox,
    QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, QRect, QSize, Signal, Slot
from PySide6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QTextCharFormat,
    QSyntaxHighlighter, QTextCursor, QTextDocument, QKeySequence,
    QAction, QPalette
)

from ..config import AppSettings, get_theme_colors, DEFAULT_FONT_SIZE, DEFAULT_FONT_FAMILY
from ..config.constants import MIN_FONT_SIZE, MAX_FONT_SIZE, MARKDOWN_EXTENSIONS
from ..syntax import get_highlighter_for_extension, CobolSyntaxHighlighter
from ..editor import CodeEditor, MarkdownPreviewWidget
from ..search import SearchWorker, SearchDialog, FileTypeFilterDialog, DirectoryFilterDialog
from .file_manager import FileManager
from .workspace import Workspace


class CobolEditor(QMainWindow):
    """Główne okno aplikacji COBOL Editor - uproszczona wersja"""
    
    def __init__(self, file_to_open=None):
        super().__init__()
        
        # Managers
        self.file_manager = FileManager()
        self.workspace = Workspace()
        self.workspace.set_file_manager(self.file_manager)
        self.settings = AppSettings()
        
        # State
        self.working_directories = []
        self.search_text = ""
        self.last_search_position = 0
        self.file_to_open = file_to_open
        self.search_worker = None
        self.open_files = {}
        self.search_file_types = set()
        self.searchable_directories = []
        
        # UI settings
        self.font_size = DEFAULT_FONT_SIZE
        self.font_family = DEFAULT_FONT_FAMILY
        self.current_theme = 'Light'
        self.tab_widget = None
        self.file_tree = None
        self.status_bar = None
        self.search_panel = None
        self.search_input_field = None
        self.search_results_list = None
        self.search_status_label = None
        self.cancel_search_button = None
        self.file_scanning_label = None
        self.tree_label = None
        self.current_search_results = []
        
        self.init_ui()
        self.load_settings()
        self.apply_theme(self.current_theme)
        
        if self.file_to_open:
            self.open_file_from_path(self.file_to_open)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("COBOL Editor")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # File tree panel
        tree_container = self._create_tree_panel()
        splitter.addWidget(tree_container)
        
        # Editor panel with tabs and search
        editor_panel = self._create_editor_panel()
        splitter.addWidget(editor_panel)
        
        # Set splitter sizes
        splitter.setSizes([200, 700])
        
        # Create menu bar
        self._create_menu()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create initial tab
        self.create_new_tab()
    
    def _create_tree_panel(self):
        """Create the file tree panel"""
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)
        
        self.tree_label = QLabel("Workspace")
        self.tree_label.setAlignment(Qt.AlignCenter)
        self.tree_label.setMaximumHeight(25)
        tree_label_font = QFont("Segoe UI", 11, QFont.Bold)
        tree_label_font.setStyleHint(QFont.SansSerif)
        self.tree_label.setFont(tree_label_font)
        tree_layout.addWidget(self.tree_label)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setMaximumWidth(300)
        self.file_tree.setMinimumWidth(150)
        tree_font = QFont("Segoe UI", 10)
        tree_font.setStyleHint(QFont.SansSerif)
        self.file_tree.setFont(tree_font)
        self.file_tree.itemDoubleClicked.connect(self.on_tree_double_click)
        self.file_tree.itemExpanded.connect(self.on_tree_item_expanded)
        tree_layout.addWidget(self.file_tree)
        
        return tree_container
    
    def _create_editor_panel(self):
        """Create the editor panel with tabs and search"""
        vertical_splitter = QSplitter(Qt.Vertical)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        vertical_splitter.addWidget(self.tab_widget)
        
        # Search panel
        self.search_panel = self._create_search_panel()
        vertical_splitter.addWidget(self.search_panel)
        
        vertical_splitter.setSizes([500, 200])
        
        return vertical_splitter
    
    def _create_search_panel(self):
        """Create the search panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        label = QLabel("Search in Files")
        label.setAlignment(Qt.AlignCenter)
        label.setMaximumHeight(25)
        header_layout.addWidget(label)
        
        close_btn = QPushButton("×")
        close_btn.setMaximumWidth(30)
        close_btn.setMaximumHeight(25)
        close_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        close_btn.clicked.connect(panel.hide)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        # Search input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Search:"))
        
        self.search_input_field = QLineEdit()
        self.search_input_field.setPlaceholderText("Type to search (min 2 chars)...")
        self.search_input_field.setMinimumHeight(30)
        self.search_input_field.setFont(QFont("Consolas", 10))
        input_layout.addWidget(self.search_input_field)
        
        # Buttons
        self.cancel_search_button = QPushButton("Cancel")
        self.cancel_search_button.setMaximumWidth(80)
        self.cancel_search_button.setEnabled(False)
        self.cancel_search_button.clicked.connect(self.cancel_search)
        input_layout.addWidget(self.cancel_search_button)
        
        layout.addLayout(input_layout)
        
        # Status labels
        self.search_status_label = QLabel("Type at least 2 characters to start searching...")
        self.search_status_label.setMinimumHeight(20)
        self.search_status_label.setStyleSheet("padding: 3px;")
        layout.addWidget(self.search_status_label)
        
        self.file_scanning_label = QLabel("")
        self.file_scanning_label.setMinimumHeight(20)
        self.file_scanning_label.setStyleSheet("padding: 3px; font-style: italic;")
        self.file_scanning_label.hide()
        layout.addWidget(self.file_scanning_label)
        
        # Results list
        self.search_results_list = QListWidget()
        self.search_results_list.setMinimumHeight(150)
        layout.addWidget(self.search_results_list)
        
        # Info label
        info = QLabel("Double-click a result to open the file at that line")
        info.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(info)
        
        # Connect signals
        self.search_input_field.textChanged.connect(self.on_search_input_changed)
        self.search_results_list.itemDoubleClicked.connect(self.on_search_result_double_clicked)
        
        panel.hide()
        return panel
    
    def _create_menu(self):
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
        
        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        add_dir_action = QAction("Add Directory to Workspace...", self)
        add_dir_action.triggered.connect(self.add_directory_to_workspace)
        file_menu.addAction(add_dir_action)
        
        remove_dir_action = QAction("Remove Directory from Workspace...", self)
        remove_dir_action.triggered.connect(self.remove_directory_from_workspace)
        file_menu.addAction(remove_dir_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        find_action = QAction("Find...", self)
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
        
        theme_menu = view_menu.addMenu("Color Theme")
        for theme_name in ['Light', 'Dark', 'High Contrast', 'Monokai']:
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
    
    # === Tab Management ===
    
    def create_new_tab(self, file_path=None, content=""):
        """Create a new tab with editor"""
        theme = get_theme_colors(self.current_theme)
        font = QFont(self.font_family, self.font_size)
        font.setStyleHint(QFont.Monospace)
        
        is_markdown = self.file_manager.is_markdown(file_path)
        
        if is_markdown:
            tab_widget = MarkdownPreviewWidget(self, theme, font)
            editor = tab_widget.editor
            highlighter = None
        else:
            editor = CodeEditor(self)
            editor.setFont(font)
            
            palette = editor.palette()
            palette.setColor(QPalette.Base, QColor(theme['bg']))
            palette.setColor(QPalette.Text, QColor(theme['fg']))
            editor.setPalette(palette)
            
            line_palette = editor.line_number_area.palette()
            line_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
            line_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
            editor.line_number_area.setPalette(line_palette)
            
            editor.set_search_highlight_color(QColor(theme['search_bg']))
            
            # Setup highlighter
            highlighter_class = get_highlighter_for_extension(
                self.file_manager.get_extension(file_path) if file_path else 'cbl'
            ) or CobolSyntaxHighlighter
            highlighter = highlighter_class(editor.document(), theme)
            
            tab_widget = editor
        
        # Set content
        if content:
            if is_markdown:
                tab_widget.setPlainText(content)
            else:
                editor.setPlainText(content)
        
        # Track modifications
        if is_markdown:
            editor.textChanged.connect(lambda: self.on_text_changed(editor))
        else:
            editor.textChanged.connect(lambda: self.on_text_changed(editor))
        
        # Add tab
        if file_path:
            tab_name = os.path.basename(file_path)
        else:
            tab_name = "Untitled"
            existing_untitled = [name for name in self.open_files.values() 
                                if name.get('path') is None]
            if existing_untitled:
                tab_name = f"Untitled ({len(existing_untitled) + 1})"
        
        tab_index = self.tab_widget.addTab(tab_widget, tab_name)
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Store file info
        self.open_files[tab_index] = {
            'path': file_path,
            'modified': False,
            'editor': editor,
            'highlighter': highlighter
        }
        
        return tab_index
    
    def close_tab(self, index):
        """Close a tab"""
        if index in self.open_files:
            file_info = self.open_files[index]
            if file_info.get('modified'):
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"Save changes to {self.tab_widget.tabText(index)}?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                if reply == QMessageBox.Save:
                    self.tab_widget.setCurrentIndex(index)
                    if not self.save_file():
                        return
                elif reply == QMessageBox.Cancel:
                    return
            
            del self.open_files[index]
            self.tab_widget.removeTab(index)
            
            # Update indices
            new_open_files = {}
            for i, (old_idx, info) in enumerate(sorted(self.open_files.items())):
                new_open_files[i] = info
            self.open_files = new_open_files
        
        if self.tab_widget.count() == 0:
            self.create_new_tab()
    
    def get_current_editor(self):
        """Get the current editor"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0 and current_index in self.open_files:
            return self.open_files[current_index].get('editor')
        return None
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        if index in self.open_files:
            file_path = self.open_files[index].get('path')
            if file_path:
                self.status_bar.showMessage(f"Editing: {file_path}")
            else:
                self.status_bar.showMessage("New file")
    
    def on_text_changed(self, editor):
        """Handle text changes"""
        current_index = self.tab_widget.currentIndex()
        if current_index in self.open_files:
            if not self.open_files[current_index].get('modified'):
                self.open_files[current_index]['modified'] = True
                tab_text = self.tab_widget.tabText(current_index)
                if not tab_text.endswith(" *"):
                    self.tab_widget.setTabText(current_index, tab_text + " *")
    
    # === File Operations ===
    
    def new_file(self):
        """Create a new file"""
        self.create_new_tab()
        self.status_bar.showMessage("New file created")
    
    def open_file(self):
        """Open a file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Files (*);;COBOL Files (*.cbl *.cob *.cobol);;Text Files (*.txt)"
        )
        if file_path:
            self.open_file_from_path(file_path)
    
    def open_file_from_path(self, file_path):
        """Open a file from path"""
        # Check if already open
        for tab_index, file_info in self.open_files.items():
            if file_info.get('path') == file_path:
                self.tab_widget.setCurrentIndex(tab_index)
                self.status_bar.showMessage(f"Switched to: {file_path}")
                return
        
        try:
            content, encoding = self.file_manager.read_file(file_path)
            self.create_new_tab(file_path, content)
            self.status_bar.showMessage(f"Opened: {file_path} (encoding: {encoding})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
    
    def save_file(self):
        """Save current file"""
        current_index = self.tab_widget.currentIndex()
        if current_index not in self.open_files:
            return False
        
        file_info = self.open_files[current_index]
        file_path = file_info.get('path')
        
        if not file_path:
            return self.save_as_file()
        
        editor = file_info.get('editor')
        content = editor.toPlainText()
        
        try:
            self.file_manager.save_file(file_path, content)
            file_info['modified'] = False
            tab_text = self.tab_widget.tabText(current_index)
            if tab_text.endswith(" *"):
                self.tab_widget.setTabText(current_index, tab_text[:-3])
            self.status_bar.showMessage(f"Saved: {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
            return False
    
    def save_as_file(self):
        """Save as dialog"""
        current_index = self.tab_widget.currentIndex()
        if current_index not in self.open_files:
            return False
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "",
            "All Files (*);;COBOL Files (*.cbl);;Text Files (*.txt)"
        )
        if file_path:
            self.open_files[current_index]['path'] = file_path
            tab_name = os.path.basename(file_path)
            self.tab_widget.setTabText(current_index, tab_name)
            return self.save_file()
        return False
    
    def select_all_text(self):
        """Select all text in current editor"""
        editor = self.get_current_editor()
        if editor:
            editor.selectAll()
    
    # === Search Operations ===
    
    def find_text(self):
        """Show find dialog"""
        dialog = SearchDialog(self, "Find", "Enter text to search:")
        if dialog.exec() == QDialog.Accepted:
            self.search_text = dialog.get_text()
            self.last_search_position = 0
            if self.search_text:
                self.find_next()
    
    def find_next(self):
        """Find next occurrence"""
        if not self.search_text:
            self.find_text()
            return
        
        editor = self.get_current_editor()
        if not editor:
            return
        
        document = editor.document()
        cursor = editor.textCursor()
        
        # Start from last position
        cursor.setPosition(self.last_search_position)
        
        # Find
        found = document.find(self.search_text, cursor)
        if found.isNull():
            # Try from beginning
            cursor.movePosition(QTextCursor.Start)
            found = document.find(self.search_text, cursor)
        
        if not found.isNull():
            editor.setTextCursor(found)
            self.last_search_position = found.position()
        else:
            QMessageBox.information(self, "Find", f"'{self.search_text}' not found.")
    
    def find_in_files(self):
        """Show search panel"""
        self.search_panel.show()
        self.search_input_field.setFocus()
    
    def on_search_input_changed(self, text):
        """Handle search input changes"""
        if len(text) < 2:
            self.search_status_label.setText("Type at least 2 characters...")
            return
        
        # Cancel previous search
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_worker.wait()
        
        # Clear previous results
        self.search_results_list.clear()
        self.current_search_results = []
        
        # Get directories to search
        dirs = self.searchable_directories if self.searchable_directories else self.working_directories
        if not dirs:
            self.search_status_label.setText("No directories to search. Add directories to workspace.")
            return
        
        # Start new search
        self.search_worker = SearchWorker(dirs, text, self.search_file_types or None)
        self.search_worker.result_found.connect(self.on_search_result_found)
        self.search_worker.progress_update.connect(self.on_search_progress_update)
        self.search_worker.file_scanning.connect(self.on_file_scanning)
        self.search_worker.search_finished.connect(self.on_search_finished)
        
        self.cancel_search_button.setEnabled(True)
        self.file_scanning_label.show()
        self.search_status_label.setText("Searching...")
        
        self.search_worker.start()
    
    def cancel_search(self):
        """Cancel current search"""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_worker.wait()
        self.cancel_search_button.setEnabled(False)
        self.file_scanning_label.hide()
        self.search_status_label.setText("Search cancelled")
    
    def on_search_result_found(self, file_path, line_num, line_text):
        """Handle search result"""
        self.current_search_results.append((file_path, line_num, line_text))
        display_text = f"{file_path}:{line_num}: {line_text[:100]}"
        self.search_results_list.addItem(display_text)
    
    def on_search_progress_update(self, files_searched, matches_found):
        """Handle search progress"""
        self.search_status_label.setText(f"Searching... Found {matches_found} matches in {files_searched} files")
    
    def on_file_scanning(self, file_path):
        """Handle file scanning update"""
        self.file_scanning_label.setText(f"Scanning: {file_path[:80]}...")
    
    def on_search_finished(self, total_files, total_matches):
        """Handle search completion"""
        self.cancel_search_button.setEnabled(False)
        self.file_scanning_label.hide()
        if total_matches == 0:
            self.search_status_label.setText(f"No matches found. Searched {total_files} files.")
        else:
            self.search_status_label.setText(f"Found {total_matches} matches in {total_files} files.")
    
    def on_search_result_double_clicked(self, item):
        """Handle search result double click"""
        index = self.search_results_list.row(item)
        if index < len(self.current_search_results):
            file_path, line_num, _ = self.current_search_results[index]
            self.open_file_at_line(file_path, line_num)
    
    def open_file_at_line(self, file_path, line_num):
        """Open file and jump to line"""
        # Check if already open
        for tab_index, file_info in self.open_files.items():
            if file_info.get('path') == file_path:
                self.tab_widget.setCurrentIndex(tab_index)
                editor = file_info.get('editor')
                if editor and hasattr(editor, 'highlight_line'):
                    editor.highlight_line(line_num)
                return
        
        # Open new
        try:
            content, _ = self.file_manager.read_file(file_path)
            self.create_new_tab(file_path, content)
            current_idx = self.tab_widget.currentIndex()
            if current_idx in self.open_files:
                editor = self.open_files[current_idx].get('editor')
                if editor and hasattr(editor, 'highlight_line'):
                    editor.highlight_line(line_num)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
    
    def search_in_working_directory_for_text(self, text):
        """Search for text from context menu"""
        self.search_panel.show()
        self.search_input_field.setText(text)
        self.search_input_field.setFocus()
    
    def configure_search_file_types(self):
        """Configure file types for search"""
        from ..config.constants import SEARCHABLE_EXTENSIONS
        dialog = FileTypeFilterDialog(self, SEARCHABLE_EXTENSIONS, self.search_file_types)
        if dialog.exec() == QDialog.Accepted:
            self.search_file_types = dialog.get_selected_extensions()
            # Restart search if there's text
            if self.search_input_field.text():
                self.on_search_input_changed(self.search_input_field.text())
    
    def configure_search_directories(self):
        """Configure directories for search"""
        dialog = DirectoryFilterDialog(self, self.working_directories, self.searchable_directories)
        if dialog.exec() == QDialog.Accepted:
            self.searchable_directories = dialog.get_selected_directories()
            # Restart search if there's text
            if self.search_input_field.text():
                self.on_search_input_changed(self.search_input_field.text())
    
    # === Workspace Operations ===
    
    def add_directory_to_workspace(self):
        """Add directory to workspace"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Add to Workspace")
        if directory:
            if self.workspace.add_directory(directory):
                self.working_directories = self.workspace.get_directories()
                self.workspace.populate_tree(self.file_tree, self.on_tree_item_expanded)
                self.save_settings()
                self.status_bar.showMessage(f"Added to workspace: {directory}")
            else:
                QMessageBox.information(self, "Info", "Directory already in workspace or invalid.")
    
    def remove_directory_from_workspace(self):
        """Remove directory from workspace"""
        if not self.working_directories:
            QMessageBox.information(self, "Info", "No directories in workspace.")
            return
        
        from ..ui.dialogs import DirectorySelectionDialog
        dialog = DirectorySelectionDialog(self, self.working_directories)
        if dialog.exec() == QDialog.Accepted:
            selected = dialog.get_selected_directory()
            if selected and self.workspace.remove_directory(selected):
                self.working_directories = self.workspace.get_directories()
                self.workspace.populate_tree(self.file_tree, self.on_tree_item_expanded)
                self.save_settings()
                self.status_bar.showMessage(f"Removed from workspace: {selected}")
    
    def on_tree_item_expanded(self, item):
        """Handle tree item expansion"""
        self.workspace.load_children_on_expand(item)
    
    def on_tree_double_click(self, item, column):
        """Handle tree double click"""
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.open_file_from_path(file_path)
    
    # === Theme & Font ===
    
    def apply_theme(self, theme_name):
        """Apply color theme"""
        self.current_theme = theme_name
        theme = get_theme_colors(theme_name)
        
        # Update all open editors
        for tab_index, file_info in self.open_files.items():
            editor = file_info.get('editor')
            highlighter = file_info.get('highlighter')
            
            if editor:
                palette = editor.palette()
                palette.setColor(QPalette.Base, QColor(theme['bg']))
                palette.setColor(QPalette.Text, QColor(theme['fg']))
                editor.setPalette(palette)
                
                if hasattr(editor, 'line_number_area'):
                    line_palette = editor.line_number_area.palette()
                    line_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
                    line_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
                    editor.line_number_area.setPalette(line_palette)
                    editor.line_number_area.update()
                
                if hasattr(editor, 'set_search_highlight_color'):
                    editor.set_search_highlight_color(QColor(theme['search_bg']))
            
            if highlighter and hasattr(highlighter, 'update_theme'):
                highlighter.update_theme(theme)
        
        self.save_settings()
    
    def increase_font_size(self):
        """Increase font size"""
        if self.font_size < MAX_FONT_SIZE:
            self.font_size += 2
            self.update_font()
    
    def decrease_font_size(self):
        """Decrease font size"""
        if self.font_size > MIN_FONT_SIZE:
            self.font_size -= 2
            self.update_font()
    
    def reset_font_size(self):
        """Reset font size"""
        self.font_size = DEFAULT_FONT_SIZE
        self.update_font()
    
    def update_font(self):
        """Update font in all editors"""
        font = QFont(self.font_family, self.font_size)
        font.setStyleHint(QFont.Monospace)
        
        for file_info in self.open_files.values():
            editor = file_info.get('editor')
            if editor:
                editor.setFont(font)
                if hasattr(editor, 'update_line_number_area_width'):
                    editor.update_line_number_area_width(0)
        
        self.save_settings()
    
    # === Settings ===
    
    def load_settings(self):
        """Load settings"""
        self.font_size = self.settings.get_font_size()
        self.font_family = self.settings.get_font_family()
        self.current_theme = self.settings.get_theme()
        self.working_directories = self.settings.get_working_directories()
        
        # Load workspace directories
        for directory in self.working_directories:
            self.workspace.add_directory(directory)
        
        if self.working_directories:
            self.workspace.populate_tree(self.file_tree, self.on_tree_item_expanded)
    
    def save_settings(self):
        """Save settings"""
        self.settings.set_font_size(self.font_size)
        self.settings.set_font_family(self.font_family)
        self.settings.set_theme(self.current_theme)
        self.settings.set_working_directories(self.working_directories)
    
    def closeEvent(self, event):
        """Handle close event"""
        # Check for unsaved changes
        for tab_index, file_info in self.open_files.items():
            if file_info.get('modified'):
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"Save changes to {self.tab_widget.tabText(tab_index)}?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                if reply == QMessageBox.Save:
                    self.tab_widget.setCurrentIndex(tab_index)
                    if not self.save_file():
                        event.ignore()
                        return
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return
        
        # Cancel any running search
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_worker.wait()
        
        self.save_settings()
        event.accept()
    
    # === About ===
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About COBOL Editor",
            "<h2>COBOL Editor</h2>"
            "<p>A modern code editor with syntax highlighting for COBOL and other languages.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Syntax highlighting for COBOL, C#, JavaScript, Python, XML, JSON, YAML</li>"
            "<li>Multiple tabs</li>"
            "<li>File tree with workspace support</li>"
            "<li>Search in files</li>"
            "<li>Multiple color themes</li>"
            "</ul>"
            "<p>Built with PySide6</p>"
        )
