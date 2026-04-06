"""Zarządzanie workspace i drzewem katalogów"""

import os
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt

from ..config.constants import SKIP_DIRS


class Workspace:
    """Zarządzanie katalogami roboczymi i drzewem plików"""
    
    def __init__(self):
        self.directories = []
        self._file_manager = None
    
    def set_file_manager(self, file_manager):
        """Ustaw referencję do file managera (do ikon)"""
        self._file_manager = file_manager
    
    def add_directory(self, path):
        """Dodaj katalog do workspace"""
        if path and os.path.isdir(path) and path not in self.directories:
            self.directories.append(path)
            return True
        return False
    
    def remove_directory(self, path):
        """Usuń katalog z workspace"""
        if path in self.directories:
            self.directories.remove(path)
            return True
        return False
    
    def get_directories(self):
        """Pobierz listę katalogów"""
        return self.directories.copy()
    
    def clear(self):
        """Wyczyść wszystkie katalogi"""
        self.directories.clear()
    
    def get_all_files(self, extensions=None):
        """
        Pobierz wszystkie pliki ze wszystkich katalogów.
        
        Args:
            extensions: Opcjonalny set rozszerzeń do filtrowania
        
        Returns:
            Lista ścieżek do plików
        """
        files = []
        for directory in self.directories:
            if os.path.exists(directory):
                for root, dirs, filenames in os.walk(directory):
                    # Skip unwanted directories
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if extensions is None or self._matches_extension(filename, extensions):
                            files.append(file_path)
        return files
    
    def _matches_extension(self, filename, extensions):
        """Sprawdź czy plik pasuje do podanych rozszerzeń"""
        _, ext = os.path.splitext(filename.lower())
        return ext in extensions
    
    def populate_tree(self, tree_widget, on_expand=None):
        """
        Wypełnij drzewo plików.
        
        Args:
            tree_widget: QTreeWidget do wypełnienia
            on_expand: Callback przy rozwijaniu (opcjonalny)
        """
        tree_widget.clear()
        
        if not self.directories:
            item = QTreeWidgetItem(tree_widget)
            item.setText(0, "No workspace directories")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            return
        
        for directory in self.directories:
            if not os.path.exists(directory):
                continue
            
            # Create root item for this directory
            dir_name = os.path.basename(directory) or directory
            root_item = QTreeWidgetItem(tree_widget)
            root_item.setText(0, f"📁 {dir_name}")
            root_item.setData(0, Qt.UserRole, directory)
            root_item.setExpanded(True)
            
            # Add children with lazy loading
            self.add_tree_nodes(root_item, directory, lazy=True)
        
        # Connect expand handler if provided
        if on_expand:
            tree_widget.itemExpanded.connect(on_expand)
    
    def add_tree_nodes(self, parent_item, path, lazy=False):
        """
        Dodaj węzły do drzewa.
        
        Args:
            parent_item: Rodzic QTreeWidgetItem
            path: Ścieżka katalogu
            lazy: Jeśli True, dodaje dummy item do załadowania później
        """
        try:
            entries = os.listdir(path)
        except (PermissionError, OSError):
            return
        
        # Sort: directories first, then files
        dirs = []
        files = []
        
        for entry in entries:
            # Skip hidden files/dirs
            if entry.startswith('.'):
                continue
            
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                if entry not in SKIP_DIRS:
                    dirs.append((entry, full_path))
            else:
                files.append((entry, full_path))
        
        dirs.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())
        
        # Add directories
        for name, full_path in dirs:
            child = QTreeWidgetItem(parent_item)
            child.setText(0, f"📁 {name}")
            child.setData(0, Qt.UserRole, full_path)
            
            if lazy:
                # Add dummy child to show expand arrow
                dummy = QTreeWidgetItem(child)
                dummy.setText(0, "Loading...")
                dummy.setData(0, Qt.UserRole, None)
            else:
                self.add_tree_nodes(child, full_path, lazy=True)
        
        # Add files
        for name, full_path in files:
            child = QTreeWidgetItem(parent_item)
            icon = "📄"
            if self._file_manager:
                icon = self._file_manager.get_file_icon(name)
            child.setText(0, f"{icon} {name}")
            child.setData(0, Qt.UserRole, full_path)
    
    def load_children_on_expand(self, item):
        """Załaduj dzieci przy rozwijaniu (lazy loading)"""
        dir_path = item.data(0, Qt.UserRole)
        
        # Skip if not a directory
        if not dir_path or not os.path.isdir(dir_path):
            return
        
        # Check if this directory already has real children loaded
        if item.childCount() > 0:
            first_child = item.child(0)
            # Check if it's a dummy item
            if first_child.data(0, Qt.UserRole) is None:
                # Remove all dummy children
                item.takeChildren()
                # Load real children
                self.add_tree_nodes(item, dir_path, lazy=True)
