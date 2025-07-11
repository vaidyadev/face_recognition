import os
import io
import smtplib
import threading
import time
import json
import re
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
try:
    from pygame import mixer
    import speech_recognition
    pygame_mixer_available = True
    speech_recognition_available = True
except ImportError:
    pygame_mixer_available = False
    speech_recognition_available = False
    print("Warning: pygame or speech_recognition not found. Speak functionality will be disabled.")
import mysql.connector
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from chatbot1 import ToolTip

class emailsender:
    check = False

    def __init__(self, root):
        self.root = root
        self.root.geometry("750x680+80+0")
        self.root.title("Email Sender")
        self.root.resizable(False, False)
        self.root.config(bg='dodger blue2')
        self.root.wm_iconbitmap('assets\\email.ico')

        # ------------------ VARIABLES ------------------ #
        self.name_var = StringVar()
        self.email_var = StringVar()
        self.subject_var = StringVar()
        self.contacts = {}
        self.attachments = []

        # Scheduling variables
        self.scheduled_time = None
        self.scheduled_email_data = None
        self.scheduled_emails_file = "scheduled_emails.json"
        self._start_schedule_monitor()

        # ------------------ Title Section ------------------ #
        img = Image.open("assets\\Email.png")
        self.photoimg = ImageTk.PhotoImage(img)
        title_frame = Frame(self.root, bg='white')
        title_frame.grid(row=0, column=0, pady=5)
        title_label = Label(title_frame, text=' Email Sender', image=self.photoimg, compound=LEFT,
                             font=('goudy old style', 28, 'bold'), bg='white', fg='dodger blue2')
        title_label.grid(row=0, column=0)

        img1 = Image.open("assets\\setting.png")
        self.photoimg1 = ImageTk.PhotoImage(img1)
        setting_button = Button(title_frame, image=self.photoimg1, bg='white', cursor='hand2',
                                activebackground='white', borderwidth=0, command=self.setting)
        setting_button.grid(row=0, column=1, padx=15)
        ToolTip(setting_button, "Email Credentials Settings")

        # ------------------ To Email Section ------------------ #
        to_label = LabelFrame(root, text='To (Email Address)',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        to_label.grid(row=1, column=0, padx=100, pady=5)

        self.to_entry = Entry(to_label, font=('times new roman', 16, 'bold'),
                              width=25, state='readonly', textvariable=self.email_var)
        self.to_entry.grid(row=0, column=0, pady=2)

        self.get_name_combo = ttk.Combobox(to_label, font=('times new roman', 12, 'bold'),
                                         width=20, state='readonly', cursor='hand2',
                                         textvariable=self.name_var)
        self.get_name_combo.set("Select Name")
        self.get_name_combo.grid(row=0, column=1, padx=15, sticky=W, pady=2)
        self.get_name_combo.bind("<<ComboboxSelected>>", self.get_data)

        subject_label = LabelFrame(root, text='Subject',
                                   font=('times new roman', 16, 'bold'),
                                   bd=5, fg='white', bg='dodger blue2')
        subject_label.grid(row=2, column=0, pady=2)

        self.subject_entry = Entry(subject_label, font=('times new roman', 16, 'bold'),
                                   width=25, textvariable=self.subject_var)
        self.subject_entry.grid(row=0, column=0)

        compose_label = LabelFrame(root, text='Compose Email',
                                   font=('times new roman', 16, 'bold'),
                                   bd=5, fg='white', bg='dodger blue2')
        compose_label.grid(row=3, column=0, pady=5, padx=20)

        img2 = Image.open("assets\\mic.png")
        img2 = img2.resize((48, 48), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)

        speak_button = Button(compose_label, text='  Speak', image=self.photoimg2, compound=LEFT,
                              font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='dodger blue2',
                              activebackground='dodger blue2', command=self.speak)
        speak_button.grid(row=0, column=0)

        img3 = Image.open("assets\\attechment.png")
        img3 = img3.resize((48, 48), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        attech_button = Button(compose_label, text='  Attachments', image=self.photoimg3, compound=LEFT,
                               font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='dodger blue2',
                               activebackground='dodger blue2', command=self.attechment)
        attech_button.grid(row=0, column=1)

        self.image_frame = Frame(compose_label)
        self.image_frame.grid(row=1, column=2, rowspan=2, padx=10, sticky='n')

        self.image_thumbnails = []

        textarea_frame = Frame(compose_label)
        textarea_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.textarea = Text(textarea_frame, font=('times new roman', 14), height=7, width=65, pady=5, wrap=WORD)
        self.textarea.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(textarea_frame, orient=VERTICAL, command=self.textarea.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.textarea.config(yscrollcommand=scrollbar.set)

        # ------------------ Action Buttons ------------------ #
        img4 = Image.open("assets\\email_send.png")
        self.photoimg4 = ImageTk.PhotoImage(img4)
        send_button = Button(root, image=self.photoimg4, bg='dodger blue2', cursor='hand2',
                             activebackground='dodger blue2', borderwidth=0, command=self.send_mail)
        send_button.place(x=290, y=540)
        ToolTip(send_button, "Send Email")

        img8 = Image.open("assets\\scheduled.png")
        self.photoimg8 = ImageTk.PhotoImage(img8)
        schedule_button = Button(self.root, image=self.photoimg8, bg='dodger blue2', cursor='hand2',
                                 activebackground='dodger blue2', borderwidth=0, command=self.open_schedule_window)
        schedule_button.place(x=390, y=540)
        ToolTip(schedule_button, "Schedule E-mail Sending")

        img5 = Image.open("assets\\Clear.png")
        self.photoimg5 = ImageTk.PhotoImage(img5)

        clear_button = Button(root, image=self.photoimg5, bg='dodger blue2', cursor='hand2',
                              activebackground='dodger blue2', borderwidth=0, command=self.clear)
        clear_button.place(x=490, y=540)
        ToolTip(clear_button, "Clear All Fields")

        img6 = Image.open("assets\\exit.png")
        self.photoimg6 = ImageTk.PhotoImage(img6)
        exit_button = Button(root, image=self.photoimg6, bg='dodger blue2', cursor='hand2',
                             activebackground='dodger blue2', borderwidth=0, command=self.iexit)
        exit_button.place(x=590, y=540)
        ToolTip(exit_button, "Exit Application")

        self.connect_db()
        self.fetch_students()

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1582",
                database="face_recognizer"
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error connecting to database:\n{e}", parent=self.root)

    def fetch_students(self):
        try:
            self.cursor.execute("SELECT Student_name,Email FROM student")
            data = self.cursor.fetchall()
            self.contacts = {name: email for name, email in data}
            self.get_name_combo['values'] = list(self.contacts.keys())
        except Exception as e:
            messagebox.showerror("Fetch Error", f"Error in fetching student data:\n{e}", parent=self.root)

    def get_data(self, event=""):
        name = self.name_var.get()
        email_address = self.contacts.get(name, "")
        self.email_var.set(email_address)

    def iexit(self):
        exit = messagebox.askyesno('Notification', 'Do you want to exit the application', parent=self.root)
        if exit > 0:
            self.root.destroy()
        else:
            return

    def clear(self):
        self.to_entry.config(state='normal')
        self.to_entry.delete(0, END)
        self.to_entry.config(state='readonly')
        self.subject_entry.delete(0, END)
        self.textarea.delete(1.0, END)
        self.attachments = []
        self.image_thumbnails = []
        self.name_var.set("Select Name")
        self.email_var.set("")
        self.scheduled_time = None
        self.scheduled_email_data = None
        messagebox.showinfo("Information", "All fields cleared.", parent=self.root)

    def speak(self):
        if not pygame_mixer_available:
            messagebox.showerror('Error', 'Pygame mixer is not available. Please install pygame to use speak functionality.', parent=self.root)
            return
        if not speech_recognition_available:
            messagebox.showerror('Error', 'SpeechRecognition is not available. Please install SpeechRecognition to use speak functionality.', parent=self.root)
            return

        mixer.init()
        try:
            mixer.music.load('assets\\beep.mp3')
            mixer.music.play()
        except Exception as e:
            messagebox.showerror('Error', f'Could not load beep.mp3: {e}', parent=self.root)
            return

        sr = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as m:
            try:
                sr.adjust_for_ambient_noise(m, duration=0.2)
                audio = sr.listen(m)
                text = sr.recognize_google(audio)
                self.textarea.insert(END, text + '.')

            except Exception as e:
                messagebox.showerror('Speech Recognition Error', f'Sorry your speech is not recognised due to {str(e)}',
                                     parent=self.root)

    def setting(self):
        self.password_visible = False

        def clear1():
            from_entry.delete(0, END)
            pass_entry.delete(0, END)

        def save():
            if from_entry.get() == '' or pass_entry.get() == '':
                messagebox.showerror("Error", 'All fields are required', parent=root1)
            else:
                with open('credentials.txt', 'w') as f1:
                    f1.write(from_entry.get() + ',' + pass_entry.get())
                    messagebox.showinfo('Information', 'Credentials Save successfully', parent=root1)

        def toggle_password_visibility():
            self.password_visible = not self.password_visible
            if self.password_visible:
                pass_entry.config(show='')
                try:
                    self.eye_toggle_button.config(image=self.eye_open_photo, text="", compound=LEFT)
                except AttributeError:
                    self.eye_toggle_button.config(text="Hide")
            else:
                pass_entry.config(show='*')
                try:
                    self.eye_toggle_button.config(image=self.eye_closed_photo, text="", compound=LEFT)
                except AttributeError:
                    self.eye_toggle_button.config(text="Show")

        root1 = Toplevel()
        root1.title('Setting')
        root1.geometry('620x350+350+70')
        root1.config(bg='dodger blue2')
        root1.resizable(False, False)
        img = Image.open("assets\\Email.png")
        root1.wm_iconbitmap('assets\\email.ico')
        self.photoimg = ImageTk.PhotoImage(img)
        title_label = Label(root1, text='Credential Settings', image=self.photoimg, compound=LEFT,
                            font=('goudy old style', 38, 'bold'), fg='white', bg='gray20')
        title_label.grid(row=0, column=0, padx=75)
        from_label = LabelFrame(root1, text='From (Email Address)',
                                font=('times new roman', 16, 'bold'),
                                bd=5, fg='white', bg='dodger blue2')
        from_label.grid(row=1, column=0, pady=15)
        from_entry = Entry(from_label, font=('times new roman', 16, 'bold'),
                           width=35)
        from_entry.grid(row=0, column=0)
        pass_label = LabelFrame(root1, text='Password',
                                font=('times new roman', 16, 'bold'),
                                bd=5, fg='white', bg='dodger blue2')
        pass_label.grid(row=2, column=0, pady=15)
        pass_entry = Entry(pass_label, font=('times new roman', 16, 'bold'),
                           width=35, show='*')
        pass_entry.grid(row=0, column=0)

        try:
            eye_open_img = Image.open("assets\\eye_open.png")
            eye_open_img = eye_open_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.eye_open_photo = ImageTk.PhotoImage(eye_open_img)

            eye_closed_img = Image.open("assets\\eye_closed.png")
            eye_closed_img = eye_closed_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.eye_closed_photo = ImageTk.PhotoImage(eye_closed_img)

            self.eye_toggle_button = Button(pass_label, image=self.eye_closed_photo,
                                            command=toggle_password_visibility,
                                            bd=0, bg='dodger blue2', activebackground='dodger blue2',
                                            cursor='hand2')
            self.eye_toggle_button.grid(row=0, column=1, padx=5, sticky=W)
            ToolTip(self.eye_toggle_button, "Show/Hide Password")

        except FileNotFoundError:
            self.eye_toggle_button = Button(pass_label, text="Show",
                                            command=toggle_password_visibility,
                                            font=('times new roman', 10), bg='dodger blue2', fg='white',
                                            activebackground='dodger blue2', activeforeground='white',
                                            cursor='hand2')
            self.eye_toggle_button.grid(row=0, column=1, padx=5, sticky=W)
            ToolTip(self.eye_toggle_button, "Show/Hide Password")
            messagebox.showwarning("Asset Warning", "assets\\eye_open.png or assets\\eye_closed.png not found. Using text button for password toggle.", parent=root1)


        save_button = Button(root1, text='Save', bg='gold2', fg='black', cursor='hand2',
                             font=('times new roman', 18, 'bold'), activebackground='gray10',
                             activeforeground='white', borderwidth=0, command=save)
        save_button.place(x=200, y=290)
        ToolTip(save_button, "Save your email credentials")

        clear_button = Button(root1, text='Clear', bg='gold2', fg='black', cursor='hand2',
                            font=('times new roman', 18, 'bold'),activebackground='gray10',activeforeground='white', borderwidth=0,command=clear1)
        clear_button.place(x=320,y=290)
        ToolTip(clear_button, "Clear credentials fields")

        try:
            with open('credentials.txt')as f:
                for i in f:
                    cr=i.strip().split(',')
            from_entry.insert(0,cr[0])
            pass_entry.insert(0,cr[1])
        except FileNotFoundError:
            pass


        root1.mainloop()

    def attechment(self):
        files = filedialog.askopenfilenames(initialdir=os.getcwd(), title='Select Files', parent=self.root)
        for file_path in files:
            if file_path not in self.attachments:
                self.attachments.append(file_path)
                filename = os.path.basename(file_path)
                self.textarea.insert(END, f"\n")

                ext = filename.split('.')[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'ico']:
                    img = Image.open(file_path)
                    img.thumbnail((50, 50))
                    thumb = ImageTk.PhotoImage(img)

                elif ext in ['mp3', 'wav']:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((0, 15), f'Audio: {filename}', fill='black')
                    thumb = ImageTk.PhotoImage(img)
                elif ext in ['mp4', 'avi']:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((5, 15), f'Video: {filename}', fill='black')
                    thumb = ImageTk.PhotoImage(img)

                else:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((0, 15), f'DOC : {filename}', fill='black')
                    thumb = ImageTk.PhotoImage(img)

                if not hasattr(self, 'thumb_refs'):
                    self.thumb_refs = []
                self.thumb_refs.append(thumb)

                self.textarea.image_create(END, image=thumb)
                self.textarea.insert(END, "\n")

    def send_mail(self):
        recipient_address = self.to_entry.get().strip()
        subject = self.subject_var.get()
        message_body = self.textarea.get(1.0, END).strip()

        if not recipient_address or not subject or not message_body:
            messagebox.showerror('Error', 'All fields (To, Subject, Message) are required', parent=self.root)
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_address):
            messagebox.showerror('Error', 'Please enter a valid email address for the recipient.', parent=self.root)
            return

        self.sending_email(recipient_address, subject, message_body)

    def sending_email(self, address, subject, msg):
        from email.message import EmailMessage
        try:
            messagebox.showwarning("Email Delivery Info",
                                "Our email may initially appear in receiver's spam or junk folder.\n\n"
                                "To ensure they receive future emails in their inbox, please tell them to mark the email as 'Not Spam' or move it their inbox.\n\n"
                                "Thank you for your cooperation.", parent=self.root)

            with open('credentials.txt') as f1:
                cr = f1.readline().strip().split(',')
            sender_email = cr[0]
            sender_password = cr[1]

            msg_full = msg + "\n\nRegards,\nDev\nEmail sender"

            message = EmailMessage()
            message['Reply-To'] = sender_email
            message['X-Mailer'] = 'Attendance System'
            message['subject'] = subject
            message['to'] = address
            message['from'] = sender_email
            message.set_content(msg_full)

            for path in self.attachments:
                filename = os.path.basename(path)
                ext = filename.split('.')[-1].lower()
                with open(path, 'rb') as f:
                    file_data = f.read()
                if ext in ['png', 'jpg', 'jpeg', 'ico']:
                    img = Image.open(io.BytesIO(file_data))
                    subtype = img.format.lower()
                    message.add_attachment(file_data, maintype='image', subtype=subtype, filename=filename)
                else:
                    message.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(sender_email, sender_password)
            s.send_message(message)
            s.quit()

            messagebox.showinfo("Information", 'Your Email has been sent successfully', parent=self.root)

        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Error", "Failed to login to SMTP server. Check your email and password in settings.", parent=self.root)
        except FileNotFoundError:
             messagebox.showerror("Error", "Credentials file (credentials.txt) not found. Please set your email and password in settings.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f'Your mail was not sent due to {str(e)}', parent=self.root)

    def open_schedule_window(self):
        schedule_window = Toplevel(self.root)
        schedule_window.title("Schedule Email")
        schedule_window.geometry("400x320+200+100")
        schedule_window.config(bg='dodger blue2')
        schedule_window.resizable(False, False)

        try:
            schedule_window.wm_iconbitmap('assets\\email.ico')
        except Exception:
            pass

        title_label = Label(schedule_window, text='Schedule Email',
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

        time_label = Label(schedule_window, text="Select Time (HH:MM) in ISO format(24 hour format):",
                           font=('times new roman', 12, 'bold'),
                           bg='dodger blue2', fg='white')
        time_label.pack(pady=5)

        time_frame = Frame(schedule_window, bg='dodger blue2')
        time_frame.pack(pady=5)

        self.hour_spinbox = Spinbox(time_frame, from_=0, to=23, width=5,
                                    font=('times new roman', 12),
                                    format="%02.0f", bd=2, relief="groove",
                                    bg='white', fg='black', buttonbackground='dodger blue4')
        self.hour_spinbox.grid(row=0, column=0, padx=5)
        ToolTip(self.hour_spinbox, "Enter hour (00-23)")
        self.hour_spinbox.delete(0, 'end')
        self.hour_spinbox.insert(0, f"{datetime.now().hour:02}")

        colon_label = Label(time_frame, text=":", font=('times new roman', 12, 'bold'), bg='dodger blue2', fg='white')
        colon_label.grid(row=0, column=1)

        self.minute_spinbox = Spinbox(time_frame, from_=0, to=59, width=5,
                                      font=('times new roman', 12),
                                      format="%02.0f", bd=2, relief="groove",
                                      bg='white', fg='black', buttonbackground='dodger blue4')
        self.minute_spinbox.grid(row=0, column=2, padx=5)

        self.minute_spinbox.delete(0, 'end')
        self.minute_spinbox.insert(0, f"{datetime.now().minute:02}")

        ToolTip(self.minute_spinbox, "Enter minutes (00-59)")
        schedule_button = Button(schedule_window, text="Schedule Email",
                                 font=('times new roman', 14, 'bold'),
                                 bg='gold2', fg='black', cursor='hand2',
                                 activebackground='dodger blue4', activeforeground='white',
                                 borderwidth=0, command=self.schedule_email)
        schedule_button.pack(pady=20)
        ToolTip(schedule_button, "Confirm and schedule the email")

    def schedule_email(self):
        recipient_address = self.to_entry.get().strip()
        subject = self.subject_var.get()
        message_body = self.textarea.get(1.0, END).strip()

        if not recipient_address or not subject or not message_body:
            messagebox.showerror('Error', 'Recipient, Subject, and Message Body must not be empty.', parent=self.root)
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_address):
            messagebox.showerror('Error', 'Please enter a valid email address for scheduling.', parent=self.root)
            return

        schedule_date_str = self.schedule_date.get()
        schedule_hour = self.hour_spinbox.get()
        schedule_minute = self.minute_spinbox.get()

        try:
            scheduled_datetime = datetime.strptime(f"{schedule_date_str} {schedule_hour}:{schedule_minute}", "%Y-%m-%d %H:%M")
            if scheduled_datetime < datetime.now():
                messagebox.showerror("Error", "Scheduled time cannot be in the past.")
                return

            scheduled_email_data = {
                "time": scheduled_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "recipients": [recipient_address],
                "subject": subject,
                "body": message_body,
                "attachments": self.attachments.copy()
            }

            if os.path.exists(self.scheduled_emails_file):
                with open(self.scheduled_emails_file, "r") as f:
                    try:
                        all_schedules = json.load(f)
                    except json.JSONDecodeError:
                        all_schedules = []
            else:
                all_schedules = []

            all_schedules.append(scheduled_email_data)
            with open(self.scheduled_emails_file, "w") as f:
                json.dump(all_schedules, f, indent=2)

            messagebox.showinfo("Scheduled", f"Email scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}", parent=self.root)
            self.clear()
            if self.schedule_date.winfo_exists():
                self.schedule_date.master.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format. Please ensure valid date and time.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error scheduling email: {e}", parent=self.root)

    def _start_schedule_monitor(self):
        monitor_thread = threading.Thread(target=self._monitor_scheduled_emails, daemon=True)
        monitor_thread.start()

    def _monitor_scheduled_emails(self):
        from email.message import EmailMessage
        while True:
            if os.path.exists(self.scheduled_emails_file):
                with open(self.scheduled_emails_file, "r+") as f:
                    try:
                        schedules = json.load(f)
                    except json.JSONDecodeError:
                        schedules = []

                    now = datetime.now()
                    remaining_schedules = []

                    for email_data in schedules:
                        try:
                            scheduled_time = datetime.strptime(email_data["time"], "%Y-%m-%d %H:%M:%S")
                            if now >= scheduled_time:
                                self._send_scheduled_email(email_data)
                            else:
                                remaining_schedules.append(email_data)
                        except Exception as e:
                            print(f"Error processing scheduled email entry: {e}. Skipping this entry.")

                    f.seek(0)
                    json.dump(remaining_schedules, f, indent=2)
                    f.truncate()

            time.sleep(30)

    def _send_scheduled_email(self, email_data):
        from email.message import EmailMessage
        try:
            with open('credentials.txt') as f1:
                cr = f1.readline().strip().split(',')
            sender_email = cr[0]
            sender_password = cr[1]

            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(sender_email, sender_password)

            recipient_list = email_data.get("recipients", [])
            subject = email_data.get("subject", "No Subject")
            body = email_data.get("body", "") + "\n\nRegards,\nDev\nEmail sender"
            attachments = email_data.get("attachments", [])

            for recipient in recipient_list:
                try:
                    msg = EmailMessage()
                    msg['From'] = sender_email
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    msg.set_content(body)

                    for path in attachments:
                        try:
                            if not os.path.exists(path):
                                print(f"Scheduled attachment not found: {path}")
                                continue

                            with open(path, 'rb') as f:
                                data = f.read()
                            filename = os.path.basename(path)
                            ext = filename.split('.')[-1].lower()
                            if ext in ['png', 'jpg', 'jpeg', 'ico']:
                                try:
                                    img = Image.open(io.BytesIO(data))
                                    subtype = img.format.lower()
                                    msg.add_attachment(data, maintype='image', subtype=subtype, filename=filename)
                                except Exception as img_e:
                                    print(f"Failed to process image attachment {filename}: {img_e}. Attaching as octet-stream.")
                                    msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
                            else:
                                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
                        except Exception as e:
                            print(f"Error adding attachment {path} to scheduled email: {e}")

                    s.send_message(msg)
                    print(f"[Scheduled Email] Sent to: {recipient} (Subject: {subject})")
                    self.root.after(0, lambda r=recipient, s=subject: messagebox.showinfo(
                        "Scheduled Email Sent",
                        f"Scheduled email sent successfully!\n\nTo: {r}\nSubject: {s}",
                        parent=self.root
                    ))

                except Exception as e:
                    print(f"[Scheduled Email] Failed to send to {recipient}: {e}")
                    self.root.after(0, lambda r=recipient, s=subject, error=str(e): messagebox.showerror(
                        "Scheduled Email Failed",
                        f"Failed to send scheduled email to {r} (Subject: {s}): {error}",
                        parent=self.root
                    ))
            s.quit()

        except FileNotFoundError:
            print("Credentials file (credentials.txt) not found for scheduled email. Cannot send.")
            self.root.after(0, lambda: messagebox.showerror(
                "Scheduled Email Error",
                "Credentials file not found. Cannot send scheduled emails. Please set your credentials in settings.",
                parent=self.root
            ))
        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication Error for scheduled email. Check credentials.")
            self.root.after(0, lambda: messagebox.showerror(
                "Scheduled Email Error",
                "Failed to authenticate with SMTP server for scheduled email. Check your email and password in settings.",
                parent=self.root
            ))
        except Exception as e:
            print(f"Unexpected error in sending scheduled email: {e}")
            self.root.after(0, lambda error=str(e): messagebox.showerror(
                "Scheduled Email Error",
                f"An unexpected error occurred while processing scheduled email: {error}",
                parent=self.root
            ))

if __name__ == '__main__':
    root = Tk()
    obj = emailsender(root)
    root.mainloop()