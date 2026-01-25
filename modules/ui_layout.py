import tkinter as tk
from tkinter import ttk, Canvas, Button, Text, Label, Frame, Menu
from tkinter import LEFT, RIGHT, BOTTOM, TOP, BOTH, X, Y, END, SOLID, FLAT, WORD, NW, EW, NSEW, NS
from PIL import Image, ImageTk, ImageDraw
from gtts.lang import tts_langs
from . import ui_utils

class ChatBotUI:
    def __init__(self, root, callbacks):
        self.root = root
        self.callbacks = callbacks
        self.root.title('HelpBot')
        self.root.geometry('1360x680+0+0')
        self.root.resizable(True, False)
        self.root.config(bg='powderblue')
        self.root.wm_iconbitmap('assets/chat.ico')
        
        self.setup_styles()
        self.create_layout()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#2e2e2e")
        style.configure("Dark.TLabel", background="#2e2e2e", foreground="white")
        style.configure("Dark.TButton", background="#444", foreground="white")

        style.configure("Color.TButton",
                        font=("Arial", 11, "bold"),
                        background="#28a745",
                        foreground="white",
                        padding=6,
                        borderwidth=0)
        style.map("Color.TButton",
                background=[("active", "#218838"), ("disabled", "#c3c3c3"), ("pressed", "#1e7e34")],
                foreground=[("active", "white")])

        style.configure("Color.TLabel",
                        background="white",
                        foreground="green",
                        font=("Arial", 13, "bold"))

        style.configure("TEntry", font=("Arial", 12))
        style.configure("TCombobox", padding=4, font=('Arial', 11))

    def create_layout(self):
        # === grid config ===
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # === title label ===
        img = Image.open('assets/chat.jpg').resize((100, 70), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)

        self.title_label = ttk.Label(self.root,  text="  Chat Me", anchor="w", 
                                    font=('Arial', 24, 'bold'),
                                    style="Color.TLabel", padding=(37, 20, 0, 0))
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.hamburger_icon = ImageTk.PhotoImage(Image.open("assets/menu.png").resize((30, 30)))
        self.hamburger_btn = Button(self.title_label, image=self.hamburger_icon,
                                        command=self.callbacks['toggle_history'], bd=0, bg='white',
                                    activebackground='white', cursor='hand2')  
        self.hamburger_btn.place(x=5, y=5)

        self.help_icon = ImageTk.PhotoImage(Image.open("assets/chat.jpg").resize((100, 60)))
        self.help_btn = Button(self.title_label, image=self.help_icon,
                                command=self.callbacks['show_help'], bd=0, bg='white',
                            activebackground='white', cursor='hand2')
        self.help_btn.place(x=190, y=5,height=60,width=100)

        self.back_btn = Button(self.title_label, text="Back", width=12, cursor='hand2', font=('times new roman', 10, 'bold'),
                          bg='red', fg='white', activebackground="green", command=self.callbacks['back'])
        self.back_btn.place(x=850, y=30, height=25)
       
        # ToolTip
        try:
            from tooltip import ToolTip
            ToolTip(self.hamburger_btn, "Toggle History Panel (Ctrl+T)")
            ToolTip(self.help_btn, "Help & Shortcuts (Ctrl+H)")
        except ImportError:
            pass

        self.time_lbl = ttk.Label(self.title_label, font=('Arial', 18, 'bold'),
                                background='white', foreground='gold')
        self.time_lbl.place(x=500, y=15, width=200, height=45)

        # === Loading Spinner ===
        self.spinner_frames = []
        try:
            spinner_gif = Image.open("assets/spinner.gif")
            for frame in range(spinner_gif.n_frames):
                spinner_gif.seek(frame)
                frame_image = ImageTk.PhotoImage(spinner_gif.copy().resize((24, 24)))
                self.spinner_frames.append(frame_image)
        except Exception as e:
            print(f"Spinner load error: {e}")
            self.spinner_frames = []

        # === main chat frame ===
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.scroll_y = ttk.Scrollbar(main_frame, orient='vertical')
        self.scroll_y.grid(row=1, column=1, sticky='ns')

        self.text = Text(main_frame, font=('Segoe UI Emoji', 13), wrap=WORD,
                        yscrollcommand=self.scroll_y.set, state='disabled')
        self.text.grid(row=1, column=0, sticky="nsew")
        self.scroll_y.config(command=self.text.yview)

        # === Right-click menu ===
        self.right_click_menu = Menu(self.text, tearoff=0)
        self.right_click_menu.add_command(label="📋 Copy Selected Text", command=self.callbacks['copy_selected'])
        self.right_click_menu.add_command(label="🔊 Speak Selected Text", command=self.callbacks['speak_selected'])

        self.text.bind("<Button-3>", self.show_context_menu)

        # === button frame (Modern Input Area) ===
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        btn_frame.columnconfigure(1, weight=1)

        if True: # Creating scope for helper
            def create_emoji_btn(parent, text, tooltip_text, command, bg_color, fg_color='white'):
                btn = Button(parent, text=text, font=("Segoe UI Emoji", 12),
                            bd=0, bg=bg_color, fg=fg_color, activebackground=bg_color, activeforeground=fg_color,
                            cursor='hand2', command=command, width=3)
                try:
                    from tooltip import ToolTip
                    ToolTip(btn, tooltip_text)
                except ImportError:
                    pass
                return btn

        # 0. Attachment Text Area (Top of btn_frame)
        self.attachment_text = Text(btn_frame, height=4, width=40, font=('Segoe UI Emoji', 10), 
                                   bd=0, bg=self.root['bg'], cursor="arrow", state='disabled')
        self.attachment_text.grid(row=0, column=0, columnspan=3, sticky='ew', padx=5, pady=(0, 5))
        
        # 1. Plus Button (Left)
        # Refactored to use emoji button
        self.plus_btn = create_emoji_btn(btn_frame, "📎", "Add Attachment (Ctrl+O)", 
                                        self.callbacks['add_attachment'],  
                                        bg_color='#17a2b8')
        self.plus_btn.grid(row=1, column=0, padx=(0, 5), sticky='s', pady=5)
        
        # 2. Input Container (Center) - Rounded look simulation with Frame
        input_container = Frame(btn_frame, bg="white", bd=1, relief="solid")
        input_container.grid(row=1, column=1, sticky='ew')
        input_container.columnconfigure(0, weight=1)

        # Multi-line Text Input
        self.entry = Text(input_container, height=2, font=('Segoe UI Emoji', 12), wrap=WORD, bd=0, padx=10, pady=8)
        self.entry.grid(row=0, column=0, sticky='ew')

        # Custom logic for focus interaction without placeholder text
        self.entry.config(fg='black')

        def on_focus_in(event):
            pass 
        def on_focus_out(event):
             pass 

        self.entry.bind("<FocusIn>", on_focus_in)
        self.entry.bind("<FocusOut>", on_focus_out)
        # Changed: Ctrl+Enter to send, Enter defaults to newline (standard behavior for Text widget)
        self.entry.bind('<Control-Return>', lambda e: self.callbacks['send']())
        
        # Scrollbar for input
        input_scroll = ttk.Scrollbar(input_container, orient="vertical", command=self.entry.yview)
        input_scroll.grid(row=0, column=1, sticky='ns')
        self.entry.config(yscrollcommand=input_scroll.set)

        # 3. Action Icons (Right - Inside or Next to Input?) 
        # User asked for: "send mic, clear, read all icon on right hand side of prompt box"
        # We'll put them in a frame to the right of the input container
        
        actions_frame = ttk.Frame(btn_frame)
        actions_frame.grid(row=1, column=2, sticky='s', padx=(5, 0), pady=0)



        self.send_btn = create_emoji_btn(actions_frame, "🚀", "Send Message (Ctrl+Enter)", self.callbacks['send'], bg_color='#28a745')
        self.send_btn.pack(side=LEFT, padx=3)

        self.mic_btn = create_emoji_btn(actions_frame, "🎙️", "Voice Input (Ctrl+M)", self.callbacks['speak'], bg_color='#fd7e14')
        self.mic_btn.pack(side=LEFT, padx=3)

        self.clear_btn = create_emoji_btn(actions_frame, "🧹", "Clear Chat (Ctrl+L)", self.callbacks['clear'], bg_color='#dc3545')
        self.clear_btn.pack(side=LEFT, padx=3)

        self.read_btn = create_emoji_btn(actions_frame, "🔊", "Read All (Ctrl+R)", self.callbacks['read_all'], bg_color='#6610f2')
        self.read_btn.pack(side=LEFT, padx=3)
        
        # === Language Data Setup (Restored for Settings) ===
        self.languages = tts_langs()
        self.language_options = {}

        common_languages = {
            "English": "en", "Hindi": "hi", "Spanish": "es", "French": "fr",
            "German": "de", "Gujarati": "gu", "Punjabi": "pa", "Chinese (Simplified)": "zh-CN", "Bengali": "bn"
        }

        for name, code in common_languages.items():
            if code in self.languages:
                self.language_options[name] = code
        for code, name in self.languages.items():
            if code not in self.language_options.values():
                self.language_options[name] = code

        # Spinner needs to be somewhere
        self.spinner_label = Label(actions_frame, bg=self.root['bg'])
        self.spinner_label.pack(side=LEFT, padx=3)
        self.spinner_label.pack_forget() # Initially hidden using pack logic

        # === history panel ===
        self.history_visible = False
        self.history_panel = ttk.Frame(self.root)
        self.history_panel.grid(row=1, column=1, rowspan=2, sticky='nsew', padx=(0, 5), pady=(0, 5))
        self.history_panel.grid_propagate(True)
        self.history_panel.grid_remove()

        self.history_panel.rowconfigure(2, weight=1)
        self.history_panel.columnconfigure(0, weight=1)
        search_row = ttk.Frame(self.history_panel)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 2))
        search_row.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var, font=("Arial", 11))
        self.search_entry.grid(row=0, column=0, sticky='ew')
        search_button = ttk.Button(search_row, text="🔍", style="Color.TButton", width=3, command=self.callbacks['update_search'])
        search_button.grid(row=0, column=1, padx=(5, 0))
        
        # Trigger search on typing
        self.search_var.trace_add("write", lambda *args: self.callbacks['update_search']())

        # === New Chat Button at Top ===
        new_chat_btn = ttk.Button(self.history_panel, text="🆕 New Chat", style="Color.TButton", command=self.callbacks['new_chat'])
        new_chat_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 2), padx=5)

        # Canvas for scrollable history
        self.history_canvas = Canvas(self.history_panel, borderwidth=0, background="#dcdad5", highlightthickness=0)
        self.history_canvas.grid(row=2, column=0, sticky="nsew")

        # Scrollbar for the canvas
        self.history_scrollbar = ttk.Scrollbar(self.history_panel, orient="vertical", command=self.history_canvas.yview)
        self.history_scrollbar.grid(row=2, column=1, sticky="ns")

        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)

        # Inner frame that holds history items
        self.history_list_frame = ttk.Frame(self.history_canvas, style="TFrame")
        self.history_window = self.history_canvas.create_window((0, 0), window=self.history_list_frame, anchor="nw")

        def on_history_frame_configure(event):
            self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))

        self.history_list_frame.bind("<Configure>", on_history_frame_configure)
        
        # Bind mousewheel using utils
        ui_utils.bind_mousewheel(self.history_canvas, self.history_canvas)


        
        # === Settings Button (Bottom Left) ===
        self.settings_btn = create_emoji_btn(self.history_panel, "⚙️", "Settings (Ctrl+,)", self.open_settings_window, bg_color='#343a40')
        self.settings_btn.grid(row=5, column=0, sticky="sw", padx=5, pady=5)


        self.text.tag_config("code", background="#f0f0f0", font=("Courier New", 11))

    def open_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x520")
        settings_win.iconbitmap('assets/chat.ico')
        settings_win.resizable(False, False)
        
        # Center the window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 260
        settings_win.geometry(f"+{x}+{y}")
        
        # --- THEME DETECTION for Dialog Styling ---
        # We need to know if the APP is currently in Dark Mode to style the dialog accordingly.
        # Best way is to check the root bg or a flag.
        is_dark = (self.root.cget('bg') == '#2e2e2e')
        
        dl_bg = "#2e2e2e" if is_dark else "#f0f0f0"
        dl_fg = "white" if is_dark else "black"
        # Labelframe style customization
        style = ttk.Style()
        style.configure("Settings.TLabelframe", background=dl_bg, foreground=dl_fg)
        style.configure("Settings.TLabelframe.Label", background=dl_bg, foreground=dl_fg, font=("Segoe UI", 11, "bold"))
        
        settings_win.configure(bg=dl_bg)

        main_container = Frame(settings_win, bg=dl_bg, padx=20, pady=20)
        main_container.pack(fill=BOTH, expand=True)

        # === Appearance Section ===
        app_frame = ttk.LabelFrame(main_container, text="Appearance", style="Settings.TLabelframe", padding=15)
        app_frame.pack(fill=X, pady=(0, 15))

        # 1. Theme
        ttk.Label(app_frame, text="Theme:", background=dl_bg, foreground=dl_fg, font=("Segoe UI", 10)).pack(anchor="w")
        
        current_theme = "System Default"
        if 'get_current_theme' in self.callbacks:
            current_theme = self.callbacks['get_current_theme']()
            
        theme_var = tk.StringVar(value=current_theme)
        theme_combo = ttk.Combobox(app_frame, textvariable=theme_var, 
                                   values=["System Default", "Light", "Dark"], 
                                   state="readonly", font=("Segoe UI", 10))
        theme_combo.pack(fill=X, pady=(5, 10))

        # 2. Language
        ttk.Label(app_frame, text="Language:", background=dl_bg, foreground=dl_fg, font=("Segoe UI", 10)).pack(anchor="w")
        
        current_lang_code = self.callbacks['get_current_language']()
        current_lang_name = "English"
        for name, code in self.language_options.items():
            if code == current_lang_code:
                current_lang_name = name
                break
        
        lang_var = tk.StringVar(value=current_lang_name)
        lang_combo = ttk.Combobox(app_frame, textvariable=lang_var, values=sorted(self.language_options.keys()), state="readonly", font=("Segoe UI", 10))
        lang_combo.pack(fill=X, pady=(5, 0))

        # 3. Model
        ttk.Label(app_frame, text="AI Model:", background=dl_bg, foreground=dl_fg, font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 0))
        
        # Model Options
        self.model_options = [
            "tngtech/deepseek-r1t2-chimera:free",
            "gemini-2.5-flash-lite-preview-09-2025",
            "bytedance-seed/seedream-4.5"
        ]
        
        current_model = "tngtech/deepseek-r1t2-chimera:free"
        if 'get_current_model' in self.callbacks:
            current_model = self.callbacks['get_current_model']()
            
        model_var = tk.StringVar(value=current_model)
        model_combo = ttk.Combobox(app_frame, textvariable=model_var, values=self.model_options, state="readonly", font=("Segoe UI", 10))
        model_combo.pack(fill=X, pady=(5, 0))

        # === Data Management Section ===
        data_frame = ttk.LabelFrame(main_container, text="Data Management", style="Settings.TLabelframe", padding=15)
        data_frame.pack(fill=X, pady=(0, 15))
        
        def create_setting_btn(parent, text, command, bg_color):
             btn = Button(parent, text=text, font=("Segoe UI", 10), bg=bg_color, fg="white", 
                          activebackground=bg_color, activeforeground="white", bd=0, padx=10, pady=8, cursor="hand2", command=command)
             return btn

        export_btn = create_setting_btn(data_frame, "📤 Export Chat History", lambda: self.callbacks['export_history'](settings_win), "#17a2b8")
        export_btn.pack(fill=X, pady=(0, 10))

        clear_btn = create_setting_btn(data_frame, "🗑️ Clear All History", lambda: self.callbacks['clear_history'](settings_win), "#dc3545")
        clear_btn.pack(fill=X)

        # === Save/Close ===
        def save_settings():
            selected_name = lang_var.get()
            selected_code = self.language_options.get(selected_name, "en")
            
            selected_model = model_var.get()
            selected_theme = theme_var.get()
            
            self.callbacks['save_settings']({
                "language": selected_code,
                "model": selected_model,
                "theme_mode": selected_theme
            })
            settings_win.destroy()
            
        save_btn = Button(main_container, text="Save & Close", font=("Segoe UI", 11, "bold"), 
                          bg="#28a745", fg="white", activebackground="#218838", activeforeground="white",
                          bd=0, padx=20, pady=10, cursor="hand2", command=save_settings)
        save_btn.pack(pady=10)

    def show_context_menu(self, event):
        try:
            self.text.tag_add("sel", "@%d,%d" % (event.x, event.y), "@%d,%d" % (event.x, event.y))
        except:
            pass  # no selection
        self.right_click_menu.tk_popup(event.x_root, event.y_root)

    def create_attachment_preview_frame(self, parent, file_path):
        import os
        filename = os.path.basename(file_path)
        ext = filename.split('.')[-1].lower()
        
        container = Frame(parent, bg="white", bd=1, relief="solid")
        
        # Generate Thumbnail logic
        thumb = None
        try:
            if ext in ['png', 'jpg', 'jpeg', 'ico', 'gif', 'bmp']:
                img = Image.open(file_path)
                img.thumbnail((50, 50))
                thumb = ImageTk.PhotoImage(img)
            else:
                img = Image.new('RGB', (100, 50), color='white')
                d = ImageDraw.Draw(img)
                prefix = ext.upper()
                d.text((5, 15), f'{prefix}', fill='black')
                thumb = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None, None

        lbl = Label(container, image=thumb, bg='white')
        lbl.pack(side=TOP, padx=2, pady=2)
        
        name_lbl = Label(container, text=filename[:8], font=("Arial", 8), bg='white')
        name_lbl.pack(side=BOTTOM)
        
        return container, thumb

    def add_attachment_thumbnail(self, file_path, on_remove=None):
        container, thumb = self.create_attachment_preview_frame(self.attachment_text, file_path)
        if not container: return

        if not hasattr(self, 'thumb_refs'):
            self.thumb_refs = []
        self.thumb_refs.append(thumb)
        
        # Add Close Button for Input Area
        top_row = Frame(container, bg='white')
        top_row.place(relx=1.0, rely=0.0, anchor="ne") 
        # Using place for overlay effect on the container can be tricky if container changes size.
        # Let's stick to packing or simple placement. Previous implementation used pack.
        # But wait, create_attachment_preview_frame packed lbl and name_lbl.
        # We need to insert the close button 'before' or 'on top'. 
        
        # Let's rebuild the container strategy slightly or just pack it at top if possible?
        # create_attachment_preview_frame packs items inside.
        # Let's simply place the close button on the container.
        
        def remove_self():
            if on_remove:
                on_remove()
            container.destroy()
            
        close_btn = Label(container, text="❌", font=("Arial", 7), cursor="hand2", bg='white', fg='red')
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=0, y=0)
        close_btn.bind("<Button-1>", lambda e: remove_self())
        
        self.attachment_text.config(state='normal')
        self.attachment_text.window_create(END, window=container)
        self.attachment_text.insert(END, "  ") 
        self.attachment_text.config(state='disabled')
        
    def render_image_preview_button(self, parent_text_widget, image_path):
        import os
        if not os.path.exists(image_path):
             parent_text_widget.insert(END, f"\n[Image missing: {image_path}]\n")
             return

        try:
             # Create container
             container = Frame(parent_text_widget, bg="white", bd=1, relief="solid", padx=5, pady=5)
             
             # Thumbnail
             img = Image.open(image_path)
             img.thumbnail((200, 200)) # Larger preview for generated images
             thumb = ImageTk.PhotoImage(img)
             
             # Keep ref
             if not hasattr(self, 'gen_thumb_refs'):
                 self.gen_thumb_refs = []
             self.gen_thumb_refs.append(thumb)
             
             btn = Button(container, image=thumb, bg='white', cursor="hand2", 
                          command=lambda: os.startfile(image_path))
             btn.pack()
             
             lbl = Label(container, text="📷 Click to View", font=("Arial", 9), bg='white', fg='blue', cursor="hand2")
             lbl.pack(pady=(2,0))
             lbl.bind("<Button-1>", lambda e: os.startfile(image_path))
             
             parent_text_widget.config(state='normal')
             parent_text_widget.window_create(END, window=container)
             parent_text_widget.insert(END, "\n")
             parent_text_widget.config(state='disabled')
             
        except Exception as e:
             parent_text_widget.insert(END, f"\n[Error rendering image: {e}]\n")

    def render_attachments_in_chat(self, attachments_list):
        if not attachments_list: return
        
        self.text.config(state='normal')
        
        # Container for the row of attachments
        row_frame = Frame(self.text, bg='white')
        
        for file_path in attachments_list:
            import os
            if not os.path.exists(file_path): continue
            
            # We need to pass row_frame as parent
            container, thumb = self.create_attachment_preview_frame(row_frame, file_path)
            if container:
                container.pack(side=LEFT, padx=5, pady=2)
                # Keep ref
                if not hasattr(self, 'chat_thumb_refs'):
                    self.chat_thumb_refs = []
                self.chat_thumb_refs.append(thumb)

        self.text.window_create(END, window=row_frame)
        self.text.insert(END, "\n")
        self.text.config(state='disabled')
        
    def render_welcome_cards(self, command_callback):
        self.text.config(state='normal')
        self.text.delete(1.0, END)
        
        # Center container
        container = Frame(self.text, bg="#f0f0f0") # Default greyish for cards background
        # Actually user wants "gemini-like". White background for main text usually.
        # Let's use white for container if text bg is white.
        bg_color = self.text.cget("bg")
        container.config(bg=bg_color)
        
        # Welcome Header
        import os
        username = os.getlogin()
        header = Label(container, text=f"Hello, {username}", font=("Arial", 28, "bold"), 
                       fg='#4285F4', bg=bg_color) 
        header.pack(pady=(20, 10))
        
        sub = Label(container, text="How can I help you today?", font=("Arial", 16), fg="grey", bg=bg_color)
        sub.pack(pady=(0, 30))
        
        # Cards Grid
        cards_frame = Frame(container, bg=bg_color)
        cards_frame.pack()
        
        suggestions = [
            {"icon": "🎨", "title": "Generate Image", "prompt": "Generate a futuristic cityscape with neon lights"},
            {"icon": "📝", "title": "Summarize", "prompt": "Summarize this document explicitly"},
            {"icon": "🐍", "title": "Python Script", "prompt": "Write a Python script to automate file organization"},
            {"icon": "💡", "title": "Explain Concept", "prompt": "Explain quantum computing in simple terms"}
        ]
        
        def create_card(parent, item, index):
             card = Frame(parent, bg="#f8f9fa", bd=1, relief="flat", width=200, height=120, cursor="hand2")
             card.pack_propagate(False) # Fixed size
             
             # Hover effect
             def on_enter(e): card.config(bg="#e8f0fe")
             def on_leave(e): card.config(bg="#f8f9fa")
             card.bind("<Enter>", on_enter)
             card.bind("<Leave>", on_leave)
             
             # Content
             icon = Label(card, text=item["icon"], font=("Segoe UI Emoji", 20), bg="#f8f9fa", fg="#5f6368",cursor='hand2')
             icon.pack(anchor="nw", padx=10, pady=(10, 0))
             
             title = Label(card, text=item["title"], font=("Arial", 11, "bold"), bg="#f8f9fa", fg="#202124",cursor='hand2')
             title.pack(anchor="nw", padx=10, pady=(5, 0))
             
             # Click bindings
             card.bind("<Button-1>", lambda e: command_callback(item["prompt"]))
             for child in card.winfo_children():
                 child.bind("<Button-1>", lambda e: command_callback(item["prompt"]))
                 # child.bind("<Enter>", lambda e: card.config(bg="#e8f0fe")) # Propagate hover?
             
             return card

        # Grid layout for cards (2x2)
        for i, item in enumerate(suggestions):
            card = create_card(cards_frame, item, i)
            row = i // 2
            col = i % 2
            card.grid(row=row, column=col, padx=10, pady=10)
            
        self.text.window_create(END, window=container)
        
        # Center the container in the Text widget?
        # Text widget alignment is tricky. verify `window_create` places it at current cursor.
        # We can center specific tag.
        self.text.tag_configure("center", justify='center')
        self.text.tag_add("center", "1.0", "end")
        
        self.text.config(state='disabled')
        
    def clear_welcome_cards(self):
        self.text.config(state='normal')
        self.text.delete(1.0, END)
        self.text.config(state='disabled')

    def clear_attachments(self):
         self.attachment_text.config(state='normal')
         self.attachment_text.delete(1.0, END)
         self.attachment_text.config(state='disabled')
         self.thumb_refs = []

    def toggle_history_panel(self):
        if self.history_visible:
            self.history_panel.grid_remove()
        else:
            self.history_panel.grid()
        self.history_visible = not self.history_visible

    def toggle_dark_mode(self, enabled):
        # Color Palettes
        THEME_LIGHT = {
            "bg": "powderblue",
            "text_bg": "white", "text_fg": "black",
            "frame_bg": "white",
            "card_bg": "#f8f9fa", "card_fg": "#202124",
            "card_hover": "#e8f0fe",
            "bubble_user": "#f0f0f0", "bubble_bot": "#white", # Bot usually transparent/white in text
            "sidebar_bg": "#f0f0f0",
            "input_bg": "white", "input_fg": "black"
        }
        
        THEME_DARK = {
            "bg": "#2e2e2e",
            "text_bg": "#1e1e1e", "text_fg": "#e0e0e0",
            "frame_bg": "#1e1e1e",
            "card_bg": "#2d2d2d", "card_fg": "#e0e0e0",
            "card_hover": "#3d3d3d",
            "bubble_user": "#2d2d2d", "bubble_bot": "#1e1e1e",
            "sidebar_bg": "#2e2e2e",
            "input_bg": "#2d2d2d", "input_fg": "white"
        }
        
        colors = THEME_DARK if enabled else THEME_LIGHT
        
        # 1. Main Shell
        self.root.config(bg=colors["bg"])
        self.title_label.config(background=colors["bg"] if enabled else "white") # Title label has specific styling
        self.time_lbl.config(background=colors["bg"] if enabled else "white", foreground="gold")
        self.hamburger_btn.config(bg=colors["text_bg"] if enabled else "white", activebackground=colors["text_bg"])
        
        # 2. Text Area
        self.text.config(bg=colors["text_bg"], fg=colors["text_fg"], insertbackground=colors["text_fg"])
        
        # Update Text Tags for Visibility
        if enabled:
             self.text.tag_configure("user_msg", foreground="#ffffff") # Bright white
             self.text.tag_configure("bot_label", foreground="#a069ff") # Light purple
             self.text.tag_configure("header_1", foreground="#a069ff")
             self.text.tag_configure("header_2", foreground="#b085ff")
        else:
             self.text.tag_configure("user_msg", foreground="#333333")
             self.text.tag_configure("bot_label", foreground="#6610f2")
             self.text.tag_configure("header_1", foreground="#2c3e50")
             self.text.tag_configure("header_2", foreground="#34495e")
        
        # 3. History Panel
        history_style = 'Dark.TFrame' if enabled else 'TFrame'
        self.history_panel.config(style=history_style)
        self.history_canvas.config(bg=colors["sidebar_bg"])
        self.history_list_frame.config(style=history_style)
        
        # 4. Embedded Widgets (Bubbles, Cards, Buttons)
        # Helper to recursively update widgets
        def update_widget_theme(widget):
            try:
                # GLOBAL EXCLUSION: Skip ANY widget that has an image content
                # This covers LaTeX labels, Thumbnails, etc.
                has_img = False
                try:
                    if str(widget.cget('image')) != "":
                        has_img = True
                except Exception:
                    pass
                
                if hasattr(widget, 'image') or has_img:
                    # print(f"DEBUG: Skipping dark mode update for image widget: {widget}")
                    return

                # Check widget type using winfo_class or isinstance
                w_class = widget.winfo_class()
                
                # Frames (Cards, Bubbles, Containers)
                if w_class == 'Frame':
                    # Heuristic: If it was white/light grey, make it dark. 
                    # If it was colorful (red/green buttons), keep it? 
                    # Use current bg to decide?
                    current_bg = widget.cget('bg')
                    
                    # Cards Logic (Welcome Screen)
                    if enabled:
                        if current_bg in ["#f8f9fa", "#e8f0fe", "white", "#f0f0f0"]:
                             widget.config(bg=colors["card_bg"])
                    else:
                        if current_bg in ["#2d2d2d", "#3d3d3d", "#1e1e1e"]:
                             widget.config(bg=colors["card_bg"])
                             
                # Labels (Text inside cards/bubbles)
                elif w_class == 'Label':
                    # Update FG/BG
                    widget.config(bg=widget.master.cget('bg')) # Match parent
                    
                    # Update Text Color
                    current_fg = widget.cget('fg')
                    if enabled:
                         if current_fg in ["black", "#202124", "#5f6368", "#333"]:
                             widget.config(fg=colors["text_fg"])
                         # Header special case
                         if "Hello," in widget.cget("text"):
                             widget.config(fg="#4285F4") # Keep blue
                    else:
                         if current_fg in ["#e0e0e0", "white"]:
                             widget.config(fg=colors["text_fg"])
                             
                # Buttons (Embedded ones)
                elif w_class == 'Button':
                     # Copy buttons etc.
                     if "📋" in widget.cget("text") or "🔊" in widget.cget("text") or "📷" in widget.cget("text"):
                         widget.config(bg=widget.master.cget('bg'), 
                                       fg=colors["text_fg"], 
                                       activebackground=widget.master.cget('bg'))
                
                # Recurse
                for child in widget.winfo_children():
                    update_widget_theme(child)
                    
            except Exception:
                pass

        # Iterate all windows embedded in Text widget
        for window_name in self.text.window_names():
            widget = self.text.nametowidget(window_name)
            update_widget_theme(widget)
            
           
            pass
        
        # 5. Input Area (If we access it, self.entry is Text)
        self.entry.config(bg=colors["input_bg"], fg=colors["input_fg"], insertbackground=colors["input_fg"])
        
        self.entry.master.config(bg=colors["input_bg"])
        
        # Attachment text
        self.attachment_text.config(bg=colors["bg"], fg=colors["text_fg"])

