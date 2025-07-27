import os
from time import strftime
from tkinter import *
from tkinter import ttk, messagebox,font
from tkinter import simpledialog
from PIL import Image, ImageTk
from pygame import mixer
import speech_recognition
from openai import OpenAI
import threading
from gtts import gTTS
import tempfile
from gtts.lang import tts_langs
import json
import re
import time
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)
latex_inline_pattern = re.compile(r'\\\((.*?)\\\)')
latex_block_pattern = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)
section_title_pattern = re.compile(r'^\d?\.*\s*\*\*(.*?)\*\*:', re.MULTILINE)

class ChatBot:

    def __init__(self, root):
        self.root = root
        self.root.title('HelpBot')
        self.root.geometry('1280x650+0+0')
        self.root.resizable(True, False)
        self.root.config(bg='powderblue')
        self.root.wm_iconbitmap('assets/chat.ico')
        self.root.bind('<Return>', self.enter_func)

        self.history_file = "chat_history.json"
        self.history_data = self.load_history()
        self.current_session = None
        self.session_messages = []
        self.search_var = StringVar()
        self.filtered_sessions = []  # holds filtered search results
        self.dark_mode_enabled = False
        self.root.bind('<Control-d>', lambda e: self.toggle_dark_mode())
        # self.root.after(1500, self.show_startup_tip)

        # Initialize cache
        self.response_cache = {}
        self.cache_file = "response_cache.json"
        self.CACHE_MIN_SIZE = 200 
        self.load_cache()
        
        # === ttk styles ===
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

        # === grid config ===
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # === title label ===
        img = Image.open('assets/chat.jpg').resize((100, 70), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)

        self.title_label = ttk.Label(self.root, image=self.photoimg, text="  Chat Me",
                                    anchor="w", compound=LEFT,
                                    font=('Arial', 24, 'bold'),
                                    style="Color.TLabel",padding=(37, 20, 0, 0))
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.hamburger_icon = ImageTk.PhotoImage(Image.open("assets/menu.png").resize((30, 30)))
        self.hamburger_btn = Button(self.title_label, image=self.hamburger_icon,
                                        command=self.toggle_history_panel,bd=0, bg='white',
                                    activebackground='white', cursor='hand2', )  
        self.hamburger_btn.place(x=5, y=5)


        self.back_btn = Button(self.title_label, text="Back", width=12, cursor='hand2', font=('times new roman', 10, 'bold'),
                          bg='red', fg='white', activebackground="green", command=self.back)
        self.back_btn.place(x=850, y=50, height=25)
       
        ToolTip(self.hamburger_btn, "Toggle History Panel")

        self.time_lbl = ttk.Label(self.title_label, font=('Arial', 18, 'bold'),
                                background='white', foreground='gold')
        self.time_lbl.place(x=500, y=15, width=200, height=45)
        self.update_time()

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
        self.right_click_menu.add_command(label="📋 Copy Selected Text", command=self.copy_selected_text)
        self.right_click_menu.add_command(label="🔊 Speak Selected Text", command=self.read_selected_text)

        # Bind right-click to open menu
        self.text.bind("<Button-3>", self.show_context_menu)

        # === button frame ===
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        for i in range(5):
            btn_frame.columnconfigure(i, weight=1)

        ttk.Label(btn_frame, text='Type Something:',background='#dcdad5', foreground='green',font=("Arial", 13, "bold")).grid(
            row=0, column=0, padx=(55,5), pady=5, sticky='w')

        self.entry = ttk.Entry(btn_frame, font=('Segoe UI Emoji', 13))
        self.entry.grid(row=0, column=1, columnspan=3, padx=(0,5), pady=5, sticky='ew')

        # Send Button
        self.send_btn = ttk.Button(btn_frame, text="Send>>", command=self.send, style="Color.TButton")
        self.send_btn.grid(row=0, column=4, padx=2, pady=5)

        self.spinner_label = Label(btn_frame, bg='#dcdad5')
        self.spinner_label.grid(row=0, column=5, padx=5)
        self.spinner_label.grid_remove()

        # === icon buttons ===
        self.photoimg2 = ImageTk.PhotoImage(Image.open("assets/Clear.png").resize((36, 36)))
        self.clear_btn = ttk.Button(btn_frame, text='Clear', image=self.photoimg2, compound=LEFT,
                                    command=self.clear, style="Color.TButton")
        self.clear_btn.grid(row=1, column=0, padx=5, pady=5)

        self.photoimg3 = ImageTk.PhotoImage(Image.open("assets/mic.png").resize((36, 36)))
        self.speak_btn = ttk.Button(btn_frame, text='Speak', image=self.photoimg3, compound=LEFT,
                                    command=self.speak, style="Color.TButton")
        self.speak_btn.grid(row=1, column=1, padx=5, pady=5)

        self.photoimg4 = ImageTk.PhotoImage(Image.open("assets/speaker.png").resize((36, 36)))
        self.read_btn = ttk.Button(btn_frame, text='Read All', image=self.photoimg4, compound=LEFT,
                                command=self.read_all_chat, style="Color.TButton")
        self.read_btn.grid(row=1, column=2, padx=5, pady=5)

        self.photoimg5 = ImageTk.PhotoImage(Image.open("assets/speaking.png").resize((36, 36)))
        self.read_selection_btn = ttk.Button(btn_frame, text='Speak Selected', image=self.photoimg5, compound=LEFT,
                                            command=self.read_selected_text, style="Color.TButton")
        self.read_selection_btn.grid(row=1, column=3, padx=5, pady=5)

        # === language dropdown ===
        self.bot_speak_language_code = "en"
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

        sorted_language_names = sorted(self.language_options.keys())
        self.language_var = StringVar()
        self.language_var.set("English" if "English" in sorted_language_names else sorted_language_names[0])

        self.language_combo = ttk.Combobox(btn_frame, textvariable=self.language_var,
                                        values=sorted_language_names, state="readonly", width=15)
        self.language_combo.grid(row=1, column=4, padx=5, pady=5, sticky='e')

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

        search_entry = ttk.Entry(search_row, textvariable=self.search_var, font=("Arial", 11))
        search_entry.grid(row=0, column=0, sticky='ew')
        search_button = ttk.Button(search_row, text="🔍", style="Color.TButton", width=3, command=self.update_search_results)
        search_button.grid(row=0, column=1, padx=(5, 0))

        # Also trigger search on typing
        self.search_var.trace_add("write", lambda *args: self.update_search_results())

        # === New Chat Button at Top ===
        new_chat_btn = ttk.Button(self.history_panel, text="🆕 New Chat", style="Color.TButton", command=self.new_chat)
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

        # Configure scrolling
        def on_history_frame_configure(event):
            self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))

        self.history_list_frame.bind("<Configure>", on_history_frame_configure)

        def on_mousewheel(event):
            self.history_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.bind_mousewheel(self.history_canvas, self.history_canvas)

        clear_btn = ttk.Button(self.history_panel, text="Clear All", command=self.clear_all_history, style="Color.TButton")
        clear_btn.grid(row=3, column=0, sticky="ew", pady=5)
        self.text.tag_config("code", background="#f0f0f0", font=("Courier New", 11))
        self.render_history()

    def show_startup_tip(self):
        message = (
            "💡 **Important Shortcuts & Tips** 💡\n\n"
            "• Press Ctrl + D to toggle Dark Mode\n"
            "• Right-click on chat to copy or speak text\n"
            "• Press Ctrl + S on tables to read selected\n"
            "• Press Ctrl + C on tables to copy selected\n"
            "• Use the 🔍 search in history panel to filter chats\n\n"
            "⚠️ *Note: Always use 'Temporary Chat' for quick queries.*\n"
            "❌ *Avoid clicking on 'New Chat' repeatedly unless you want to start fresh!*"
        )
        messagebox.showinfo("Welcome to HelpBot!", message, parent=self.root)

    def toggle_dark_mode(self):
        self.dark_mode_enabled = not self.dark_mode_enabled

        if self.dark_mode_enabled:
            self.root.config(bg='#2e2e2e')
            self.text.config(bg='#1e1e1e', fg='white', insertbackground='white')
            self.title_label.config(background='#2e2e2e')
            self.time_lbl.config(background='#2e2e2e')
            self.hamburger_btn.config(bg='black',activebackground='black')

            self.language_combo.config(background='#1e1e1e', foreground='white')
            self.history_panel.config(style='Dark.TFrame')
        else:
            self.root.config(bg='powderblue')
            self.text.config(bg='white', fg='black', insertbackground='black')
            self.title_label.config(background='white')
            self.time_lbl.config(background='white')
            self.hamburger_btn.config(bg='white',activebackground='white')

            self.language_combo.config(background='white', foreground='black')
            self.history_panel.config(style='TFrame')

    def back(self):
        self.root.destroy()

    def rename_session(self, index):
        session = self.history_data[index]
        new_title = simpledialog.askstring("Rename Chat", "Enter new chat title:", initialvalue=session["title"], parent=self.root)
        if new_title:
            session["title"] = new_title.strip()[:60]
            self.save_history()
            self.render_history()

    def new_chat(self):
        self.text.config(state='normal')
        self.text.delete(1.0, END)
        self.text.config(state='disabled')
        self.session_messages = []
        self.current_session = None
        self.entry.delete(0, END)

    def show_context_menu(self, event):
        try:
            self.text.tag_add("sel", "@%d,%d" % (event.x, event.y), "@%d,%d" % (event.x, event.y))
        except:
            pass  # no selection
        self.right_click_menu.tk_popup(event.x_root, event.y_root)
    
    def copy_selected_text(self):
        try:
            self.text.config(state='normal')
            selected_text = self.text.get(SEL_FIRST, SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.text.config(state='disabled')
        except Exception:
            messagebox.showinfo("Copy", "No text selected!", parent=self.root)

    def start_spinner(self):
        if not self.spinner_frames:
            return
        self.spinner_label.grid()
        self.spinner_running = True
        self.current_spinner_frame = 0
        self.animate_spinner()

    def animate_spinner(self):
        if not self.spinner_running:
            return
        frame = self.spinner_frames[self.current_spinner_frame]
        self.spinner_label.config(image=frame)
        self.current_spinner_frame = (self.current_spinner_frame + 1) % len(self.spinner_frames)
        self.root.after(100, self.animate_spinner)  # Adjust speed if needed

    def stop_spinner(self):
        self.spinner_running = False
        self.spinner_label.grid_remove()

    def load_cache(self):
        """Load cached responses from file if it exists"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.response_cache = json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.response_cache = {}

    def save_cache(self):
        """Save current cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.response_cache, f)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def read_selected_text(self):
        try:
            self.text.config(state='normal')
            selected_text = self.text.get(SEL_FIRST, SEL_LAST).strip()
            self.text.config(state='disabled')
        except Exception:
            messagebox.showinfo("Speak Selected", "No text selected!", parent=self.root)
            return

        if not selected_text:
            messagebox.showinfo("Speak Selected", "No text selected!", parent=self.root)
            return

        selected_lang_name = self.language_var.get()
        selected_lang_code = self.language_options.get(selected_lang_name, "en")
        self.speak_text_gtts(selected_text, selected_lang_code)

    def bind_mousewheel(self, widget, target_canvas):
        def on_enter(event):
            widget.bind_all("<MouseWheel>", lambda e: target_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
            widget.bind_all("<Shift-MouseWheel>", lambda e: target_canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))

        def on_leave(event):
            widget.unbind_all("<MouseWheel>")
            widget.unbind_all("<Shift-MouseWheel>")

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)

    def toggle_history_panel(self):
        if self.history_visible:
            self.history_panel.grid_remove()
        else:
            self.history_panel.grid()
        self.history_visible = not self.history_visible

    def enter_func(self, event):
        self.send_btn.invoke()
        self.entry.delete(0, END)
   
    def speak_text_gtts(self, text, lang_code):
        try:
            tts = gTTS(text=text, lang=lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                tts.save(temp_audio.name)
                temp_path = temp_audio.name

            mixer.init()
            mixer.music.load(temp_path)
            mixer.music.play()

            def wait_and_delete():
                try:
                    while mixer.music.get_busy():
                        continue
                    mixer.music.unload()
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Cleanup error: {e}")

            threading.Thread(target=wait_and_delete, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Speech Error", f"Could not play audio for '{lang_code}':\n{e}", parent=self.root)
   
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        with open(self.history_file, 'w') as f:

            json.dump(self.history_data, f)

    def delete_history_entry(self, index):
        del self.history_data[index]
        self.save_history()
        self.render_history()

    def clear_all_history(self):
        if messagebox.askyesno('Delete','Do you want to delete all records'):
            self.history_data = []
            self.save_history()
            self.render_history()
            self.text.config(state='normal')
            self.text.delete(1.0, END)
            self.text.config(bg='white')  # 👈 make it white here too
            self.text.config(state='disabled')

    def load_history_entry(self, text):
        self.entry.delete(0, END)
        self.entry.insert(0, text)

    def load_and_send_history_entry(self, text):
        self.load_history_entry(text)
        self.send_btn.invoke()

    def render_history(self):
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()

        if not self.history_data:
            placeholder = Label(self.history_list_frame,
                                text="🕳️ No chat sessions yet.",
                                bg='white', fg='gray',
                                font=('Arial', 11, 'italic'),
                                pady=10)
            placeholder.pack(anchor='center', pady=20)
            return

        sessions = self.filtered_sessions if self.search_var.get().strip() else self.history_data
        for index, session in enumerate(sessions):
            frame = Frame(self.history_list_frame, bg='white')
            frame.pack(fill=X, padx=5, pady=2)

            preview_text = f"{session['timestamp']} | {session['title'][:30]}..."
            label = Label(frame, text=preview_text, anchor='w', bg='white', fg='black',
                        font=('arial', 9), justify=LEFT)
            label.pack(side=LEFT, fill=X, expand=True)

            label.bind("<Button-1>", lambda e, i=index: self.load_session(i))

            menu_btn = Button(frame, text="⋯", font=("Arial", 10), bg='white', bd=0, cursor='hand2', command=lambda i=index: self.show_session_menu(i))
            menu_btn.pack(side=RIGHT, padx=3)

    def update_search_results(self):
        keyword = self.search_var.get().strip().lower()
        if keyword == "":
            self.filtered_sessions = []
        else:
            self.filtered_sessions = [
                s for s in self.history_data if keyword in s["title"].lower()
            ]
        self.render_history()

    def show_session_menu(self, index):
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="✏️ Rename", command=lambda: self.rename_session(index))
        menu.add_command(label="🗑️ Delete", command=lambda: self.delete_history_entry(index))

        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def load_session(self, index):
        self.current_session = self.history_data[index]
        self.session_messages = self.current_session["messages"][:]

        self.text.config(state='normal')
        self.text.delete(1.0, END)

        for msg in self.session_messages:
            if msg["role"] == "user":
                self.text.insert(END, f"\n\t\tYou Typed: {msg['content']}")
            elif msg["role"] == "assistant":
                self.render_bot_response(msg["content"])

        self.text.config(state='disabled')
  
    def send(self):
        user_input = self.entry.get().strip().lower()
        user_text = self.entry.get().strip()
        if user_input == '':
            messagebox.showerror('Error', 'Message must contain some content',parent=self.root)
            return
        
        self.send_btn.config(state=DISABLED, text="Loading...")
        self.start_spinner()
        self.entry.config(state=DISABLED)

        def process():
            self.text.config(state='normal')
            self.text.yview(END)
            self.text.insert(END, f"\n\t\tYou Typed: {self.entry.get()}")

            responses = {
                'hi': 'Hi',
                'how are you': 'I am fine. What about you?',
                'who made you?': 'I am a bot made by Dev, trained by Dev and LAMA.',
                'who created you?': 'I am a bot made by Dev, trained by Dev and LAMA.',
                "what's your name": 'My name is HelpBot. I always assist you.',
                'what is your name?': 'My name is HelpBot. I always assist you.',
                'what is your name': 'My name is HelpBot. I always assist you.'
            }

            if user_input in responses:
                response = responses[user_input]
            else:
                response = self.ask_openai(user_input)
               
            selected_lang_name = self.language_var.get()
            selected_lang_code = self.language_options.get(selected_lang_name, "en")

            self.entry.config(state=NORMAL)
            self.entry.delete(0, END)
            self.render_bot_response(response)
            timestamp = strftime('%I:%M:%S %p')

            # If no current session, create a new one
            if not self.current_session:
                self.current_session = {
                    "title": user_text[:25],
                    "messages": [],
                    "timestamp": timestamp
                }
                self.history_data.append(self.current_session)

            # Add current message to session
            self.current_session["messages"].append({"role": "user", "content": user_text})
            self.current_session["messages"].append({"role": "assistant", "content": response})

            # Update in-memory session context
            self.session_messages.append({"role": "user", "content": user_text})
            self.session_messages.append({"role": "assistant", "content": response})

            self.save_history()
            self.render_history()
            self.text.config(state='disabled')
            self.stop_spinner()
            self.send_btn.config(state=NORMAL, text="Send>>")
            
        threading.Thread(target=process).start()

    def remove_explanation_lines(self, code):
        """Removes all explanation lines and keeps only the actual code."""
        patterns = [
            r'#.*(you can|save this|run this|extension|\.py|when you run|output will be).*',
            r'"""[\s\S]*?"""',
            r"'''[\s\S]*?'''",
            r'#.*(example|note:|tip:|warning:).*'
        ]
        
        for pattern in patterns:
            code = re.sub(pattern, '', code, flags=re.IGNORECASE)
        
        # Only remove completely empty lines, not just whitespace ones
        lines = [line for line in code.split('\n') if line.strip() or line == '']
        return '\n'.join(lines).strip()

    def render_latex_equation(self, latex_expr):
        try:
            # Create the figure and render math
            fig, ax = plt.subplots(figsize=(0.01, 0.01))
            fig.patch.set_visible(False)
            ax.axis('off')
            ax.text(0.5, 0.5, f"${latex_expr}$", horizontalalignment='center',
                    verticalalignment='center', fontsize=16)

            # Save to temp file and close plot
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"latex_{int(time.time() * 1000)}.png")
            plt.savefig(temp_path, dpi=150, bbox_inches='tight', pad_inches=0.2)
            plt.close(fig)

            # Load image in main thread (from file)
            img = Image.open(temp_path)
            img = ImageTk.PhotoImage(img)
            os.remove(temp_path)

            # Embed into tkinter text widget
            image_label = Label(self.text, image=img, bg='white')
            image_label.image = img  # Keep reference
            self.text.window_create(END, window=image_label)
            self.text.insert(END, '\n')

        except Exception as e:
            print(f"LaTeX render error: {e}")

    def render_bot_response(self, response):
        self.text.config(state='normal')
        self.text.insert(END, "\n\nBot:\n")

        # Fix over-escaped LaTeX (\\frac → \frac, etc.)
        response = response.replace('\\\\', '\\')

        # Beautify step headers (### Step 1: ...)
        step_title_pattern = re.compile(r'###\s*(Step \d+:.*?)\n', re.IGNORECASE)
        response = step_title_pattern.sub(r'\n\n🧩 \1\n' + '-'*40 + '\n', response)

        # Replace numbered list (1.) with bullets for readability
        response = re.sub(r'^\s*\d+\.', '•', response, flags=re.MULTILINE)

        # Handle markdown-style headings (### Heading)
        heading_pattern = re.compile(r'^(#{2,})\s+(.*)', re.MULTILINE)
        response = heading_pattern.sub(lambda m: f"\n\n{'=' * len(m.group(1))} {m.group(2)} {'=' * len(m.group(1))}\n", response)

        # First extract all special content (code blocks, tables, LaTeX)
        content_blocks = []
        current_pos = 0

        # Find all special content in order
        for match in re.finditer(
            r'(\$\$.*?\$\$|\\\(.*?\\\)|```[\s\S]+?```|(?:\|.*\|[\r\n]+)+)', 
            response, 
            re.DOTALL
        ):
            # Add text before the special content
            if match.start() > current_pos:
                content_blocks.append(('text', response[current_pos:match.start()]))
            
            # Add the special content
            content = match.group(0)
            if content.startswith('$$'):
                content_blocks.append(('latex_block', content[2:-2].strip()))
            elif content.startswith(r'\('):
                content_blocks.append(('latex_inline', content[2:-2].strip()))
            elif content.startswith('```'):
                # Extract language and code
                lang_match = re.match(r'```(\w*)\n([\s\S]+?)```', content)
                if lang_match:
                    lang = lang_match.group(1).strip().lower() or "text"
                    code = self.remove_explanation_lines(lang_match.group(2)).strip()
                    content_blocks.append(('code', (lang, code)))
            elif '|' in content:  # Table
                content_blocks.append(('table', content.strip()))
            
            current_pos = match.end()

        # Add remaining text after last special content
        if current_pos < len(response):
            content_blocks.append(('text', response[current_pos:]))

        # Now render all content blocks in order
        for block_type, content in content_blocks:
            if block_type == 'text':
                if content.strip():
                    self.text.insert(END, content.strip() + "\n\n")
            elif block_type == 'latex_block':
                self.render_latex_equation(content)
                self.text.insert(END, '\n\n')
            elif block_type == 'latex_inline':
                self.render_latex_equation(content)
            elif block_type == 'code':
                lang, code = content
                self.insert_code_snippet(lang, code)
                self.text.insert(END, '\n\n')
            elif block_type == 'table':
                self.insert_markdown_table(content)
                self.text.insert(END, '\n\n')

        self.text.config(state='disabled')
 
    def insert_markdown_table(self, table_text):
        import tkinter as tk
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        if len(lines) < 2:
            return

        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        rows = []
        for line in lines[2:]:
            values = [v.strip() for v in line.split('|') if v.strip()]
            if len(values) == len(headers):
                rows.append(values)

        col_widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
        col_pixel_widths = [min(max(w * 7, 150), 400) for w in col_widths]

        # === OUTER table frame ===
        outer_frame = Frame(self.text, bg='white', bd=1, relief=SOLID)
        outer_frame.config(width=700, height=240)
        outer_frame.pack_propagate(False)

        # === Canvas for scrollable table ===
        canvas = Canvas(outer_frame, bg='white', highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        vsb = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        vsb.pack(side=RIGHT, fill=Y)

        hsb = ttk.Scrollbar(outer_frame, orient="horizontal", command=canvas.xview)
        hsb.pack(side=BOTTOM, fill=X)

        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # === Inner frame ===
        inner_frame = Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # === Scroll region binding ===
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if inner_frame.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure("all", width=inner_frame.winfo_reqwidth())

        inner_frame.bind("<Configure>", configure_scroll_region)

        self.bind_mousewheel(canvas, canvas)
        

        # === Headers ===
        for col_index, header in enumerate(headers):
            label = Label(inner_frame, text=header, bg="#4CAF50", fg="white",
                        font=("Arial", 10, "bold"), borderwidth=1, relief="solid",
                        padx=8, pady=4, wraplength=col_pixel_widths[col_index], justify=LEFT)
            label.grid(row=0, column=col_index, sticky="nsew")

        # === Cells ===
        for row_index, row_values in enumerate(rows, start=1):
            for col_index, value in enumerate(row_values):
                text_widget = Text(inner_frame, height=4, width=int(col_pixel_widths[col_index] / 7),
                                wrap=WORD, padx=6, pady=2, font=("Arial", 10),
                                bd=1, relief="solid", bg="white")
                text_widget.insert(END, value)
                text_widget.config(state=DISABLED)
                text_widget.grid(row=row_index, column=col_index, sticky="nsew")

                # Right-click to show menu for individual cell
                # Ctrl+S to speak selected text
                text_widget.bind("<Control-s>", lambda e, w=text_widget: (w.focus_set(), self.read_selected_text_from_widget(w)))
                text_widget.bind("<Control-c>", lambda e, w=text_widget: (w.focus_set(), self.copy_selected_text_from_widget(w)))



        for col in range(len(headers)):
            inner_frame.grid_columnconfigure(col, weight=1)

        # === Copy Button (outside canvas) ===
        copy_btn_text = tk.StringVar(value="📋 Copy")
        copy_btn = Button(outer_frame, textvariable=copy_btn_text,
                        font=("Arial", 6), bg="#e0e0e0", activebackground="#d0d0d0",
                        relief=FLAT, cursor="hand2",
                        command=lambda: self.copy_code_with_feedback(table_text, copy_btn_text))
        copy_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=3)

        self.text.window_create(END, window=outer_frame)
        self.text.insert(END, "\n\n")

    def read_selected_text_from_widget(self, widget):
        try:
            widget.focus_set()
            widget.config(state='normal')
            selected_text = widget.get(SEL_FIRST, SEL_LAST).strip()
            widget.config(state='disabled')
        except Exception:
            messagebox.showinfo("Speak Selected", "No text selected!", parent=self.root)
            return

        if not selected_text:
            messagebox.showinfo("Speak Selected", "No text selected!", parent=self.root)
            return

        selected_lang_name = self.language_var.get()
        selected_lang_code = self.language_options.get(selected_lang_name, "en")
        self.speak_text_gtts(selected_text, selected_lang_code)

    def copy_selected_text_from_widget(self, widget):
        try:
            widget.focus_set()
            widget.config(state='normal')
            selected_text = widget.get(SEL_FIRST, SEL_LAST)
            widget.config(state='disabled')
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except Exception:
            messagebox.showinfo("Copy", "No text selected!", parent=self.root)

    def insert_comparison_table(self, title, rows):
        """Insert a comparison table from text-based format"""
        table_frame = Frame(self.text, bg='white', bd=1, relief=SOLID)
        table_frame.pack_propagate(False)
        
        # Add title label
        title_label = Label(table_frame,
                        text=title,
                        font=("Arial", 11, "bold"),
                        bg="#4CAF50",
                        fg="white",
                        padx=10,
                        pady=5)
        title_label.pack(fill=X)
        
        # Create the Treeview
        tree = ttk.Treeview(table_frame, columns=["Aspect", "Details"], show="headings")
        tree.heading("Aspect", text="Aspect")
        tree.heading("Details", text="Details")
        tree.column("Aspect", width=150, anchor='w')
        tree.column("Details", width=500, anchor='w')
        
        # Add rows
        for aspect, details in rows:
            tree.insert('', 'end', values=(aspect, details))
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.text.window_create(END, window=table_frame)
            
    def insert_table(self, title, content):
        """Insert a formatted table into the chat window"""
        # Parse the table content
        rows = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Determine if it's a markdown-style table
        is_markdown_table = len(rows) > 1 and '|' in rows[0] and '|' in rows[1] and '---' in rows[1]
        
        if is_markdown_table:
            # Process markdown table
            headers = [h.strip() for h in rows[0].split('|') if h.strip()]
            rows = rows[2:]  # Skip header and separator lines
            
            # Create a frame for the table
            table_frame = Frame(self.text, bg='white', bd=1, relief=SOLID)
            table_frame.pack_propagate(False)
            
            # Add title label
            title_label = Label(table_frame, 
                            text=title,
                            font=("Arial", 11, "bold"),
                            bg="#4CAF50",
                            fg="white",
                            padx=10,
                            pady=5)
            title_label.pack(fill=X)
            
            # Create the table
            tree = ttk.Treeview(table_frame, columns=headers, show="headings")
            
            # Add headers
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=150, anchor='w')
            
            # Add rows
            for row in rows:
                if '|' in row:
                    values = [v.strip() for v in row.split('|') if v.strip()]
                    if len(values) == len(headers):
                        tree.insert('', 'end', values=values)
            
            # Add scrollbars
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Pack everything
            tree.pack(side=LEFT, fill=BOTH, expand=True)
            vsb.pack(side=RIGHT, fill=Y)
            hsb.pack(side=BOTTOM, fill=X)
            
            # Insert into the text widget
            self.text.window_create(END, window=table_frame)
            self.text.insert(END, '\n\n')
        else:
            # Process simple text-based table (one item per line)
            table_frame = Frame(self.text, bg='white', bd=1, relief=SOLID)
            table_frame.pack_propagate(False)
            
            # Add title label
            title_label = Label(table_frame, 
                            text=title,
                            font=("Arial", 11, "bold"),
                            bg="#4CAF50",
                            fg="white",
                            padx=10,
                            pady=5)
            title_label.pack(fill=X)
            
            # Create a text widget for the table
            table_text = Text(table_frame,
                            wrap=NONE,
                            font=("Arial", 10),
                            padx=5,
                            pady=5,
                            bd=0,
                            highlightthickness=0)
            
            # Add content
            for row in rows:
                # Highlight key-value pairs if they exist
                if ':' in row:
                    parts = row.split(':', 1)
                    table_text.insert(END, parts[0].strip() + ":\t", "bold")
                    table_text.insert(END, parts[1].strip() + "\n")
                else:
                    table_text.insert(END, "• " + row + "\n")
            
            table_text.tag_configure("bold", font=("Arial", 10, "bold"))
            table_text.config(state=DISABLED)
            
            # Add scrollbars
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table_text.yview)
            hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=table_text.xview)
            table_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Pack everything
            table_text.pack(side=LEFT, fill=BOTH, expand=True)
            vsb.pack(side=RIGHT, fill=Y)
            hsb.pack(side=BOTTOM, fill=X)
            
            # Insert into the text widget
            self.text.window_create(END, window=table_frame)
            self.text.insert(END, '\n\n')

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
        
        # Add copy button at top-right
        copy_btn_text = StringVar(value="📋 Copy")
        copy_btn = Button(code_frame,
                          textvariable=copy_btn_text,
                          font=("Arial", 8),
                          command=lambda c=code, btn=copy_btn_text: self.copy_code_with_feedback(c, btn),
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
    
    def apply_yaml_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        self.highlight_pattern(text_widget, r'^\s*[\w\-\.]+:', "keyword")  # Keys
        self.highlight_pattern(text_widget, r':\s*".*?"', "string")         # Quoted values
        self.highlight_pattern(text_widget, r':\s*\d+(\.\d+)?', "number")   # Numbers
        self.highlight_pattern(text_widget, r'#.*$', "comment")             # Comments

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

    def apply_markdown_highlighting(self, text_widget):
        text_widget.config(state=NORMAL)
        self.apply_common_highlighting(text_widget)

        self.highlight_pattern(text_widget, r'^#+\s.*$', "keyword")           # Headings
        self.highlight_pattern(text_widget, r'\*\*(.*?)\*\*', "string")       # Bold
        self.highlight_pattern(text_widget, r'\*(.*?)\*', "string")           # Italic
        self.highlight_pattern(text_widget, r'`[^`]+`', "number")             # Inline code
        self.highlight_pattern(text_widget, r'\[.*?\]\(.*?\)', "operator")    # Links

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

    def apply_common_highlighting(self, text_widget):
        """Common syntax elements for many languages"""
        # Configure basic tags
        text_widget.tag_config("keyword", foreground="blue", font=("Courier New", 11, "bold"))
        text_widget.tag_config("comment", foreground="green", font=("Courier New", 11, "italic"))
        text_widget.tag_config("string", foreground="#b58900")  # Orange
        text_widget.tag_config("number", foreground="#cb4b16")  # Red-orange
        text_widget.tag_config("operator", foreground="purple")

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

    def highlight_pattern(self, text_widget, pattern, tag):
        """Helper function to highlight text patterns"""
        start = "1.0"
        while True:
            pos = text_widget.search(pattern, start, stopindex=END, regexp=True)
            if not pos:
                break
            end = text_widget.index(f"{pos}+{len(text_widget.get(pos, f'{pos} lineend'))}c")
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

    def copy_code_with_feedback(self, code, text_var):
        self.root.clipboard_clear()
        self.root.clipboard_append(code)

        original_text = text_var.get()
        text_var.set("✔ Copied")

        def reset():
            time.sleep(2)
            text_var.set(original_text)

        threading.Thread(target=reset, daemon=True).start()

    def insert_code_block(self, code):
        self.text.insert(END, '\n')
        start_index = self.text.index(END)
        self.text.insert(END, code + '\n')
        end_index = self.text.index(END)

        self.text.tag_add("code", start_index, end_index)
        self.text.tag_config("code", background="#f4f4f4", foreground="black", font=("Courier New", 11, "normal"))

        copy_btn = Button(self.text, text="📋 Copy", font=("arial", 8, "bold"),
                        bg="white", fg="blue", bd=1, cursor="hand2",
                        command=lambda c=code: self.root.clipboard_clear() or self.root.clipboard_append(c))
        self.text.window_create(end_index, window=copy_btn)

    def clear(self):
        self.text.config(state='normal')
        self.entry.delete(0, END)
        self.text.delete(1.0, END)
        self.text.config(state='disabled')

    def speak(self):
        mixer.init()
        mixer.music.load('assets/beep.mp3')
        mixer.music.play()
        sr = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as m:
            try:
                sr.adjust_for_ambient_noise(m, duration=0.2)
                audio = sr.listen(m)
                text = sr.recognize_google(audio)
                self.entry.insert(0, text)
            except Exception as e:
                messagebox.showerror('Speech Recognition Error', f'Sorry, your speech was not recognized: {str(e)}', parent=self.root)

    def read_all_chat(self):
        full_chat_text = self.text.get(1.0, END).strip()
        if not full_chat_text:
            messagebox.showwarning('Empty', 'No chat content to read!', parent=self.root)
            return

        selected_lang_name = self.language_var.get()
        selected_lang_code = self.language_options.get(selected_lang_name, "en")
        self.speak_text_gtts('So far we have talked about: ' + full_chat_text, selected_lang_code)

    def ask_openai(self, prompt):
        try:
            # Append user prompt to session context
            self.session_messages.append({"role": "user", "content": prompt})

            # Combine system + last 10 turns of context
            messages = [
                {"role": "system", "content": (
                "You are a helpful, friendly, and intelligent female assistant named HelpBot. "
                "Speak in a polite and empathetic manner. When explaining math or physics, use LaTeX format. "
                "Always format inline math with \\(...\\) and block equations with $$...$$. "
                "Do not use single dollar signs ($) for LaTeX, as it causes rendering issues in the user's environment. "
                "Do not explain how LaTeX works — just format it directly."
                 )}] + self.session_messages[-10:]

            # Check cache first
            if prompt in self.response_cache:
                return self.response_cache[prompt]

            # Make OpenAI API request
            completion = client.chat.completions.create(
                extra_headers={"X-Title": "HelpBot"},
                model="mistralai/mistral-small-3.2-24b-instruct:free",
                messages=messages
            )

            response = completion.choices[0].message.content.strip()

            # Add assistant reply to session context
            self.session_messages.append({"role": "assistant", "content": response})

            # --- Long Response Caching ---
            word_count = len(response.split())
            if word_count >= 200:
                self.response_cache[prompt] = response

                # Enforce max 10 cache entries
                if len(self.response_cache) > 10:
                    first_key = next(iter(self.response_cache))
                    del self.response_cache[first_key]

                self.save_cache()

            return response

        except Exception as e:
            print(e)
            return f"OpenRouter error: {str(e)}"

class ToolTip(object):
    def __init__(self, widget, text='widget info', wraplength=300):
        self.widget = widget
        self.text = text
        self.wraplength = wraplength
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 30
        y += self.widget.winfo_rooty() + 30
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = Label(tw, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=('tahoma', 9), wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

if __name__ == '__main__':
    root = Tk()
    obj = ChatBot(root)
    root.mainloop()