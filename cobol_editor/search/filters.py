"""Dialogi filtrowania dla wyszukiwania"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox, 
    QDialogButtonBox, QHBoxLayout, QPushButton,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt


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
