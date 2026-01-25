import tkinter as tk
from tkinter import Scrollbar, Text, Button, Frame, Label, StringVar
from tkinter import HORIZONTAL, VERTICAL, BOTTOM, RIGHT, LEFT, BOTH, X, Y, END, SOLID, FLAT, NORMAL, DISABLED, NW, NE, TOP, NONE
from .ui_utils import copy_code_with_feedback

class SyntaxHighlighter:
    def __init__(self, text_widget, root):
        self.text = text_widget
        self.root = root

    def detect_language(self, code):
        """Rule-based fallback language detector for code snippets"""
        code = code.strip()

        if "<html" in code or "<!DOCTYPE html>" in code:
            return "html"
        elif "def " in code or "import " in code or "print(" in code:
            return "python"
        elif "function " in code or "console.log(" in code or "let " in code or "const " in code:
            return "javascript"
        elif "#include" in code or "printf(" in code or "scanf(" in code:
            return "c"
        elif "public static void main" in code:
            return "java"
        elif "class " in code and "::" in code:
            return "cpp"
        elif "using System" in code or "Console.WriteLine" in code:
            return "c#"
        elif "package main" in code and "func " in code:
            return "go"
        elif "fn main()" in code:
            return "rust"
        elif "<?php" in code:
            return "php"
        elif code.strip().startswith("{") and ":" in code:
            return "json"
        elif code.strip().startswith("---") or ":" in code and "\n" in code:
            return "yaml"
        elif "SELECT" in code.upper() or "FROM" in code.upper():
            return "sql"
        elif "# " in code or "##" in code or "**" in code:
            return "markdown"
        elif code.startswith("#!") or any(cmd in code for cmd in ["#!/bin/bash", "echo ", "$HOME"]):
            return "bash"
        return "text"

    def insert_code_snippet(self, lang, code):
        self.text.insert(END, '\n')
        
        # Create a frame for the code block with border
        code_frame = Frame(self.text, bg='#f0f0f0', bd=1, relief=SOLID)
        
        # Add language label at top-left with better styling
        lang_label = Label(code_frame, 
                        text=lang.upper(), 
                        font=("Arial", 9, "bold"),
                        bg="#4CAF50",  # Green background
                        fg="white",    # White text
                        padx=6,
                        pady=2,
                        bd=0)
        lang_label.pack(side=TOP, anchor=NW, padx=5, pady=(5,0))
        
        # Create inner frame for code and scrollbars
        inner_frame = Frame(code_frame, bg='#f4f4f4')
        inner_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0,5))
        
        # Add line numbers
        lines = code.split('\n')
        numbered_code = "\n".join(f"{i+1:3d}  {line}" for i, line in enumerate(lines))
        
        # Create the text widget for code display
        code_text = Text(inner_frame, 
                        bg='#f4f4f4', 
                        font=("Courier New", 11), 
                        wrap=NONE,
                        padx=5, 
                        pady=5,
                        relief=FLAT,
                        borderwidth=0,
                        width=82)
        
        # Add scrollbars
        scroll_x = Scrollbar(inner_frame, orient=HORIZONTAL, command=code_text.xview)
        scroll_y = Scrollbar(inner_frame, orient=VERTICAL, command=code_text.yview)
        code_text.config(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        code_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Insert the code
        code_text.insert(END, numbered_code)
        
        # Apply language-specific syntax highlighting
        lang = lang.lower()  # Normalize language name
        if lang in ["html", "xml"]:
            self.apply_html_highlighting(code_text)
        elif lang == "python":
            self.apply_python_highlighting(code_text)
        elif lang in ["javascript", "js"]:
            self.apply_javascript_highlighting(code_text)
        elif lang == "css":
            self.apply_css_highlighting(code_text)
        elif lang in ["java", "c", "cpp", "c++", "c#", "go", "rust"]:
            self.apply_cstyle_highlighting(code_text)
        elif lang in ["bash", "sh", "shell"]:
            self.apply_shell_highlighting(code_text)
        elif lang == "json":
            self.apply_json_highlighting(code_text)
        elif lang == "yaml" or lang == "yml":
            self.apply_yaml_highlighting(code_text)
        elif lang == "sql":
            self.apply_sql_highlighting(code_text)
        elif lang == "markdown" or lang == "md":
            self.apply_markdown_highlighting(code_text)
        elif lang == "php":
            self.apply_php_highlighting(code_text)
        
        # Add the code frame to main text widget
        self.text.window_create(END, window=code_frame)
        
        # --- Context Menu for Code Block ---
        def show_code_context_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="📋 Copy All", command=lambda: copy_code_with_feedback(self.root, code, copy_btn_text))
            
            # Speak option
            def speak_code():
                try:
                    # Try to speak selected text if any
                    if code_text.tag_ranges(tk.SEL):
                        selected = code_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                        from .audio import speak_text_gtts 
                        # We need a way to get language options, for now default to en or simple speak
                        # Since we don't have direct access to language_options here easily without refactor,
                        # we'll assume a method exists or import simple speak.
                        # Actually ui_utils imports speak_text_gtts.
                        speak_text_gtts(selected, "en", self.root)
                    else:
                        # Speak all code (might be too long, but user asked for it)
                         from .audio import speak_text_gtts
                         speak_text_gtts(code, "en", self.root)
                except Exception:
                    pass

            menu.add_command(label="🗣️ Speak", command=speak_code)
            
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        code_text.bind("<Button-3>", show_code_context_menu)

        # Add copy button at top-right
        copy_btn_text = StringVar(value="📋 Copy")
        copy_btn = Button(code_frame,
                          textvariable=copy_btn_text,
                          font=("Arial", 8),
                          command=lambda c=code, btn=copy_btn_text: copy_code_with_feedback(self.root, c, btn),
                          relief=FLAT,
                          bg="#e0e0e0",
                          activebackground="#d0d0d0",
                          cursor='hand2')
        copy_btn.place(relx=1.0, rely=0.0, anchor=NE, x=-85, y=5)

        # --- Edit Button ---
        def toggle_edit():
            editable = code_text.cget("state") == NORMAL
            if editable:
                code_text.config(state=DISABLED)
                edit_btn.config(text="✏️ Edit")
            else:
                code_text.config(state=NORMAL)
                edit_btn.config(text="✅ Done")

        edit_btn = Button(code_frame,
                          text="✏️ Edit",
                          font=("Arial", 8),
                          command=toggle_edit,
                          relief=FLAT,
                          bg="#e0e0e0",
                          activebackground="#d0d0d0",
                          cursor='hand2')
        edit_btn.place(relx=1.0, rely=0.0, anchor=NE, x=-25, y=5)

    def apply_common_highlighting(self, text_widget):
        """Common syntax elements for many languages"""
        # Configure basic tags
        text_widget.tag_config("keyword", foreground="blue", font=("Courier New", 11, "bold"))
        text_widget.tag_config("comment", foreground="green", font=("Courier New", 11, "italic"))
        text_widget.tag_config("string", foreground="#b58900")  # Orange
        text_widget.tag_config("number", foreground="#cb4b16")  # Red-orange
        text_widget.tag_config("operator", foreground="purple")

    def highlight_pattern(self, text_widget, pattern, tag):
        """Helper function to highlight text patterns"""
        start = "1.0"
        while True:
            count_var = tk.IntVar()
            pos = text_widget.search(pattern, start, stopindex=END, regexp=True, count=count_var)
            if not pos:
                break
            end = text_widget.index(f"{pos}+{count_var.get()}c")
            text_widget.tag_add(tag, pos, end)
            start = end

    def highlight_strings(self, text_widget):
        """Helper function to highlight strings in multiple languages"""
        string_patterns = [
            r'""".*?"""', r"'''.*?'''",  # Triple quoted
            r'"[^"\\]*(\\.[^"\\]*)*"',     # Double quoted
            r"'[^'\\]*(\\.[^'\\]*)*'"      # Single quoted
        ]
        
        for pattern in string_patterns:
            self.highlight_pattern(text_widget, pattern, "string")

    def apply_python_highlighting(self, text_widget):
        import keyword
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)
        
        # Python keywords
        for kw in keyword.kwlist + ["self", "cls", "True", "False", "None"]:
            self.highlight_pattern(text_widget, rf'\y{kw}\y', "keyword")
        
        # Comments and strings
        self.highlight_pattern(text_widget, r'#.*$', "comment")
        self.highlight_strings(text_widget)
        
        text_widget.config(state=DISABLED)

    def apply_javascript_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)
        
        # JavaScript keywords
        js_keywords = ["function", "var", "let", "const", "if", "else", "for", 
                    "while", "return", "class", "import", "export", "try", 
                    "catch", "finally", "throw", "new", "this", "typeof"]
        
        for kw in js_keywords:
            self.highlight_pattern(text_widget, rf'\y{kw}\y', "keyword")
        
        # JS-specific patterns
        self.highlight_pattern(text_widget, r'//.*$', "comment")
        self.highlight_pattern(text_widget, r'/\*.*?\*/', "comment")
        self.highlight_strings(text_widget)
        
        text_widget.config(state=DISABLED)

    def apply_html_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)
        
        # HTML tags (including self-closing)
        self.highlight_pattern(text_widget, r'<\/?[a-zA-Z][a-zA-Z0-9-]*\b[^>]*>', "keyword")
        
        # HTML comments
        self.highlight_pattern(text_widget, r'<!--.*?-->', "comment")
        
        # Attributes
        self.highlight_pattern(text_widget, r'\b[a-zA-Z-]+=', "string")
        
        # Attribute values
        self.highlight_pattern(text_widget, r'=\s*["\'][^"\']*["\']', "string")
        
        # DOCTYPE
        self.highlight_pattern(text_widget, r'<!DOCTYPE.*?>', "keyword")
        
        # Special characters
        self.highlight_pattern(text_widget, r'&[a-zA-Z]+;', "number")
        
        text_widget.config(state=DISABLED)

    def apply_css_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        # Highlight CSS selectors (starting lines without whitespace)
        self.highlight_pattern(text_widget, r'^[^\s][^{]+(?=\s*\{)', "keyword")

        # Highlight properties (e.g., color:)
        self.highlight_pattern(text_widget, r'\b[\w-]+\s*:', "string")

        # Highlight values (e.g., #fff, red, 10px)
        self.highlight_pattern(text_widget, r':\s*[^;]+', "number")

        # Highlight comments /* ... */
        self.highlight_pattern(text_widget, r'/\*.*?\*/', "comment")

        self.highlight_strings(text_widget)
        text_widget.config(state=DISABLED)

    def apply_cstyle_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        c_keywords = [
            "int", "float", "double", "char", "void", "if", "else", "for", "while",
            "switch", "case", "break", "continue", "return", "struct", "class",
            "public", "private", "protected", "include", "define", "namespace",
            "main", "static", "const", "new", "delete", "try", "catch", "throw"
        ]

        for kw in c_keywords:
            self.highlight_pattern(text_widget, rf'\y{kw}\y', "keyword")

        # Single-line C-style comments
        self.highlight_pattern(text_widget, r'//.*$', "comment")

        # Multi-line C-style comments (Tcl-safe)
        self.highlight_pattern(text_widget, r'/\*.*?\*/', "comment")

        self.highlight_strings(text_widget)
        text_widget.config(state=DISABLED)

    def apply_json_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        # Keys (in quotes followed by colon)
        self.highlight_pattern(text_widget, r'"[^"]*"\s*:', "keyword")

        # Values (quoted strings)
        self.highlight_pattern(text_widget, r':\s*"[^"]*"', "string")

        # Numbers
        self.highlight_pattern(text_widget, r':\s*[\d\.]+', "number")

        # Booleans and null
        self.highlight_pattern(text_widget, r'\b(true|false|null)\b', "operator")

        text_widget.config(state=DISABLED)

    def apply_shell_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        # Common shell commands
        shell_keywords = [
            "echo", "cd", "ls", "pwd", "mkdir", "rm", "touch", "cp", "mv", "grep", "cat",
            "chmod", "chown", "sudo", "exit", "if", "then", "else", "fi", "while", "do", "done"
        ]

        for kw in shell_keywords:
            self.highlight_pattern(text_widget, rf'\y{kw}\y', "keyword")

        # Highlight variables like $HOME, $1, $var
        self.highlight_pattern(text_widget, r'\$\w+', "number")

        # Highlight comments
        self.highlight_pattern(text_widget, r'#.*$', "comment")

        self.highlight_strings(text_widget)
        text_widget.config(state=DISABLED)

    def apply_php_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        php_keywords = [
            "echo", "print", "if", "else", "elseif", "while", "for", "foreach", "function",
            "return", "class", "public", "private", "protected", "new", "try", "catch", "finally",
            "null", "true", "false", "isset", "unset", "empty", "var", "global", "static"
        ]

        for kw in php_keywords:
            self.highlight_pattern(text_widget, rf'\y{kw}\y', "keyword")

        self.highlight_pattern(text_widget, r'//.*$', "comment")
        self.highlight_pattern(text_widget, r'/\*.*?\*/', "comment")
        self.highlight_pattern(text_widget, r'\$[a-zA-Z_][a-zA-Z0-9_]*', "number")  # Variables

        self.highlight_strings(text_widget)
        text_widget.config(state=DISABLED)

    def apply_markdown_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        self.highlight_pattern(text_widget, r'^#+\s.*$', "keyword")           # Headings
        self.highlight_pattern(text_widget, r'\*\*(.*?)\*\*', "string")       # Bold
        self.highlight_pattern(text_widget, r'\*(.*?)\*', "string")           # Italic
        self.highlight_pattern(text_widget, r'`[^`]+`', "number")             # Inline code
        self.highlight_pattern(text_widget, r'\[.*?\]\(.*?\)', "operator")    # Links

        text_widget.config(state=DISABLED)

    def apply_sql_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        sql_keywords = [
            "select", "from", "where", "insert", "into", "values", "update", "set",
            "delete", "join", "left", "right", "inner", "outer", "on", "as", "create",
            "table", "drop", "alter", "add", "and", "or", "not", "in", "null", "is", "distinct", "order", "by", "group", "limit", "offset"
        ]
        
        for kw in sql_keywords:
            kw=kw.upper()
            self.highlight_pattern(text_widget, rf'\y{kw}\y', "keyword")

        self.highlight_pattern(text_widget, r'--.*$', "comment")   # Line comments
        self.highlight_strings(text_widget)

        text_widget.config(state=DISABLED)

    def apply_yaml_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        self.highlight_pattern(text_widget, r'^\s*[\w\-\.]+:', "keyword")  # Keys
        self.highlight_pattern(text_widget, r':\s*".*?"', "string")         # Quoted values
        self.highlight_pattern(text_widget, r':\s*\d+(\.\d+)?', "number")   # Numbers
        self.highlight_pattern(text_widget, r'#.*$', "comment")             # Comments

        text_widget.config(state=DISABLED)
