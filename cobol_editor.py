#!/usr/bin/env python3
"""
COBOL Editor with Syntax Highlighting and Search
Migrated to PySide6
"""

import sys
import os
import re
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QLabel, QFrame,
    QFileDialog, QMessageBox, QInputDialog, QDialog, QListWidget,
    QScrollBar, QSplitter, QStatusBar, QMenuBar, QMenu, QTabWidget,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QFormLayout, QDialogButtonBox,
    QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, QRect, QSize, Signal, Slot, QSettings, QThread
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


class SearchDialog(QDialog):
    """Custom search dialog with larger text input area"""
    def __init__(self, parent=None, title="Search", label="Enter text to search:"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setMinimumHeight(150)

        layout = QVBoxLayout(self)

        # Add label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Add large text input
        self.text_input = QLineEdit()
        self.text_input.setMinimumHeight(40)
        font = QFont("Consolas", 12)
        self.text_input.setFont(font)
        layout.addWidget(self.text_input)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to text input
        self.text_input.setFocus()

    def get_text(self):
        """Get the entered text"""
        return self.text_input.text()


class LiveSearchDialog(QDialog):
    """Search dialog with live results that appear as you type"""
    def __init__(self, parent=None, working_dir=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.working_directory = working_dir
        self.search_results = []

        self.setWindowTitle("Find in Files (Live Search)")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # Add label
        label_widget = QLabel("Enter text to search (minimum 2 characters):")
        layout.addWidget(label_widget)

        # Add large text input
        self.text_input = QLineEdit()
        self.text_input.setMinimumHeight(40)
        self.text_input.setPlaceholderText("Type to search...")
        font = QFont("Consolas", 12)
        self.text_input.setFont(font)
        layout.addWidget(self.text_input)

        # Add status label
        self.status_label = QLabel("Type at least 2 characters to start searching...")
        self.status_label.setMinimumHeight(25)
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)

        # Add results list
        results_label = QLabel("Search Results:")
        layout.addWidget(results_label)

        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(400)
        layout.addWidget(self.results_list)

        # Add info label
        info_label = QLabel("Double-click a result to open the file at that line")
        info_label.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(info_label)

        # Add Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to text input
        self.text_input.setFocus()

        # Connect signals
        self.text_input.textChanged.connect(self.on_text_changed)
        self.results_list.itemDoubleClicked.connect(self.on_result_double_clicked)

    def on_text_changed(self, text):
        """Handle text change and perform live search"""
        if len(text) < 2:
            self.results_list.clear()
            self.search_results = []
            if len(text) == 0:
                self.status_label.setText("Type at least 2 characters to start searching...")
            else:
                self.status_label.setText(f"Type {2 - len(text)} more character(s)...")
            return

        # Perform search
        self.perform_search(text)

    def perform_search(self, text):
        """Perform search in working directory"""
        if not self.working_directory or not os.path.exists(self.working_directory):
            self.status_label.setText("No working directory set. Use File > Select Working Directory")
            self.results_list.clear()
            self.search_results = []
            return

        self.status_label.setText("Searching...")
        self.results_list.clear()
        self.search_results = []

        # Search in files
        match_count = 0
        file_count = 0
        for root, dirs, files in os.walk(self.working_directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_count += 1
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if text.lower() in line.lower():
                                self.search_results.append((file_path, line_num, line.strip()))
                                display_text = f"{file_path}:{line_num}: {line.strip()}"
                                self.results_list.addItem(display_text)
                                match_count += 1

                                # Limit results to prevent UI slowdown
                                if match_count >= 1000:
                                    self.status_label.setText(f"Found 1000+ matches (showing first 1000). Searched {file_count} files.")
                                    return
                except Exception:
                    continue

        # Update status
        if match_count == 0:
            self.status_label.setText(f"No matches found. Searched {file_count} files in: {self.working_directory}")
        else:
            self.status_label.setText(f"Found {match_count} matches in {file_count} files. Double-click to open.")

    def on_result_double_clicked(self, item):
        """Handle double-click on result - open file"""
        index = self.results_list.row(item)
        if index < len(self.search_results):
            file_path, line_num, _ = self.search_results[index]
            if self.parent_editor and hasattr(self.parent_editor, 'open_file_at_line'):
                self.parent_editor.open_file_at_line(file_path, line_num)
                self.accept()  # Close dialog after opening file

    def get_text(self):
        """Get the entered text"""
        return self.text_input.text()


class SearchWorker(QThread):
    """Worker thread for performing file searches without blocking UI"""

    # Signals
    result_found = Signal(str, int, str)  # file_path, line_num, line_text
    progress_update = Signal(int, int)    # files_searched, matches_found
    search_finished = Signal(int, int)    # total_files, total_matches
    file_scanning = Signal(str)           # current_file_path being scanned

    # Directories to skip during search
    SKIP_DIRS = {
        '.git', '.svn', '.hg', '.bzr',  # Version control
        'node_modules', 'bower_components',  # JavaScript
        '__pycache__', '.pytest_cache', '.tox', 'venv', 'env', '.env',  # Python
        'bin', 'obj', '.vs', '.vscode',  # Build outputs and IDE
        'target', 'build', 'dist', '.gradle',  # Build systems
        '.idea', '.settings', '.eclipse',  # IDEs
        'vendor', 'packages'  # Dependencies
    }

    # File extensions to search (text files only)
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

    def __init__(self, working_directories, search_text, searchable_extensions=None):
        super().__init__()
        # Support both single directory (string) and multiple directories (list)
        if isinstance(working_directories, str):
            self.working_directories = [working_directories]
        else:
            self.working_directories = working_directories if working_directories else []
        self.search_text = search_text.lower()
        self.cancelled = False
        self.max_results = 1000
        # Use provided extensions or default to class variable
        self.searchable_extensions = searchable_extensions if searchable_extensions is not None else self.SEARCHABLE_EXTENSIONS

    def cancel(self):
        """Cancel the search operation"""
        self.cancelled = True

    def is_searchable_file(self, filename):
        """Check if file should be searched based on extension"""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.searchable_extensions

    def run(self):
        """Execute the search in background thread"""
        match_count = 0
        file_count = 0
        batch_results = []
        batch_size = 50  # Emit results in batches for better UI performance

        try:
            # Search through all working directories
            for working_dir in self.working_directories:
                if self.cancelled:
                    break

                if not os.path.exists(working_dir):
                    continue

                for root, dirs, files in os.walk(working_dir):
                    # Check for cancellation
                    if self.cancelled:
                        break

                    # Skip unwanted directories (modify dirs in-place to skip traversal)
                    dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS and not d.startswith('.')]

                    for file in files:
                        # Check for cancellation
                        if self.cancelled:
                            break

                        # Skip non-searchable files
                        if not self.is_searchable_file(file):
                            continue

                        file_path = os.path.join(root, file)
                        file_count += 1

                        # Emit signal for currently scanning file
                        self.file_scanning.emit(file_path)

                        try:
                            # Skip large files (> 10MB)
                            if os.path.getsize(file_path) > 10 * 1024 * 1024:
                                continue

                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    if self.cancelled:
                                        break

                                    if self.search_text in line.lower():
                                        batch_results.append((file_path, line_num, line.strip()))
                                        match_count += 1

                                        # Emit batch of results
                                        if len(batch_results) >= batch_size:
                                            for result in batch_results:
                                                self.result_found.emit(*result)
                                            batch_results.clear()
                                            self.progress_update.emit(file_count, match_count)

                                        # Stop if max results reached
                                        if match_count >= self.max_results:
                                            # Emit remaining results
                                            for result in batch_results:
                                                self.result_found.emit(*result)
                                            self.search_finished.emit(file_count, match_count)
                                            return

                        except Exception:
                            # Skip files that can't be read
                            continue

                        # Periodic progress updates
                        if file_count % 100 == 0:
                            self.progress_update.emit(file_count, match_count)

            # Emit any remaining results
            for result in batch_results:
                self.result_found.emit(*result)

        except Exception as e:
            # Handle any unexpected errors gracefully
            pass

        # Emit final results
        if not self.cancelled:
            self.search_finished.emit(file_count, match_count)


class SyntaxConfigDialog(QDialog):
    """Dialog for configuring file extension to syntax highlighter mappings"""
    def __init__(self, parent=None, current_mappings=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Syntax Highlighting")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)

        # Add description
        desc = QLabel("Configure which file extensions use which syntax highlighter.\n"
                     "Enter extensions separated by commas (e.g., cs,csharp)")
        layout.addWidget(desc)

        # Create form for each language
        form_layout = QFormLayout()

        self.extension_inputs = {}
        languages = ['COBOL', 'C#', 'JavaScript', 'Python', 'XML', 'JSON', 'YAML']

        for lang in languages:
            line_edit = QLineEdit()
            if current_mappings and lang in current_mappings:
                line_edit.setText(','.join(current_mappings[lang]))
            self.extension_inputs[lang] = line_edit
            form_layout.addRow(f"{lang}:", line_edit)

        layout.addLayout(form_layout)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_mappings(self):
        """Get the configured mappings"""
        mappings = {}
        for lang, line_edit in self.extension_inputs.items():
            text = line_edit.text().strip()
            if text:
                # Split by comma and clean up
                extensions = [ext.strip().lstrip('.') for ext in text.split(',') if ext.strip()]
                if extensions:
                    mappings[lang] = extensions
        return mappings


class FileTypeFilterDialog(QDialog):
    """Dialog for selecting which file types to include in search"""
    def __init__(self, parent=None, all_extensions=None, selected_extensions=None):
        super().__init__(parent)
        self.setWindowTitle("File Type Filter")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        # Store all available extensions
        self.all_extensions = all_extensions or set()
        self.selected_extensions = selected_extensions or self.all_extensions.copy()

        layout = QVBoxLayout(self)

        # Add description
        desc = QLabel("Select which file types to include in search:")
        desc.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(desc)

        # Add Select All / Deselect All buttons
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Create scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Group extensions by category
        extension_groups = {
            'COBOL': ['.cob', '.cbl', '.cobol', '.cpy'],
            'C#': ['.cs', '.csharp'],
            'JavaScript/TypeScript': ['.js', '.jsx', '.ts', '.tsx'],
            'Python': ['.py', '.pyw'],
            'Markup': ['.xml', '.xaml', '.html', '.htm'],
            'Configuration': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'],
            'Documentation': ['.txt', '.md', '.rst'],
            'C/C++': ['.c', '.cpp', '.h', '.hpp'],
            'JVM Languages': ['.java', '.kt'],
            'Other Languages': ['.go', '.rs', '.rb', '.php'],
            'Scripts': ['.sql', '.sh', '.bat', '.ps1'],
            'Styles': ['.css', '.scss', '.sass', '.less'],
            'Logs': ['.log']
        }

        # Create checkboxes for each group
        self.checkboxes = {}
        for group_name, extensions in extension_groups.items():
            # Add group label
            group_label = QLabel(group_name)
            group_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #0066cc;")
            scroll_layout.addWidget(group_label)

            # Add checkboxes for extensions in this group
            for ext in extensions:
                if ext in self.all_extensions:
                    checkbox = QCheckBox(ext)
                    checkbox.setChecked(ext in self.selected_extensions)
                    checkbox.setStyleSheet("margin-left: 20px;")
                    scroll_layout.addWidget(checkbox)
                    self.checkboxes[ext] = checkbox

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Add info label
        self.info_label = QLabel()
        self.update_info_label()
        self.info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; margin-top: 5px;")
        layout.addWidget(self.info_label)

        # Connect checkbox changes to update info
        for checkbox in self.checkboxes.values():
            checkbox.stateChanged.connect(self.update_info_label)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_all(self):
        """Select all file types"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all(self):
        """Deselect all file types"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def update_info_label(self):
        """Update the info label with count of selected types"""
        selected_count = sum(1 for cb in self.checkboxes.values() if cb.isChecked())
        total_count = len(self.checkboxes)
        self.info_label.setText(f"Selected: {selected_count} of {total_count} file types")

    def get_selected_extensions(self):
        """Get the set of selected file extensions"""
        return {ext for ext, checkbox in self.checkboxes.items() if checkbox.isChecked()}


class DirectoryFilterDialog(QDialog):
    """Dialog for selecting which directories to include in search"""
    def __init__(self, parent=None, all_directories=None, selected_directories=None):
        super().__init__(parent)
        self.setWindowTitle("Directory Search Filter")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Store all available directories
        self.all_directories = all_directories or []
        self.selected_directories = selected_directories or self.all_directories.copy()

        layout = QVBoxLayout(self)

        # Add description
        desc = QLabel("Select which directories to include in search:")
        desc.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(desc)

        # Add Select All / Deselect All buttons
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Create scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Create checkboxes for each directory
        self.checkboxes = {}
        for directory in self.all_directories:
            checkbox = QCheckBox(directory)
            checkbox.setChecked(directory in self.selected_directories)
            checkbox.setStyleSheet("margin: 5px; padding: 5px;")
            checkbox.setToolTip(directory)
            scroll_layout.addWidget(checkbox)
            self.checkboxes[directory] = checkbox

        if not self.all_directories:
            no_dirs_label = QLabel("No directories in workspace.\nAdd directories using File > Add Directory to Workspace")
            no_dirs_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            no_dirs_label.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(no_dirs_label)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Add info label
        self.info_label = QLabel()
        self.update_info_label()
        self.info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; margin-top: 5px;")
        layout.addWidget(self.info_label)

        # Connect checkbox changes to update info
        for checkbox in self.checkboxes.values():
            checkbox.stateChanged.connect(self.update_info_label)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_all(self):
        """Select all directories"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all(self):
        """Deselect all directories"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def update_info_label(self):
        """Update the info label with count of selected directories"""
        selected_count = sum(1 for cb in self.checkboxes.values() if cb.isChecked())
        total_count = len(self.checkboxes)
        self.info_label.setText(f"Selected: {selected_count} of {total_count} directories")

    def get_selected_directories(self):
        """Get the list of selected directories"""
        return [directory for directory, checkbox in self.checkboxes.items() if checkbox.isChecked()]


class SyntaxHighlighterBase(QSyntaxHighlighter):
    """Base class for all syntax highlighters"""
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
        """Setup highlighting rules - to be overridden by subclasses"""
        pass

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given text block"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class CSharpSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for C#"""
    def update_highlighting_rules(self):
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'abstract', 'as', 'base', 'bool', 'break', 'byte', 'case', 'catch', 'char', 'checked',
            'class', 'const', 'continue', 'decimal', 'default', 'delegate', 'do', 'double', 'else',
            'enum', 'event', 'explicit', 'extern', 'false', 'finally', 'fixed', 'float', 'for',
            'foreach', 'goto', 'if', 'implicit', 'in', 'int', 'interface', 'internal', 'is', 'lock',
            'long', 'namespace', 'new', 'null', 'object', 'operator', 'out', 'override', 'params',
            'private', 'protected', 'public', 'readonly', 'ref', 'return', 'sbyte', 'sealed',
            'short', 'sizeof', 'stackalloc', 'static', 'string', 'struct', 'switch', 'this',
            'throw', 'true', 'try', 'typeof', 'uint', 'ulong', 'unchecked', 'unsafe', 'ushort',
            'using', 'virtual', 'void', 'volatile', 'while', 'async', 'await', 'var'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern), keyword_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+(\.\d+)?\b'), number_format))


class JavaScriptSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for JavaScript"""
    def update_highlighting_rules(self):
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
            'if', 'import', 'in', 'instanceof', 'let', 'new', 'return', 'super', 'switch', 'this',
            'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'true', 'false',
            'null', 'undefined'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern), keyword_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        self.highlighting_rules.append((re.compile(r'`[^`\\]*(\\.[^`\\]*)*`'), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+(\.\d+)?\b'), number_format))


class PythonSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for Python"""
    def update_highlighting_rules(self):
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class',
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keyword_pattern), keyword_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((re.compile(r'"""[^"]*"""'), string_format))
        self.highlighting_rules.append((re.compile(r"'''[^']*'''"), string_format))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((re.compile(r'\b\d+(\.\d+)?\b'), number_format))


class XMLSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for XML"""
    def update_highlighting_rules(self):
        self.highlighting_rules = []

        # Tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(self.theme['keyword']))
        tag_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'<[/]?[\w:]+'), tag_format))
        self.highlighting_rules.append((re.compile(r'[/]?>'), tag_format))

        # Attributes
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(self.theme['datatype']))
        self.highlighting_rules.append((re.compile(r'\b[\w:]+(?==)'), datatype_format))

        # Strings (attribute values)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"]*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^']*'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'<!--[^-]*-->'), comment_format))


class JSONSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for JSON"""
    def update_highlighting_rules(self):
        self.highlighting_rules = []

        # Keywords (true, false, null)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'\b(true|false|null)\b'), keyword_format))

        # Keys
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(self.theme['datatype']))
        self.highlighting_rules.append((re.compile(r'"[\w-]+"(?=\s*:)'), datatype_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((re.compile(r'\b-?\d+(\.\d+)?([eE][+-]?\d+)?\b'), number_format))


class YAMLSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for YAML"""
    def update_highlighting_rules(self):
        self.highlighting_rules = []

        # Keywords (true, false, null, yes, no)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'\b(true|false|null|yes|no|on|off)\b'), keyword_format))

        # Keys
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(self.theme['datatype']))
        self.highlighting_rules.append((re.compile(r'^[\w-]+(?=:)'), datatype_format))
        self.highlighting_rules.append((re.compile(r'\s[\w-]+(?=:)'), datatype_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((re.compile(r'"[^"]*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^']*'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((re.compile(r'\b-?\d+(\.\d+)?\b'), number_format))


class CobolSyntaxHighlighter(SyntaxHighlighterBase):
    """Syntax highlighter for COBOL"""
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


class CobolEditor(QMainWindow):
    def __init__(self, file_to_open=None):
        super().__init__()
        self.working_directories = []  # Changed from single directory to list of directories
        self.search_text = ""
        self.last_search_position = 0
        self.file_to_open = file_to_open
        self.search_worker = None  # Will hold the SearchWorker thread

        # Track open files: {tab_index: {'path': file_path, 'modified': bool}}
        self.open_files = {}

        # Store selected file types for search (default: all types from SearchWorker.SEARCHABLE_EXTENSIONS)
        self.search_file_types = SearchWorker.SEARCHABLE_EXTENSIONS.copy()

        # Store selected directories for search (default: all working directories)
        # This will be updated when working_directories are loaded
        self.searchable_directories = []

        # Initialize settings
        self.settings = QSettings('CobolEditor', 'CobolEditor')

        # Default values
        self.font_size = 18
        self.font_family = 'Consolas'
        self.current_theme = 'Light'
        self.markdown_extensions = {'.md', '.markdown', '.mdown', '.mkd'}

        # Default syntax highlighter mappings
        self.default_syntax_mappings = {
            'COBOL': ['cbl', 'cob', 'cobol'],
            'C#': ['cs', 'csharp'],
            'JavaScript': ['js', 'jsx', 'mjs'],
            'Python': ['py', 'pyw'],
            'XML': ['xml', 'xaml', 'svg'],
            'JSON': ['json'],
            'YAML': ['yaml', 'yml']
        }
        self.syntax_mappings = self.default_syntax_mappings.copy()

        # Highlighter class mapping
        self.highlighter_classes = {
            'COBOL': CobolSyntaxHighlighter,
            'C#': CSharpSyntaxHighlighter,
            'JavaScript': JavaScriptSyntaxHighlighter,
            'Python': PythonSyntaxHighlighter,
            'XML': XMLSyntaxHighlighter,
            'JSON': JSONSyntaxHighlighter,
            'YAML': YAMLSyntaxHighlighter
        }

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

        # Open file if specified via command line
        if self.file_to_open:
            self.open_file_from_path(self.file_to_open)

    def get_highlighter_for_file(self, file_path):
        """Get the appropriate syntax highlighter class for a file based on its extension"""
        if not file_path:
            return CobolSyntaxHighlighter  # Default to COBOL

        # Get file extension
        ext = os.path.splitext(file_path)[1].lstrip('.').lower()

        # Find which language this extension belongs to
        for lang, extensions in self.syntax_mappings.items():
            if ext in [e.lower() for e in extensions]:
                return self.highlighter_classes.get(lang, CobolSyntaxHighlighter)

        # Default to COBOL if no match
        return CobolSyntaxHighlighter

    def is_markdown_file(self, file_path):
        """Check whether the provided path points to a Markdown file."""
        if not file_path:
            return False
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.markdown_extensions

    def read_file_with_encoding(self, file_path):
        """
        Try to read a file with multiple encodings.
        Returns tuple: (content, encoding_used)
        """
        encodings = [
            'utf-8',
            'utf-8-sig',  # UTF-8 with BOM
            'latin-1',    # ISO-8859-1
            'cp1252',     # Windows-1252
            'cp1250',     # Polish/Central European
            'iso-8859-2', # Latin-2 (Central European)
        ]

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    return content, encoding
            except (UnicodeDecodeError, LookupError):
                continue

        # If all encodings fail, try with error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
                return content, 'utf-8 (with replacements)'
        except Exception as e:
            raise Exception(f"Could not read file with any encoding: {str(e)}")

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
        search_panel_layout.setContentsMargins(5, 5, 5, 5)
        search_panel_layout.setSpacing(5)

        # Search panel header with close button
        header_layout = QHBoxLayout()
        self.search_panel_label = QLabel("Search in Files")
        self.search_panel_label.setAlignment(Qt.AlignCenter)
        self.search_panel_label.setMaximumHeight(25)
        header_layout.addWidget(self.search_panel_label)

        close_search_button = QPushButton("×")
        close_search_button.setMaximumWidth(30)
        close_search_button.setMaximumHeight(25)
        close_search_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        close_search_button.setToolTip("Close search panel")
        close_search_button.clicked.connect(self.search_panel.hide)
        header_layout.addWidget(close_search_button)

        search_panel_layout.addLayout(header_layout)

        # Search input field
        search_input_layout = QHBoxLayout()
        search_input_label = QLabel("Search:")
        search_input_label.setMaximumWidth(60)
        search_input_layout.addWidget(search_input_label)

        self.search_input_field = QLineEdit()
        self.search_input_field.setPlaceholderText("Type to search (minimum 2 characters)...")
        self.search_input_field.setMinimumHeight(30)
        font = QFont("Consolas", 10)
        self.search_input_field.setFont(font)
        search_input_layout.addWidget(self.search_input_field)

        # File Types filter button
        self.file_types_button = QPushButton("File Types...")
        self.file_types_button.setMaximumWidth(100)
        self.file_types_button.setMinimumHeight(30)
        self.file_types_button.setToolTip("Select which file types to search")
        self.file_types_button.clicked.connect(self.configure_search_file_types)
        search_input_layout.addWidget(self.file_types_button)

        # Directories filter button
        self.directories_button = QPushButton("Directories...")
        self.directories_button.setMaximumWidth(100)
        self.directories_button.setMinimumHeight(30)
        self.directories_button.setToolTip("Select which directories to search")
        self.directories_button.clicked.connect(self.configure_search_directories)
        search_input_layout.addWidget(self.directories_button)

        # Cancel search button
        self.cancel_search_button = QPushButton("Cancel")
        self.cancel_search_button.setMaximumWidth(80)
        self.cancel_search_button.setMinimumHeight(30)
        self.cancel_search_button.setEnabled(False)  # Disabled until search starts
        self.cancel_search_button.clicked.connect(self.cancel_search)
        search_input_layout.addWidget(self.cancel_search_button)

        search_panel_layout.addLayout(search_input_layout)

        # Search status label
        self.search_status_label = QLabel("Type at least 2 characters to start searching...")
        self.search_status_label.setMinimumHeight(20)
        self.search_status_label.setStyleSheet("padding: 3px;")
        self.search_status_label.setAutoFillBackground(True)
        search_panel_layout.addWidget(self.search_status_label)

        # File scanning label (shows currently scanned file)
        self.file_scanning_label = QLabel("")
        self.file_scanning_label.setMinimumHeight(20)
        self.file_scanning_label.setStyleSheet("padding: 3px; font-style: italic;")
        self.file_scanning_label.setAutoFillBackground(True)
        self.file_scanning_label.setWordWrap(True)
        self.file_scanning_label.hide()  # Initially hidden
        search_panel_layout.addWidget(self.file_scanning_label)

        # Search results list
        self.search_results_list = QListWidget()
        self.search_results_list.setMinimumHeight(150)
        search_panel_layout.addWidget(self.search_results_list)

        # Info label
        info_label = QLabel("Double-click a result to open the file at that line")
        info_label.setStyleSheet("font-style: italic; color: #666;")
        search_panel_layout.addWidget(info_label)

        # Initially hide search panel
        self.search_panel.hide()

        # Store search results
        self.current_search_results = []

        # Connect search input signal
        self.search_input_field.textChanged.connect(self.on_search_input_changed)
        self.search_results_list.itemDoubleClicked.connect(self.on_search_result_double_clicked)

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

        view_menu.addSeparator()

        syntax_config_action = QAction("Configure Syntax Highlighting...", self)
        syntax_config_action.triggered.connect(self.configure_syntax_highlighting)
        view_menu.addAction(syntax_config_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_new_tab(self, file_path=None, content=""):
        """Create a new tab with a code editor"""
        theme = self.themes[self.current_theme]
        font = QFont(self.font_family, self.font_size)
        font.setStyleHint(QFont.Monospace)

        is_markdown = self.is_markdown_file(file_path)

        if is_markdown:
            tab_widget = MarkdownPreviewWidget(self, theme, font)
            editor = tab_widget.editor
            preview = tab_widget.preview
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

            highlighter_class = self.get_highlighter_for_file(file_path)
            highlighter = highlighter_class(editor.document(), theme)

            tab_widget = editor
            preview = None

        if not is_markdown:
            editor.update_line_number_area_width(0)

        # Set content before connecting change tracking so that loading a file
        # doesn't immediately flag the tab as modified.  Some PySide widgets
        # emit ``textChanged`` when text is programmatically inserted which
        # previously caused files to appear dirty as soon as they were opened
        # or focused.  Blocking the signal during the initial load ensures the
        # modified state is only toggled after the user makes an actual edit.
        if content:
            editor.blockSignals(True)
            editor.setPlainText(content)
            editor.blockSignals(False)

            # Reset the document's modified flag so that future edits are the
            # only changes that mark the tab as dirty.
            editor.document().setModified(False)
        else:
            editor.document().setModified(False)

        editor.textChanged.connect(lambda: self.on_text_changed(editor))

        if is_markdown:
            # Ensure the preview reflects the loaded content when signals were
            # blocked during ``setPlainText``.
            tab_widget.update_preview()

        # Determine tab title
        tab_title = os.path.basename(file_path) if file_path else "Untitled"

        # Add tab
        tab_index = self.tab_widget.addTab(tab_widget, tab_title)

        # Track the file
        file_info = {
            'path': file_path,
            'modified': False,
            'widget': tab_widget,
            'editor': editor,
            'is_markdown': is_markdown
        }

        if highlighter:
            file_info['highlighter'] = highlighter

        if preview:
            file_info['preview'] = preview

        self.open_files[tab_index] = file_info

        # Switch to new tab
        self.tab_widget.setCurrentIndex(tab_index)

        return tab_index

    def close_tab(self, index):
        """Close a tab with save confirmation if modified"""
        if index < 0 or index >= self.tab_widget.count():
            return

        editor = self.get_editor_by_index(index)
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
        self.open_files.pop(index, None)

        # Reindex open_files dictionary to match new tab order
        remaining_infos = self.open_files.copy()
        self.open_files = {}
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            matched_key = None
            for old_index, info in remaining_infos.items():
                if info.get('widget') is widget:
                    matched_key = old_index
                    break
            if matched_key is not None:
                self.open_files[i] = remaining_infos.pop(matched_key)

        # Create new tab if all tabs are closed
        if self.tab_widget.count() == 0:
            self.create_new_tab()

    def get_current_editor(self):
        """Get the current active editor widget"""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return None
        return self.get_editor_by_index(current_index)

    def get_editor_by_index(self, index):
        """Retrieve the editor widget for a given tab index."""
        if index < 0:
            return None
        file_info = self.open_files.get(index)
        if file_info and file_info.get('editor'):
            return file_info['editor']

        widget = self.tab_widget.widget(index)
        if isinstance(widget, CodeEditor):
            return widget
        if isinstance(widget, MarkdownPreviewWidget):
            return widget.editor
        return None

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

        # Load syntax highlighting mappings
        syntax_json = self.settings.value('syntax_mappings', '', type=str)
        if syntax_json:
            try:
                self.syntax_mappings = json.loads(syntax_json)
            except (json.JSONDecodeError, TypeError):
                self.syntax_mappings = self.default_syntax_mappings.copy()
        else:
            self.syntax_mappings = self.default_syntax_mappings.copy()

        # Load working directories (support both old single directory and new list format)
        working_dirs_json = self.settings.value('working_directories', '', type=str)
        if working_dirs_json:
            try:
                loaded_dirs = json.loads(working_dirs_json)
                # Validate that each directory still exists
                self.working_directories = [d for d in loaded_dirs if os.path.exists(d)]
            except (json.JSONDecodeError, TypeError):
                self.working_directories = []
        else:
            # Legacy support: try loading old single directory format
            working_dir = self.settings.value('working_directory', '', type=str)
            if working_dir and os.path.exists(working_dir):
                self.working_directories = [working_dir]
            else:
                self.working_directories = []

        # Only populate tree if file_tree widget exists
        if hasattr(self, 'file_tree'):
            self.populate_tree()

        # Load search file types
        search_types_json = self.settings.value('search_file_types', '', type=str)
        if search_types_json:
            try:
                self.search_file_types = set(json.loads(search_types_json))
            except (json.JSONDecodeError, TypeError):
                self.search_file_types = SearchWorker.SEARCHABLE_EXTENSIONS.copy()
        else:
            self.search_file_types = SearchWorker.SEARCHABLE_EXTENSIONS.copy()

        # Load searchable directories
        searchable_dirs_json = self.settings.value('searchable_directories', '', type=str)
        if searchable_dirs_json:
            try:
                loaded_searchable_dirs = json.loads(searchable_dirs_json)
                # Only keep directories that are still in working_directories
                self.searchable_directories = [d for d in loaded_searchable_dirs if d in self.working_directories]
            except (json.JSONDecodeError, TypeError):
                self.searchable_directories = self.working_directories.copy()
        else:
            # Default: all working directories are searchable
            self.searchable_directories = self.working_directories.copy()

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

        # Save syntax highlighting mappings
        syntax_json = json.dumps(self.syntax_mappings)
        self.settings.setValue('syntax_mappings', syntax_json)

        # Save working directories
        if self.working_directories:
            working_dirs_json = json.dumps(self.working_directories)
            self.settings.setValue('working_directories', working_dirs_json)

        # Save search file types
        search_types_json = json.dumps(list(self.search_file_types))
        self.settings.setValue('search_file_types', search_types_json)

        # Save searchable directories
        searchable_dirs_json = json.dumps(self.searchable_directories)
        self.settings.setValue('searchable_directories', searchable_dirs_json)

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
                content, encoding = self.read_file_with_encoding(file_path)
                self.create_new_tab(file_path, content)
                self.status_bar.showMessage(f"Opened: {file_path} (encoding: {encoding})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def open_file_from_path(self, file_path):
        """Open a file from a given path in a new tab or switch to existing tab"""
        if not file_path:
            return

        # Check if file is already open
        for tab_index, file_info in self.open_files.items():
            if file_info.get('path') == file_path:
                # File already open, switch to that tab
                self.tab_widget.setCurrentIndex(tab_index)
                self.status_bar.showMessage(f"Switched to: {file_path}")
                return

        # Open file in new tab
        try:
            content, encoding = self.read_file_with_encoding(file_path)
            # Close the default empty tab if it's still empty
            if self.tab_widget.count() == 1:
                first_editor = self.get_editor_by_index(0)
                file_info = self.open_files.get(0, {})
                if first_editor and not file_info.get('path') and not first_editor.toPlainText():
                    self.tab_widget.removeTab(0)
                    self.open_files.clear()
            self.create_new_tab(file_path, content)
            self.status_bar.showMessage(f"Opened: {file_path} (encoding: {encoding})")
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
        dialog = SearchDialog(self, "Find", "Enter text to find:")
        if dialog.exec() == QDialog.Accepted:
            text = dialog.get_text()
            if text:
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
            "multi-file live search, and adjustable font size.\n\n"
            "Shortcuts:\n"
            "Ctrl+N - New File\n"
            "Ctrl+O - Open File\n"
            "Ctrl+S - Save File\n"
            "Ctrl+F - Find\n"
            "F3 - Find Next\n"
            "Ctrl+Shift+F - Find in Files (Live Search)\n"
            "Ctrl++ - Increase Font Size\n"
            "Ctrl+- - Decrease Font Size\n\n"
            "Features:\n"
            "- Live search: Results appear as you type\n"
            "- Double-click results to open files\n"
            "- Right-click selected text to search in working directory"
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
            widget = self.tab_widget.widget(i)
            if isinstance(widget, MarkdownPreviewWidget):
                widget.apply_font(font)
            else:
                editor = self.get_editor_by_index(i)
                if editor:
                    editor.setFont(font)
                    editor.update_line_number_area_width(0)

    def configure_syntax_highlighting(self):
        """Open dialog to configure syntax highlighting mappings"""
        dialog = SyntaxConfigDialog(self, self.syntax_mappings)
        if dialog.exec() == QDialog.Accepted:
            new_mappings = dialog.get_mappings()
            if new_mappings:
                self.syntax_mappings = new_mappings
                self.save_settings()
                self.status_bar.showMessage("Syntax highlighting configuration updated")
                QMessageBox.information(self, "Configuration Updated",
                    "Syntax highlighting configuration has been saved.\n"
                    "New settings will apply to newly opened files.")

    def apply_theme(self, theme_name):
        """Apply a color theme to all editors"""
        if theme_name not in self.themes:
            QMessageBox.critical(self, "Error", f"Theme '{theme_name}' not found")
            return

        self.current_theme = theme_name
        theme = self.themes[theme_name]

        # Update all tabs
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            file_info = self.open_files.get(i, {})

            if isinstance(widget, MarkdownPreviewWidget):
                widget.apply_theme(theme)
            else:
                editor = self.get_editor_by_index(i)
                if editor:
                    palette = editor.palette()
                    palette.setColor(QPalette.Base, QColor(theme['bg']))
                    palette.setColor(QPalette.Text, QColor(theme['fg']))
                    editor.setPalette(palette)

                    line_palette = editor.line_number_area.palette()
                    line_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
                    line_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
                    editor.line_number_area.setPalette(line_palette)

                    editor.set_search_highlight_color(QColor(theme['search_bg']))

                    if 'highlighter' in file_info:
                        file_info['highlighter'].update_theme(theme)

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

        # Update search status label colors
        status_label_palette = self.search_status_label.palette()
        status_label_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
        status_label_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
        self.search_status_label.setPalette(status_label_palette)

        # Update file scanning label colors
        scanning_label_palette = self.file_scanning_label.palette()
        scanning_label_palette.setColor(QPalette.Window, QColor(theme['line_numbers_bg']))
        scanning_label_palette.setColor(QPalette.WindowText, QColor(theme['line_numbers_fg']))
        self.file_scanning_label.setPalette(scanning_label_palette)

        self.save_settings()
        self.status_bar.showMessage(f"Theme changed to: {theme_name}")

    def find_in_files(self):
        """Show docked search panel with live search"""
        # Use working directories if available, otherwise ask for directory
        if not self.working_directories:
            # Ask user to add a directory
            directory = QFileDialog.getExistingDirectory(self, "Add directory to workspace")
            if not directory:
                return
            self.working_directories.append(directory)
            self.populate_tree()
            self.save_settings()

        # Show the search panel
        self.search_panel.show()

        # Clear previous search and focus on input field
        self.search_input_field.clear()
        self.search_input_field.setFocus()
        self.search_results_list.clear()
        self.current_search_results = []
        self.search_status_label.setText("Type at least 2 characters to start searching...")

    def search_in_working_directory_for_text(self, text):
        """Search for given text in working directories using docked search panel"""
        if not self.working_directories:
            QMessageBox.warning(self, "No Working Directories",
                              "Please add directories to workspace first using File > Add Directory to Workspace")
            return

        if not text:
            return

        # Show the search panel and pre-fill search text
        self.search_panel.show()
        self.search_input_field.setText(text)  # Pre-fill the search text
        self.search_input_field.setFocus()

    def on_search_input_changed(self, text):
        """Handle search input change and perform live search"""
        if len(text) < 2:
            self.search_results_list.clear()
            self.current_search_results = []
            if len(text) == 0:
                self.search_status_label.setText("Type at least 2 characters to start searching...")
            else:
                self.search_status_label.setText(f"Type {2 - len(text)} more character(s)...")
            return

        # Perform search
        self.perform_live_search(text)

    def perform_live_search(self, text):
        """Perform live search in working directories using background thread"""
        if not self.working_directories:
            self.search_status_label.setText("No working directories set. Use File > Add Directory to Workspace")
            self.search_results_list.clear()
            self.current_search_results = []
            return

        # Use searchable_directories if set, otherwise use all working_directories
        directories_to_search = self.searchable_directories if self.searchable_directories else self.working_directories

        if not directories_to_search:
            self.search_status_label.setText("No directories selected for search. Use 'Directories...' button to select.")
            self.search_results_list.clear()
            self.current_search_results = []
            return

        # Cancel any existing search
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_worker.wait()

        # Clear previous results
        self.search_status_label.setText("Searching...")
        self.search_results_list.clear()
        self.current_search_results = []

        # Show file scanning label
        self.file_scanning_label.show()
        self.file_scanning_label.setText("Preparing to scan files...")

        # Enable cancel button
        self.cancel_search_button.setEnabled(True)

        # Create and start new search worker with filtered file types and selected directories
        self.search_worker = SearchWorker(directories_to_search, text, self.search_file_types)

        # Connect signals
        self.search_worker.result_found.connect(self.on_search_result_found)
        self.search_worker.progress_update.connect(self.on_search_progress_update)
        self.search_worker.search_finished.connect(self.on_search_finished)
        self.search_worker.file_scanning.connect(self.on_file_scanning)

        # Start the search in background
        self.search_worker.start()

    def cancel_search(self):
        """Cancel the current search operation"""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_status_label.setText("Search cancelled by user")
            self.cancel_search_button.setEnabled(False)
            self.file_scanning_label.hide()

    def configure_search_file_types(self):
        """Open dialog to configure which file types to search"""
        dialog = FileTypeFilterDialog(
            self,
            all_extensions=SearchWorker.SEARCHABLE_EXTENSIONS,
            selected_extensions=self.search_file_types
        )
        if dialog.exec() == QDialog.Accepted:
            new_selection = dialog.get_selected_extensions()
            if new_selection:
                self.search_file_types = new_selection
                self.save_settings()
                self.status_bar.showMessage(f"File type filter updated: {len(new_selection)} types selected")
            else:
                QMessageBox.warning(self, "No File Types Selected",
                                  "Please select at least one file type to search.")

    def configure_search_directories(self):
        """Open dialog to configure which directories to search"""
        if not self.working_directories:
            QMessageBox.information(self, "No Directories",
                                  "No directories in workspace. Add directories using File > Add Directory to Workspace")
            return

        dialog = DirectoryFilterDialog(
            self,
            all_directories=self.working_directories,
            selected_directories=self.searchable_directories
        )
        if dialog.exec() == QDialog.Accepted:
            new_selection = dialog.get_selected_directories()
            if new_selection:
                self.searchable_directories = new_selection
                self.save_settings()
                self.status_bar.showMessage(f"Directory filter updated: {len(new_selection)} directories selected")
            else:
                QMessageBox.warning(self, "No Directories Selected",
                                  "Please select at least one directory to search.")

    def on_search_result_found(self, file_path, line_num, line_text):
        """Handle individual search result from worker thread"""
        self.current_search_results.append((file_path, line_num, line_text))
        display_text = f"{file_path}:{line_num}: {line_text}"
        self.search_results_list.addItem(display_text)

    def on_search_progress_update(self, files_searched, matches_found):
        """Handle progress update from worker thread"""
        self.search_status_label.setText(
            f"Searching... Found {matches_found} matches in {files_searched} files"
        )

    def on_file_scanning(self, file_path):
        """Handle file scanning update from worker thread"""
        self.file_scanning_label.setText(f"Scanning: {file_path}")

    def on_search_finished(self, total_files, total_matches):
        """Handle search completion from worker thread"""
        self.cancel_search_button.setEnabled(False)

        # Hide file scanning label when search is complete
        self.file_scanning_label.hide()

        if total_matches == 0:
            dir_count = len(self.working_directories)
            dir_text = f"{dir_count} workspace {'directory' if dir_count == 1 else 'directories'}"
            self.search_status_label.setText(
                f"No matches found. Searched {total_files} files in {dir_text}"
            )
        elif total_matches >= 1000:
            self.search_status_label.setText(
                f"Found 1000+ matches (showing first 1000). Searched {total_files} files. Double-click to open."
            )
        else:
            self.search_status_label.setText(
                f"Found {total_matches} matches in {total_files} files. Double-click to open."
            )

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
                    editor.highlight_line(line_num)
                    self.status_bar.showMessage(f"Jumped to line {line_num} in {file_path}")
                return

        # Open file in new tab
        try:
            content, encoding = self.read_file_with_encoding(file_path)
            tab_index = self.create_new_tab(file_path, content)

            # Jump to line
            editor = self.get_current_editor()
            if editor:
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num - 1)
                editor.setTextCursor(cursor)
                editor.centerCursor()
                editor.highlight_line(line_num)

            self.status_bar.showMessage(f"Opened: {file_path} at line {line_num} (encoding: {encoding})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def add_directory_to_workspace(self):
        """Add a directory to the workspace"""
        directory = QFileDialog.getExistingDirectory(self, "Add Directory to Workspace")
        if directory:
            # Check if directory is already in workspace
            if directory in self.working_directories:
                self.status_bar.showMessage(f"Directory already in workspace: {directory}")
                return

            # Add directory to workspace
            self.working_directories.append(directory)
            # Automatically add to searchable directories
            self.searchable_directories.append(directory)
            self.populate_tree()
            self.save_settings()
            self.status_bar.showMessage(f"Added to workspace: {directory}")

    def remove_directory_from_workspace(self):
        """Remove a directory from the workspace"""
        if not self.working_directories:
            QMessageBox.information(self, "No Directories", "No directories in workspace to remove.")
            return

        # Show dialog to select which directory to remove
        from PySide6.QtWidgets import QInputDialog
        directory, ok = QInputDialog.getItem(
            self, "Remove Directory", "Select directory to remove:",
            self.working_directories, 0, False
        )

        if ok and directory:
            self.working_directories.remove(directory)
            # Also remove from searchable directories if present
            if directory in self.searchable_directories:
                self.searchable_directories.remove(directory)
            self.populate_tree()
            self.save_settings()
            self.status_bar.showMessage(f"Removed from workspace: {directory}")

    def populate_tree(self):
        """Populate the tree view with files and directories from all workspace directories"""
        self.file_tree.clear()

        if not self.working_directories:
            return

        # Add each working directory as a root node
        for working_dir in self.working_directories:
            if not os.path.exists(working_dir):
                continue

            # Add root directory
            root_name = os.path.basename(working_dir) or working_dir
            root_item = QTreeWidgetItem(self.file_tree, [root_name])
            root_item.setData(0, Qt.UserRole, working_dir)

            # Populate tree with lazy loading (only first level)
            self.add_tree_nodes(root_item, working_dir, lazy=True)
            root_item.setExpanded(True)

    def add_tree_nodes(self, parent_item, path, lazy=False):
        """Add nodes to the tree (with optional lazy loading)

        Args:
            parent_item: The parent tree widget item
            path: The directory path to scan
            lazy: If True, only load direct children (no recursion)
        """
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

                    # Add a dummy child to make the directory expandable
                    # The real children will be loaded when expanded
                    if lazy:
                        dummy = QTreeWidgetItem(tree_item, ["Loading..."])
                        dummy.setData(0, Qt.UserRole, None)  # Mark as dummy
                    else:
                        # Non-lazy mode: recursively load children
                        self.add_tree_nodes(tree_item, full_path, lazy=False)
                else:
                    # Add file
                    icon = self.get_file_icon(item)
                    tree_item = QTreeWidgetItem(parent_item, [f"{icon} {item}"])
                    tree_item.setData(0, Qt.UserRole, full_path)
        except PermissionError:
            pass

    def get_file_icon(self, file_name):
        """Return an emoji icon that reflects the file's type/version."""
        extension = os.path.splitext(file_name)[1].lower()
        icon_map = {
            ".cbl": "🧾",
            ".cob": "🧾",
            ".cobol": "🧾",
            ".py": "🐍",
            ".js": "🟨",
            ".ts": "🟦",
            ".json": "🧩",
            ".xml": "🧷",
            ".yml": "🗂️",
            ".yaml": "🗂️",
            ".cs": "♯",
            ".java": "☕",
            ".txt": "📄",
            ".md": "📝",
            ".html": "🌐",
            ".css": "🎨",
            ".sql": "🗃️",
            ".sh": "💻",
            ".bat": "💾",
            ".rb": "💎",
            ".go": "🐹",
        }
        return icon_map.get(extension, "📄")

    def on_tree_item_expanded(self, item):
        """Handle tree item expansion - load children on demand (lazy loading)"""
        dir_path = item.data(0, Qt.UserRole)

        # Skip if not a directory
        if not dir_path or not os.path.isdir(dir_path):
            return

        # Check if this directory already has real children loaded
        # If the first child is a dummy ("Loading..."), we need to load real children
        if item.childCount() > 0:
            first_child = item.child(0)
            # Check if it's a dummy item (has None as UserRole data)
            if first_child.data(0, Qt.UserRole) is None:
                # Remove all dummy children
                item.takeChildren()
                # Load real children with lazy loading enabled
                self.add_tree_nodes(item, dir_path, lazy=True)

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
                content, encoding = self.read_file_with_encoding(file_path)
                self.create_new_tab(file_path, content)
                self.status_bar.showMessage(f"Opened: {file_path} (encoding: {encoding})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")


def main():
    app = QApplication(sys.argv)

    # Parse command-line arguments for file to open
    file_to_open = None
    if len(sys.argv) > 1:
        file_to_open = sys.argv[1]
        # Check if file exists
        if not os.path.exists(file_to_open):
            print(f"Warning: File '{file_to_open}' does not exist")
            file_to_open = None
        elif not os.path.isfile(file_to_open):
            print(f"Warning: '{file_to_open}' is not a file")
            file_to_open = None

    editor = CobolEditor(file_to_open=file_to_open)
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
