from tkinter import *
from tkinter import ttk, messagebox,filedialog
from PIL import Image, ImageTk, ImageDraw
import mysql.connector
from pygame import mixer
import speech_recognition 
from email.message import EmailMessage
import smtplib
import os
import io

# Import the ToolTip class from your chatbot1.py file
from chatbot1 import ToolTip 


class emailsender:
    check=False
    def __init__(self, root):
        self.root = root
        self.root.geometry("750x590+80+40")
        self.root.title("Email Sender")
        self.root.resizable(False, False)
        self.root.config(bg='dodger blue2')
        self.root.wm_iconbitmap('assets\\email.ico')

        # ------------------ VARIABLES ------------------ #
        self.name_var = StringVar()
        self.email_var = StringVar()
        self.subject_var=StringVar()
        self.contacts = {}
        self.attachments = []  # To store file paths


        # ------------------ Title Section ------------------ #
        img = Image.open("assets\\Email.png")
        self.photoimg = ImageTk.PhotoImage(img)
        title_frame = Frame(self.root, bg='white')
        title_frame.grid(row=0, column=0)
        title_label = Label(title_frame, text=' Email Sender', image=self.photoimg, compound=LEFT,font=('goudy old style', 28, 'bold'), bg='white', fg='dodger blue2')
        title_label.grid(row=0, column=0)

        img1 = Image.open("assets\\setting.png")
        self.photoimg1 = ImageTk.PhotoImage(img1)
        setting_button = Button(title_frame, image=self.photoimg1, bg='white', cursor='hand2',
                                activebackground='white', borderwidth=0,command=self.setting)
        setting_button.grid(row=0, column=1, padx=15)
        # Add tooltip to setting button
        ToolTip(setting_button, "Email Credentials Settings") 


        # ------------------ To Email Section ------------------ #
        to_label = LabelFrame(root, text='To (Email Address)',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        to_label.grid(row=1, column=0, padx=100,pady=10)

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

        compose_label = LabelFrame(root, text='Compose Email',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        compose_label.grid(row=4, column=0,pady=10,padx=20)

        img2 = Image.open("assets\\mic.png")
        img2 = img2.resize((48,48), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)

        speak_button=Button(compose_label,text='  Speak',image=self.photoimg2,compound=LEFT,
                            font=('arial',12,'bold'),cursor='hand2',bd=0,bg='dodger blue2',activebackground='dodger blue2',command=self.speak)
        speak_button.grid(row=0,column=0)
        

        img3 = Image.open("assets\\attechment.png")
        img3 = img3.resize((48,48), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        attech_button=Button(compose_label,text='  Attachments',image=self.photoimg3,compound=LEFT,font=('arial',12,'bold'),cursor='hand2',bd=0,bg='dodger blue2',activebackground='dodger blue2',command=self.attechment)
        attech_button.grid(row=0,column=1)
        

        # Label for image preview (initially empty)
        self.image_frame = Frame(compose_label)
        self.image_frame.grid(row=1, column=2, rowspan=2, padx=10, sticky='n')

        # List to keep references to thumbnails
        self.image_thumbnails = []

        # textarea
        textarea_frame = Frame(compose_label)
        textarea_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.textarea = Text(textarea_frame, font=('times new roman', 14), height=7, width=77, pady=5, wrap=WORD)
        self.textarea.grid(row=0, column=0, sticky="nsew")

        # Create Scrollbar widget
        scrollbar = Scrollbar(textarea_frame, orient=VERTICAL, command=self.textarea.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Connect Scrollbar to Text
        self.textarea.config(yscrollcommand=scrollbar.set)

        
        

        img4 = Image.open("assets\\email_send.png")
        self.photoimg4 = ImageTk.PhotoImage(img4)

        send_button = Button(root, image=self.photoimg4, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.send_mail)
        send_button.place(x=450,y=500)
        # Add tooltip to send button
        ToolTip(send_button, "Send Email")

        img5 = Image.open("assets\\Clear.png")
        self.photoimg5 = ImageTk.PhotoImage(img5)

        clear_button = Button(root, image=self.photoimg5, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.clear)
        clear_button.place(x=550,y=500)
        # Add tooltip to clear button
        ToolTip(clear_button, "Clear All Fields")

        img6 = Image.open("assets\\exit.png")
        self.photoimg6 = ImageTk.PhotoImage(img6)

        exit_button = Button(root, image=self.photoimg6, bg='dodger blue2', cursor='hand2',
                                activebackground='dodger blue2', borderwidth=0,command=self.iexit)
        exit_button.place(x=650,y=500)
        # Add tooltip to exit button
        ToolTip(exit_button, "Exit Application")




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
            self.cursor.execute("SELECT Student_name,Email FROM student")
            data = self.cursor.fetchall()
            #compress the dictionary and set names and corresponding email value
            self.contacts = {name: email for name, email in data}
            self.get_name_combo['values'] = list(self.contacts.keys())
        except Exception as e:
            messagebox.showerror("Fetch Error", f"Error in fetching student data:\n{e}",parent=self.root)

    def get_data(self, event=""):
        name = self.name_var.get()
        email_address = self.contacts.get(name, "")
        self.email_var.set(email_address)

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
        # Clear attachments and thumbnails as well
        self.attachments = []
        for thumb_ref in self.image_thumbnails:
            # You might need to manage deletion of images from textarea if they are inline
            # For now, just clear the list.
            pass 
        self.image_thumbnails = []

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
                
    
    def setting(self):
        def clear1():
            from_entry.delete(0,END)
            pass_entry.delete(0,END)
        def save():
            if from_entry.get()==''or pass_entry.get()=='':
                messagebox.showerror("Error",'All field are required',parent=root1)
            else:
                with open ('credentials.txt','w') as f1:
                    f1.write(from_entry.get()+','+pass_entry.get())
                    messagebox.showinfo('Information','Credentials Save succesfuly',parent=root1)
        root1=Toplevel()
        root1.title('Setting')
        root1.geometry('620x300+350+70')
        root1.config(bg='dodger blue2')
        root1.resizable(False,False)
        img = Image.open("assets\\Email.png")
        root1.wm_iconbitmap('assets\\email.ico')
        self.photoimg = ImageTk.PhotoImage(img)
        title_label = Label(root1, text='Credential Settings', image=self.photoimg, compound=LEFT,font=('goudy old style', 38, 'bold'), fg='white', bg='gray20')
        title_label.grid(row=0, column=0,padx=75)
        from_label = LabelFrame(root1, text='From (Email Address)',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        from_label.grid(row=1, column=0,pady=15)
        from_entry = Entry(from_label, font=('times new roman', 16, 'bold'),
                              width=35)
        from_entry.grid(row=0, column=0)
        pass_label = LabelFrame(root1, text='Password',
                              font=('times new roman', 16, 'bold'),
                              bd=5, fg='white', bg='dodger blue2')
        pass_label.grid(row=2, column=0,pady=15)
        pass_entry = Entry(pass_label, font=('times new roman', 16, 'bold'),
                              width=35,show='*')
        pass_entry.grid(row=0, column=0)
        save_button = Button(root1, text='Save', bg='gold2',fg='black',cursor='hand2',
                            font=('times new roman', 18, 'bold'),activebackground='gray10',activeforeground='white', borderwidth=0,command=save)
        save_button.place(x=200,y=250)
        # Add tooltip to save button in settings
        ToolTip(save_button, "Save your email credentials")

        clear_button = Button(root1, text='Clear', bg='gold2',fg='black',cursor='hand2',
                            font=('times new roman', 18, 'bold'),activebackground='gray10',activeforeground='white', borderwidth=0,command=clear1)
        clear_button.place(x=320,y=250)
        # Add tooltip to clear button in settings
        ToolTip(clear_button, "Clear credentials fields")

        with open ('credentials.txt')as f:
            for i in f:
                cr=i.strip().split(',')
        from_entry.insert(0,cr[0])
        pass_entry.insert(0,cr[1])

        
        root1.mainloop()

    def attechment(self):
        files = filedialog.askopenfilenames(initialdir='c:/', title='Select Files',parent=self.root)
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

                elif ext in ['mp3','wav']:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((0, 15), f'Audio: {filename}', fill='black')
                    thumb = ImageTk.PhotoImage(img)
                elif ext in ['mp4','avi']:
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((5, 15), f'Video: {filename}', fill='black')
                    thumb = ImageTk.PhotoImage(img)

                else:
                    # Create a placeholder icon for non-image files
                    img = Image.new('RGB', (100, 50), color='lightgray')
                    d = ImageDraw.Draw(img)
                    d.text((0, 15), f'DOC : {filename}', fill='black')
                    thumb = ImageTk.PhotoImage(img)

                # Store reference to prevent garbage collection
                if not hasattr(self, 'thumb_refs'):
                    self.thumb_refs = []
                self.thumb_refs.append(thumb)

                self.textarea.image_create(END, image=thumb)
                self.textarea.insert(END, "\n")



   
    def send_mail(self):
        if self.to_entry.get()=='' or self.subject_entry.get()=='' or self.textarea.get(1.0,END)=='\n':
            messagebox.showerror('Error','All field are required',parent=self.root)
        else:
            self.sending_email(self.to_entry.get(),self.subject_entry.get(),self.textarea.get(1.0,END))

    def sending_email(self,address,subject,msg):
        try:
            messagebox.showwarning("Email Delivery Info",
                                "Our email may initially appear in reciever spam or junk folder.\n\n"
                                "To ensure they receive future emails in their inbox, please tell them to mark the email as 'Not Spam' or move it their inbox.\n\n"
                                "Thank you for your cooperation.",parent=self.root)

            with open ('credentials.txt') as f1:
                for i in f1:
                    cr= i.strip().split(',')
            msg += "\n\nRegards,\nDev\nEmail sender"


            message=EmailMessage()
            message['Reply-To'] = cr[0]
            message['X-Mailer'] = 'Attendence System'
            message['subject']=subject
            message['to']=address
            message['from']=cr[0]
            message.set_content(msg)
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

            

        # here we instantiate the smtp class present in smtp module provide arugument for gmail server and then provide port which in our case is 587 as we use tls method if we used ssl method port would be 465
        #tls = transport layered security
        # ssl =secured socket layer
            s=smtplib.SMTP('smtp.gmail.com',587)
            # start the tls server
            s.starttls()
            s.login(cr[0],cr[1])
            s.send_message(message)

            messagebox.showinfo("Information",'Your Email has been send succesfully',parent=self.root)

        except Exception as e:
            messagebox.showerror("Error",f'Your mail was not sent due to {str(e)}',parent=self.root)



    

if __name__ == '__main__':
    root = Tk()
    obj = emailsender(root)
    root.mainloop()