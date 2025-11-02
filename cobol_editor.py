#!/usr/bin/env python3
"""
COBOL Editor with Syntax Highlighting and Search
Kivy version
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton, ActionGroup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import re
import os


class CobolTextInput(TextInput):
    """Custom TextInput widget for COBOL code editing with syntax highlighting"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'RobotoMono-Regular'
        self.font_size = 18
        self.multiline = True
        self.do_wrap = False
        self.background_color = [1, 1, 1, 1]
        self.foreground_color = [0, 0, 0, 1]
        self.cursor_color = [0, 0, 0, 1]

    def insert_text(self, substring, from_undo=False):
        """Override to trigger syntax highlighting after text insertion"""
        result = super().insert_text(substring, from_undo)
        return result


class LineNumbersLabel(Label):
    """Widget to display line numbers"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'RobotoMono-Regular'
        self.font_size = 18
        self.size_hint_x = None
        self.width = 60
        self.text_size = (self.width, None)
        self.halign = 'right'
        self.valign = 'top'
        self.padding = [5, 0]

    def update_line_numbers(self, text_widget):
        """Update line numbers based on text content"""
        if hasattr(text_widget, 'text'):
            lines = text_widget.text.count('\n') + 1
            self.text = '\n'.join(str(i) for i in range(1, lines + 1))


class CobolEditor(BoxLayout):
    """Main COBOL Editor widget"""

    current_file = StringProperty(None, allownone=True)
    font_size = NumericProperty(18)
    current_theme = StringProperty('Light')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.search_text = ''
        self.search_index = 0
        self.working_directory = None

        # Define color themes
        self.themes = {
            'Light': {
                'bg': [1, 1, 1, 1],
                'fg': [0, 0, 0, 1],
                'line_numbers_bg': [0.88, 0.88, 0.88, 1],
                'line_numbers_fg': [0.33, 0.33, 0.33, 1],
                'keyword': [0, 0, 1, 1],
                'datatype': [0, 0.5, 0.5, 1],
                'string': [0.64, 0.08, 0.08, 1],
                'comment': [0, 0.5, 0, 1],
                'number': [0.04, 0.52, 0.35, 1],
                'division': [0.69, 0, 0.86, 1],
                'section': [0.69, 0, 0.86, 1],
                'search_bg': [1, 1, 0, 1],
                'search_fg': [0, 0, 0, 1]
            },
            'Dark': {
                'bg': [0.12, 0.12, 0.12, 1],
                'fg': [0.83, 0.83, 0.83, 1],
                'line_numbers_bg': [0.15, 0.15, 0.15, 1],
                'line_numbers_fg': [0.52, 0.52, 0.52, 1],
                'keyword': [0.34, 0.61, 0.84, 1],
                'datatype': [0.31, 0.79, 0.69, 1],
                'string': [0.81, 0.57, 0.47, 1],
                'comment': [0.42, 0.60, 0.33, 1],
                'number': [0.71, 0.81, 0.66, 1],
                'division': [0.77, 0.53, 0.75, 1],
                'section': [0.77, 0.53, 0.75, 1],
                'search_bg': [0.32, 0.36, 0.42, 1],
                'search_fg': [1, 1, 1, 1]
            },
            'High Contrast': {
                'bg': [0, 0, 0, 1],
                'fg': [1, 1, 1, 1],
                'line_numbers_bg': [0.12, 0.12, 0.12, 1],
                'line_numbers_fg': [1, 1, 1, 1],
                'keyword': [0, 1, 1, 1],
                'datatype': [0, 1, 0, 1],
                'string': [1, 0, 1, 1],
                'comment': [0.5, 1, 0, 1],
                'number': [1, 1, 0, 1],
                'division': [1, 0.53, 0, 1],
                'section': [1, 0.53, 0, 1],
                'search_bg': [1, 1, 0, 1],
                'search_fg': [0, 0, 0, 1]
            },
            'Monokai': {
                'bg': [0.15, 0.16, 0.13, 1],
                'fg': [0.97, 0.97, 0.95, 1],
                'line_numbers_bg': [0.24, 0.24, 0.20, 1],
                'line_numbers_fg': [0.56, 0.56, 0.54, 1],
                'keyword': [0.98, 0.15, 0.45, 1],
                'datatype': [0.40, 0.85, 0.94, 1],
                'string': [0.90, 0.86, 0.45, 1],
                'comment': [0.46, 0.44, 0.37, 1],
                'number': [0.68, 0.51, 1, 1],
                'division': [0.65, 0.89, 0.18, 1],
                'section': [0.65, 0.89, 0.18, 1],
                'search_bg': [0.29, 0.28, 0.24, 1],
                'search_fg': [1, 1, 1, 1]
            }
        }

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create the user interface"""
        # Action bar (menu)
        self.action_bar = ActionBar()
        action_view = ActionView()
        action_view.add_widget(ActionPrevious(title='COBOL Editor', with_previous=False))

        # File menu
        file_menu = ActionGroup(text='File', mode='spinner')
        file_menu.add_widget(ActionButton(text='New', on_press=self.new_file))
        file_menu.add_widget(ActionButton(text='Open', on_press=self.open_file))
        file_menu.add_widget(ActionButton(text='Save', on_press=self.save_file))
        file_menu.add_widget(ActionButton(text='Save As', on_press=self.save_as_file))
        file_menu.add_widget(ActionButton(text='Select Working Directory', on_press=self.select_working_directory))
        file_menu.add_widget(ActionButton(text='Exit', on_press=self.exit_editor))
        action_view.add_widget(file_menu)

        # Edit menu
        edit_menu = ActionGroup(text='Edit', mode='spinner')
        edit_menu.add_widget(ActionButton(text='Find', on_press=self.find_text))
        edit_menu.add_widget(ActionButton(text='Find Next', on_press=self.find_next))
        edit_menu.add_widget(ActionButton(text='Find in Files', on_press=self.find_in_files))
        edit_menu.add_widget(ActionButton(text='Select All', on_press=self.select_all))
        action_view.add_widget(edit_menu)

        # View menu
        view_menu = ActionGroup(text='View', mode='spinner')
        view_menu.add_widget(ActionButton(text='Light Theme', on_press=lambda x: self.apply_theme('Light')))
        view_menu.add_widget(ActionButton(text='Dark Theme', on_press=lambda x: self.apply_theme('Dark')))
        view_menu.add_widget(ActionButton(text='High Contrast', on_press=lambda x: self.apply_theme('High Contrast')))
        view_menu.add_widget(ActionButton(text='Monokai Theme', on_press=lambda x: self.apply_theme('Monokai')))
        view_menu.add_widget(ActionButton(text='Increase Font', on_press=self.increase_font_size))
        view_menu.add_widget(ActionButton(text='Decrease Font', on_press=self.decrease_font_size))
        view_menu.add_widget(ActionButton(text='Reset Font', on_press=self.reset_font_size))
        action_view.add_widget(view_menu)

        # Help menu
        help_menu = ActionGroup(text='Help', mode='spinner')
        help_menu.add_widget(ActionButton(text='About', on_press=self.show_about))
        action_view.add_widget(help_menu)

        self.action_bar.add_widget(action_view)
        self.add_widget(self.action_bar)

        # Main content area
        content_layout = BoxLayout(orientation='horizontal')

        # File tree (left panel)
        self.tree_panel = BoxLayout(orientation='vertical', size_hint_x=0.2)
        tree_label = Label(text='Workspace', size_hint_y=None, height=30, bold=True)
        self.tree_panel.add_widget(tree_label)

        tree_scroll = ScrollView()
        self.file_tree = TreeView(hide_root=True, size_hint_y=None)
        self.file_tree.bind(minimum_height=self.file_tree.setter('height'))
        tree_scroll.add_widget(self.file_tree)
        self.tree_panel.add_widget(tree_scroll)

        content_layout.add_widget(self.tree_panel)

        # Editor area
        editor_layout = BoxLayout(orientation='horizontal')

        # Line numbers
        line_scroll = ScrollView(size_hint_x=None, width=60, do_scroll_x=False)
        self.line_numbers = LineNumbersLabel()
        line_scroll.add_widget(self.line_numbers)
        editor_layout.add_widget(line_scroll)

        # Text area
        text_scroll = ScrollView()
        self.text_area = CobolTextInput()
        self.text_area.bind(text=self.on_text_change)
        text_scroll.add_widget(self.text_area)
        editor_layout.add_widget(text_scroll)

        content_layout.add_widget(editor_layout)
        self.add_widget(content_layout)

        # Status bar
        self.status_bar = Label(text='Ready', size_hint_y=None, height=30, halign='left')
        self.status_bar.bind(size=self._update_status_bar)
        self.add_widget(self.status_bar)

        # Apply initial theme
        self.apply_theme(self.current_theme)

        # Bind keyboard shortcuts
        Window.bind(on_key_down=self.on_keyboard_down)

    def _update_status_bar(self, *args):
        """Update status bar text size"""
        self.status_bar.text_size = (self.status_bar.width, None)

    def on_keyboard_down(self, window, key, scancode, codepoint, modifiers):
        """Handle keyboard shortcuts"""
        if 'ctrl' in modifiers:
            if codepoint == 'f':
                self.find_text(None)
                return True
            elif codepoint == 's':
                self.save_file(None)
                return True
            elif codepoint == 'o':
                self.open_file(None)
                return True
            elif codepoint == 'n':
                self.new_file(None)
                return True
            elif key == 61:  # Ctrl++ (equals key)
                self.increase_font_size(None)
                return True
            elif key == 45:  # Ctrl+-
                self.decrease_font_size(None)
                return True
        elif key == 286:  # F3
            self.find_next(None)
            return True
        return False

    def on_text_change(self, instance, value):
        """Handle text changes"""
        self.line_numbers.update_line_numbers(self.text_area)
        # Note: Syntax highlighting in Kivy requires a different approach
        # than tkinter. For simplicity, we'll use monochrome for now,
        # but this can be enhanced with custom rendering

    def new_file(self, instance):
        """Create a new file"""
        if self.text_area.text:
            popup = Popup(title='New File',
                         content=Label(text='Discard current changes?'),
                         size_hint=(0.6, 0.3))

            button_layout = BoxLayout()
            yes_btn = Button(text='Yes')
            yes_btn.bind(on_press=lambda x: self._do_new_file(popup))
            no_btn = Button(text='No')
            no_btn.bind(on_press=popup.dismiss)
            button_layout.add_widget(yes_btn)
            button_layout.add_widget(no_btn)

            popup.content = BoxLayout(orientation='vertical')
            popup.content.add_widget(Label(text='Discard current changes?'))
            popup.content.add_widget(button_layout)
            popup.open()
        else:
            self._do_new_file(None)

    def _do_new_file(self, popup):
        """Actually create new file"""
        if popup:
            popup.dismiss()
        self.text_area.text = ''
        self.current_file = None
        Window.set_title('COBOL Editor - New File')

    def open_file(self, instance):
        """Open a file"""
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(filters=['*.cbl', '*.cob', '*.cobol', '*.*'])
        content.add_widget(file_chooser)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        open_btn = Button(text='Open')
        cancel_btn = Button(text='Cancel')
        button_layout.add_widget(open_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        popup = Popup(title='Open File', content=content, size_hint=(0.9, 0.9))

        def do_open(instance):
            if file_chooser.selection:
                self._load_file(file_chooser.selection[0])
                popup.dismiss()

        open_btn.bind(on_press=do_open)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _load_file(self, file_path):
        """Load a file into the editor"""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_area.text = content
                self.current_file = file_path
                Window.set_title(f'COBOL Editor - {os.path.basename(file_path)}')
                self.status_bar.text = f'Opened: {file_path}'
        except Exception as e:
            self._show_error('Error', f'Failed to open file:\n{str(e)}')

    def save_file(self, instance):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.text_area.text)
                self.status_bar.text = f'Saved: {self.current_file}'
            except Exception as e:
                self._show_error('Error', f'Failed to save file:\n{str(e)}')
        else:
            self.save_as_file(instance)

    def save_as_file(self, instance):
        """Save the file with a new name"""
        content = BoxLayout(orientation='vertical')

        file_chooser = FileChooserListView(filters=['*.cbl', '*.cob', '*.cobol'])
        content.add_widget(file_chooser)

        filename_input = TextInput(hint_text='Enter filename', size_hint_y=None, height=40, multiline=False)
        content.add_widget(filename_input)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        save_btn = Button(text='Save')
        cancel_btn = Button(text='Cancel')
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        popup = Popup(title='Save As', content=content, size_hint=(0.9, 0.9))

        def do_save(instance):
            if filename_input.text:
                path = file_chooser.path
                file_path = os.path.join(path, filename_input.text)
                if not file_path.endswith(('.cbl', '.cob', '.cobol')):
                    file_path += '.cbl'
                try:
                    with open(file_path, 'w') as file:
                        file.write(self.text_area.text)
                    self.current_file = file_path
                    Window.set_title(f'COBOL Editor - {os.path.basename(file_path)}')
                    self.status_bar.text = f'Saved as: {file_path}'
                    popup.dismiss()
                except Exception as e:
                    self._show_error('Error', f'Failed to save file:\n{str(e)}')

        save_btn.bind(on_press=do_save)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def find_text(self, instance):
        """Open find dialog"""
        content = BoxLayout(orientation='vertical')
        search_input = TextInput(hint_text='Enter text to find', size_hint_y=None, height=40, multiline=False)
        content.add_widget(search_input)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        find_btn = Button(text='Find')
        cancel_btn = Button(text='Cancel')
        button_layout.add_widget(find_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        popup = Popup(title='Find', content=content, size_hint=(0.6, 0.3))

        def do_find(instance):
            self.search_text = search_input.text
            if self.search_text:
                self.search_index = 0
                self.find_next(None)
                popup.dismiss()

        find_btn.bind(on_press=do_find)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def find_next(self, instance):
        """Find next occurrence of search text"""
        if not self.search_text:
            self.find_text(instance)
            return

        text = self.text_area.text.lower()
        search_text = self.search_text.lower()

        pos = text.find(search_text, self.search_index)

        if pos >= 0:
            self.text_area.select_text(pos, pos + len(search_text))
            self.search_index = pos + len(search_text)
            self.status_bar.text = f'Found: {self.search_text} at position {pos}'
        else:
            # Wrap around
            pos = text.find(search_text, 0)
            if pos >= 0:
                self.text_area.select_text(pos, pos + len(search_text))
                self.search_index = pos + len(search_text)
                self.status_bar.text = f'Found: {self.search_text} at position {pos} (wrapped)'
            else:
                self._show_info('Find', f"Text '{self.search_text}' not found")

    def find_in_files(self, instance):
        """Open multi-file search dialog"""
        content = BoxLayout(orientation='vertical')

        dir_label = Label(text='Select directory:', size_hint_y=None, height=30)
        content.add_widget(dir_label)

        file_chooser = FileChooserListView(dirselect=True)
        content.add_widget(file_chooser)

        search_input = TextInput(hint_text='Enter text to find', size_hint_y=None, height=40, multiline=False)
        content.add_widget(search_input)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        search_btn = Button(text='Search')
        cancel_btn = Button(text='Cancel')
        button_layout.add_widget(search_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        popup = Popup(title='Find in Files', content=content, size_hint=(0.9, 0.9))

        def do_search(instance):
            directory = file_chooser.path
            search_text = search_input.text
            if directory and search_text:
                results = self._search_in_files(directory, search_text)
                if results:
                    popup.dismiss()
                    self._show_search_results(search_text, results)
                else:
                    self._show_info('Find in Files', f"No matches found for '{search_text}'")

        search_btn.bind(on_press=do_search)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _search_in_files(self, directory, search_text):
        """Search for text in COBOL files"""
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
                    except:
                        continue
        return results

    def _show_search_results(self, search_text, results):
        """Show search results in a popup"""
        content = BoxLayout(orientation='vertical')

        results_text = '\n'.join([f'{fp}:{ln}: {txt}' for fp, ln, txt in results[:100]])
        results_label = Label(text=f'Found {len(results)} matches:\n\n{results_text}',
                            halign='left', valign='top')
        results_label.bind(size=lambda *x: setattr(results_label, 'text_size', results_label.size))

        scroll = ScrollView()
        scroll.add_widget(results_label)
        content.add_widget(scroll)

        close_btn = Button(text='Close', size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(title=f"Search Results: '{search_text}'", content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def select_all(self, instance):
        """Select all text"""
        self.text_area.select_all()

    def show_about(self, instance):
        """Show about dialog"""
        about_text = ("COBOL Editor (Kivy Version)\n\n"
                     "A COBOL editor with syntax highlighting, search,\n"
                     "multi-file search, and adjustable font size.\n\n"
                     "Shortcuts:\n"
                     "Ctrl+N - New File\n"
                     "Ctrl+O - Open File\n"
                     "Ctrl+S - Save File\n"
                     "Ctrl+F - Find\n"
                     "F3 - Find Next\n"
                     "Ctrl++ - Increase Font Size\n"
                     "Ctrl+- - Decrease Font Size")
        self._show_info('About', about_text)

    def increase_font_size(self, instance):
        """Increase font size"""
        if self.font_size < 72:
            self.font_size += 2
            self.update_font()
            self.status_bar.text = f'Font size: {self.font_size}'

    def decrease_font_size(self, instance):
        """Decrease font size"""
        if self.font_size > 6:
            self.font_size -= 2
            self.update_font()
            self.status_bar.text = f'Font size: {self.font_size}'

    def reset_font_size(self, instance):
        """Reset font size to default"""
        self.font_size = 18
        self.update_font()
        self.status_bar.text = f'Font size reset to: {self.font_size}'

    def update_font(self):
        """Update font for all text widgets"""
        self.text_area.font_size = self.font_size
        self.line_numbers.font_size = self.font_size

    def apply_theme(self, theme_name):
        """Apply a color theme to the editor"""
        if theme_name not in self.themes:
            self._show_error('Error', f"Theme '{theme_name}' not found")
            return

        self.current_theme = theme_name
        theme = self.themes[theme_name]

        # Update text area colors
        self.text_area.background_color = theme['bg']
        self.text_area.foreground_color = theme['fg']
        self.text_area.cursor_color = theme['fg']

        # Update line numbers colors
        with self.line_numbers.canvas.before:
            Color(*theme['line_numbers_bg'])
            Rectangle(pos=self.line_numbers.pos, size=self.line_numbers.size)
        self.line_numbers.color = theme['line_numbers_fg']

        # Update status bar
        self.status_bar.text = f'Theme changed to: {theme_name}'

    def select_working_directory(self, instance):
        """Select a working directory to browse"""
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(dirselect=True)
        content.add_widget(file_chooser)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)

        popup = Popup(title='Select Working Directory', content=content, size_hint=(0.9, 0.9))

        def do_select(instance):
            self.working_directory = file_chooser.path
            self.populate_tree()
            self.status_bar.text = f'Working directory: {self.working_directory}'
            popup.dismiss()

        select_btn.bind(on_press=do_select)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def populate_tree(self):
        """Populate the tree view with files and directories"""
        self.file_tree.clear_widgets()

        if not self.working_directory or not os.path.exists(self.working_directory):
            return

        root_name = os.path.basename(self.working_directory) or self.working_directory
        root_node = self.file_tree.add_node(TreeViewLabel(text=f'📁 {root_name}',
                                                          is_open=True))

        self._add_tree_nodes(root_node, self.working_directory)

    def _add_tree_nodes(self, parent, path):
        """Recursively add nodes to the tree"""
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))

            for item in items:
                if item.startswith('.'):
                    continue

                full_path = os.path.join(path, item)

                if os.path.isdir(full_path):
                    node = TreeViewLabel(text=f'📁 {item}')
                    node.full_path = full_path
                    self.file_tree.add_node(node, parent)
                    self._add_tree_nodes(node, full_path)
                else:
                    if item.endswith(('.cbl', '.cob', '.cobol')):
                        icon = "📄"
                    else:
                        icon = "📋"
                    node = TreeViewLabel(text=f'{icon} {item}')
                    node.full_path = full_path
                    node.bind(on_touch_down=self._on_tree_node_click)
                    self.file_tree.add_node(node, parent)
        except PermissionError:
            pass

    def _on_tree_node_click(self, instance, touch):
        """Handle tree node click"""
        if instance.collide_point(*touch.pos) and touch.is_double_tap:
            if hasattr(instance, 'full_path') and os.path.isfile(instance.full_path):
                self._load_file(instance.full_path)

    def exit_editor(self, instance):
        """Exit the editor"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Are you sure you want to exit?'))

        button_layout = BoxLayout(size_hint_y=None, height=50)
        yes_btn = Button(text='Yes')
        no_btn = Button(text='No')
        button_layout.add_widget(yes_btn)
        button_layout.add_widget(no_btn)
        content.add_widget(button_layout)

        popup = Popup(title='Exit', content=content, size_hint=(0.6, 0.3))

        yes_btn.bind(on_press=lambda x: App.get_running_app().stop())
        no_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _show_error(self, title, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        close_btn = Button(text='Close', size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _show_info(self, title, message):
        """Show info popup"""
        content = BoxLayout(orientation='vertical')
        label = Label(text=message, halign='left', valign='top')
        label.bind(size=lambda *x: setattr(label, 'text_size', label.size))
        content.add_widget(label)
        close_btn = Button(text='Close', size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class CobolEditorApp(App):
    """Main Kivy application"""

    def build(self):
        self.title = 'COBOL Editor'
        Window.size = (1200, 800)
        return CobolEditor()


def main():
    CobolEditorApp().run()


if __name__ == "__main__":
    main()
