from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from register import register
import mysql.connector
import smtplib
import random
import re
from email.message import EmailMessage

class login_window:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        ##############variables################################
        self.var_email = StringVar()
        self.var_pass = StringVar()
        self.remember_var = IntVar()
        try:
            with open('remember.txt', 'r') as f:
                data = f.read().strip()
                if data:
                    email, password = data.split(',')
                    self.var_email.set(email)
                    self.var_pass.set(password)
                    self.remember_var.set(1)
        except FileNotFoundError:
            pass

        # Background image
        img3 = Image.open("college_images\\u.jpg")
        img3 = img3.resize((1360, 680), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=0, width=1360, height=680)

        self.login_attempts = 0
        self.locked_out = False
        self.lock_timer_label = None

        # Login frame
        frame = Frame(self.root, bg='black')
        frame.place(x=500, y=150, width=340, height=450)

        img = Image.open("college_images\\LoginIconAppl.png")
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        label_img = Label(frame, image=self.photoimg, bg='black', borderwidth=0)
        label_img.place(x=125, y=0, width=100, height=100)

        get_sta = Label(frame, text='Get Started', font=('times new roman', 20, 'bold'), fg='white', bg='black')
        get_sta.place(x=100, y=100)

        username = Label(frame, text='Useremail', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        username.place(x=70, y=155)

        self.txt = ttk.Entry(frame, font=('times new roman', 15, 'bold'), textvariable=self.var_email)
        self.txt.place(x=40, y=180, width=270)
        self.txt.focus()

        password = Label(frame, text='Password', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        password.place(x=70, y=225)
        
        self.passw = ttk.Entry(frame, font=('times new roman', 15, 'bold'), textvariable=self.var_pass, show='*')
        self.passw.place(x=40, y=250, width=270)

        remember_me = Checkbutton(frame, text="Remember Me", variable=self.remember_var,
                          font=('times new roman', 10), bg='black', fg='white',
                          activebackground='black', activeforeground='white',
                          selectcolor='black')
        remember_me.place(x=40, y=290)

        # Toggle show/hide icons for login password field
        self.show_icon2 = ImageTk.PhotoImage(Image.open("college_images/pass_show.png").resize((25, 29), Image.Resampling.LANCZOS))
        self.hide_icon2 = ImageTk.PhotoImage(Image.open("college_images/pass_hide.png").resize((25, 29), Image.Resampling.LANCZOS))
        self.show_hide_btn2 = Button(frame, image=self.show_icon2, command=self.toggle_login_password, bg='black', bd=0, activebackground='black', cursor='hand2')
        self.show_hide_btn2.place(x=310, y=250, height=29)
        self.login_password_visible = False

        ####################Icon Images######################################
        img1 = Image.open("college_images\\LoginIconAppl.png")
        img1 = img1.resize((25, 25), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        label_img1 = Label(frame, image=self.photoimg1, bg='black', borderwidth=0)
        label_img1.place(x=45, y=153, width=25, height=25)
        img2 = Image.open("college_images\\lock-512.png")
        img2 = img2.resize((25, 25), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        label_img2 = Label(frame, image=self.photoimg2, bg='black', borderwidth=0)
        label_img2.place(x=45, y=223, width=25, height=25)

        log_btn = Button(frame, text='Login', font=('times new roman', 15, 'bold'), fg='white', bg='red', activeforeground='white', activebackground='red', cursor='hand2', command=self.login)
        log_btn.place(x=110, y=320, width=120, height=35)

        reg_btn = Button(frame, text='Register New User', font=('times new roman', 10, 'bold'), bd=0, fg='white', bg='black', activeforeground='white', activebackground='black', cursor='hand2', command=self.register_window)
        reg_btn.place(x=15, y=370, width=160)

        forgot_btn = Button(frame, text='Forgot Password', font=('times new roman', 10, 'bold'), bd=0, fg='white', bg='black', activeforeground='white', activebackground='black', cursor='hand2', command=self.forgot_password)
        forgot_btn.place(x=10, y=390, width=160)

    def register_window(self):
        self.root.destroy()  # Close login window
        root = Tk()
        reg_app = register(root)
        root.mainloop()

    def login(self):
        if self.locked_out:
            messagebox.showwarning('Locked Out', 'Too many failed attempts. Please wait...')
            return

        if self.txt.get() == '' or self.passw.get() == '':
            messagebox.showerror('Error', 'All fields are required!')
        else:
            conn = mysql.connector.connect(host='localhost', username='root', password='1582', database='face_recognizer')
            my_cursor = conn.cursor()
            my_cursor.execute('select * from register where email=%s and password=%s', (
                self.var_email.get(),
                self.var_pass.get()
            ))
            row = my_cursor.fetchone()

            if row is None:
                self.login_attempts += 1
                if self.login_attempts >= 3:
                    self.lock_login()
                else:
                    messagebox.showerror('Error', f'Invalid credentials! {3 - self.login_attempts} attempts left.')
            else:
                # Success: Reset attempts and send a login notification email
                self.login_attempts = 0
                full_name = f"{row[0]} {row[1]}"
                self.send_login_email(row[3], full_name)
                if self.remember_var.get() == 1:
                    with open('remember.txt', 'w') as f:
                        f.write(f"{self.var_email.get()},{self.var_pass.get()}")
                else:
                    with open('remember.txt', 'w') as f:
                        f.write("")  # Clear if not checked
                from main import face_recog
                self.root.destroy()
                root = Tk()
                main_app = face_recog(root)
                root.mainloop()

            conn.commit()
            conn.close()

    def toggle_login_password(self):
        if self.login_password_visible:
            self.passw.config(show='*')
            self.show_hide_btn2.config(image=self.show_icon2)
            self.login_password_visible = False
        else:
            self.passw.config(show='')
            self.show_hide_btn2.config(image=self.hide_icon2)
            self.login_password_visible = True

    def send_login_email(self, to_email, name):
        # Re-use credentials from credentials.txt
        with open('credentials.txt') as f1:
            for i in f1:
                cr = i.strip().split(',')
        msg = EmailMessage()
        msg['Subject'] = 'Login Notification – Face Recognition System'
        msg['From']    = cr[0]    # your sender
        msg['To']      = to_email

        html = f"""
        <html>
        <body>
            <h3>Hello, {name}</h3>
            <p>You have just logged into the <b>Face Recognition System</b>.</p>
            <p>If this wasn’t you, please reset your password immediately.</p>
        </body>
        </html>
        """
        msg.set_content("Login notification")
        msg.add_alternative(html, subtype='html')

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(cr[0], cr[1])
        server.send_message(msg)
        server.quit()
        messagebox.showinfo('Success', 'Login email has been sent to your email.')

    def lock_login(self):
        self.locked_out = True
        self.lock_time = 60  # seconds
        messagebox.showerror("Locked Out", "Too many failed attempts. Login disabled for 1 minute.")
        
        # Disable login button
        for widget in self.root.winfo_children():
            if isinstance(widget, Frame):
                for w in widget.winfo_children():
                    if isinstance(w, Button) and w.cget("text") == "Login":
                        w.config(state=DISABLED)
        
        # Add label for countdown
        if self.lock_timer_label is None:
            self.lock_timer_label = Label(self.root, text='', font=('times new roman', 14, 'bold'), fg='red', bg='black')
            self.lock_timer_label.place(x=570, y=620)

        self.countdown(self.lock_time)

    def countdown(self, remaining):
        if remaining <= 0:
            self.locked_out = False
            self.login_attempts = 0
            self.lock_timer_label.config(text='Login re-enabled.')
            
            # Re-enable login button
            for widget in self.root.winfo_children():
                if isinstance(widget, Frame):
                    for w in widget.winfo_children():
                        if isinstance(w, Button) and w.cget("text") == "Login":
                            w.config(state=NORMAL)
            if self.lock_timer_label:
                self.lock_timer_label.destroy()
                self.lock_timer_label = None
        else:
            mins, secs = divmod(remaining, 60)
            self.lock_timer_label.config(text=f'Try again in {mins:02}:{secs:02}')
            self.root.after(1000, self.countdown, remaining - 1)

    ################################################################################
    # Password reset with OTP functionality
    ################################################################################
    def forgot_password(self):
        if self.txt.get() == '':
            messagebox.showerror('Error', 'Please enter the email address to reset password')
        else:
            conn = mysql.connector.connect(host='localhost', username='root', password='1582', database='face_recognizer')
            my_cursor = conn.cursor()
            query = 'select * from register where email=%s'
            value = (self.txt.get(),)
            my_cursor.execute(query, value)
            row = my_cursor.fetchone()
            if row is None:
                messagebox.showerror('Error', 'Please enter a valid user email')
            else:
                conn.close()
                # Open the password reset window
                self.root1 = Toplevel()
                self.root1.geometry("340x500+500+150")
                self.root1.title("Face Recognition System")
                self.root1.resizable(False, False)
                self.root1.wm_iconbitmap('college_images\\bg1.ico')
                self.root1.configure(background='aqua')

                ############################ Variables ##############################
                self.var_pass1 = StringVar()
                self.generated_otp = None  # Will store our generated OTP

                title = Label(self.root1, text='Forgot Password', font=('times new roman', 20, 'bold'), fg='red', bg='aqua')
                title.place(x=0, y=10, relwidth=1)

                security_q = Label(self.root1, text='Select Security Question', font=('times new roman', 15, 'bold'), bg='aqua', fg='DarkGoldenrod1')
                security_q.place(x=50, y=60)

                self.security_q_combo = ttk.Combobox(self.root1, font=('times new roman', 15, 'bold'), state='readonly')
                self.security_q_combo['values'] = ('Your Birthplace', 'Your FriendName', 'Your BirthDate')
                self.security_q_combo.set("Select")
                self.security_q_combo.place(x=50, y=90, width=250)

                security_a = Label(self.root1, text='Security Answer', font=('times new roman', 15, 'bold'), bg='aqua', fg='DarkGoldenrod1')
                security_a.place(x=50, y=130)

                self.security_a = ttk.Entry(self.root1, font=('times new roman', 15, 'bold'))
                self.security_a.place(x=50, y=160, width=250)

                # Button to send OTP after verifying the security answer
                send_otp_btn = Button(self.root1, text='Send OTP', font=('times new roman', 12, 'bold'), fg='violet', bg='blue', cursor='hand2', command=self.send_security_otp,activebackground='red',activeforeground='green')
                send_otp_btn.place(x=110, y=210, width=120, height=30)

                otp_lbl = Label(self.root1, text='Enter OTP', font=('times new roman', 15, 'bold'), bg='aqua', fg='DarkGoldenrod1')
                otp_lbl.place(x=50, y=250)

                self.otp = ttk.Entry(self.root1, font=('times new roman', 15, 'bold'))
                self.otp.place(x=50, y=280, width=250)

                new_passw_lbl = Label(self.root1, text='New Password', font=('times new roman', 15, 'bold'), bg='aqua', fg='DarkGoldenrod1')
                new_passw_lbl.place(x=50, y=320)

                self.new_passw = ttk.Entry(self.root1, font=('times new roman', 15, 'bold'), textvariable=self.var_pass1, show='*')
                self.new_passw.place(x=50, y=350, width=250)
                self.new_passw.bind('<KeyRelease>', self.check_password_strength)
                self.new_passw.bind("<Control-c>", lambda e: "break")
                self.new_passw.bind("<Control-v>", lambda e: "break")
                self.new_passw.bind("<Button-3>", lambda e: "break")  # disable right-click
                self.strength_label = Label(self.root1, text="", font=('times new roman', 12, 'bold'), fg='red', bg='aqua')
                self.strength_label.place(x=50, y=380)

                # Load show/hide images for password field in reset window
                self.show_icon = ImageTk.PhotoImage(Image.open("college_images/pass_show.png").resize((25, 29), Image.Resampling.LANCZOS))
                self.hide_icon = ImageTk.PhotoImage(Image.open("college_images/pass_hide.png").resize((25, 29), Image.Resampling.LANCZOS))
                self.show_hide_btn = Button(self.root1, image=self.show_icon, command=self.toggle_reset_password, bg='aqua', bd=0, activebackground='aqua', cursor='hand2')
                self.show_hide_btn.place(x=300, y=350)
                self.password_visible = False

                

                reset_btn = Button(self.root1, text='Reset', font=('times new roman', 15, 'bold'), fg='yellow', bg='green', cursor='hand2',activebackground='dodgerblue',activeforeground='red', command=self.reset_pass)
                reset_btn.place(x=100, y=420, width=130)
                
    def send_security_otp(self):
        """
        Called when the user clicks 'Send OTP'.
        Validates the email and security answer.
        If correct, generate a 4-digit OTP, save it in self.generated_otp, and send it via email.
        """
        email = self.txt.get()
        sec_q = self.security_q_combo.get()
        sec_a = self.security_a.get()

        if sec_q == 'Select' or sec_a == '':
            messagebox.showerror('Error', 'Please select a security question and provide the answer', parent=self.root1)
            return

        # Verify the answer in the database
        conn = mysql.connector.connect(host='localhost', username='root', password='1582', database='face_recognizer')
        my_cursor = conn.cursor()
        query = 'select * from register where email=%s and securityq=%s and securitya=%s'
        my_cursor.execute(query, (self.txt.get(), sec_q, sec_a))
        row = my_cursor.fetchone()
        conn.close()
        if row is None:
            messagebox.showerror('Error', 'Incorrect security question or answer', parent=self.root1)
            return

        # Generate a random 4-digit OTP
        self.generated_otp = str(random.randint(1000, 9999))
        try:
            # Read email credentials from credentials.txt
            with open('credentials.txt') as f:
                for line in f:
                    cr = line.strip().split(',')
            sender = cr[0]
            sender_pass = cr[1]

            msg = EmailMessage()
            msg['Subject'] = 'Your OTP for Password Reset'
            msg['From'] = sender
            msg['To'] = email
            html_content = f"""
            <html>
            <body>
                <h3>Your OTP is: {self.generated_otp}</h3>
                <p>Please use this OTP to reset your password.</p>
            </body>
            </html>
            """
            msg.set_content("OTP for password reset")
            msg.add_alternative(html_content, subtype='html')

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, sender_pass)
            server.send_message(msg)
            server.quit()
            messagebox.showinfo('Success', 'A 4-digit OTP has been sent to your email.', parent=self.root1)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to send OTP.\n{e}', parent=self.root1)

    def toggle_reset_password(self):
        if self.password_visible:
            self.new_passw.config(show='*')
            self.show_hide_btn.config(image=self.show_icon)
            self.password_visible = False
        else:
            self.new_passw.config(show='')
            self.show_hide_btn.config(image=self.hide_icon)
            self.password_visible = True

    def check_password_strength(self, event=None):
        password = self.var_pass1.get()
        if len(password) < 6:
            strength = "Too Short"
            color = "red"
        elif (re.search(r'[A-Z]', password) and
              re.search(r'[a-z]', password) and
              re.search(r'\d', password) and
              re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
            strength = "Strong"
            color = "green"
        elif (re.search(r'[A-Za-z]', password) and
              re.search(r'\d', password)):
            strength = "Medium"
            color = "orange"
        else:
            strength = "Weak"
            color = "red"
        self.strength_label.config(text=f"Strength: {strength}", fg=color)

    def is_strong_password(self, password):
        return (
            len(password) >= 6 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'\d', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        )

    def reset_pass(self):
        """
        Called when the user clicks the Reset button in the password reset window.
        Checks the OTP entered by the user and resets the password if the OTP matches.
        """
        if not self.generated_otp:
            messagebox.showerror('Error', 'OTP not generated. Please click "Send OTP" first.', parent=self.root1)
            return

        if self.otp.get() == '':
            messagebox.showerror('Error', 'Please enter the OTP', parent=self.root1)
            return

        if self.otp.get() != self.generated_otp:
            messagebox.showerror('Error', 'Incorrect OTP', parent=self.root1)
            return

        if self.new_passw.get() == '':
            messagebox.showerror('Error', 'Please enter the new password', parent=self.root1)
            return

        if not self.is_strong_password(self.var_pass1.get()):
            messagebox.showerror(
                        title='Error',
                        message=(
                            'Password must be strong. It should contain at least:\n'
                            '- One digit\n'
                            '- One lowercase letter\n'
                            '- One uppercase letter\n'
                            '- One special character'
                        ),
                        parent=self.root1
                    )

            return

        conn = mysql.connector.connect(host='localhost', username='root', password='1582', database='face_recognizer')
        my_cursor = conn.cursor()
        query = 'update register set password=%s where email=%s'
        value = (self.new_passw.get(), self.txt.get())
        my_cursor.execute(query, value)
        conn.commit()
        conn.close()
        messagebox.showinfo('Information', 'Your password has been successfully reset. Please login with your new password.', parent=self.root1)
        self.root1.destroy()

if __name__ == '__main__':
    root = Tk()
    obj = login_window(root)
    root.mainloop()
