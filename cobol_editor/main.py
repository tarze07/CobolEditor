"""Entry point dla aplikacji COBOL Editor"""

import sys
import os
from PySide6.QtWidgets import QApplication

from .core import CobolEditor


def parse_args():
    """Parse command line arguments"""
    file_to_open = None
    if len(sys.argv) > 1:
        file_to_open = sys.argv[1]
        if not os.path.exists(file_to_open):
            print(f"Warning: File '{file_to_open}' does not exist")
            file_to_open = None
        elif not os.path.isfile(file_to_open):
            print(f"Warning: '{file_to_open}' is not a file")
            file_to_open = None
    return file_to_open


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("COBOL Editor")
    app.setApplicationVersion("2.0.0")
    
    file_to_open = parse_args()
    editor = CobolEditor(file_to_open=file_to_open)
    editor.show()
    
    sys.exit(app.exec())
