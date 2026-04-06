"""Dialogi wyszukiwania"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QDialogButtonBox, QListWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


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
