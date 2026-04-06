"""Dodatkowe dialogi UI"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QDialogButtonBox, QFormLayout, QComboBox,
    QListWidget, QHBoxLayout, QPushButton
)


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


class DirectorySelectionDialog(QDialog):
    """Dialog for selecting a directory from list"""
    
    def __init__(self, parent=None, directories=None):
        super().__init__(parent)
        self.setWindowTitle("Remove Directory from Workspace")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self.directories = directories or []
        self.selected_directory = None
        
        layout = QVBoxLayout(self)
        
        # Description
        desc = QLabel("Select directory to remove:")
        desc.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(desc)
        
        # List widget
        self.list_widget = QListWidget()
        for directory in self.directories:
            self.list_widget.addItem(directory)
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.on_remove)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Double click to select
        self.list_widget.itemDoubleClicked.connect(self.on_remove)
    
    def on_remove(self):
        """Handle remove button"""
        current = self.list_widget.currentItem()
        if current:
            self.selected_directory = current.text()
            self.accept()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Select Directory", "Please select a directory to remove.")
    
    def get_selected_directory(self):
        """Get selected directory"""
        return self.selected_directory
