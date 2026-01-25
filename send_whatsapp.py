from tkinter import *
from tkinter import ttk, messagebox, Spinbox
from tkcalendar import DateEntry
import json
import threading
import time
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import mysql.connector
from pygame import mixer
import speech_recognition 
import pywhatkit

from tooltip import ToolTip

class msgsender:
    check=False
    def __init__(self, root):
        self.root = root
        self.root.geometry("850x590+80+40")
        self.root.title("Whatsapp Sender")
        self.root.resizable(False, False)
        self.root.config(bg='dodger blue2')
        self.root.wm_iconbitmap('assets\\whatsapp.ico')

        # ------------------ VARIABLES ------------------ #
        self.name_var = StringVar()
        self.email_var = StringVar()
        self.subject_var=StringVar()
        
        # Scheduling variables
        self.scheduled_time = None
        self.scheduled_whatsapp_data = None
        self.scheduled_whatsapp_file = "scheduled_whatsapp.json"
        self._start_schedule_monitor()
        


        # ------------------ Title Section ------------------ #
        img = Image.open("assets\\whatsapp.png")
        self.photoimg = ImageTk.PhotoImage(img)
        title_frame = Frame(self.root, bg='white')
        title_frame.grid(row=0, column=0)
        help_button = Button(title_frame,image=self.photoimg ,bg='white', cursor='hand2',
                                activebackground='white', borderwidth=0, command=self.show_shortcuts)
        help_button.grid(row=0, column=0, padx=15)
        ToolTip(help_button, "Help For Shortcuts <Control-h> ")
        title_label = Label(title_frame, text=' Whatsapp Message Sender',font=('goudy old style', 28, 'bold'), bg='white', fg='dodger blue2')
        title_label.grid(row=0, column=1)

       

        # ------------------ To Email Section ------------------ #
        to_label = LabelFrame(root, text='To (Phone Number)',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        to_label.grid(row=1, column=0, padx=100,pady=15)

        # Entry for Email (bound to self.email_var)
        self.to_entry = Entry(to_label, font=('times new roman', 16, 'bold'),
                              width=25,state='readonly', textvariable=self.email_var)
        self.to_entry.grid(row=0, column=0)

        # ComboBox for Names (bound to self.name_var)
        self.get_name_combo = ttk.Combobox(to_label, font=('times new roman', 12, 'bold'),
                                         width=20, state='readonly', cursor='hand2',
                                         textvariable=self.name_var)
        self.get_name_combo.set("Select Name")
        self.get_name_combo.grid(row=0, column=1, padx=15, sticky=W)
        self.get_name_combo.bind("<<ComboboxSelected>>", self.get_data)

        subject_label=LabelFrame(root, text='Subject',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        subject_label.grid(row=3, column=0,pady=10)

        self.subject_entry=Entry(subject_label, font=('times new roman', 16, 'bold'),
                              width=25, textvariable=self.subject_var)
        self.subject_entry.grid(row=0,column=0)

        compose_label = LabelFrame(root, text='Compose Message ',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        compose_label.grid(row=4, column=0,pady=10,padx=20)

        img2 = Image.open("assets\\mic.png")
        img2 = img2.resize((52,52), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)

        speak_button=Button(compose_label,text='  Speak',image=self.photoimg2,compound=LEFT,
                            font=('arial',18,'bold'),cursor='hand2',bd=0,bg='dodger blue2',activebackground='dodger blue2',command=self.speak)
        speak_button.grid(row=0,column=0)
        ToolTip(speak_button, "Speak <Control-m>")
        


       

        # textarea
        textarea_frame = Frame(compose_label)
        textarea_frame.grid(row=1, column=0,sticky="nsew")
        self.textarea = Text(textarea_frame, font=('times new roman', 14), height=7, width=77, pady=0, wrap=WORD)
        self.textarea.grid(row=0, column=0, sticky="nsew")

        # Create Scrollbar widget
        scrollbar = Scrollbar(textarea_frame, orient=VERTICAL, command=self.textarea.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Connect Scrollbar to Text
        self.textarea.config(yscrollcommand=scrollbar.set)

        
        

        img4 = Image.open("assets\\email_send.png")
        self.photoimg4 = ImageTk.PhotoImage(img4)

        send_button = Button(root, image=self.photoimg4, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.send_whatsapp)
        send_button.place(x=450,y=500)
        # Add tooltip to send button
        ToolTip(send_button, "Send WhatsApp message <Control-Return>")


        img8 = Image.open("assets\\scheduled.png")
        self.photoimg8 = ImageTk.PhotoImage(img8)
        schedule_button = Button(self.root, image=self.photoimg8, bg='dodger blue2', cursor='hand2',
                                 activebackground='dodger blue2', borderwidth=0, command=self.open_schedule_window)
        schedule_button.place(x=550, y=500)
        ToolTip(schedule_button, "Schedule WhatsApp Message <Control-s>")

        img5 = Image.open("assets\\Clear.png")
        self.photoimg5 = ImageTk.PhotoImage(img5)

        clear_button = Button(root, image=self.photoimg5, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.clear)
        clear_button.place(x=650,y=500)
        # Add tooltip to clear button
        ToolTip(clear_button, "Clear all fields <Control-l>")

        img6 = Image.open("assets\\exit.png")
        self.photoimg6 = ImageTk.PhotoImage(img6)

        exit_button = Button(root, image=self.photoimg6, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.iexit)
        exit_button.place(x=750,y=500)
        # Add tooltip to exit button
        ToolTip(exit_button, "Exit application <Control-q>")
        messagebox.showwarning("Whatsapp Delivery Info",
                                    "You must log in to WhatsApp in your default browser before proceeding.",parent=self.root)

        




        # ------------------ Fetch from DB ------------------ #
        self.connect_db()
        self.fetch_students()
        self.bind_shortcuts()
        # self.show_shortcuts()

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
            messagebox.showerror("Database Error", f"Error connecting to database:\n{e}",parent=self.root)

    def fetch_students(self):
        try:
            self.cursor.execute("SELECT Student_name,Phone FROM student")
            data = self.cursor.fetchall()
            #compress the dictionary and set names and corresponding email value
            self.contacts = {name: phone for name, phone in data}
            self.get_name_combo['values'] = list(self.contacts.keys())
        except Exception as e:
            messagebox.showerror("Fetch Error", f"Error in fetching student data:\n{e}",parent=self.root)

    def get_data(self, event=""):
        name = self.name_var.get()
        phone_no = self.contacts.get(name, "")
        self.email_var.set(phone_no)

    def iexit(self):
        exit=messagebox.askyesno('Notification','Do you want to exit the application',parent=self.root)
        if exit>0:
            self.root.destroy()
        else:
            return
        
    def clear(self):
        self.to_entry.delete(0,END)
        self.subject_entry.delete(0,END)
        self.textarea.delete(1.0,END)
        self.scheduled_time = None
        self.scheduled_whatsapp_data = None

    def speak(self):
        mixer.init()
        mixer.music.load('assets\\beep.mp3')
        mixer.music.play()
        sr=speech_recognition.Recognizer()
        with speech_recognition.Microphone() as m:
            try:
                sr.adjust_for_ambient_noise(m,duration=0.2)
                audio=sr.listen(m)
                text=sr.recognize_google(audio)
                self.textarea.insert(END,text+'.')
                
            except Exception as e:
                messagebox.showerror('Speech Recognition Error',f'Sorry your speech is not recognised due to {str(e)}',parent=self.root)
                
    def bind_shortcuts(self):
        self.root.bind("<Control-Return>", lambda e: self.send_whatsapp())

        self.root.bind("<Control-s>", lambda e: self.open_schedule_window())
        self.root.bind("<Control-S>", lambda e: self.open_schedule_window())

        self.root.bind("<Control-l>", lambda e: self.clear())
        self.root.bind("<Control-L>", lambda e: self.clear())

        self.root.bind("<Control-q>", lambda e: self.iexit())
        self.root.bind("<Control-Q>", lambda e: self.iexit())
        self.root.bind("<Control-m>", lambda e: self.speak())
        self.root.bind("<Control-M>", lambda e: self.speak())
        self.root.bind("<Control-h>", lambda e: self.show_shortcuts())
        self.root.bind("<Control-H>", lambda e: self.show_shortcuts())

   
    def show_shortcuts(self):
        messagebox.showinfo(
            "WhatsApp Sender Shortcuts",
            "Keyboard Shortcuts:\n\n"
            "Ctrl + Enter  → Send WhatsApp Message\n"
            "Ctrl + S      → Schedule WhatsApp Message\n"
            "Ctrl + M      → Speak (Voice Input)\n"
            "Ctrl + L      → Clear All Fields\n"
            "Ctrl + H      → HELP\n"
            "Ctrl + Q      → Exit Application\n",
            parent=self.root
        )


    def send_whatsapp(self):
        phone_raw = self.to_entry.get().strip()
        subject = self.subject_entry.get().strip()
        message_raw = self.textarea.get(1.0, END).strip()

        if not phone_raw or not subject or not message_raw:
            messagebox.showerror("Error", "All fields are required.", parent=self.root)
            return

        phone = f'+91{phone_raw}'
        message = f'Subject : \n{subject}\n\n {message_raw} \n\n Your Regards'

        try:
            # Send instantly with wait_time=30 seconds before typing starts
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=30, tab_close=True)
            messagebox.showinfo("Success", "Message sent (or being sent) succesfuly!", parent=self.root)
            self.clear()
        except Exception as e:
                messagebox.showerror("Error", str(e),parent=self.root)

    def open_schedule_window(self):
        self.schedule_window = Toplevel(self.root)
        self.schedule_window.title("Schedule WhatsApp Message")
        self.schedule_window.geometry("400x320+200+100")
        self.schedule_window.config(bg='dodger blue2')
        self.schedule_window.resizable(False, False)

        try:
            self.schedule_window.wm_iconbitmap('assets\\whatsapp.ico')
        except Exception:
            pass

        title_label = Label(self.schedule_window, text='Schedule Message',
                            font=('goudy old style', 20, 'bold'),
                            fg='white', bg='dodger blue2')
        title_label.pack(pady=15)

        schedule_label = Label(self.schedule_window, text="Select Date:",
                               font=('times new roman', 14, 'bold'),
                               bg='dodger blue2', fg='white')
        schedule_label.pack(pady=5)

        self.schedule_date = DateEntry(self.schedule_window, width=15,
                                       font=('times new roman', 12),
                                       date_pattern='yyyy-mm-dd',
                                       background='dodger blue4', foreground='white',
                                       borderwidth=2, relief="groove")
        self.schedule_date.pack(pady=5)

        time_label = Label(self.schedule_window, text="Select Time (HH:MM) in 24-hour format:",
                           font=('times new roman', 12, 'bold'),
                           bg='dodger blue2', fg='white')
        time_label.pack(pady=5)

        time_frame = Frame(self.schedule_window, bg='dodger blue2')
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
        schedule_button = Button(self.schedule_window, text="Schedule Message",
                                 font=('times new roman', 14, 'bold'),
                                 bg='gold2', fg='black', cursor='hand2',
                                 activebackground='dodger blue4', activeforeground='white',
                                 borderwidth=0, command=self.schedule_whatsapp)
        schedule_button.pack(pady=20)
        ToolTip(schedule_button, "Confirm and schedule the message")

    def schedule_whatsapp(self):
        phone = self.to_entry.get().strip()
        subject = self.subject_var.get()
        message_body = self.textarea.get(1.0, END).strip()

        if not phone or not subject or not message_body:
            messagebox.showerror('Error', 'Phone, Subject, and Message Body must not be empty.', parent=self.root)
            return

        phone = f'+91{phone}'
        full_message = f'Subject : \n{subject}\n\n {message_body} \n\n Your Regards'

        schedule_date_str = self.schedule_date.get()
        schedule_hour = self.hour_spinbox.get()
        schedule_minute = self.minute_spinbox.get()

        try:
            scheduled_datetime = datetime.strptime(f"{schedule_date_str} {schedule_hour}:{schedule_minute}", "%Y-%m-%d %H:%M")
            now = datetime.now()

            # Require scheduled time to be at least 1 minute ahead
            min_allowed_time = now + timedelta(minutes=1)

            if scheduled_datetime <= min_allowed_time:
                messagebox.showerror(
                    "Invalid Time",
                    "Scheduled time must be at least 1 minute ahead of the current time.",
                    parent=self.schedule_window
                )
                return

            scheduled_whatsapp_data = {
                "time": scheduled_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "phone": phone,
                "message": full_message,
            }

            if os.path.exists(self.scheduled_whatsapp_file):
                with open(self.scheduled_whatsapp_file, "r") as f:
                    try:
                        all_schedules = json.load(f)
                    except json.JSONDecodeError:
                        all_schedules = []
            else:
                all_schedules = []

            all_schedules.append(scheduled_whatsapp_data)
            with open(self.scheduled_whatsapp_file, "w") as f:
                json.dump(all_schedules, f, indent=2)

            messagebox.showinfo("Scheduled", f"Message scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}", parent=self.root)
            self.clear()
            if self.schedule_window.winfo_exists():
                self.schedule_window.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format. Please ensure valid date and time.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error scheduling message: {e}", parent=self.root)

    def _start_schedule_monitor(self):
        monitor_thread = threading.Thread(target=self._monitor_scheduled_messages, daemon=True)
        monitor_thread.start()

    def _monitor_scheduled_messages(self):
        while True:
            if os.path.exists(self.scheduled_whatsapp_file):
                with open(self.scheduled_whatsapp_file, "r+") as f:
                    try:
                        schedules = json.load(f)
                    except json.JSONDecodeError:
                        schedules = []

                    now = datetime.now()
                    remaining_schedules = []

                    for msg_data in schedules:
                        try:
                            scheduled_time = datetime.strptime(msg_data["time"], "%Y-%m-%d %H:%M:%S")
                            if now >= scheduled_time:
                                self._send_scheduled_whatsapp(msg_data)
                            else:
                                remaining_schedules.append(msg_data)
                        except Exception as e:
                            print(f"Error processing scheduled message entry: {e}. Skipping this entry.")

                    f.seek(0)
                    json.dump(remaining_schedules, f, indent=2)
                    f.truncate()

            time.sleep(30)

    def _send_scheduled_whatsapp(self, msg_data):
        try:
            phone = msg_data.get("phone")
            message = msg_data.get("message")
            
            # Send instantly with wait_time=30 seconds before typing starts
            # Using pywhatkit to send instantly opens a new tab
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=30, tab_close=True)
            messagebox.showinfo("Scheduled WhatsApp", f"[Scheduled WhatsApp] Sent or being sent to: {phone}",parent=self.root)
            
        except Exception as e:
            print(f"[Scheduled WhatsApp] Failed to send to {phone}: {e}")
        
  
if __name__ == '__main__':
    root = Tk()
    obj = msgsender(root)
    root.mainloop()