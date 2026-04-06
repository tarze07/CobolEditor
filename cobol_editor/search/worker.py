"""Wątek wyszukiwania w tle"""

import os
from PySide6.QtCore import QThread, Signal

from ..config.constants import SKIP_DIRS, MAX_SEARCH_RESULTS, MAX_FILE_SIZE_MB, BATCH_SIZE


class SearchWorker(QThread):
    """Worker thread for performing file searches without blocking UI"""
    
    # Signals
    result_found = Signal(str, int, str)  # file_path, line_num, line_text
    progress_update = Signal(int, int)    # files_searched, matches_found
    search_finished = Signal(int, int)    # total_files, total_matches
    file_scanning = Signal(str)           # current_file_path being scanned
    
    def __init__(self, working_directories, search_text, searchable_extensions=None):
        super().__init__()
        # Support both single directory (string) and multiple directories (list)
        if isinstance(working_directories, str):
            self.working_directories = [working_directories]
        else:
            self.working_directories = working_directories if working_directories else []
        self.search_text = search_text.lower()
        self.cancelled = False
        self.max_results = MAX_SEARCH_RESULTS
        # Use provided extensions or default to class variable
        from ..config.constants import SEARCHABLE_EXTENSIONS
        self.searchable_extensions = searchable_extensions if searchable_extensions is not None else SEARCHABLE_EXTENSIONS
    
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
        batch_size = BATCH_SIZE  # Emit results in batches for better UI performance
        max_file_size = MAX_FILE_SIZE_MB * 1024 * 1024
        
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
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
                    
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
                            # Skip large files
                            if os.path.getsize(file_path) > max_file_size:
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
