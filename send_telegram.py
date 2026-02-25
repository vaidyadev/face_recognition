import os
import io
import json
import threading
import time
import re
import asyncio  # Added for async telegram support
from tkinter import *
from utils import resource_path
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk, ImageDraw
from tkcalendar import DateEntry
from datetime import datetime, timedelta

# --- Telegram Bot Import ---
from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.error import TelegramError
# --- Database Import ---
import mysql.connector

# --- Optional Audio Imports ---
try:
    from pygame import mixer
    import speech_recognition
    pygame_mixer_available = True
    speech_recognition_available = True
except ImportError:
    pygame_mixer_available = False
    speech_recognition_available = False
    print("Warning: pygame or speech_recognition not found. Speak functionality will be disabled.")

# --- Constants ---
CREDENTIALS_FILE = resource_path("telegram_bot_credentials.json")
SCHEDULE_FILE = resource_path("telegram_bot_schedule.json")

# Note: Ensure tooltip.py exists in your directory
from tooltip import ToolTip

class TelegramBotSender:
    def __init__(self, root):
        self.root = root
        self.root.geometry("850x700+80+0")
        self.root.minsize(800, 600)
        self.root.title("Telegram Bot Sender")
        self.root.resizable(True, True)
        self.root.config(bg='#2B2B52')
        try:
            self.root.wm_iconbitmap(resource_path('assets\\telegram.ico'))
        except:
            pass

        # ------------------ VARIABLES ------------------ #
        self.name_var = StringVar()
        self.chat_id_var = StringVar()
        self.subject_var = StringVar()
        self.contacts = {}
        self.attachments = []
        
        # Bot Token
        self.bot_token_var = StringVar()
        self.bot_token = ""
        self.load_credentials()

        # Scheduling
        self._start_schedule_monitor()

        # ------------------ GRID CONFIG ------------------ #
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1) # Compose area expands

        # ------------------ Title Section ------------------ #
        try:
            img = Image.open(resource_path("assets\\telegram.png"))
            self.photoimg = ImageTk.PhotoImage(img)
        except:
            self.photoimg = None

        title_frame = Frame(self.root, bg='white')
        title_frame.grid(row=0, column=0, pady=5, sticky="ew", padx=20)
        title_frame.columnconfigure(1, weight=1)

        help_button = Button(title_frame, image=self.photoimg, bg='white', cursor='hand2',
                                activebackground='white', borderwidth=0, command=self.show_shortcuts)
        help_button.grid(row=0, column=0, padx=15, pady=5)
        ToolTip(help_button, "Help For Shortcuts <Control-h> ")
        
        title_label = Label(title_frame, text=' Telegram Bot Sender',
                             font=('goudy old style', 28, 'bold'), bg='white', fg='#2B2B52')
        title_label.grid(row=0, column=1, sticky="w")

        try:
            img1 = Image.open(resource_path("assets\\setting.png"))
            self.photoimg1 = ImageTk.PhotoImage(img1)
            setting_button = Button(title_frame, image=self.photoimg1, bg='white', cursor='hand2',
                                    activebackground='white', borderwidth=0, command=self.setting)
            setting_button.grid(row=0, column=2, padx=15, pady=5)
            ToolTip(setting_button, "Telegram Bot Settings <Control-c>")
        except:
            setting_button = Button(title_frame, text="Settings", command=self.setting)
            setting_button.grid(row=0, column=2, padx=15, pady=5)

        # ------------------ To Section ------------------ #
        to_label = LabelFrame(root, text='To (Chat ID / Username)',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='#2B2B52')
        to_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        to_label.columnconfigure(0, weight=3)
        to_label.columnconfigure(1, weight=1)

        self.to_entry = Entry(to_label, font=('times new roman', 16, 'bold'),
                              textvariable=self.chat_id_var, state='readonly')
        self.to_entry.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        self.get_name_combo = ttk.Combobox(to_label, font=('times new roman', 12, 'bold'),
                                         state='readonly', cursor='hand2',
                                         textvariable=self.name_var)
        self.get_name_combo.set("Select Name")
        self.get_name_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.get_name_combo.bind("<<ComboboxSelected>>", self.get_data)
        
        # ------------------ Subject Section ------------------ #
        subject_label = LabelFrame(root, text='Subject',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='#2B2B52')
        subject_label.grid(row=2, column=0, pady=5, padx=20, sticky="ew")
        subject_label.columnconfigure(0, weight=1)

        self.subject_entry = Entry(subject_label, font=('times new roman', 16, 'bold'),
                              textvariable=self.subject_var)
        self.subject_entry.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # ------------------ Compose Section ------------------ #
        compose_label = LabelFrame(root, text='Compose Message',
                                   font=('times new roman', 16, 'bold'),
                                   bd=5, fg='white', bg='#2B2B52')
        compose_label.grid(row=3, column=0, pady=5, padx=20, sticky="nsew")
        compose_label.columnconfigure(0, weight=0)
        compose_label.columnconfigure(1, weight=0)
        compose_label.columnconfigure(2, weight=1)
        compose_label.rowconfigure(1, weight=1)

        # Speak Button
        try:
            img2 = Image.open(resource_path("assets\\mic.png"))
            img2 = img2.resize((48, 48), Image.Resampling.LANCZOS)
            self.photoimg2 = ImageTk.PhotoImage(img2)
            speak_button = Button(compose_label, text='  Speak', image=self.photoimg2, compound=LEFT,
                                font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='#2B2B52', fg='white',
                                activebackground='#483D8B', activeforeground='white', command=self.speak)
        except:
            speak_button = Button(compose_label, text='Speak', command=self.speak)
        speak_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ToolTip(speak_button, "Speak <Control-m>")

        # Attachment Button
        try:
            img3 = Image.open(resource_path("assets\\attechment.png"))
            img3 = img3.resize((48, 48), Image.Resampling.LANCZOS)
            self.photoimg3 = ImageTk.PhotoImage(img3)
            attech_button = Button(compose_label, text='  Attachments', image=self.photoimg3, compound=LEFT,
                                font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='#2B2B52', fg='white',
                                activebackground='#483D8B', activeforeground='white', command=self.attechment)
        except:
             attech_button = Button(compose_label, text='Attachments', command=self.attechment)
        attech_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ToolTip(attech_button, "Attachments for Message <Control-a>")
        
        self.image_frame = Frame(compose_label)
        self.image_frame.grid(row=0, column=2, padx=10, sticky='e')
        self.thumb_refs = []

        textarea_frame = Frame(compose_label)
        textarea_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        textarea_frame.columnconfigure(0, weight=1)
        textarea_frame.rowconfigure(0, weight=1)
        
        self.textarea = Text(textarea_frame, font=('times new roman', 14), height=10, width=65, pady=5, wrap=WORD)
        self.textarea.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(textarea_frame, orient=VERTICAL, command=self.textarea.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.textarea.config(yscrollcommand=scrollbar.set)

        # ------------------ Action Buttons ------------------ #
        button_frame = Frame(root, bg='#2B2B52')
        button_frame.grid(row=4, column=0, pady=10, sticky="ew")
        
        btn_inner = Frame(button_frame, bg='#2B2B52')
        btn_inner.pack(pady=5)
        
        # Send
        try:
            img4 = Image.open(resource_path("assets\\email_send.png"))
            self.photoimg4 = ImageTk.PhotoImage(img4)
            send_button = Button(btn_inner, image=self.photoimg4, bg='#2B2B52', cursor='hand2',
                                activebackground='#483D8B', borderwidth=0, command=self.send_msg)
        except:
            send_button = Button(btn_inner, text="Send", command=self.send_msg)
        send_button.pack(side=LEFT, padx=15)
        ToolTip(send_button, "Send  <Control-Return>")

        # Schedule
        try:
            img8 = Image.open(resource_path("assets\\scheduled.png"))
            self.photoimg8 = ImageTk.PhotoImage(img8)
            schedule_button = Button(btn_inner, image=self.photoimg8, bg='#2B2B52', cursor='hand2',
                                    activebackground='#483D8B', borderwidth=0, command=self.open_schedule_window)
        except:
            schedule_button = Button(btn_inner, text="Schedule", command=self.open_schedule_window)
        schedule_button.pack(side=LEFT, padx=15)
        ToolTip(schedule_button, "Schedule Sending <Control-s>")
        
        # Clear
        try:
            img5 = Image.open(resource_path("assets\\Clear.png"))
            self.photoimg5 = ImageTk.PhotoImage(img5)
            clear_button = Button(btn_inner, image=self.photoimg5, bg='#2B2B52', cursor='hand2',
                                activebackground='#483D8B', borderwidth=0, command=self.clear)
        except:
            clear_button = Button(btn_inner, text="Clear", command=self.clear)
        clear_button.pack(side=LEFT, padx=15)
        ToolTip(clear_button, "Clear All Fields <Control-l>")

        # Exit
        try:
            img6 = Image.open(resource_path("assets\\exit.png"))
            self.photoimg6 = ImageTk.PhotoImage(img6)
            exit_button = Button(btn_inner, image=self.photoimg6, bg='#2B2B52', cursor='hand2',
                                activebackground='#483D8B', borderwidth=0, command=self.iexit)
        except:
            exit_button = Button(btn_inner, text="Exit", command=self.iexit)
        exit_button.pack(side=LEFT, padx=15)
        
        def bind_hover(btn, normal_bg, hover_bg):
            btn.bind('<Enter>', lambda e: btn.config(bg=hover_bg))
            btn.bind('<Leave>', lambda e: btn.config(bg=normal_bg))
            
        bind_hover(speak_button, '#2B2B52', '#483D8B')
        bind_hover(attech_button, '#2B2B52', '#483D8B')
        bind_hover(send_button, '#2B2B52', '#483D8B')
        bind_hover(schedule_button, '#2B2B52', '#483D8B')
        bind_hover(clear_button, '#2B2B52', '#483D8B')
        bind_hover(exit_button, '#2B2B52', '#483D8B')
        ToolTip(exit_button, "Exit Application <Control-q>")
        messagebox.showwarning("Telegram Delivery Info",
                                    "Reciever must Start the chat with chatbot named @devvaidya36bot Otherwise it will give error",parent=self.root)

        # Connect to DB and Fetch
        self.connect_db()
        self.fetch_students()
        self.bind_shortcuts()

    # ------------------ LOGIC ------------------ #
    
    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                port=3307,
                user="root",
                password="1582",
                database="face_recognizer"
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error connecting to database:\n{e}", parent=self.root)

    def fetch_students(self):
        try:
            self.cursor.execute("SELECT Student_name, TelegramID FROM student")
            data = self.cursor.fetchall()
            self.contacts = {name: telegram_id for name, telegram_id in data}
            self.get_name_combo['values'] = list(self.contacts.keys())
        except Exception as e:
            messagebox.showerror("Fetch Error", f"Error in fetching student data:\n{e}", parent=self.root)

    def get_data(self, event=""):
        name = self.name_var.get()
        chat_id = self.contacts.get(name, "")
        self.chat_id_var.set(chat_id)

    def load_credentials(self):
        if os.path.exists(CREDENTIALS_FILE):
            try:
                with open(CREDENTIALS_FILE, 'r') as f:
                    data = json.load(f)
                    self.bot_token = data.get('bot_token', '')
                    self.bot_token_var.set(self.bot_token)
            except:
                pass

    def iexit(self):
        exit_val = messagebox.askyesno('Notification', 'Do you want to exit the application', parent=self.root)
        if exit_val > 0:
            self.root.destroy()

    def clear(self):
        self.to_entry.config(state='normal')
        self.to_entry.delete(0, END)
        self.to_entry.config(state='readonly')
        self.subject_entry.delete(0, END)
        self.textarea.delete(1.0, END)
        self.attachments = []
        self.thumb_refs = []
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        self.name_var.set("Select Name")
        # messagebox.showinfo("Information", "All fields cleared.", parent=self.root)

    def speak(self):
        if not pygame_mixer_available or not speech_recognition_available:
            messagebox.showerror('Error', 'Audio libraries not installed.', parent=self.root)
            return

        mixer.init()
        try:
            mixer.music.load('assets\\beep.mp3')
            mixer.music.play()
        except: 
            pass

        sr = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as m:
            try:
                sr.adjust_for_ambient_noise(m, duration=0.2)
                audio = sr.listen(m)
                text = sr.recognize_google(audio)
                self.textarea.insert(END, text + ' ')
            except Exception as e:
                messagebox.showerror('Error', f'Speech not recognized: {str(e)}', parent=self.root)

    def attechment(self):
        files = filedialog.askopenfilenames(initialdir=os.getcwd(), title='Select Files', parent=self.root)
        for file_path in files:
            if file_path not in self.attachments:
                self.attachments.append(file_path)
                filename = os.path.basename(file_path)
                
                self.textarea.insert(END, f"\n")

                ext = filename.split('.')[-1].lower()
                thumb = None
                
                if ext in ['png', 'jpg', 'jpeg', 'ico', 'bmp', 'webp']:
                    try:
                        img = Image.open(file_path)
                        img.thumbnail((50, 50))
                        thumb = ImageTk.PhotoImage(img)
                    except: 
                        pass
                elif ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac']:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((5, 15), f'Audio: {filename[:10]}', fill='black')
                    thumb = ImageTk.PhotoImage(img)
                elif ext in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((5, 15), f'Video: {filename[:10]}', fill='black')
                    thumb = ImageTk.PhotoImage(img)
                else:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((5, 15), f'FILE: {filename[:10]}', fill='black')
                    thumb = ImageTk.PhotoImage(img)

                if thumb:
                    self.thumb_refs.append(thumb)
                    self.textarea.image_create(END, image=thumb)
                    self.textarea.insert(END, "\n")

    def bind_shortcuts(self):
        self.root.bind("<Control-Return>", lambda e: self.send_msg())
        self.root.bind("<Control-s>", lambda e: self.open_schedule_window())
        self.root.bind("<Control-S>", lambda e: self.open_schedule_window())
        self.root.bind("<Control-a>", lambda e: self.attechment())
        self.root.bind("<Control-A>", lambda e: self.attechment())
        self.root.bind("<Control-m>", lambda e: self.speak())
        self.root.bind("<Control-M>", lambda e: self.speak())
        self.root.bind("<Control-c>", lambda e: self.setting())
        self.root.bind("<Control-C>", lambda e: self.setting())
        self.root.bind("<Control-h>", lambda e: self.show_shortcuts())
        self.root.bind("<Control-H>", lambda e: self.show_shortcuts())
        self.root.bind("<Control-l>", lambda e: self.clear())
        self.root.bind("<Control-L>", lambda e: self.clear())
        self.root.bind("<Control-q>", lambda e: self.iexit())
        self.root.bind("<Control-Q>", lambda e: self.iexit())

    def setting(self):
        self.token_visible = False
        
        root1 = Toplevel()
        root1.title('Telegram Bot Settings')
        root1.geometry('620x250+350+150')
        root1.config(bg='dodger blue2')
        root1.resizable(False, False)
        try:
            root1.wm_iconbitmap(resource_path('assets\\telegram.ico'))
            img = Image.open(resource_path("assets\\Email.png"))
            self.photoimg_s = ImageTk.PhotoImage(img)
        except: 
            self.photoimg_s = None

        title_label = Label(root1, text='Bot Token Settings', image=self.photoimg_s, compound=LEFT,
                            font=('goudy old style', 38, 'bold'), fg='white', bg='gray20')
        title_label.grid(row=0, column=0, padx=75, pady=10)

        # Pre-load eye icons
        self.eye_open_photo = None
        self.eye_closed_photo = None
        has_icons = False
        try:
            eye_open_img = Image.open(resource_path("assets\\eye_open.png"))
            eye_open_img = eye_open_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.eye_open_photo = ImageTk.PhotoImage(eye_open_img)

            eye_closed_img = Image.open(resource_path("assets\\eye_closed.png"))
            eye_closed_img = eye_closed_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.eye_closed_photo = ImageTk.PhotoImage(eye_closed_img)
            has_icons = True
        except Exception:
            has_icons = False

        # Bot Token Section
        token_label = LabelFrame(root1, text='Bot Token', font=('times new roman', 16, 'bold'),
                                bd=5, fg='white', bg='dodger blue2')
        token_label.grid(row=1, column=0, pady=15)
        
        token_entry = Entry(token_label, font=('times new roman', 14, 'bold'), width=40, show='*')
        token_entry.grid(row=0, column=0, padx=5)
        token_entry.insert(0, self.bot_token_var.get())

        def toggle_token_visibility():
            self.token_visible = not self.token_visible
            if self.token_visible:
                token_entry.config(show='')
                if has_icons: 
                    eye_toggle_btn.config(image=self.eye_open_photo)
                else: 
                    eye_toggle_btn.config(text="Hide")
            else:
                token_entry.config(show='*')
                if has_icons: 
                    eye_toggle_btn.config(image=self.eye_closed_photo)
                else: 
                    eye_toggle_btn.config(text="Show")
        
        if has_icons:
            eye_toggle_btn = Button(token_label, image=self.eye_closed_photo,
                                   command=toggle_token_visibility,
                                   bd=0, bg='dodger blue2', activebackground='dodger blue2', cursor='hand2')
        else:
            eye_toggle_btn = Button(token_label, text="Show",
                                   command=toggle_token_visibility,
                                   bg='dodger blue2', fg='white', cursor='hand2')
        eye_toggle_btn.grid(row=0, column=1, padx=5)
        ToolTip(eye_toggle_btn, "Show/Hide Bot Token")

        def save():
            if token_entry.get() == '':
                messagebox.showerror("Error", 'Bot Token is required', parent=root1)
            else:
                data = {'bot_token': token_entry.get()}
                with open(CREDENTIALS_FILE, 'w') as f:
                    json.dump(data, f)
                self.bot_token = token_entry.get()
                self.bot_token_var.set(self.bot_token)
                messagebox.showinfo('Information', 'Bot Token saved successfully', parent=root1)
                root1.destroy()

        def clear1():
            token_entry.delete(0, END)

        save_button = Button(root1, text='Save', bg='gold2', fg='black', cursor='hand2',
                             font=('times new roman', 18, 'bold'), activebackground='gray10',
                             activeforeground='white', borderwidth=0, command=save)
        save_button.place(x=200, y=180)

        clear_button = Button(root1, text='Clear', bg='gold2', fg='black', cursor='hand2',
                            font=('times new roman', 18, 'bold'), activebackground='gray10',
                            activeforeground='white', borderwidth=0, command=clear1)
        clear_button.place(x=320, y=180)
        
        root1.mainloop()

    # ------------------ ASYNC SENDING LOGIC ------------------ #
    
    async def _send_telegram_bot_async(self, bot_token, chat_id, message, file_paths):
        """
        Sends message and files using Asynchronous Telegram Bot API.
       
        """
        try:
            request = HTTPXRequest(connect_timeout=60, read_timeout=60)
            bot = Bot(token=bot_token, request=request)
            
            # Validate chat_id format
            if chat_id.lstrip('-').isdigit():
                chat_id = int(chat_id)
            
            # Use 'async with' to properly manage the bot's session
            async with bot:
                # Send text message
                if message.strip():
                    await bot.send_message(chat_id=chat_id, text=message)
                
                # Send files
                if file_paths:
                    for file_path in file_paths:
                        if not os.path.exists(file_path):
                            continue
                        
                        ext = file_path.split('.')[-1].lower()
                        with open(file_path, 'rb') as file:
                            if ext in ['png', 'jpg', 'jpeg', 'webp', 'bmp']:
                                await bot.send_photo(chat_id=chat_id, photo=file)
                            elif ext in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
                                await bot.send_video(chat_id=chat_id, video=file)
                            elif ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac']:
                                await bot.send_audio(chat_id=chat_id, audio=file)
                            elif ext in ['gif']:
                                await bot.send_animation(chat_id=chat_id, animation=file)
                            else:
                                await bot.send_document(chat_id=chat_id, document=file)
            
            return True, "Message sent successfully!"
            
        except TelegramError as e:
            return False, f"Telegram Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _send_telegram_bot(self, bot_token, chat_id, message, file_paths):
        """
        Synchronous bridge to run the async send function.
       
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._send_telegram_bot_async(bot_token, chat_id, message, file_paths))
            finally:
                loop.close()
        except Exception as e:
            return False, str(e)


    def _run_in_thread(self, target_func, *args, callback=None):
        """Run a function in a separate thread to avoid blocking UI"""
        def wrapper():
            result = target_func(*args)
            if callback:
                self.root.after(0, lambda: callback(result))
        
        threading.Thread(target=wrapper, daemon=True).start()

    def send_msg(self):
        chat_id = self.chat_id_var.get().strip()
        subject = self.subject_var.get().strip()
        body = self.textarea.get(1.0, END).strip()

        if not chat_id or not subject or not body:
            messagebox.showerror('Error', 'All fields are required (To, Subject, Message)', parent=self.root)
            return

        message = f'Subject: {subject}\n\n{body}\n\nYour Regards'

        bot_token = self.bot_token_var.get().strip()
        
        if not bot_token:
            messagebox.showerror('Error', 'Please configure Bot Token in Settings', parent=self.root)
            return

        def on_complete(result):
            success, msg = result
            if success:
                messagebox.showinfo("Success", msg, parent=self.root)
                self.clear()
            else:
                messagebox.showerror("Error", f"Failed: {msg}", parent=self.root)
                print(msg)

        self._run_in_thread(
            self._send_telegram_bot,
            bot_token, chat_id, message, self.attachments,
            callback=on_complete
        )

    # ------------------ SCHEDULING LOGIC ------------------ #
    
    def open_schedule_window(self):
        schedule_window = Toplevel(self.root)
        schedule_window.title("Schedule Telegram Message")
        schedule_window.geometry("400x320+200+100")
        schedule_window.config(bg='dodger blue2')
        schedule_window.resizable(False, False)
        
        try:
            schedule_window.wm_iconbitmap(resource_path('assets\\telegram.ico'))
        except: 
            pass

        title_label = Label(schedule_window, text='Schedule Message',
                            font=('goudy old style', 20, 'bold'),
                            fg='white', bg='dodger blue2')
        title_label.pack(pady=15)

        schedule_label = Label(schedule_window, text="Select Date:",
                               font=('times new roman', 14, 'bold'),
                               bg='dodger blue2', fg='white')
        schedule_label.pack(pady=5)

        self.schedule_date = DateEntry(schedule_window, width=15,
                                       font=('times new roman', 12),
                                       date_pattern='yyyy-mm-dd',
                                       background='dodger blue4', foreground='white',
                                       borderwidth=2, relief="groove")
        self.schedule_date.pack(pady=5)

        time_label = Label(schedule_window, text="Select Time (HH:MM) 24h format:",
                           font=('times new roman', 12, 'bold'),
                           bg='dodger blue2', fg='white')
        time_label.pack(pady=5)

        time_frame = Frame(schedule_window, bg='dodger blue2')
        time_frame.pack(pady=5)

        self.hour_spinbox = Spinbox(time_frame, from_=0, to=23, width=5,
                                    font=('times new roman', 12),
                                    format="%02.0f", bd=2, relief="groove",
                                    bg='white', fg='black')
        self.hour_spinbox.grid(row=0, column=0, padx=5)
        self.hour_spinbox.delete(0, 'end')
        self.hour_spinbox.insert(0, f"{datetime.now().hour:02}")

        Label(time_frame, text=":", font=('times new roman', 12, 'bold'), 
              bg='dodger blue2', fg='white').grid(row=0, column=1)

        self.minute_spinbox = Spinbox(time_frame, from_=0, to=59, width=5,
                                      font=('times new roman', 12),
                                      format="%02.0f", bd=2, relief="groove",
                                      bg='white', fg='black')
        self.minute_spinbox.grid(row=0, column=2, padx=5)
        self.minute_spinbox.delete(0, 'end')
        self.minute_spinbox.insert(0, f"{datetime.now().minute:02}")

        schedule_button = Button(schedule_window, text="Schedule",
                                 font=('times new roman', 14, 'bold'),
                                 bg='gold2', fg='black', cursor='hand2',
                                 activebackground='dodger blue4', activeforeground='white',
                                 borderwidth=0, command=lambda: self.save_schedule(schedule_window))
        schedule_button.pack(pady=20)
   
    def show_shortcuts(self):
        messagebox.showinfo(
            "Telegram Bot Sender Shortcuts",
            "Keyboard Shortcuts:\n\n"
            "Ctrl + Enter  → Send Message\n"
            "Ctrl + S      → Schedule Message\n"
            "Ctrl + A      → Add Attachments\n"
            "Ctrl + M      → Speak (Voice Input)\n"
            "Ctrl + L      → Clear All Fields\n"
            "Ctrl + C      → Open Settings Dialog\n"
            "Ctrl + H      → Help\n"
            "Ctrl + Q      → Exit Application\n",
            parent=self.root
        )

    def save_schedule(self, window):
        chat_id = self.chat_id_var.get().strip()
        subject = self.subject_var.get().strip()
        body = self.textarea.get(1.0, END).strip()
        
        if not chat_id or not subject or not body:
            messagebox.showerror('Error', 'All fields (Recipient, Subject, Message) are required', parent=window)
            return

        message = f'Subject: {subject}\n\n{body}\n\nYour Regards'

        date_str = self.schedule_date.get()
        time_str = f"{self.hour_spinbox.get()}:{self.minute_spinbox.get()}"
        full_time = f"{date_str} {time_str}:00"
        scheduled_dt = datetime.strptime(full_time, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        if scheduled_dt <= now + timedelta(minutes=1):
            messagebox.showerror(
                "Invalid Time",
                "Scheduled time must be at least 1 minute ahead of the current time.",
                parent=window
            )
            return

        task = {
            "time": full_time,
            "chat_id": chat_id,
            "message": message,
            "attachments": self.attachments.copy()
        }

        tasks = []
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, 'r') as f:
                    tasks = json.load(f)
            except: 
                pass
        
        tasks.append(task)
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)

        messagebox.showinfo("Scheduled", f"Message scheduled for {full_time}", parent=window)
        window.destroy()
        self.clear()

    def _start_schedule_monitor(self):
        """Start background thread to monitor scheduled messages"""
        t = threading.Thread(target=self._monitor_schedule, daemon=True)
        t.start()

    def _monitor_schedule(self):
        """Background thread that checks and sends scheduled messages"""
        while True:
            if os.path.exists(SCHEDULE_FILE):
                try:
                    with open(SCHEDULE_FILE, 'r') as f:
                        tasks = json.load(f)
                    
                    now = datetime.now()
                    remaining = []
                    
                    now = datetime.now()
                    remaining = []
                    
                    bot_token = self.bot_token

                    for task in tasks:

                        task_time = datetime.strptime(task['time'], "%Y-%m-%d %H:%M:%S")
                        if now >= task_time:
                            if bot_token:
                                # Use the synchronous bridge for scheduled sends
                                success, msg = self._send_telegram_bot(
                                    bot_token,
                                    task['chat_id'],
                                    task['message'],
                                    task['attachments']
                                )
                                if success:
                                    self.root.after(0, lambda m=msg: messagebox.showinfo("Scheduled Message Sent", m, parent=self.root))
                                else:
                                    print(f"Scheduled send failed: {msg}")
                                    self.root.after(0, lambda m=msg: messagebox.showerror("Scheduled Message Error", f"Failed: {m}", parent=self.root))
                        else:
                            remaining.append(task)
                    
                    # Update schedule file with remaining tasks
                    with open(SCHEDULE_FILE, 'w') as f:
                        json.dump(remaining, f, indent=2)
                        
                except Exception as e:
                    print(f"Scheduler Error: {e}")
            
            time.sleep(30)  # Check every 30 seconds


if __name__ == '__main__':
    root = Tk()
    obj = TelegramBotSender(root)
    root.mainloop()