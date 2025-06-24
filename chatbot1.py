import os
from time import strftime
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pygame import mixer
import speech_recognition
from openai import OpenAI
import threading
from gtts import gTTS
import tempfile
from gtts.lang import tts_langs
import json


client = OpenAI(
base_url="https://openrouter.ai/api/v1",
api_key="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",
)


class ChatBot:

    def __init__(self, root):
        self.root = root
        self.root.title('HelpBot')
        self.root.geometry('1050x650+0+0')
        self.root.resizable(False, False)
        self.root.config(bg='powderblue')
        self.root.wm_iconbitmap('college_images/bg1.ico')
        self.root.bind('<Return>', self.enter_func)
        

        self.history_file = "chat_history.json"
        self.history_data = self.load_history()


        main_frame = Frame(self.root, bd=4, bg='powder blue', width=610)
        main_frame.place(x=0,y=0)

        img = Image.open('college_images/chat.jpg')
        img = img.resize((200, 70), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)

        self.title_label = Label(main_frame, bd=3, relief=RAISED, anchor='nw', width=730,
                                 image=self.photoimg, text='Chat Me', font=('arial', 30, 'bold'),
                                 bg='white', fg='green', compound=LEFT)
        self.title_label.pack(side=TOP)
        # Hamburger icon
        self.hamburger_icon = ImageTk.PhotoImage(Image.open("assets/menu.png").resize((30, 30)))
        self.hamburger_btn = Button(self.title_label, image=self.hamburger_icon, bd=0, bg='white',
                                    activebackground='white', cursor='hand2', command=self.toggle_history_panel)
        self.hamburger_btn.place(x=5, y=5)
        ToolTip(self.hamburger_btn, "Toggle History Panel")



        self.time_lbl = Label(self.title_label, font=('times new roman', 15, 'bold'),
                              bg='white', fg='gold', borderwidth=0, highlightthickness=0)
        self.time_lbl.place(x=390, y=15, width=120, height=45)
        self.update_time()

        back_btn = Button(self.title_label, text="Back", width=20, cursor='hand2',
                          font=('times new roman', 10, 'bold'), bg='red', fg='white',
                          activebackground="green", command=self.back)
        back_btn.place(x=550, y=25, height=25)

        self.scroll_y = ttk.Scrollbar(main_frame, orient='vertical')
        self.scroll_y.pack(side=RIGHT, fill=Y)

        self.text = Text(main_frame, width=65, height=20, bd=3, relief=RAISED,
                        font=('arial', 14), wrap=WORD, yscrollcommand=self.scroll_y.set,state='disabled')
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        self.scroll_y.config(command=self.text.yview)
        

        btn_frame = Frame(self.root, bd=4, bg='white', width=745, height=120)
        btn_frame.pack_propagate(0)  # Prevent auto-resizing
        btn_frame.place(x=0,y=535)

        type_label = Label(btn_frame, text='Type Something:', font=('arial', 14, 'bold'),
                   bg='white', fg='green')
        type_label.place(x=10, y=5)

        self.entry = Entry(btn_frame, width=40, font=('times new roman', 16, 'bold'))
        self.entry.place(x=175, y=7)


        self.send_btn = Button(btn_frame, text='Send>>', font=('arial', 13, 'bold'), width=7,
                       bg='green', fg='red', activebackground='yellow', activeforeground='blue',
                       cursor='hand2', command=self.send)
        self.send_btn.place(x=640, y=7)

        self.photoimg2 = ImageTk.PhotoImage(Image.open("assets/Clear.png").resize((48, 48), Image.Resampling.LANCZOS))
        self.clear_btn = Button(btn_frame, text='Clear', image=self.photoimg2, compound=LEFT,
                        font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='white',
                        activebackground='white', fg='yellow', activeforeground='green',
                        command=self.clear)
        self.clear_btn.place(x=10, y=50)
        self.photoimg3 = ImageTk.PhotoImage(Image.open("assets/mic.png").resize((48, 48), Image.Resampling.LANCZOS))
        self.speak_btn = Button(btn_frame, text='Speak', image=self.photoimg3, compound=LEFT,
                        font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='white',
                        activebackground='white', fg='cyan2', activeforeground='orange red',
                        command=self.speak)
        self.speak_btn.place(x=170, y=50)


        self.photoimg4 = ImageTk.PhotoImage(Image.open("assets/speaker.png").resize((48, 48), Image.Resampling.LANCZOS))
        self.read_btn = Button(btn_frame, text='Read All', image=self.photoimg4, compound=LEFT,
                       font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='white',
                       activebackground='white', fg='purple', activeforeground='pink',
                       command=self.read_all_chat)
        self.read_btn.place(x=330, y=50)
        self.photoimg5 = ImageTk.PhotoImage(Image.open("assets/speaking.png").resize((48, 48), Image.Resampling.LANCZOS))
        self.read_selection_btn = Button(btn_frame, text='Speak Selected', image=self.photoimg5, compound=LEFT,
                            font=('arial', 10, 'bold'), cursor='hand2', bd=0, bg='white',
                            activebackground='white', fg='blue', activeforeground='orange red',
                            command=self.read_selected_text)
        self.read_selection_btn.place(x=480, y=50)


        # Set a default language for the chatbot's speech
        self.bot_speak_language_code = "en" # Default to English, you can change this
        
        # Dynamic Language selection
        self.languages = tts_langs() # Get all supported languages from gTTS
        
        self.language_options = {}
        # Manually add some common languages with preferred display names
        common_languages = {
            "English": "en",
            "Hindi": "hi",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Gujarati": "gu",
            "Punjabi": "pa",
            "Chinese (Simplified)": "zh-CN",
            "Bengali": "bn"
        }

        # Populate language_options, prioritizing common_languages names
        for name, code in common_languages.items():
            if code in self.languages:
                self.language_options[name] = code
        
        # Add remaining languages from tts_langs that weren't in common_languages
        for code, name in self.languages.items():
            if code not in self.language_options.values(): # Check if code already added
                self.language_options[name] = code

        # Sort the language options for a clean dropdown
        sorted_language_names = sorted(self.language_options.keys())

        self.language_var = StringVar()
        # Set default value to 'English' if available, otherwise the first in the sorted list
        if "English" in sorted_language_names:
            self.language_var.set("English")
        elif sorted_language_names:
            self.language_var.set(sorted_language_names[0])
        else:
            self.language_var.set("") # No languages available


        style = ttk.Style()
        style.theme_use('default')  # Use 'clam' or 'alt' for different styles if needed
        style.configure("TCombobox",
                        fieldbackground="white",
                        background="white",
                        foreground="blue",
                        font=('arial', 12, 'bold'))

        self.language_combo = ttk.Combobox(btn_frame, textvariable=self.language_var,
                                        values=sorted_language_names, state="readonly",
                                        font=('arial', 12, 'bold'), width=15)
        self.language_combo.place(x=650, y=55, width=80, height=35)


        # History panel (initially hidden)
        self.history_visible = False

        self.history_panel = Frame(self.root, bg='white', width=200, height=650)
        self.history_panel.place(x=745, y=0)
        self.history_panel.place_forget()

        self.history_list_frame = Frame(self.history_panel, bg='white')
        self.history_list_frame.pack(fill=BOTH, expand=True)
        self.render_history()


        # Add Clear All button
        clear_btn = Button(self.history_panel, text="Clear All", bg="red", fg="white",
                        font=('arial', 10, 'bold'),activebackground='green',activeforeground='black',cursor='hand2', command=self.clear_all_history)
        clear_btn.pack(side=BOTTOM, fill=X)

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


    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)

    def back(self):
            self.root.destroy()

    def toggle_history_panel(self):
        if self.history_visible:
            self.history_panel.place_forget()
        else:
            self.history_panel.place(x=745, y=0)
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
        self.history_data = []
        self.save_history()
        self.render_history()
    
    def load_history_entry(self, text):
        # self.entry.config(state='normal')
        self.entry.delete(0, END)
        self.entry.insert(0, text)

    def load_and_send_history_entry(self, text):
        self.load_history_entry(text)
        self.send_btn.invoke()

    def render_history(self):
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()

        for index, entry in enumerate(self.history_data):
            frame = Frame(self.history_list_frame, bg='white')
            frame.pack(fill=X, padx=5, pady=2)

            preview_text = f"{entry['time']} | You: {entry['user'][:10]} | Bot: {entry['bot'][:10]}..."
            label = Label(frame, text=preview_text, anchor='w', bg='white', fg='black',
                        font=('arial', 9), justify=LEFT)
            label.pack(side=LEFT, fill=X, expand=True)
            tooltip_text = f"User: {entry['user']}\nBot: {entry['bot']}"
            ToolTip(label,tooltip_text)  


            # Restore on double-click
            label.bind("<Button-1>", lambda e, text=entry['user']: self.load_history_entry(text))
            label.bind("<Double-Button-1>", lambda e, text=entry['user']: self.load_and_send_history_entry(text))

            del_btn = Button(frame, text="🗑", bg='white',activebackground='white',fg='red',activeforeground='green', bd=0, font=('arial', 10),cursor='hand2',
                            command=lambda i=index: self.delete_history_entry(i))
            del_btn.pack(side=RIGHT)
    
    def send(self):
        user_input = self.entry.get().strip().lower()
        user_text = self.entry.get().strip()
        if user_input == '':
            messagebox.showerror('Error', 'Message must contain some content',parent=self.root)
            return
        # Disable send button and entry field
        self.send_btn.config(state=DISABLED, text="Loading...")
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
                res = 'Sorry I didn\'t get it. It\'s out of my content, but I got your answer from server.\n'
                response = self.ask_openai(user_input)
                response = res + response

           
            # Get the language code from the selected language name
            selected_lang_name = self.language_var.get()
            selected_lang_code = self.language_options.get(selected_lang_name, "en") # Default to 'en' if not found
            self.speak_text_gtts(response, selected_lang_code)


            self.entry.config(state=NORMAL)
            self.entry.delete(0, END)
            self.text.insert(END, f'\n\n Bot : {response}')
            log = {
                "user": user_text,
                "bot": response,
                "time": strftime('%I:%M:%S %p')
            }
            self.history_data.append(log)
            self.save_history()
            self.render_history()
            self.text.config(state='disabled')

            # Re-enable button and reset text
            self.send_btn.config(state=NORMAL, text="Send>>")
            # Start the thread to process in background
        threading.Thread(target=process).start()

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

    def read_all_chat(self): # Renamed function
        full_chat_text = self.text.get(1.0, END).strip()
        if not full_chat_text:
            messagebox.showwarning('Empty', 'No chat content to read!', parent=self.root)
            return

        # Use the automatically set language for reading the chat
        selected_lang_name = self.language_var.get()
        selected_lang_code = self.language_options.get(selected_lang_name, "en") # Default to 'en' if not found
        self.speak_text_gtts('So far we have talked about: ' + full_chat_text, selected_lang_code)

    def ask_openai(self, prompt):
        try:
            completion = client.chat.completions.create(
                extra_headers={

                    "X-Title": "HelpBot"
                },
                model="meta-llama/llama-3.3-70b-instruct:free",
                
                messages=[
                {"role": "system", "content": "You are a helpful, friendly, and intelligent female assistant named HelpBot. Speak in a polite and empathetic manner."},
                {"role": "user", "content": prompt}]

                
            )
            return completion.choices[0].message.content.strip()
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