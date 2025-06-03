from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
from pygame import mixer
import speech_recognition 
import pywhatkit
from chatbot1 import ToolTip 


class msgsender:
    check=False
    def __init__(self, root):
        self.root = root
        self.root.geometry("750x590+80+40")
        self.root.title("Email Sender")
        self.root.resizable(False, False)
        self.root.config(bg='dodger blue2')
        self.root.wm_iconbitmap('assets\\whatsapp.ico')

        # ------------------ VARIABLES ------------------ #
        self.name_var = StringVar()
        self.email_var = StringVar()
        self.subject_var=StringVar()
        


        # ------------------ Title Section ------------------ #
        img = Image.open("assets\\whatsapp.png")
        self.photoimg = ImageTk.PhotoImage(img)
        title_frame = Frame(self.root, bg='white')
        title_frame.grid(row=0, column=0)
        title_label = Label(title_frame, text=' Whatsapp Message Sender', image=self.photoimg, compound=LEFT,font=('goudy old style', 28, 'bold'), bg='white', fg='dodger blue2')
        title_label.grid(row=0, column=0)

       

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
        ToolTip(send_button, "Send WhatsApp message")

        img5 = Image.open("assets\\Clear.png")
        self.photoimg5 = ImageTk.PhotoImage(img5)

        clear_button = Button(root, image=self.photoimg5, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.clear)
        clear_button.place(x=550,y=500)
        # Add tooltip to clear button
        ToolTip(clear_button, "Clear all fields")

        img6 = Image.open("assets\\exit.png")
        self.photoimg6 = ImageTk.PhotoImage(img6)

        exit_button = Button(root, image=self.photoimg6, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.iexit)
        exit_button.place(x=650,y=500)
        # Add tooltip to exit button
        ToolTip(exit_button, "Exit application")




        # ------------------ Fetch from DB ------------------ #
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
                
    def send_whatsapp(self):
        phone = self.to_entry.get()
        phone=f'+91{phone}'
        subject=self.subject_entry.get()
        message = self.textarea.get(1.0,END)
        message=f'Subject : \n{subject}\n\n {message} \n\n Your Regards'

        if  self.to_entry.get=='' or self.subject_entry.get()==''or self.textarea.get(1.0,END).strip()=='':
            messagebox.showerror("Error", "All fields are required.",parent=self.root)
            
        else:

            try:
                messagebox.showwarning("Whatsapp Delivery Info",
                                    "You must log in to WhatsApp in your default browser before proceeding.",parent=self.root)
                # Send instantly with wait_time=30 seconds before typing starts
                pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=30, tab_close=True)
                messagebox.showinfo("Success", "Message sent (or being sent) succesfuly!",parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", str(e),parent=self.root)
        
   

   
       


if __name__ == '__main__':
    root = Tk()
    obj = msgsender(root)
    root.mainloop()