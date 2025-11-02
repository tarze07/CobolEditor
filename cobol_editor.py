#!/usr/bin/env python3
"""
COBOL Editor with Syntax Highlighting and Search
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import re
import os


class CobolEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("COBOL Editor")
        self.root.geometry("900x700")

        self.current_file = None
        self.working_directory = None
        self.search_index = "1.0"
        self.font_size = 11  # Default font size
        self.font_family = 'Courier New'
        self.current_theme = 'Light'  # Default theme

        # Initialize ttk style for ttk themes
        self.style = ttk.Style()
        self.current_ttk_theme = self.style.theme_use()  # Get current ttk theme

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

        # Create menu bar
        self.create_menu()

        # Create directory tree view
        theme = self.themes[self.current_theme]
        self.tree_frame = tk.Frame(root, width=200, bg=theme['line_numbers_bg'])
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.tree_frame.pack_propagate(False)  # Maintain fixed width

        # Add tree label
        self.tree_label = tk.Label(self.tree_frame, text="Workspace",
                                   bg=theme['line_numbers_bg'],
                                   fg=theme['line_numbers_fg'],
                                   font=(self.font_family, 9, 'bold'))
        self.tree_label.pack(side=tk.TOP, fill=tk.X, pady=2)

        # Create tree view with scrollbar
        tree_scroll_frame = tk.Frame(self.tree_frame, bg=theme['line_numbers_bg'])
        tree_scroll_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tree_scrollbar = tk.Scrollbar(tree_scroll_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_tree = ttk.Treeview(tree_scroll_frame, yscrollcommand=tree_scrollbar.set)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.config(command=self.file_tree.yview)

        # Bind tree events
        self.file_tree.bind('<Double-Button-1>', self.on_tree_double_click)

        # Create line numbers
        self.line_numbers = tk.Text(root, width=4, padx=3, takefocus=0,
                                     border=0, background=theme['line_numbers_bg'],
                                     foreground=theme['line_numbers_fg'],
                                     state='disabled', wrap='none',
                                     font=(self.font_family, self.font_size))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Create scrollbar
        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create text widget
        self.text_area = tk.Text(root, wrap=tk.NONE, undo=True,
                                  yscrollcommand=scrollbar.set,
                                  font=(self.font_family, self.font_size),
                                  background=theme['bg'],
                                  foreground=theme['fg'],
                                  insertbackground=theme['fg'])
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        # Bind events
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<Control-f>', lambda e: self.find_text())
        self.text_area.bind('<Control-s>', lambda e: self.save_file())
        self.text_area.bind('<Control-o>', lambda e: self.open_file())
        self.text_area.bind('<Control-n>', lambda e: self.new_file())
        self.text_area.bind('<Control-plus>', lambda e: (self.increase_font_size(), "break")[1])
        self.text_area.bind('<Control-equal>', lambda e: (self.increase_font_size(), "break")[1])  # Ctrl+= (same as Ctrl++)
        self.text_area.bind('<Control-minus>', lambda e: (self.decrease_font_size(), "break")[1])

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
        file_menu.add_command(label="Select Working Directory...", command=self.select_working_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_editor)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Find Next", command=self.find_next, accelerator="F3")
        edit_menu.add_command(label="Find in Files...", command=self.find_in_files, accelerator="Ctrl+Shift+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)

        # Theme submenu (color schemes)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Color Theme", menu=theme_menu)
        theme_menu.add_command(label="Light", command=lambda: self.apply_theme('Light'))
        theme_menu.add_command(label="Dark", command=lambda: self.apply_theme('Dark'))
        theme_menu.add_command(label="High Contrast", command=lambda: self.apply_theme('High Contrast'))
        theme_menu.add_command(label="Monokai", command=lambda: self.apply_theme('Monokai'))

        # TTK Theme submenu (widget styles)
        ttk_theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="TTK Theme", menu=ttk_theme_menu)

        # Add available ttk themes dynamically
        available_themes = self.style.theme_names()
        for theme in sorted(available_themes):
            ttk_theme_menu.add_command(label=theme.capitalize(),
                                      command=lambda t=theme: self.apply_ttk_theme(t))

        view_menu.add_separator()
        view_menu.add_command(label="Increase Font Size", command=self.increase_font_size, accelerator="Ctrl++")
        view_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Font Size", command=self.reset_font_size)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def configure_tags(self):
        """Configure text tags for COBOL syntax highlighting"""
        theme = self.themes[self.current_theme]

        # Keywords
        self.text_area.tag_config('keyword', foreground=theme['keyword'],
                                  font=(self.font_family, self.font_size, 'bold'))
        # Data types
        self.text_area.tag_config('datatype', foreground=theme['datatype'],
                                  font=(self.font_family, self.font_size, 'bold'))
        # Strings
        self.text_area.tag_config('string', foreground=theme['string'])
        # Comments
        self.text_area.tag_config('comment', foreground=theme['comment'],
                                  font=(self.font_family, self.font_size, 'italic'))
        # Numbers
        self.text_area.tag_config('number', foreground=theme['number'])
        # Division headers
        self.text_area.tag_config('division', foreground=theme['division'],
                                  font=(self.font_family, self.font_size, 'bold'))
        # Section headers
        self.text_area.tag_config('section', foreground=theme['section'],
                                  font=(self.font_family, self.font_size))
        # Search highlight
        self.text_area.tag_config('search', background=theme['search_bg'],
                                  foreground=theme['search_fg'])

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
                           "Ctrl+- - Decrease Font Size")

    def increase_font_size(self):
        """Increase font size"""
        if self.font_size < 72:  # Maximum font size
            self.font_size += 2
            self.update_font()
            self.status_bar.config(text=f"Font size: {self.font_size}")

    def decrease_font_size(self):
        """Decrease font size"""
        if self.font_size > 6:  # Minimum font size
            self.font_size -= 2
            self.update_font()
            self.status_bar.config(text=f"Font size: {self.font_size}")

    def reset_font_size(self):
        """Reset font size to default"""
        self.font_size = 11
        self.update_font()
        self.status_bar.config(text=f"Font size reset to: {self.font_size}")

    def update_font(self):
        """Update font for all text widgets"""
        # Update main text area font
        self.text_area.config(font=(self.font_family, self.font_size))
        # Update line numbers font
        self.line_numbers.config(font=(self.font_family, self.font_size))
        # Reconfigure tags with new font size
        self.configure_tags()
        # Reapply syntax highlighting
        self.highlight_syntax()

    def apply_theme(self, theme_name):
        """Apply a color theme to the editor"""
        if theme_name not in self.themes:
            messagebox.showerror("Error", f"Theme '{theme_name}' not found")
            return

        self.current_theme = theme_name
        theme = self.themes[theme_name]

        # Update text area colors
        self.text_area.config(
            background=theme['bg'],
            foreground=theme['fg'],
            insertbackground=theme['fg']
        )

        # Update line numbers colors
        self.line_numbers.config(
            background=theme['line_numbers_bg'],
            foreground=theme['line_numbers_fg']
        )

        # Update tree frame colors
        self.tree_frame.config(bg=theme['line_numbers_bg'])
        self.tree_label.config(
            bg=theme['line_numbers_bg'],
            fg=theme['line_numbers_fg']
        )

        # Reconfigure tags with new theme colors
        self.configure_tags()

        # Reapply syntax highlighting to update colors
        self.highlight_syntax()

        # Update status bar
        self.status_bar.config(text=f"Theme changed to: {theme_name}")

    def apply_ttk_theme(self, theme_name):
        """Apply a ttk theme to the editor widgets"""
        try:
            self.style.theme_use(theme_name)
            self.current_ttk_theme = theme_name
            self.status_bar.config(text=f"TTK Theme changed to: {theme_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply TTK theme '{theme_name}':\n{str(e)}")

    def find_in_files(self):
        """Open multi-file search dialog"""
        # Ask for directory
        directory = filedialog.askdirectory(title="Select directory to search in")
        if not directory:
            return

        # Ask for search text
        search_text = simpledialog.askstring("Find in Files", "Enter text to find:")
        if not search_text:
            return

        # Search in files
        results = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.cbl', '.cob', '.cobol')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if search_text.lower() in line.lower():
                                    results.append((file_path, line_num, line.strip()))
                    except Exception as e:
                        continue

        # Display results
        if results:
            self.show_search_results(search_text, results)
        else:
            messagebox.showinfo("Find in Files", f"No matches found for '{search_text}'")

    def show_search_results(self, search_text, results):
        """Show search results in a new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results: '{search_text}' ({len(results)} matches)")
        results_window.geometry("800x500")

        # Create frame for results
        frame = tk.Frame(results_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create listbox for results
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=(self.font_family, 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Add results to listbox
        for file_path, line_num, line_text in results:
            display_text = f"{file_path}:{line_num}: {line_text}"
            listbox.insert(tk.END, display_text)

        # Bind double-click to open file
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                file_path, line_num, _ = results[index]
                self.open_file_at_line(file_path, line_num)
                results_window.destroy()

        listbox.bind('<Double-Button-1>', on_double_click)

        # Add status label
        status_label = tk.Label(results_window, text=f"Found {len(results)} matches. Double-click to open file.",
                               anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def open_file_at_line(self, file_path, line_num):
        """Open a file and jump to specific line"""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_area.delete('1.0', 'end')
                self.text_area.insert('1.0', content)
                self.current_file = file_path
                self.root.title(f"COBOL Editor - {os.path.basename(file_path)}")
                self.highlight_syntax()

                # Jump to line
                self.text_area.mark_set('insert', f"{line_num}.0")
                self.text_area.see(f"{line_num}.0")

                self.status_bar.config(text=f"Opened: {file_path} at line {line_num}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def select_working_directory(self):
        """Select a working directory to browse"""
        directory = filedialog.askdirectory(title="Select Working Directory")
        if directory:
            self.working_directory = directory
            self.populate_tree()
            self.status_bar.config(text=f"Working directory: {directory}")

    def populate_tree(self):
        """Populate the tree view with files and directories"""
        # Clear existing items
        self.file_tree.delete(*self.file_tree.get_children())

        if not self.working_directory or not os.path.exists(self.working_directory):
            return

        # Add root directory
        root_name = os.path.basename(self.working_directory) or self.working_directory
        root_node = self.file_tree.insert('', 'end', text=root_name,
                                          values=[self.working_directory], open=True)

        # Populate tree recursively
        self.add_tree_nodes(root_node, self.working_directory)

    def add_tree_nodes(self, parent, path):
        """Recursively add nodes to the tree"""
        try:
            items = os.listdir(path)
            # Sort: directories first, then files
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))

            for item in items:
                # Skip hidden files and directories
                if item.startswith('.'):
                    continue

                full_path = os.path.join(path, item)

                if os.path.isdir(full_path):
                    # Add directory
                    node = self.file_tree.insert(parent, 'end', text=f"📁 {item}",
                                                values=[full_path])
                    # Add subdirectories and files
                    self.add_tree_nodes(node, full_path)
                else:
                    # Add file with appropriate icon
                    if item.endswith(('.cbl', '.cob', '.cobol')):
                        icon = "📄"
                    else:
                        icon = "📋"
                    self.file_tree.insert(parent, 'end', text=f"{icon} {item}",
                                        values=[full_path])
        except PermissionError:
            # Skip directories we don't have permission to read
            pass

    def on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        item = self.file_tree.selection()
        if item:
            values = self.file_tree.item(item[0], 'values')
            if values:
                file_path = values[0]
                if os.path.isfile(file_path):
                    # Open the file
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

    def exit_editor(self):
        """Exit the editor"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()


def main():
    root = tk.Tk()
    editor = CobolEditor(root)

    # Bind F3 for Find Next
    root.bind('<F3>', lambda e: editor.find_next())

    # Bind Ctrl+Shift+F for Find in Files
    root.bind('<Control-Shift-F>', lambda e: editor.find_in_files())

    root.mainloop()


if __name__ == "__main__":
    main()
