from tkinter import *
from tkinter import Toplevel, Text, BOTH, WORD, END, ttk, Scrollbar
from PIL import Image,ImageTk
from tkinter import messagebox
import re
from config import get_db_connection
import smtplib
from email.message import EmailMessage
from tooltip import ToolTip
from utils import resource_path

class register:
    def __init__(self,root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(True, True) # Enable resizing
        self.root.minsize(1024, 600)    # Match main.py minimum size
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))
    ########################Variables#####################################
        self.var_fname=StringVar()
        self.var_lname=StringVar()
        self.var_contact=StringVar()
        self.var_email=StringVar()
        self.var_security=StringVar()
        self.var_securitya=StringVar()
        self.var_pass=StringVar()
        self.var_cpass=StringVar()
        self.var_chk=StringVar()


        
        self.bg_image_original = Image.open(resource_path("college_images\\di.jpg"))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image_original.resize((1360, 680), Image.Resampling.LANCZOS))
        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Debounce timer for resizing
        self.resize_timer = None
        # Bind resize event
        self.root.bind("<Configure>", self.on_resize)

        # Main Container to hold both the left image and the form
        self.main_container = Frame(self.root, bg='maroon1')
        self.main_container.place(relx=0.5, rely=0.5, anchor=CENTER, width=1100, height=500)

        img4 = Image.open(resource_path("college_images\\reg.jpg"))
        img4 = img4.resize((400,500), Image.Resampling.LANCZOS)
        self.photoimg4 = ImageTk.PhotoImage(img4)
        left_img = Label(self.main_container, image=self.photoimg4)
        left_img.place(x=0, y=0, width=400, height=500)

        # Form frame now sits inside the container
        frame=Frame(self.main_container, bg='maroon1')
        frame.place(x=400, y=0, width=700, height=500)

        register_lbl=Label(frame,text='REGISTER HERE',font=('times new roman',20,'bold'),fg='green',bg='maroon1')
        register_lbl.place(x=20,y=20)

        fname=Label(frame,text='First Name',font=('times new roman',15,'bold'),bg='maroon1')
        fname.place(x=50,y=70)

        self.f_name=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_fname)
        self.f_name.place(x=50,y=110,width=250)

        lname=Label(frame,text='Last Name',font=('times new roman',15,'bold'),bg='maroon1')
        lname.place(x=350,y=70)

        self.l_name=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_lname)
        self.l_name.place(x=350,y=110,width=250)


        contact=Label(frame,text='Contact',font=('times new roman',15,'bold'),bg='maroon1')
        contact.place(x=50,y=150)

        self.contact=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_contact)
        self.contact.place(x=50,y=190,width=250)

        email=Label(frame,text='Email',font=('times new roman',15,'bold'),bg='maroon1')
        email.place(x=350,y=150)

        self.email=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_email)
        self.email.place(x=350,y=190,width=250)

        security_q=Label(frame,text='Select Security Questions',font=('times new roman',15,'bold'),bg='maroon1')
        security_q.place(x=50,y=230)

        security_q_combo=ttk.Combobox(frame,font=('times new roman', 15, 'bold'),state='read',textvariable=self.var_security)
        security_q_combo['values']=('Your Birthplace','Your FriendName','Your BirthDate')
        security_q_combo.set("Select")
        security_q_combo.place(x=50,y=270,width=250)

        security_a=Label(frame,text='Security Answer',font=('times new roman',15,'bold'),bg='maroon1')
        security_a.place(x=350,y=230)

        self.security_a=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_securitya)
        self.security_a.place(x=350,y=270,width=250)

        pasw=Label(frame,text='Password',font=('times new roman',15,'bold'),bg='maroon1')
        pasw.place(x=50,y=310)

        self.pasw=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_pass,show='*')
        self.pasw.place(x=50,y=350,width=250)
        self.pasw.bind('<KeyRelease>', self.check_password_strength)
        self.strength_label = Label(frame, text="", font=('times new roman', 12, 'bold'), fg='red', bg='maroon1')
        self.strength_label.place(x=50, y=380)
        # Prevent copy/paste
        self.pasw.bind("<Control-c>", lambda e: "break")
        self.pasw.bind("<Control-v>", lambda e: "break")
        self.pasw.bind("<Button-3>", lambda e: "break")  # disable right-click

        # Load show/hide images
        self.show_icon = ImageTk.PhotoImage(Image.open(resource_path("college_images/pass_show.png")).resize((25, 25), Image.Resampling.LANCZOS))
        self.hide_icon = ImageTk.PhotoImage(Image.open(resource_path("college_images/pass_hide.png")).resize((25, 25), Image.Resampling.LANCZOS))

        # Password toggle button
        self.show_hide_btn = Button(frame, image=self.show_icon, command=self.toggle_password, bg='maroon1', bd=0, activebackground='maroon1', cursor='hand2')
        self.show_hide_btn.place(x=300, y=350)
        self.password_visible = False

        cnpass=Label(frame,text='Confirm Password',font=('times new roman',15,'bold'),bg='maroon1')
        cnpass.place(x=350,y=310)

        self.cnpass=ttk.Entry(frame,font=('times new roman',15,'bold'),textvariable=self.var_cpass,show='*')
        self.cnpass.place(x=350,y=350,width=250)
          # Prevent copy/paste
        self.cnpass.bind("<Control-c>", lambda e: "break")
        self.cnpass.bind("<Control-v>", lambda e: "break")
        self.cnpass.bind("<Button-3>", lambda e: "break")

        # Toggle show/hide for confirm password
        self.show_icon2 = ImageTk.PhotoImage(Image.open(resource_path("college_images/pass_show.png")).resize((25, 25), Image.Resampling.LANCZOS))
        self.hide_icon2 = ImageTk.PhotoImage(Image.open(resource_path("college_images/pass_hide.png")).resize((25, 25), Image.Resampling.LANCZOS))

        self.show_hide_btn2 = Button(frame, image=self.show_icon2, command=self.toggle_confirm_password, bg='maroon1', bd=0, activebackground='maroon1', cursor='hand2')
        self.show_hide_btn2.place(x=600, y=350)
        self.confirm_password_visible = False

    ##########################################check box#########################
        chk_button = Checkbutton(frame, text="I Agree", onvalue="on", offvalue="off", font=('times new roman', 12, 'bold'), variable=self.var_chk, bg='maroon1',activebackground='maroon1')
        chk_button.place(x=50, y=400)
        self.var_chk.set('off')

        # Add label for Terms & Conditions
        terms_lbl = Label(frame, text="Terms & Conditions", font=('times new roman', 12, 'underline'), fg='blue', bg='maroon1', cursor='hand2')
        terms_lbl.place(x=130, y=400)
        terms_lbl.bind("<Button-1>", self.open_terms_conditions)
        ToolTip(terms_lbl,'Click to read terms and conditions')

        img1 = Image.open(resource_path("college_images\\register-now-button1.jpg"))
        img1 = img1.resize((150,50), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        register_img =Button(frame, image=self.photoimg1,bg='maroon1',borderwidth=0,cursor='hand2',font=('times new roman',15,'bold'),activebackground='maroon1',command=self.register)
        register_img.place(x=50, y=440, width=150)

        img2 = Image.open(resource_path("college_images\\loginpng.png"))
        img2 = img2.resize((150,50), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        login_img = Button(frame, image=self.photoimg2,bg='maroon1',borderwidth=0,cursor='hand2',font=('times new roman',15,'bold'),activebackground='maroon1',command=self.login_now)
        login_img.place(x=450, y=440, width=150)
        ToolTip(register_img, "Shortcut: Ctrl + Enter")
        ToolTip(login_img, "Shortcut: Ctrl + L")
                # Keyboard shortcuts
        self.root.bind("<Control-Return>", lambda e: self.register())
        self.root.bind("<Control-l>", lambda e: self.login_now())

        # Show shortcuts info on startup
        # self.root.after(500, self.show_shortcuts_info)




    #####################Functions################################

    def on_resize(self, event):
        """Variable delay to prevent lag while dragging"""
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_background)

    def update_background(self):
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        
        if new_width < 100 or new_height < 100: return

        image = self.bg_image_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(image)
        self.bg_label.config(image=self.bg_photo)

    def open_terms_conditions(self, event=None):
        terms_window = Toplevel(self.root)
        terms_window.title("Terms and Conditions")
        terms_window.geometry("700x550+100+50")
        terms_window.iconbitmap(resource_path("college_images\\bg1.ico"))
        terms_window.configure(bg='maroon1')
        terms_window.resizable(False, False)

        # Load logo image
        logo_img = Image.open(resource_path("college_images/facialrecognition (1).png")).resize((100, 100), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = Label(terms_window, image=self.logo_photo, bg='maroon1')
        logo_label.pack(pady=(10, 0))

        self.marquee_text = "  FACIAL RECOGNITION ATTENDANCE SYSTEM  "
        self.marquee_label = Label(terms_window, font=("Segoe UI", 16, "bold"), bg="green", fg="red")
        self.marquee_label.pack(pady=(0, 10))
        self.animate_marquee()

        back_btn = Button(terms_window, text="Back", font=('times new roman', 15, 'bold'), bg='red', fg='white',activebackground='green',activeforeground='black',
                          cursor='hand2', command=terms_window.destroy)
        back_btn.pack(pady=10) 

        
        frame = Frame(terms_window, bg="maroon1")
        frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        terms_text = Text(frame, wrap=WORD, font=('Segoe UI', 12), bg='white', fg='#333333', insertbackground='black', relief=FLAT, bd=0, padx=15, pady=15)
        terms_text.pack(side=LEFT, fill=BOTH, expand=True)

        scroll = ttk.Scrollbar(frame, orient=VERTICAL, command=terms_text.yview, style="Vertical.TScrollbar")
        scroll.pack(side=RIGHT, fill=Y)
        terms_text.config(yscrollcommand=scroll.set)

        def on_mousewheel(event):
            terms_text.yview_scroll(int(-1*(event.delta/120)), "units")

        terms_text.bind("<Enter>", lambda e: terms_text.bind_all("<MouseWheel>", on_mousewheel))
        terms_text.bind("<Leave>", lambda e: terms_text.unbind_all("<MouseWheel>"))

        # Configure tags for beautiful formatting
        terms_text.tag_configure("title", font=("Segoe UI", 18, "bold"), justify="center", foreground="#004a99", spacing1=15, spacing3=5)
        terms_text.tag_configure("subtitle", font=("Segoe UI", 13, "bold"), justify="center", foreground="#e63900", spacing3=25)
        terms_text.tag_configure("heading", font=("Segoe UI", 12, "bold"), foreground="#000000", spacing1=15, spacing3=5, lmargin1=10, lmargin2=10)
        terms_text.tag_configure("body", font=("Segoe UI", 11), foreground="#444444", lmargin1=30, lmargin2=30, spacing3=15)
        terms_text.tag_configure("footer", font=("Segoe UI", 11, "italic", "bold"), justify="center", foreground="#004a99", spacing1=30, spacing3=20)

        try:
            with open(resource_path("terms.txt"), "r", encoding="utf-8") as file:
                lines = file.readlines()
                
            for index, line in enumerate(lines):
                line_stripped = line.strip()
                
                if line_stripped == "":
                    continue
                    
                if index == 0:
                    terms_text.insert(END, line_stripped + "\n", "title")
                elif index == 1:
                    terms_text.insert(END, line_stripped + "\n", "subtitle")
                elif re.match(r"^\d+\.\s.*:", line_stripped):
                    terms_text.insert(END, line_stripped + "\n", "heading")
                elif line_stripped.startswith("By continuing"):
                    terms_text.insert(END, line_stripped + "\n", "footer")
                else:
                    terms_text.insert(END, line_stripped + "\n", "body")
                    
        except FileNotFoundError:
            terms_text.insert(END, "⚠️ Terms and Conditions file not found.\n", "title")

        terms_text.config(state=DISABLED)

        
        

    def animate_marquee(self):
        text = self.marquee_text
        self.marquee_text = text[1:] + text[0]
        self.marquee_label.config(text=self.marquee_text)
        self.marquee_label.after(150, self.animate_marquee)

    def register(self):
        self.vemail=self.var_email.get()
        if self.var_fname.get()==''or self.var_lname.get()==''or self.var_contact.get()==''or self.var_email.get()=='' or self.var_security.get()=='Select' or self.var_securitya.get()=='' or self.var_pass.get()=='' or self.var_cpass.get()=='' :
            messagebox.showerror('Error','All fields are required!!')
        elif self.var_pass.get()!= self.var_cpass.get():
            messagebox.showerror('Error','Password and confirm Password must be same')
        elif self.var_chk.get() =='off':
            messagebox.showerror('Error','Please accept our terms and conditions')
        elif not self.vemail.endswith("@gmail.com") or not any(char.isdigit() for char in self.vemail):
                messagebox.showerror("Error", "Please enter a valid Gmail address with at least one digit.")
        elif len(self.var_contact.get())!=10 or not self.var_contact.get().isdigit():
            messagebox.showerror("Error","Please enter a valid Phone No with 10 digits")
        elif not self.is_strong_password(self.var_pass.get()):
           messagebox.showerror(
                        title='Error',
                        message=(
                            'Password must be strong. It should contain at least:\n'
                            '- One digit\n'
                            '- One lowercase letter\n'
                            '- One uppercase letter\n'
                            '- One special character'
                        )
                    )
        else:
            self.var_fname.set(self.var_fname.get().title())
            self.var_lname.set(self.var_lname.get().title())

            try:
                conn=get_db_connection()
                my_cursor=conn.cursor()
                query=('select * from register where email=%s')
                value=(self.var_email.get(),)
                my_cursor.execute(query,value)
                row=my_cursor.fetchone()
                if row!=None:
                    messagebox.showerror('Error','User already exist with this email please try with another email')
                    conn.close()
                    return 
                else:
                    my_cursor.execute('insert into register values(%s,%s,%s,%s,%s,%s,%s)',(
                                self.var_fname.get(),
                                self.var_lname.get(),
                                self.var_contact.get(),
                                self.var_email.get(),
                                self.var_security.get(),
                                self.var_securitya.get(),
                                self.var_pass.get()
                                

                    ))
                conn.commit()
                conn.close()
                messagebox.showinfo('Success','Register Successfuly')
                try:
                    self.send_confirmation_email(self.var_email.get(), self.var_fname.get())
                except Exception as e:
                    messagebox.showerror(f"Email error: {e}")

            except Exception as e:
                messagebox.showerror(f'Registration has not done due to {str(e)}')
                
    def check_password_strength(self, event=None):
        password = self.var_pass.get()

        if len(password) < 6:
            strength = "Too Short"
            color = "bisque"
        elif (re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[0-9]', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
            strength = "Strong"
            color = "green"
        elif (re.search(r'[A-Za-z]', password) and
            re.search(r'[0-9]', password)):
            strength = "Medium"
            color = "cyan"
        else:
            strength = "Weak"
            color = "azure"

        self.strength_label.config(text=f"Strength: {strength}", fg=color)

    def show_shortcuts_info(self):
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "Available Shortcuts:\n\n"
            "Ctrl + Enter  → Register\n"
            "Ctrl + L        → Login"
        )

 
    def toggle_password(self):
        if self.password_visible:
            self.pasw.config(show='*')
            self.show_hide_btn.config(image=self.show_icon)
            self.password_visible = False
        else:
            self.pasw.config(show='')
            self.show_hide_btn.config(image=self.hide_icon)
            self.password_visible = True

    def toggle_confirm_password(self):
        if self.confirm_password_visible:
            self.cnpass.config(show='*')
            self.show_hide_btn2.config(image=self.show_icon2)
            self.confirm_password_visible = False
        else:
            self.cnpass.config(show='')
            self.show_hide_btn2.config(image=self.hide_icon2)
            self.confirm_password_visible = True

    def is_strong_password(self, password):
        return (
            len(password) >= 6 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[0-9]', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        )
  
    def login_now(self):
        self.root.destroy()
        import login  
        root = Tk()
        obj = login.login_window(root)
        root.mainloop()
 
    def send_confirmation_email(self, to_email, name):
            with open (resource_path('credentials.txt')) as f1:
                for i in f1:
                    cr= i.strip().split(',')
            msg = EmailMessage()
            msg['Subject'] = 'Welcome to Face Recognition System'
            msg['From'] = cr[0]       
            msg['To'] = to_email

            # HTML Email Body
            html = f"""
            <html>
                <body>
                    <h2 style="color: green;">Welcome, {name}!</h2>
                    <p>Thank you for registering with <b>Face Recognition System</b>.</p>
                    <p>Your registration is successful!</p>
                    <hr>
                    <p style="font-size: 13px;">If you did not request this registration, please ignore this email.</p>
                </body>
            </html>
            """
            msg.set_content("Registration successful")  # plain fallback
            msg.add_alternative(html, subtype='html')

            # SMTP Send
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(cr[0],cr[1])
            server.send_message(msg)
            server.quit()
            messagebox.showinfo('Success','Registration email has successfully send to user email')

if __name__ == '__main__':
    root=Tk()
    obj=register(root)
    root.mainloop() 