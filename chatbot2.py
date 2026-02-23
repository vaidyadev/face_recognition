import os
from time import strftime
from tkinter import *
from tkinter import ttk, messagebox, font
from tkinter import simpledialog, filedialog
import threading
import json
import re
from modules import database, ai_chat, history, audio, syntax_highlighter, ui_utils, ui_layout
from modules.settings_manager import SettingsManager
from utils import resource_path

class ChatBot:

    def __init__(self, root):
        self.root = root
        
        # Initialize Settings Manager
        self.settings_manager = SettingsManager()

        # Define callbacks to pass to UI
        callbacks = {
            'send': self.send,
            'clear': self.clear,
            'speak': self.speak,
            'read_all': self.read_all_chat,
            'speak_selected': self.read_selected_text,
            'copy_selected': self.copy_selected_text,
            'toggle_history': self.toggle_history_panel,
            'back': self.back,
            'update_search': self.update_search_results,
            'new_chat': self.new_chat,
            'export_history': self.export_history_dialog,
            'clear_history': self.clear_all_history,
            'add_attachment': self.add_attachment,
            # Settings Callbacks
        # Settings Callbacks
            'get_current_language': lambda: self.settings_manager.get("language", "en"),
            'get_current_model': lambda: self.settings_manager.get("model", "openai/gpt-oss-120b:free"),
            'get_current_theme': lambda: self.settings_manager.get("theme_mode", "System Default"),
            'get_reasoning_enabled': lambda: self.settings_manager.get("reasoning_enabled", True),
            'get_thinking_budget': lambda: self.settings_manager.get("thinking_budget", 1024),
            'save_settings': self.save_settings_callback,
            'show_help': self.show_help,
            'open_settings': self.open_settings_current,
            'show_help': self.show_help,
            'open_settings': self.open_settings_current,
            'focus_search': self.focus_search,
            'toggle_search': self.toggle_search
        }
        
        # Initialize UI
        # Initialize UI
        self.ui = ui_layout.ChatBotUI(root, callbacks)
        
        # === Keyboard Shortcuts ===
        self.root.bind('<Control-Enter>', lambda e: self.send())
        self.root.bind('<Control-d>', lambda e: self.toggle_dark_mode())
        self.root.bind('<Control-l>', lambda e: self.clear())
        self.root.bind('<Control-h>', lambda e: self.show_help())
        self.root.bind('<Control-t>', lambda e: self.toggle_history_panel())
        self.root.bind('<Control-n>', lambda e: self.new_chat())
        self.root.bind('<Control-o>', lambda e: self.add_attachment())
        self.root.bind('<Control-m>', lambda e: self.speak())
        self.root.bind('<Control-r>', lambda e: self.read_all_chat())
        self.root.bind('<Escape>', lambda e: self.back())
        self.root.bind('<Control-e>', lambda e: self.export_history_dialog())
        self.root.bind('<Control-Shift-Delete>', lambda e: self.clear_all_history())
        self.root.bind('<Control-f>', lambda e: self.focus_search())
        self.root.bind('<Control-w>', lambda e: self.ui.toggle_search_button())
        self.root.bind('<Control-comma>', lambda e: self.open_settings_current())
        
        self.root.protocol("WM_DELETE_WINDOW", self.back)
        
        self.history_file = resource_path("chat_history.json")
        
        
        self.history_data = history.load_history(self.history_file)
        self.current_session = None
        self.session_messages = []
        self.filtered_sessions = []
        
        # Configure Chat Styles (Moved before theme application)
        self.ui.text.tag_configure("user_msg", justify='right', foreground="#333", spacing1=5, spacing3=5, font=("Segoe UI Emoji", 12))
        self.ui.text.tag_configure("bot_label", justify='left', foreground="#6610f2", spacing1=10, spacing3=2, font=("Segoe UI Emoji", 12, "bold"))
        self.ui.text.tag_configure("spinner", justify='left')

        self.ui.text.tag_configure("spinner", justify='left')

        # Theme Initialization
        self.dark_mode_enabled = False # Logic state
        self.apply_theme(self.settings_manager.get("theme_mode", "System Default"))

        # Show Welcome Cards on Startup (After Theme)
        self.ui.render_welcome_cards(self.handle_card_click)
        
        # Initialize cache
        self.cache_file = resource_path("response_cache.json")
        self.response_cache = ai_chat.load_cache(self.cache_file)
        
        # Sticky Gemini State
        self.sticky_gemini_turns = 0
        self.gemini_chat_session = None
        
        # Initialize Syntax Highlighter
        self.syntax_highlighter = syntax_highlighter.SyntaxHighlighter(self.ui.text, self.root)
        
        self.update_time()
        
        # Audio State
        self.current_speaking_btn = None
        self.chat_spinner_label = None
        
        self.attachments = []
        
        self.search_enabled = False
        
        self.render_history()
        # self.show_startup_tip()
        # self.show_help()

    def _get_system_theme(self):
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            print("Light" if value == 1 else "Dark")
            return "Light" if value == 1 else "Dark"
        except Exception:
            print("fallback")
            return "Light" # Default fallback

    def apply_theme(self, mode):
        # Determine actual visual mode
        target_mode = mode
        if mode == "System Default":
            target_mode = self._get_system_theme()
        
        is_dark = (target_mode == "Dark")
        self.dark_mode_enabled = is_dark
        self.ui.toggle_dark_mode(is_dark)

    def _reset_entry_style(self):
        """Resets entry style based on current theme"""
        color = 'white' if self.dark_mode_enabled else 'black'
        self.ui.entry.config(fg=color)

    def save_settings_callback(self, new_settings):
        # Check if theme changed
        old_theme = self.settings_manager.get("theme_mode", "System Default")
        new_theme = new_settings.get("theme_mode", old_theme)
        
        self.settings_manager.save_settings(new_settings)
        
        # Apply new theme immediately
        self.apply_theme(new_theme)

    def show_startup_tip(self):
        message = (
            "🤖 **Model Usage Instructions** 🤖\n\n"
            "🔹 **gpt-oss-120b**: Use for general chat, coding,searching,and reasoning tasks.\n"
            "🔹 **SeedDream**: Use for editing and creating images.\n"
            "🔹 **Gemini**: Use for analyzing documents and uploaded photos to get information about their content.\n\n"
            "⌨️ **Shortcuts**:\n"
            "• Ctrl + Enter : Send Message | Ctrl + L : Clear Chat\n"
            "• Ctrl + O : Add Attachment | Ctrl + M : Voice Input\n"
            "• Ctrl + N : New Chat | Ctrl + T : Toggle History\n"
            "• Ctrl + F : Search History | Ctrl + E : Export History\n"
            "• Ctrl + R : Read All | Ctrl + D : Dark Mode\n"
            "• Ctrl + H : Show Help | Ctrl + , : Settings\n"
            "• Ctrl + Shift + Delete : Clear All History\n"
            "• Ctrl + W : Search\n"
            "• Esc : Exit/Back"
        )
        messagebox.showinfo("Welcome to HelpBot!", message, parent=self.root)

        self.render_history()
        
    def handle_card_click(self, prompt):
        self.ui.entry.delete("1.0", END)
        self.ui.entry.insert("1.0", prompt)
        self._reset_entry_style()
        self.ui.entry.focus_set()

    def show_help(self):
        help_text = (
            "🤖 **Model Usage Instructions** 🤖\n\n"
            "🔹 **gpt-oss-120b**: Use for general chat, coding,searching,and reasoning tasks.\n"
            "🔹 **SeedDream**: Use for editing and creating images.\n"
            "🔹 **Gemini**: Use for analyzing documents and uploaded photos to get information about their content.\n\n"
            "⌨️ **Shortcuts**:\n"
            "• Ctrl + Enter : Send Message | Ctrl + L : Clear Chat\n"
            "• Ctrl + O : Add Attachment | Ctrl + M : Voice Input\n"
            "• Ctrl + N : New Chat | Ctrl + T : Toggle History\n"
            "• Ctrl + F : Search History | Ctrl + E : Export History\n"
            "• Ctrl + R : Read All | Ctrl + D : Dark Mode\n"
            "• Ctrl + H : Show Help | Ctrl + , : Settings\n"
             "• Ctrl + Shift + Delete : Clear All History\n"
            "• Ctrl + W : Search\n"
            "• Esc : Exit/Back"
        )
        messagebox.showinfo("Chatbot Help", help_text, parent=self.root)

    def focus_search(self):
        if not self.ui.history_visible:
            self.ui.toggle_history_panel()
        self.ui.search_entry.focus_set()

    def open_settings_current(self):
        self.ui.open_settings_window()

    def toggle_dark_mode(self):
        # Toggling via shortcut now sets explicit preference
        # If currently Dark -> Light
        # If currently Light -> Dark
        new_mode = "Light" if self.dark_mode_enabled else "Dark"
        
        # Update settings so it persists
        current_settings = self.settings_manager.settings
        current_settings["theme_mode"] = new_mode
        self.settings_manager.save_settings(current_settings)
        
        self.apply_theme(new_mode)

    def back(self):
        audio.stop_speech()
        self.root.destroy()

    def rename_session(self, index):
        self._show_rename_dialog(index)

    def _show_rename_dialog(self, index):
        session = self.history_data[index]
        current_title = session["title"]
        
        # Theme colors
        is_dark = getattr(self.ui, 'is_dark', False)
        bg_color = "#2d2d2d" if is_dark else "white"
        fg_color = "white" if is_dark else "black"
        entry_bg = "#404040" if is_dark else "white"
        entry_fg = "white" if is_dark else "black"
        btn_bg = "#4CAF50" # Green for save
        cancel_bg = "#dc3545" # Red for cancel

        # Dialog Window
        dialog = Toplevel(self.root)
        dialog.title("Rename Chat")
        dialog.geometry("400x180")
        dialog.wm_iconbitmap(resource_path('assets/chat.ico'))
        dialog.config(bg=bg_color)
        dialog.resizable(False, False)
        
        # Center dialog
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 90
        dialog.geometry(f"+{x}+{y}")
        
        # UI Elements
        Label(dialog, text="Enter new chat title:", font=("Arial", 11), bg=bg_color, fg=fg_color).pack(pady=(20, 10))
        
        entry = Entry(dialog, font=("Arial", 11), bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
        entry.pack(fill=X, padx=30, pady=5)
        entry.insert(0, current_title)
        entry.focus_set()
        
        btn_frame = Frame(dialog, bg=bg_color)
        btn_frame.pack(pady=20)
        
        def save():
            new_title = entry.get().strip()
            if new_title:
                session["title"] = new_title[:60]
                history.save_history(self.history_file, self.history_data)
                self.render_history()
            dialog.destroy()
            
        Button(btn_frame, text="Save", bg=btn_bg, fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=save).pack(side=LEFT, padx=10)
        Button(btn_frame, text="Cancel", bg=cancel_bg, fg="white", font=("Arial", 10), bd=0, padx=15, pady=5, cursor="hand2", command=dialog.destroy).pack(side=LEFT, padx=10)
        
        dialog.bind("<Return>", lambda e: save())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def new_chat(self):
        self.session_messages = []
        self.current_session = None
        
        self.ui.entry.delete("1.0", END)
        # self.ui.entry.insert("1.0", self.ui.placeholder_text) # Placeholder removed
        self._reset_entry_style()

        self.attachments = []
        self.ui.clear_attachments()
        
        # Render Welcome Cards
        self.ui.render_welcome_cards(self.handle_card_click)
    
    def copy_selected_text(self):
        try:
            self.ui.text.config(state='normal')
            selected_text = self.ui.text.get(SEL_FIRST, SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.ui.text.config(state='disabled')
            
            # Show floating "Copied!" indicator
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            
            float_copy = Toplevel(self.root)
            float_copy.wm_overrideredirect(True)
            float_copy.geometry(f"+{x+10}+{y+10}")
            float_copy.attributes("-topmost", True)
            
            is_dark = getattr(self.ui, 'is_dark', False)
            bg_color = "#4CAF50" # Green
            fg_color = "white"
            
            float_copy.config(bg=bg_color)
            
            lbl = Label(float_copy, text="✔ Copied!", font=("Arial", 9, "bold"), 
                       bg=bg_color, fg=fg_color, padx=8, pady=4)
            lbl.pack()
            
            self.root.after(1500, float_copy.destroy)
            
        except Exception:
            messagebox.showinfo("Copy", "No text selected!", parent=self.root)

    def start_spinner(self):
        if not self.ui.spinner_frames:
            return
        
        self.ui.text.config(state='normal')
        self.ui.text.insert(END, "\n") # Spacing
        
        # Create spinner label inside text widget
        # Using a Frame to center or style if needed, but Label is fine
        spinner_bg = "#1e1e1e" if self.ui.is_dark else "white"
        self.chat_spinner_label = Label(self.ui.text, bg=spinner_bg, image=self.ui.spinner_frames[0], bd=0)
        self.ui.text.window_create(END, window=self.chat_spinner_label)
        self.ui.text.insert(END, "\n")
        # Ensure spinner is left-aligned by removing user_msg tag if inherited
        self.ui.text.tag_remove("user_msg", "end-3c", "end") 
        self.ui.text.tag_add("spinner", "end-2c", "end")
        self.ui.text.see(END) # Scroll to bottom
        self.ui.text.config(state='disabled')
        
        self.spinner_running = True
        self.current_spinner_frame = 0
        self.animate_spinner()

    def animate_spinner(self):
        if not self.spinner_running or not self.chat_spinner_label:
            return
        try:
            frame = self.ui.spinner_frames[self.current_spinner_frame]
            self.chat_spinner_label.config(image=frame)
            self.current_spinner_frame = (self.current_spinner_frame + 1) % len(self.ui.spinner_frames)
            self.root.after(100, self.animate_spinner)
        except Exception:
            self.spinner_running = False

    def stop_spinner(self):
        self.spinner_running = False
        if self.chat_spinner_label:
            try:
               
                self.chat_spinner_label.destroy()
                self.chat_spinner_label = None
                
                
            except:
                pass

    def read_selected_text(self):
        try:
            self.ui.text.config(state='normal')
            selected_text = self.ui.text.get(SEL_FIRST, SEL_LAST).strip()
            self.ui.text.config(state='disabled')
        except Exception:
            messagebox.showinfo("Speak Selected", "No text selected!", parent=self.root)
            return

        if not selected_text:
            messagebox.showinfo("Speak Selected", "No text selected!", parent=self.root)
            return

        selected_lang_code = self.settings_manager.get("language", "en")
        
        audio.stop_speech()
        
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        
        floating_win = Toplevel(self.root)
        floating_win.wm_overrideredirect(True)
        floating_win.geometry(f"+{x+15}+{y+15}")
        floating_win.attributes("-topmost", True)
        floating_win.config(bg="#4285F4")
        
        floating_btn = Button(floating_win, text="⏹️ Stop Speaking", font=("Arial", 10, "bold"),
                          bg="#4285F4", fg="white", activebackground="#3367D6", activeforeground="white",
                          bd=0, cursor="hand2", padx=10, pady=5)
        floating_btn.pack()
        
        self.current_speaking_btn = floating_btn
        
        def on_floating_stop():
            audio.stop_speech()
            try:
                floating_win.destroy()
            except:
                pass
            if self.current_speaking_btn == floating_btn:
                self.current_speaking_btn = None
                
        floating_btn.config(command=on_floating_stop)
        
        def on_floating_complete():
            try:
                floating_win.destroy()
            except:
                pass
            if self.current_speaking_btn == floating_btn:
                self.current_speaking_btn = None
                
        audio.speak_text_gtts(selected_text, selected_lang_code, self.root, on_finish=on_floating_complete)

    def toggle_speech(self, text, btn):
        # 1. Stop current
        audio.stop_speech()
        
        # 2. If valid button passed, reset previous button if exists
        if self.current_speaking_btn and self.current_speaking_btn != btn:
             self.reset_speech_button(self.current_speaking_btn)
             self.current_speaking_btn = None
        
        # 3. If clicking the SAME button that is active -> It was a Stop command. Done.
        if btn and btn == self.current_speaking_btn:
            self.reset_speech_button(btn)
            self.current_speaking_btn = None
            return

        # 4. Starting new speech
        if btn:
            # Change icon to Stop
            if btn == self.ui.read_btn:
                # Read All button
                 # We can't easily change image on the fly without keeping references, 
                 # but for emoji buttons (text) it is easy.
                 # ui_layout uses emoji for read_btn now: "🔊"
                 btn.config(text="⏹️", bg="#dc3545") # Red for stop
            else:
                 # Chat message buttons
                 btn.config(text="⏹️")
            
            self.current_speaking_btn = btn
            
        selected_lang_code = self.settings_manager.get("language", "en")
        
        def on_complete():
            if btn:
                self.reset_speech_button(btn)
                if self.current_speaking_btn == btn:
                    self.current_speaking_btn = None
        
        audio.speak_text_gtts(text, selected_lang_code, self.root, on_finish=on_complete)

    def reset_speech_button(self, btn):
        if not btn: return
        try:
             if btn == self.ui.read_btn:
                 btn.config(text="🔊", bg='#6610f2') # Original purple
             else:
                 btn.config(text="🔊")
        except:
             pass

    def copy_to_clipboard(self, text, btn=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        if btn:
            original_text = "📋" # Assuming it was the clipboard icon
            btn.config(text="✔ Copied")
            
            def reset():
                try:
                    btn.config(text=original_text)
                except:
                    pass
            self.root.after(2000, reset)

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.ui.time_lbl.config(text=current_time)
        self.ui.time_lbl.after(1000, self.update_time)

    def toggle_history_panel(self):
        self.ui.toggle_history_panel()
    
    def delete_history_entry(self, index):
        if not messagebox.askyesno("Delete", "Delete this chat?", parent=self.root):
           return

        session_to_delete = self.history_data[index]
        was_current = (self.current_session == session_to_delete)
        
        del self.history_data[index]
        history.save_history(self.history_file, self.history_data)
        self.render_history()

        if was_current:
            self.current_session = None
            self.session_messages = []
            self.attachments = []
            self.ui.clear_attachments()
            
            self.ui.text.config(state='normal')
            self.ui.text.delete(1.0, END)
            self.ui.text.config(state='disabled')
            
            self.ui.entry.delete("1.0", END)
            # self.ui.entry.insert("1.0", self.ui.placeholder_text) 
            self._reset_entry_style()

    def export_history_dialog(self, parent=None):
        target_parent = parent if parent else self.root
        if not self.history_data:
            messagebox.showinfo("Export", "No history to export!", parent=target_parent)
            return

        timestamp = strftime('%Y%m%d_%H%M%S')
        default_filename = f"chat_history_{timestamp}"
        
        file_types = [
            ("PDF Document", "*.pdf"),
            ("Text File", "*.txt"),
            ("JSON Data", "*.json"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=file_types,
            initialfile=default_filename,
            title="Export History",
            parent=target_parent
        )

        if not file_path:
            return

        try:
            if file_path.lower().endswith('.pdf'):
                history.generate_pdf(file_path, self.history_data)
            elif file_path.lower().endswith('.txt'):
                history.generate_txt(file_path, self.history_data)
            elif file_path.lower().endswith('.json'):
                history.generate_json(file_path, self.history_data)
            else:
                history.generate_txt(file_path + ".txt", self.history_data)
            
            messagebox.showinfo("Success", f"History exported successfully to:\n{file_path}", parent=target_parent)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export history:\n{str(e)}", parent=target_parent)

    def clear_all_history(self, parent=None):
        target_parent = parent if parent else self.root
        if messagebox.askyesno('Delete','Do you want to delete all records', parent=target_parent):
            if True: # Bypass confirmation for testing
                self.history_data = []
                history.save_history(self.history_file, self.history_data)
                self.render_history()
                
                # Reset current session state
                self.current_session = None
                self.session_messages = []
                self.attachments = []
                self.ui.clear_attachments()
                
                # Show Welcome Cards instead of blank
                self.ui.render_welcome_cards(self.handle_card_click)
                
                # Reset entry
                self.ui.entry.delete("1.0", END)
                # self.ui.entry.insert("1.0", self.ui.placeholder_text) # Removed
                self._reset_entry_style()

    def render_history(self):
        for widget in self.ui.history_list_frame.winfo_children():
            widget.destroy()

        # Determine colors based on current theme
        is_dark = getattr(self.ui, 'is_dark', False)
        bg_color = "#2d2d2d" if is_dark else "white"
        fg_color = "white" if is_dark else "black"
        hover_bg = "#3d3d3d" if is_dark else "#f0f0f0" # Optional hover color

        if not self.history_data:
            placeholder = Label(self.ui.history_list_frame,
                                text="🕳️ No chat sessions yet.",
                                bg=bg_color, fg='gray',
                                font=('Arial', 11, 'italic'),
                                pady=10)
            placeholder.pack(anchor='center', pady=20)
            return

        sessions = self.filtered_sessions if self.ui.search_var.get().strip() else self.history_data
        for index, session in enumerate(sessions):
            frame = Frame(self.ui.history_list_frame, bg=bg_color)
            frame.pack(fill=X, padx=5, pady=2)

            preview_text = f"{session['timestamp']} | {session['title'][:30]}..."
            label = Label(frame, text=preview_text, anchor='w', bg=bg_color, fg=fg_color,
                        font=('arial', 9), justify=LEFT)
            label.pack(side=LEFT, fill=X, expand=True)

            label.bind("<Button-1>", lambda e, i=index: self.load_session(i))

            menu_btn = Button(frame, text="⋯", font=("Arial", 10), bg=bg_color, fg=fg_color, bd=0, cursor='hand2', command=lambda i=index: self.show_session_menu(i))
            menu_btn.pack(side=RIGHT, padx=3)

    def update_search_results(self):
        keyword = self.ui.search_var.get().strip().lower()
        if keyword == "":
            self.filtered_sessions = []
        else:
            self.filtered_sessions = [
                s for s in self.history_data if keyword in s["title"].lower()
            ]
        self.render_history()

    def show_session_menu(self, index):
        # Determine colors based on theme
        is_dark = getattr(self.ui, 'is_dark', False)
        bg_color = "#2d2d2d" if is_dark else "white"
        fg_color = "white" if is_dark else "black"
        active_bg = "#3d3d3d" if is_dark else "#e0e0e0"
        active_fg = "white" if is_dark else "black"

        menu = Menu(self.root, tearoff=0, bg=bg_color, fg=fg_color, 
                   activebackground=active_bg, activeforeground=active_fg)
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

        self.ui.text.config(state='normal')
        self.ui.text.delete(1.0, END)
        self.ui.text.config(state='disabled')

        # Create a copy of messages to process
        msg_queue = self.session_messages[:]
        
        def process_queue():
            if not msg_queue:
                return

            msg = msg_queue.pop(0)
            
            if msg["role"] == "user":
                if 'attachments' in msg and msg['attachments']:
                     self.ui.render_attachments_in_chat(msg['attachments'])

                self.ui.text.config(state='normal')
                content = msg['content']
                self.ui.text.insert(END, f"\n{content} 👤\n", "user_msg")
                
                # Copy Button Frame
                # Capture start index to ensure tag is applied correctly
                btn_start = self.ui.text.index(END)

                # Theme-aware colors
                is_dark = self.dark_mode_enabled
                theme_bg = "#1e1e1e" if is_dark else "white"
                theme_fg = "#e0e0e0" if is_dark else "black"
                theme_active = "#2d2d2d" if is_dark else "#f0f0f0"

                btn_frame = Frame(self.ui.text, bg=theme_bg)
                copy_btn = Button(btn_frame, text="📋", font=("Segoe UI Emoji", 9), cursor="hand2",
                                  bd=0, bg=theme_bg, fg=theme_fg, activebackground=theme_active, activeforeground=theme_fg)
                copy_btn.config(command=lambda b=copy_btn, c=content: self.copy_to_clipboard(c, b))
                copy_btn.pack(side=RIGHT, padx=5)
                
                # Speak User
                speak_btn = Button(btn_frame, text="🔊", font=("Segoe UI Emoji", 9), cursor="hand2",
                                  bd=0, bg=theme_bg, fg=theme_fg, activebackground=theme_active, activeforeground=theme_fg)
                speak_btn.config(command=lambda b=speak_btn, c=content: self.toggle_speech(c, b))
                speak_btn.pack(side=RIGHT, padx=5)
                
                self.ui.text.window_create(END, window=btn_frame)
                self.ui.text.insert(END, "\n")

                # Fix alignment by ensuring user_msg tag covers the button line
                self.ui.text.tag_remove("bot_label", btn_start, END)
                self.ui.text.tag_add("user_msg", btn_start, END)
                
                self.ui.text.config(state='disabled')
                # Schedule next message immediately
                self.root.after(1, process_queue)
            elif msg["role"] == "assistant":
                # Render response and wait for it to complete before next message
                self.render_bot_response(msg["content"], on_complete=process_queue)

        # Start processing
        process_queue()

    def send(self):
        # Handle Text widget instead of Entry
        user_input = self.ui.entry.get("1.0", END).strip().lower()
        user_text = self.ui.entry.get("1.0", END).strip()
        
        if user_input == '':
            messagebox.showerror('Error', 'Message must contain some content',parent=self.root)
            return
        
        # Disable button, but don't change text since it's an icon now
        self.ui.send_btn.config(state=DISABLED) 
        
        if not self.current_session:
             # Clear welcome screen if this is the first message
             self.ui.clear_welcome_cards()
             
             timestamp = strftime('%Y-%m-%d %I:%M:%S %p')
             self.current_session = {
                "title": user_text[:25],
                "messages": [],
                "timestamp": timestamp
            }
             self.history_data.append(self.current_session)

        if self.attachments:
             self.ui.render_attachments_in_chat(self.attachments)

        # Update UI first (User message)
        self.ui.text.config(state='normal')
        self.ui.text.yview(END)
        self.ui.text.insert(END, f"\n{user_text} 👤\n", "user_msg")
        
        # Inject Copy Button for User
        def copy_user(btn):
             self.copy_to_clipboard(user_text, btn)
             
        # Copy Button Frame (Below message, Right Aligned)
        # Theme-aware colors
        is_dark = self.dark_mode_enabled
        theme_bg = "#1e1e1e" if is_dark else "white"
        theme_fg = "#e0e0e0" if is_dark else "black"
        theme_active = "#2d2d2d" if is_dark else "#f0f0f0"

        # Copy Button Frame (Below message, Right Aligned)
        btn_frame = Frame(self.ui.text, bg=theme_bg)
        copy_btn = Button(btn_frame, text="📋", font=("Segoe UI Emoji", 9), cursor="hand2",
                          bd=0, bg=theme_bg, fg=theme_fg, activebackground=theme_active, activeforeground=theme_fg)
        copy_btn.config(command=lambda b=copy_btn: copy_user(b))
        copy_btn.pack(side=RIGHT, padx=5)
        
        # Speak User Button
        speak_btn = Button(btn_frame, text="🔊", font=("Segoe UI Emoji", 9), cursor="hand2",
                          bd=0, bg=theme_bg, fg=theme_fg, activebackground=theme_active, activeforeground=theme_fg)
        speak_btn.config(command=lambda b=speak_btn: self.toggle_speech(user_text, b))
        speak_btn.pack(side=RIGHT, padx=5)
        
        self.ui.text.window_create(END, window=btn_frame)
        self.ui.text.insert(END, "\n")
        self.ui.text.tag_remove("bot_label", "end-2c", "end")
        self.ui.text.tag_add("user_msg", "end-2c", "end")
        
        self.ui.text.config(state='disabled')
        
        self.current_session["messages"].append({
            "role": "user", 
            "content": user_text,
            "attachments": self.attachments[:]
        })

        # Start spinner AFTER user message
        self.start_spinner()

        # Capture attachments for this message
        current_attachments = self.attachments[:]
        
        # Clear attachments from UI and memory immediately after sending
        self.attachments = []
        self.ui.clear_attachments()

        def process():
            try:
                
                
                # Default model
                model_name = self.settings_manager.get("model", "openai/gpt-oss-120b:free")
                
                # Get Search State
                search_enabled = self.ui.search_active
                
                # Auto-Switch Logic
                has_image = any(os.path.splitext(f)[1].lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico'] for f in current_attachments)
                
                if current_attachments and has_image and ("edit" in user_input or "make changes" in user_input):
                     messagebox.showinfo("Information", f"Auto-switching to SeedDream for Image Editing",parent=self.root)
                     model_name = "bytedance-seed/seedream-4.5"
                     self.sticky_seedream_turns = 3
                     self.sticky_gemini_turns = 0
                     self.gemini_chat_session = None
                     
                elif current_attachments:
                    messagebox.showinfo("Information", f"Auto-switching to Gemini due to attachments (Sticky for 3 turns)",parent=self.root)
                    model_name = "gemini-2.5-flash"
                    self.sticky_gemini_turns = 3
                    if hasattr(self, 'sticky_seedream_turns'): self.sticky_seedream_turns = 0
                
                elif self.sticky_gemini_turns > 0:
                     model_name = "gemini-2.5-flash"
                     # Decrement unless reset by new attachment
                     self.sticky_gemini_turns -= 1
                     if hasattr(self, 'sticky_seedream_turns'): self.sticky_seedream_turns = 0
                     if self.sticky_gemini_turns == 0:
                         print("DEBUG: Sticky Gemini mode ended.")
                
                elif "generate" in user_input or "make image" in user_input:
                    messagebox.showinfo("Information", f"Auto-switching to SeedDream due to keywords (Sticky for 3 turns)",parent=self.root)
                    model_name = "bytedance-seed/seedream-4.5"
                    self.sticky_seedream_turns = 3
                    self.sticky_gemini_turns = 0
                    self.gemini_chat_session = None
                    
                elif hasattr(self, 'sticky_seedream_turns') and self.sticky_seedream_turns > 0:
                     model_name = "bytedance-seed/seedream-4.5"
                     self.sticky_seedream_turns -= 1
                     self.sticky_gemini_turns = 0
                     self.gemini_chat_session = None
                     if self.sticky_seedream_turns == 0:
                         print("DEBUG: Sticky Seedream mode ended.")
                
                else:
                    # Default model - clear gym session if switching naturally?
                    # or keep it until sticky runs out (handled above)
                    if self.sticky_gemini_turns <= 0:
                         self.gemini_chat_session = None

                
                # Get Reasoning Preference
                reasoning_enabled = self.settings_manager.get("reasoning_enabled", True)
                thinking_budget = self.settings_manager.get("thinking_budget", 1024)

                # Execute Request
                if 'gemini' in model_name.lower():
                     # Use Sticky Session if possible
                     if not self.gemini_chat_session:
                          # Convert history for Context
                          print("DEBUG: Creating new Gemini Session with Context")
                          initial_history = ai_chat.convert_history_to_gemini(self.session_messages)
                          self.gemini_chat_session = ai_chat.create_gemini_chat(history=initial_history)
                     
                     response = ai_chat.ask_gemini_chat(
                         self.gemini_chat_session, 
                         user_input, 
                         attachments=current_attachments,
                         search_enabled=search_enabled,
                         reasoning_enabled=reasoning_enabled,
                         thinking_budget=thinking_budget
                     )
                else:
                    response = ai_chat.ask_openai(
                        user_input, 
                        self.session_messages, 
                        self.response_cache, 
                        self.cache_file, 
                        attachments=current_attachments, 
                        model_name=model_name,
                        search_enabled=search_enabled,
                        reasoning_enabled=reasoning_enabled,
                        thinking_budget=thinking_budget
                    )
                
                # Schedule UI update on main thread
                self.root.after(0, lambda: self.finish_send(response, user_text))
            except Exception as e:
               error_msg = str(e)
               self.root.after(0, lambda: self.handle_send_error(error_msg))

        threading.Thread(target=process).start()

    def finish_send(self, response, user_text):
        self.ui.entry.config(state=NORMAL)
        # Clear properly for Text widget with placeholder logic
        self.ui.entry.delete("1.0", END)
        # self.ui.entry.insert("1.0", self.ui.placeholder_text)
        self._reset_entry_style()
        
        # Render response - no next step needed here for simple send, 
        # but we can pass cleanup/logging as callback if needed.
        
        # Render response - no next step needed here for simple send, 
        # but we can pass cleanup/logging as callback if needed.
        self.render_bot_response(response)
        
        timestamp = strftime('%Y-%m-%d %I:%M:%S %p')

        # If no current session, create a new one
        if not self.current_session:
             # Already handled in send() now
             pass
             
        # Add bot response to history
        self.current_session["messages"].append({
            "role": "assistant",
            "content": response
        })

        # Update in-memory context for next turn
        self.session_messages.append({"role": "user", "content": user_text})
        self.session_messages.append({"role": "assistant", "content": response})

        history.save_history(self.history_file, self.history_data)
        self.render_history()
        self.stop_spinner()
        self.ui.send_btn.config(state=NORMAL)

    def handle_send_error(self, error):
        messagebox.showerror("Error", f"An error occurred: {error}", parent=self.root)
        self.ui.entry.config(state=NORMAL)
        self.stop_spinner()
        self.ui.send_btn.config(state=NORMAL)

    def render_bot_response(self, response, on_complete=None):
        self.ui.text.config(state='normal')
        self.ui.text.insert(END, "\n✨ HelpBot\n", "bot_label")
        self.ui.text.config(state='disabled')
        
        # Check for Image Generation Response
        if response.startswith("[IMAGE_GENERATED]:"):
            image_path = response.replace("[IMAGE_GENERATED]:", "").strip()
            self.ui.render_image_preview_button(self.ui.text, image_path)
            
            # Call on_complete if provided
            if on_complete:
                self.root.after(100, on_complete)
            return

        # Fix over-escaped LaTeX (\\frac → \frac, etc.)
        response = response.replace('\\\\', '\\')

        step_title_pattern = re.compile(r'###\s*(Step \d+:.*?)\n', re.IGNORECASE)
        response = step_title_pattern.sub(r'\n\n🧩 \1\n' + '-'*40 + '\n', response)

        response = re.sub(r'^\s*\d+\.', '•', response, flags=re.MULTILINE)

        heading_pattern = re.compile(r'^(#{2,})\s+(.*)', re.MULTILINE)
        response = heading_pattern.sub(lambda m: f"\n\n{'=' * len(m.group(1))} {m.group(2)} {'=' * len(m.group(1))}\n", response)

        content_blocks = []
        current_pos = 0

        for match in re.finditer(
            r'(\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|```[\s\S]+?```|(?:(?:^|\n)\|.+?\|[\r\n]+)+)', 
            response, 
            re.MULTILINE | re.DOTALL
        ):
            if match.start() > current_pos:
                content_blocks.append(('text', response[current_pos:match.start()]))
            
            content = match.group(0)
            if content.startswith('$$'):
                content_blocks.append(('latex_block', content[2:-2].strip()))
            elif content.startswith(r'\['):
                content_blocks.append(('latex_block', content[2:-2].strip()))
            elif content.startswith(r'\('):
                content_blocks.append(('latex_inline', content[2:-2].strip()))
            elif content.startswith('```'):
                lang_match = re.match(r'```(\w*)\n([\s\S]+?)```', content)
                if lang_match:
                    lang = lang_match.group(1).strip().lower() or "text"
                    code = ui_utils.remove_explanation_lines(lang_match.group(2)).strip()
                    content_blocks.append(('code', (lang, code)))
            elif '|' in content:
                content_blocks.append(('table', content.strip()))
            
            current_pos = match.end()

        if current_pos < len(response):
            content_blocks.append(('text', response[current_pos:]))

        # Configure tags for bold and headers (idempotent, safe to repeat)
        self.ui.text.tag_configure("bold", font=("Segoe UI Emoji", 13, "bold"))
        self.ui.text.tag_configure("header_1", font=("Segoe UI Emoji", 16, "bold"), foreground="#2c3e50")
        self.ui.text.tag_configure("header_2", font=("Segoe UI Emoji", 14, "bold"), foreground="#34495e")

        # Process blocks asynchronously in chunks
        def process_block_chunk(index):
            chunk_size = 2 # Process 2 blocks at a time to keep UI responsive
            end_index = min(index + chunk_size, len(content_blocks))
            
            self.ui.text.config(state='normal')
            
            for i in range(index, end_index):
                block_type, content = content_blocks[i]
                
                if block_type == 'text':
                    if content.strip():
                        lines = content.split('\n')
                        for line in lines:
                            if not line.strip():
                                self.ui.text.insert(END, "\n")
                                continue
                                
                            if line.strip().startswith("===") or line.strip().endswith("==="):
                                 clean_line = line.replace("===", "").strip()
                                 self.ui.text.insert(END, clean_line + "\n", "header_2")
                            elif line.strip().startswith("==") or line.strip().endswith("=="):
                                 clean_line = line.replace("==", "").strip()
                                 self.ui.text.insert(END, clean_line + "\n", "header_1")
                            else:
                                parts = line.split('**')
                                for k, part in enumerate(parts):
                                    if k % 2 == 1:
                                        self.ui.text.insert(END, part, "bold")
                                    else:
                                        self.ui.text.insert(END, part)
                                self.ui.text.insert(END, "\n")
                        self.ui.text.insert(END, "\n")
                elif block_type == 'latex_block':
                    ui_utils.render_latex_equation(self.ui.text, content, is_dark=self.dark_mode_enabled)
                    self.ui.text.insert(END, '\n\n')
                elif block_type == 'latex_inline':
                    ui_utils.render_latex_equation(self.ui.text, content, is_dark=self.dark_mode_enabled)
                elif block_type == 'code':
                    lang, code = content
                    self.syntax_highlighter.insert_code_snippet(lang, code, is_dark=self.dark_mode_enabled)
                    self.ui.text.insert(END, '\n\n')
                elif block_type == 'table':
                    # Passing language code directly now, ui_utils needs update
                    # Use self.dark_mode_enabled logic (passed or read?)
                    # Need to make sure self.dark_mode_enabled is accessible here. 
                    # Yes, self is ChatBot instance.
                    ui_utils.insert_markdown_table(self.ui.text, content, self.root, \
                        self.settings_manager.get("language", "en"), is_dark=self.dark_mode_enabled)
                    self.ui.text.insert(END, '\n\n')

            self.ui.text.config(state='disabled')

            if end_index < len(content_blocks):
                self.root.after(5, lambda: process_block_chunk(end_index))
            else:
                # All blocks done - Inject Buttons
                self.ui.text.config(state='normal')
                                
                # Create a frame to hold buttons to keep them together
                # Theme-aware colors
                is_dark = self.dark_mode_enabled
                theme_bg = "#1e1e1e" if is_dark else "white"
                theme_fg = "#e0e0e0" if is_dark else "black"
                theme_active = "#2d2d2d" if is_dark else "#f0f0f0"

                # Create a frame to hold buttons to keep them together
                btn_frame = Frame(self.ui.text, bg=theme_bg)
                
                # Copy Button
                copy_btn = Button(btn_frame, text="📋", font=("Segoe UI Emoji", 10), cursor="hand2",
                                  bd=0, bg=theme_bg, fg=theme_fg, activebackground=theme_active, activeforeground=theme_fg,
                                  command=lambda: self.copy_to_clipboard(response)) # Will fail because missing arg usage below needs update
                copy_btn.config(command=lambda b=copy_btn: self.copy_to_clipboard(response, b)) # Correct usage
                copy_btn.pack(side=LEFT, padx=5)
                
                # Speak Button
                speak_btn = Button(btn_frame, text="🔊", font=("Segoe UI Emoji", 10), cursor="hand2",
                                  bd=0, bg=theme_bg, fg=theme_fg, activebackground=theme_active, activeforeground=theme_fg)
                speak_btn.config(command=lambda b=speak_btn: self.toggle_speech(response, b))
                speak_btn.pack(side=LEFT, padx=5)
                
                self.ui.text.window_create(END, window=btn_frame)
                self.ui.text.insert(END, "\n") # Spacing after buttons
                self.ui.text.config(state='disabled')

                if on_complete:
                    on_complete()

        # Start processing
        process_block_chunk(0)

    def clear(self):
        self.ui.text.config(state='normal')
        # Clear input box
        self.ui.entry.delete("1.0", END)
        # self.ui.entry.insert("1.0", self.ui.placeholder_text) # Placeholder removed
        # self.ui.entry.config(fg='grey') # Placeholder logic removed
        
        self.ui.text.delete(1.0, END)
        self.ui.text.config(state='disabled')
        
        self.attachments = []
        self.ui.clear_attachments()

    def speak(self):
        try:
            text = audio.listen_speech()
            # Clear placeholder first if present
            if self.ui.entry.get("1.0", "end-1c") == self.ui.placeholder_text:
                self.ui.entry.delete("1.0", END)
                self.ui.entry.config(fg='black')
            
            self.ui.entry.insert(END, text)
        except Exception as e:
            messagebox.showerror('Speech Recognition Error', f'Sorry, your speech was not recognized: {str(e)}', parent=self.root)

    def read_all_chat(self):
        full_chat_text = self.ui.text.get(1.0, END).strip()
        if not full_chat_text:
            messagebox.showwarning('Empty', 'No chat content to read!', parent=self.root)
            return

        if not full_chat_text:
            messagebox.showwarning('Empty', 'No chat content to read!', parent=self.root)
            return

        self.toggle_speech(full_chat_text, self.ui.read_btn)
        
    def add_attachment(self):
        file_types = [
            ("Supported Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.ico;*.pdf;*.txt;*.py;*.mp3;*.wav;*.aac;*.flac;*.ogg;*.mp4;*.mpeg;*.mov;*.avi;*.flv;*.mpg;*.webm;*.wmv;*.3gpp;*.js;*.html;*.c;*.cpp;*.css;*.java"),
            ("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.ico"),
            ("Documents", "*.pdf;*.txt;*.py;*.js;*.html;*.c;*.cpp;*.css;*.java"),
            ("Audio", "*.mp3;*.wav;*.aac;*.flac;*.ogg"),
            ("Video", "*.mp4;*.mpeg;*.mov;*.avi;*.flv;*.mpg;*.webm;*.wmv;*.3gpp")
        ]
        
        files = filedialog.askopenfilenames(
            initialdir=os.getcwd(), 
            title="Select Attachments", 
            filetypes=file_types, 
            parent=self.root
        )
        
        excluded_exts = ['.json', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']
        
        for file_path in files:
            # Check for excluded extensions
            ext = os.path.splitext(file_path)[1].lower()
            if ext in excluded_exts:
                messagebox.showwarning("Invalid File", f"The following file type is not allowed: {ext}\nFile: {os.path.basename(file_path)}", parent=self.root)
                continue
            
            # Check file size (5 MB limit)
            try:
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > 5:
                    messagebox.showwarning("File Too Large", f"File size exceeds 5MB limit:\n{os.path.basename(file_path)} ({file_size_mb:.2f} MB)", parent=self.root)
                    continue
            except OSError:
                continue

            if file_path not in self.attachments:
                self.attachments.append(file_path)
                # Pass a callback to remove this specific file
                self.ui.add_attachment_thumbnail(file_path, on_remove=lambda fp=file_path: self.remove_attachment(fp))

    def remove_attachment(self, file_path):
        if file_path in self.attachments:
            self.attachments.remove(file_path)
            # print(f"Removed attachment: {file_path}")

    def toggle_search(self):
        self.search_enabled = not self.search_enabled
        self.ui.toggle_search_btn_state(self.search_enabled)
        
        status = "Enabled" if self.search_enabled else "Disabled"
        # Optional: Toast notification or just rely on button color
        # messagebox.showinfo("Web Search", f"Web Search is now {status}")

if __name__ == '__main__':
    root = Tk()
    obj = ChatBot(root)
    root.mainloop()

