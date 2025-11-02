#!/usr/bin/env python3
"""
COBOL Editor with Syntax Highlighting and Search
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import re
import os


class CobolEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("COBOL Editor")
        self.root.geometry("900x700")

        self.current_file = None
        self.search_index = "1.0"

        # Create menu bar
        self.create_menu()

        # Create line numbers
        self.line_numbers = tk.Text(root, width=4, padx=3, takefocus=0,
                                     border=0, background='lightgray',
                                     state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Create scrollbar
        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create text widget
        self.text_area = tk.Text(root, wrap=tk.NONE, undo=True,
                                  yscrollcommand=scrollbar.set,
                                  font=('Courier New', 11))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        # Bind events
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<Control-f>', lambda e: self.find_text())
        self.text_area.bind('<Control-s>', lambda e: self.save_file())
        self.text_area.bind('<Control-o>', lambda e: self.open_file())
        self.text_area.bind('<Control-n>', lambda e: self.new_file())

        # Configure tags for syntax highlighting
        self.configure_tags()

        # Status bar
        self.status_bar = tk.Label(root, text="Ready", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_editor)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Find Next", command=self.find_next, accelerator="F3")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def configure_tags(self):
        """Configure text tags for COBOL syntax highlighting"""
        # Keywords
        self.text_area.tag_config('keyword', foreground='#0000FF', font=('Courier New', 11, 'bold'))
        # Data types
        self.text_area.tag_config('datatype', foreground='#008080', font=('Courier New', 11, 'bold'))
        # Strings
        self.text_area.tag_config('string', foreground='#A31515')
        # Comments
        self.text_area.tag_config('comment', foreground='#008000', font=('Courier New', 11, 'italic'))
        # Numbers
        self.text_area.tag_config('number', foreground='#098658')
        # Division headers
        self.text_area.tag_config('division', foreground='#AF00DB', font=('Courier New', 11, 'bold'))
        # Section headers
        self.text_area.tag_config('section', foreground='#AF00DB', font=('Courier New', 11))
        # Search highlight
        self.text_area.tag_config('search', background='yellow')

    def get_cobol_patterns(self):
        """Return regex patterns for COBOL syntax"""
        return {
            'division': r'\b(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION\b',
            'section': r'\b(CONFIGURATION|INPUT-OUTPUT|FILE|WORKING-STORAGE|LINKAGE|LOCAL-STORAGE)\s+SECTION\b',
            'keyword': r'\b(ACCEPT|ACCESS|ADD|ADDRESS|ADVANCING|AFTER|ALL|ALPHABET|ALPHABETIC|'
                      r'ALPHABETIC-LOWER|ALPHABETIC-UPPER|ALPHANUMERIC|ALPHANUMERIC-EDITED|'
                      r'ALSO|ALTER|ALTERNATE|AND|ANY|ARE|AREA|AREAS|ASCENDING|ASSIGN|AT|'
                      r'AUTHOR|BEFORE|BINARY|BLANK|BLOCK|BOTTOM|BY|CALL|CANCEL|CD|CF|CH|'
                      r'CHARACTER|CHARACTERS|CLASS|CLOCK-UNITS|CLOSE|COBOL|CODE|CODE-SET|'
                      r'COLLATING|COLUMN|COMMA|COMMON|COMMUNICATION|COMP|COMPUTE|'
                      r'COMPUTATIONAL|CONFIGURATION|CONTAINS|CONTENT|CONTINUE|CONTROL|'
                      r'CONTROLS|CONVERTING|COPY|CORR|CORRESPONDING|COUNT|CURRENCY|DATE|'
                      r'DATE-COMPILED|DATE-WRITTEN|DAY|DAY-OF-WEEK|DE|DEBUG-CONTENTS|'
                      r'DEBUG-ITEM|DEBUG-LINE|DEBUG-NAME|DEBUG-SUB-1|DEBUG-SUB-2|'
                      r'DEBUG-SUB-3|DEBUGGING|DECIMAL-POINT|DECLARATIVES|DELETE|DELIMITED|'
                      r'DELIMITER|DEPENDING|DESCENDING|DESTINATION|DETAIL|DISABLE|DISPLAY|'
                      r'DIVIDE|DOWN|DUPLICATES|DYNAMIC|EGI|ELSE|EMI|ENABLE|END|END-ADD|'
                      r'END-CALL|END-COMPUTE|END-DELETE|END-DIVIDE|END-EVALUATE|END-IF|'
                      r'END-MULTIPLY|END-OF-PAGE|END-PERFORM|END-READ|END-RECEIVE|'
                      r'END-RETURN|END-REWRITE|END-SEARCH|END-START|END-STRING|END-SUBTRACT|'
                      r'END-UNSTRING|END-WRITE|ENTER|ENTRY|ENVIRONMENT|EOP|EQUAL|ERROR|ESI|'
                      r'EVALUATE|EVERY|EXCEPTION|EXIT|EXTEND|EXTERNAL|FALSE|FD|FILE|'
                      r'FILE-CONTROL|FILLER|FINAL|FIRST|FOOTING|FOR|FROM|FUNCTION|GENERATE|'
                      r'GIVING|GLOBAL|GO|GOBACK|GREATER|GROUP|HEADING|HIGH-VALUE|HIGH-VALUES|'
                      r'I-O|I-O-CONTROL|IF|IN|INDEX|INDEXED|INDICATE|INITIAL|INITIALIZE|'
                      r'INITIATE|INPUT|INPUT-OUTPUT|INSPECT|INSTALLATION|INTO|INVALID|IS|'
                      r'JUST|JUSTIFIED|KEY|LABEL|LAST|LEADING|LEFT|LENGTH|LESS|LIMIT|LIMITS|'
                      r'LINAGE|LINAGE-COUNTER|LINE|LINE-COUNTER|LINES|LINKAGE|LOCK|'
                      r'LOW-VALUE|LOW-VALUES|MEMORY|MERGE|MESSAGE|MODE|MODULES|MOVE|MULTIPLE|'
                      r'MULTIPLY|NATIVE|NEGATIVE|NEXT|NO|NOT|NUMBER|NUMERIC|NUMERIC-EDITED|'
                      r'OBJECT-COMPUTER|OCCURS|OF|OFF|OMITTED|ON|OPEN|OPTIONAL|OR|ORDER|'
                      r'ORGANIZATION|OTHER|OUTPUT|OVERFLOW|PACKED-DECIMAL|PADDING|PAGE|'
                      r'PAGE-COUNTER|PERFORM|PF|PH|PICTURE|PIC|PLUS|POINTER|POSITION|POSITIVE|'
                      r'PRINTING|PROCEDURE|PROCEDURES|PROCEED|PROGRAM|PROGRAM-ID|PURGE|QUEUE|'
                      r'QUOTE|QUOTES|RANDOM|RD|READ|RECEIVE|RECORD|RECORDS|REDEFINES|REEL|'
                      r'REFERENCE|REFERENCES|RELATIVE|RELEASE|REMAINDER|REMOVAL|RENAMES|'
                      r'REPLACE|REPLACING|REPORT|REPORTING|REPORTS|RERUN|RESERVE|RESET|'
                      r'RETURN|REVERSED|REWIND|REWRITE|RF|RH|RIGHT|ROUNDED|RUN|SAME|SD|'
                      r'SEARCH|SECTION|SECURITY|SEGMENT|SEGMENT-LIMIT|SELECT|SEND|SENTENCE|'
                      r'SEPARATE|SEQUENCE|SEQUENTIAL|SET|SIGN|SIZE|SORT|SORT-MERGE|SOURCE|'
                      r'SOURCE-COMPUTER|SPACE|SPACES|SPECIAL-NAMES|STANDARD|STANDARD-1|'
                      r'STANDARD-2|START|STATUS|STOP|STRING|SUB-QUEUE-1|SUB-QUEUE-2|'
                      r'SUB-QUEUE-3|SUBTRACT|SUM|SUPPRESS|SYMBOLIC|SYNC|SYNCHRONIZED|TABLE|'
                      r'TALLYING|TAPE|TERMINAL|TERMINATE|TEST|TEXT|THAN|THEN|THROUGH|THRU|'
                      r'TIME|TIMES|TO|TOP|TRAILING|TRUE|TYPE|UNIT|UNSTRING|UNTIL|UP|UPON|'
                      r'USAGE|USE|USING|VALUE|VALUES|VARYING|WHEN|WITH|WORDS|'
                      r'WORKING-STORAGE|WRITE|ZERO|ZEROES|ZEROS)\b',
            'datatype': r'\bPIC\s+[X9A\(\)V\-\+\*\$\,\.ZS]+\b',
            'comment': r'^\s*\*.*$',
            'string': r'["\']([^"\']*)["\']',
            'number': r'\b\d+(\.\d+)?\b'
        }

    def highlight_syntax(self):
        """Apply syntax highlighting to the entire text"""
        # Remove all existing tags
        for tag in ['keyword', 'datatype', 'string', 'comment', 'number', 'division', 'section']:
            self.text_area.tag_remove(tag, '1.0', 'end')

        content = self.text_area.get('1.0', 'end')
        patterns = self.get_cobol_patterns()

        # Apply syntax highlighting for each pattern type
        for tag_name, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                start_index = f"1.0 + {match.start()} chars"
                end_index = f"1.0 + {match.end()} chars"
                self.text_area.tag_add(tag_name, start_index, end_index)

        # Update line numbers
        self.update_line_numbers()

    def update_line_numbers(self):
        """Update line numbers display"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')

        line_count = int(self.text_area.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')

    def on_key_release(self, event=None):
        """Handle key release events for syntax highlighting"""
        self.highlight_syntax()

    def new_file(self):
        """Create a new file"""
        if self.text_area.get('1.0', 'end-1c'):
            if messagebox.askyesno("New File", "Discard current changes?"):
                self.text_area.delete('1.0', 'end')
                self.current_file = None
                self.root.title("COBOL Editor - New File")
        else:
            self.text_area.delete('1.0', 'end')
            self.current_file = None
            self.root.title("COBOL Editor - New File")

    def open_file(self):
        """Open a file"""
        file_path = filedialog.askopenfilename(
            defaultextension=".cbl",
            filetypes=[("COBOL Files", "*.cbl *.cob *.cobol"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_area.delete('1.0', 'end')
                    self.text_area.insert('1.0', content)
                    self.current_file = file_path
                    self.root.title(f"COBOL Editor - {os.path.basename(file_path)}")
                    self.highlight_syntax()
                    self.status_bar.config(text=f"Opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.text_area.get('1.0', 'end-1c')
                with open(self.current_file, 'w') as file:
                    file.write(content)
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save the file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cbl",
            filetypes=[("COBOL Files", "*.cbl"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                content = self.text_area.get('1.0', 'end-1c')
                with open(file_path, 'w') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"COBOL Editor - {os.path.basename(file_path)}")
                self.status_bar.config(text=f"Saved as: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def find_text(self):
        """Open find dialog"""
        self.search_text = simpledialog.askstring("Find", "Enter text to find:")
        if self.search_text:
            self.search_index = "1.0"
            self.find_next()

    def find_next(self):
        """Find next occurrence of search text"""
        if not hasattr(self, 'search_text') or not self.search_text:
            self.find_text()
            return

        # Remove previous search highlights
        self.text_area.tag_remove('search', '1.0', 'end')

        # Search for text
        pos = self.text_area.search(self.search_text, self.search_index,
                                     stopindex='end', nocase=True)

        if pos:
            # Highlight found text
            end_pos = f"{pos}+{len(self.search_text)}c"
            self.text_area.tag_add('search', pos, end_pos)
            self.text_area.see(pos)
            self.text_area.mark_set('insert', pos)
            self.search_index = end_pos
            self.status_bar.config(text=f"Found: {self.search_text} at {pos}")
        else:
            # Wrap around to beginning
            self.search_index = "1.0"
            pos = self.text_area.search(self.search_text, self.search_index,
                                        stopindex='end', nocase=True)
            if pos:
                end_pos = f"{pos}+{len(self.search_text)}c"
                self.text_area.tag_add('search', pos, end_pos)
                self.text_area.see(pos)
                self.text_area.mark_set('insert', pos)
                self.search_index = end_pos
                self.status_bar.config(text=f"Found: {self.search_text} at {pos} (wrapped)")
            else:
                messagebox.showinfo("Find", f"Text '{self.search_text}' not found")

    def select_all(self):
        """Select all text"""
        self.text_area.tag_add('sel', '1.0', 'end')

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
                           "COBOL Editor\n\n"
                           "A simple COBOL editor with syntax highlighting and search.\n\n"
                           "Shortcuts:\n"
                           "Ctrl+N - New File\n"
                           "Ctrl+O - Open File\n"
                           "Ctrl+S - Save File\n"
                           "Ctrl+F - Find\n"
                           "F3 - Find Next")

    def exit_editor(self):
        """Exit the editor"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()


def main():
    root = tk.Tk()
    editor = CobolEditor(root)

    # Bind F3 for Find Next
    root.bind('<F3>', lambda e: editor.find_next())

    root.mainloop()


if __name__ == "__main__":
    main()
