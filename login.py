from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from register import register
from config import get_db_connection
import smtplib
import random
import re
from email.message import EmailMessage
import threading
import sys
from tooltip import ToolTip
from utils import resource_path
from loading import LoadingSplash

class login_window:

    def preload_main_app(self):
        """
        Preloads the main application in the background to improve perceived performance.
        The heavy imports (torch, cv2, etc.) happen effectively when 'import main' is executed.
        """
        try:
            import main
            print("Main application preloaded successfully in background.")
        except Exception as e:
            print(f"Background preload failed (non-critical): {e}")

    def __init__(self, root):
        # Start preloading main module immediately in a background thread
        threading.Thread(target=self.preload_main_app, daemon=True).start()

        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(True, True)  # Enable resizing
        self.root.minsize(1024, 600)     # Match main.py minimum size
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))

        ##############variables################################
        self.var_email = StringVar()
        self.var_pass = StringVar()
        self.remember_var = IntVar()
        try:
            with open(resource_path('remember.txt'), 'r') as f:
                data = f.read().strip()
                if data:
                    email, password = data.split(',')
                    self.var_email.set(email)
                    self.var_pass.set(password)
                    self.remember_var.set(1)
        except FileNotFoundError:
            pass

        # Background image setup
        self.bg_image_original = Image.open(resource_path("college_images\\u.jpg"))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image_original.resize((1360, 680), Image.Resampling.LANCZOS))
        
        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Debounce timer for resizing
        self.resize_timer = None
        # Bind resize event
        self.root.bind("<Configure>", self.on_resize)

        self.login_attempts = 0
        self.locked_out = False
        self.lock_timer_label = None

        # Login frame
        frame = Frame(self.root, bg='maroon1')
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=340, height=450)

        img = Image.open(resource_path("college_images\\LoginIconAppl.png"))
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        label_img = Label(frame, image=self.photoimg, bg='maroon1', borderwidth=0)
        label_img.place(x=125, y=0, width=100, height=100)

        get_sta = Label(frame, text='Get Started', font=('times new roman', 20, 'bold'), fg='white', bg='maroon1')
        get_sta.place(x=100, y=100)

        username = Label(frame, text='User email', font=('times new roman', 15, 'bold'), fg='white', bg='maroon1')
        username.place(x=70, y=155)

        self.txt = ttk.Entry(frame, font=('times new roman', 15, 'bold'), textvariable=self.var_email)
        self.txt.place(x=40, y=180, width=270)
        self.txt.focus()

        password = Label(frame, text='Password', font=('times new roman', 15, 'bold'), fg='white', bg='maroon1')
        password.place(x=70, y=225)
        
        self.passw = ttk.Entry(frame, font=('times new roman', 15, 'bold'), textvariable=self.var_pass, show='*')
        self.passw.place(x=40, y=250, width=270)

        remember_me = Checkbutton(frame, text="Remember Me", variable=self.remember_var,
                          font=('times new roman', 10), bg='maroon1', fg='white',
                          activebackground='maroon1', activeforeground='white',
                          selectcolor='maroon1')
        remember_me.place(x=40, y=290)

        # Toggle show/hide icons for login password field
        self.show_icon2 = ImageTk.PhotoImage(Image.open(resource_path("college_images/pass_show.png")).resize((25, 29), Image.Resampling.LANCZOS))
        self.hide_icon2 = ImageTk.PhotoImage(Image.open(resource_path("college_images/pass_hide.png")).resize((25, 29), Image.Resampling.LANCZOS))
        self.show_hide_btn2 = Button(frame, image=self.show_icon2, command=self.toggle_login_password, bg='maroon1', bd=0, activebackground='maroon1', cursor='hand2')
        self.show_hide_btn2.place(x=310, y=250, height=29)
        self.login_password_visible = False

        ####################Icon Images######################################
        img1 = Image.open(resource_path("college_images\\LoginIconAppl.png"))
        img1 = img1.resize((25, 25), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        label_img1 = Label(frame, image=self.photoimg1, bg='maroon1', borderwidth=0)
        label_img1.place(x=45, y=153, width=25, height=25)
        img2 = Image.open(resource_path("college_images\\lock-512.png"))
        img2 = img2.resize((25, 25), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        label_img2 = Label(frame, image=self.photoimg2, bg='maroon1', borderwidth=0)
        label_img2.place(x=45, y=223, width=25, height=25)

        log_btn = Button(frame, text='Login', font=('times new roman', 15, 'bold'), fg='white', bg='blue2', activeforeground='white', activebackground='blue2', cursor='hand2', command=self.login)
        log_btn.place(x=110, y=320, width=120, height=35)
        ToolTip(log_btn,"Shortcut: Ctrl + Enter")

        reg_btn = Button(frame, text='Register New User', font=('times new roman', 10, 'bold'), bd=0, fg='white', bg='maroon1', activeforeground='white', activebackground='maroon1', cursor='hand2', command=self.register_window)
        reg_btn.place(x=15, y=370, width=160)
        ToolTip(reg_btn,"Shortcut: Ctrl + L")

        forgot_btn = Button(frame, text='Forgot Password', font=('times new roman', 10, 'bold'), bd=0, fg='white', bg='maroon1', activeforeground='white', activebackground='maroon1', cursor='hand2', command=self.forgot_password)
        forgot_btn.place(x=10, y=390, width=160)
        ToolTip(forgot_btn,"Shortcut: Ctrl + F")
                # Keyboard shortcuts
        self.root.bind("<Control-Return>", lambda e: self.login())
        self.root.bind("<Control-r>", lambda e: self.register_window())
        self.root.bind("<Control-f>", lambda e: self.forgot_password())
        # Show shortcuts info on startup
        self.root.after(500, self.show_shortcuts_info)

    def on_resize(self, event):
        """Variable delay to prevent lag while dragging, same as main.py"""
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_background)

    def update_background(self):
        """Resizes background image to fit current window size"""
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        
        # Avoid resizing if window is too small (startup glitches)
        if new_width < 100 or new_height < 100: return

        image = self.bg_image_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(image)
        self.bg_label.config(image=self.bg_photo)

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
            conn = get_db_connection()
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
                
                if self.remember_var.get() == 1:
                    with open(resource_path('remember.txt'), 'w') as f:
                        f.write(f"{self.var_email.get()},{self.var_pass.get()}")
                else:
                    with open(resource_path('remember.txt'), 'w') as f:
                        f.write("")  # Clear if not checked

                # SHOW LOADING SPLASH BEFORE DESTROYING WINDOW
                self.loading_splash = LoadingSplash(self.root, message="Authenticating...")
                self.root.update_idletasks() # Force UI update immediately so 'Authenticating...' renders
                self.loading_splash.update_message("Sending Login Email...")
                
                # Disable login button to prevent multiple clicks
                for widget in self.root.winfo_children():
                    if isinstance(widget, Frame):
                        for w in widget.winfo_children():
                            if isinstance(w, Button) and w.cget("text") == "Login":
                                w.config(state=DISABLED)

                # Run email sending and heavy imports sequentially in background thread
                threading.Thread(target=self.load_main_app_thread, args=(row[3], full_name), daemon=True).start()

            conn.commit()
            conn.close()

    def load_main_app_thread(self, to_email, name):
        try:
            # 1. Send Login Email
            email_success = self.send_login_email(to_email, name)
            
            # 2. Show Messagebox on main thread
            if email_success:
                # Use wait_window or simple blocking call on main thread by using an event/after?
                # Using root.after to safely show message box from UI thread, blocking logic using a flag is complex.
                # Simplest is scheduling the message box, then scheduling the import thread again.
                self.root.after(0, self.show_email_success_and_continue)
            else:
                 self.root.after(0, self.show_email_fail_and_continue)
            
        except Exception as e:
            print(f"Error in background process: {e}")
            if hasattr(self, 'loading_splash'):
                self.root.after(0, self.loading_splash.destroy)

    def show_email_success_and_continue(self):
         if hasattr(self, 'loading_splash') and self.loading_splash.window.winfo_exists():
             parent_win = self.loading_splash.window
         else:
             parent_win = self.root
         messagebox.showinfo('Success', 'Login email has been sent to your email.', parent=parent_win, icon='info')
         self.continue_loading_main_app()

    def show_email_fail_and_continue(self):
         self.continue_loading_main_app()

    def continue_loading_main_app(self):
        # 3. Update splash message
        if hasattr(self, 'loading_splash'):
             self.loading_splash.update_message("Loading Face Recognition Models...")
             self.loading_splash.window.update_idletasks() # Force UI to update text immediately
        
        # 4. Load models in background again
        threading.Thread(target=self._do_import_and_transition, daemon=True).start()

    def _do_import_and_transition(self):
        try:
            from main import face_recog
            self.root.after(0, self.transition_to_main, face_recog)
        except Exception as e:
            print(f"Error loading main app: {e}")
            if hasattr(self, 'loading_splash'):
                self.root.after(0, self.loading_splash.destroy)

    def transition_to_main(self, face_recog_class):
        if hasattr(self, 'loading_splash'):
            self.loading_splash.destroy()
        self.root.destroy()
        root = Tk()
        main_app = face_recog_class(root)
        root.mainloop()

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
        try:
            with open(resource_path('credentials.txt')) as f1:
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
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

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
            self.lock_timer_label = Label(self.root, text='', font=('times new roman', 14, 'bold'), fg='blue2', bg='red')
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
            return

        conn = get_db_connection()
        my_cursor = conn.cursor()
        my_cursor.execute('select * from register where email=%s', (self.txt.get(),))
        row = my_cursor.fetchone()
        conn.close()

        if row is None:
            messagebox.showerror('Error', 'Please enter a valid user email')
            return

        # ================= RESET WINDOW =================
        self.root1 = Toplevel(self.root)
        self.root1.geometry("340x520+500+150")
        self.root1.title("Forgot Password")
        self.root1.wm_iconbitmap(resource_path('college_images\\bg1.ico'))
        self.root1.resizable(False, False)
        self.root1.configure(bg='maroon1')

        # ================= VARIABLES =================
        self.var_pass1 = StringVar()
        self.generated_otp = None
        self.otp_time_left = 60
        self.otp_expired = False
        self.otp_send_attempts = 0  # Counter for attempts
        self.max_otp_attempts = 3   # Max allowed attempts

        # ================= UI =================
        Label(self.root1, text='Forgot Password', font=('times new roman', 20, 'bold'),
              fg='blue2', bg='maroon1').pack(pady=10)

        Label(self.root1, text='Security Question', font=('times new roman', 14, 'bold'),
              bg='maroon1').place(x=50, y=60)

        self.security_q_combo = ttk.Combobox(self.root1, font=('times new roman', 13),
                                             state='readonly',
                                             values=('Your Birthplace', 'Your FriendName', 'Your BirthDate'))
        self.security_q_combo.set("Select")
        self.security_q_combo.place(x=50, y=90, width=240)

        Label(self.root1, text='Security Answer', font=('times new roman', 14, 'bold'),
              bg='maroon1').place(x=50, y=130)

        self.security_a = ttk.Entry(self.root1, font=('times new roman', 13))
        self.security_a.place(x=50, y=160, width=240)

        # ================= SEND OTP BUTTON =================
        self.send_otp_btn = Button(self.root1, text='Send OTP',
                                   font=('times new roman', 12, 'bold'),
                                   bg='blue', fg='white', cursor='hand2',
                                   command=self.send_security_otp)
        self.send_otp_btn.place(x=100, y=205, width=120)

        Label(self.root1, text='Enter OTP', font=('times new roman', 14, 'bold'),
              bg='maroon1').place(x=50, y=245)

        self.otp = ttk.Entry(self.root1, font=('times new roman', 13))
        self.otp.place(x=50, y=275, width=240)

        Label(self.root1, text='New Password', font=('times new roman', 14, 'bold'),
              bg='maroon1').place(x=50, y=315)

        self.new_passw = ttk.Entry(self.root1, textvariable=self.var_pass1,
                                   font=('times new roman', 13), show='*')
        self.new_passw.place(x=50, y=345, width=240)
        self.new_passw.bind('<KeyRelease>', self.check_password_strength)
        self.show_icon = ImageTk.PhotoImage(
        Image.open(resource_path("college_images/pass_show.png")).resize((22, 22), Image.Resampling.LANCZOS)
    )
        self.hide_icon = ImageTk.PhotoImage(
            Image.open(resource_path("college_images/pass_hide.png")).resize((22, 22), Image.Resampling.LANCZOS)
        )

        self.password_visible = False
        self.show_hide_btn = Button(
        self.root1,
        image=self.show_icon,
        command=self.toggle_reset_password,
        bg='maroon1',
        activebackground='maroon1',
        bd=0,
        cursor='hand2'
    )
        self.show_hide_btn.place(x=295, y=345)


        self.strength_label_fp = Label(
            self.root1,
            text="",
            font=('times new roman', 11, 'bold'),
            fg='blue2',
            bg='maroon1'
        )
        self.strength_label_fp.place(x=50, y=370)

        # ================= RESET BUTTON =================
        Button(self.root1, text='Reset Password',
               font=('times new roman', 14, 'bold'),
               bg='green', fg='white', cursor='hand2',
               command=self.reset_pass).place(x=90, y=390, width=160)

        # ================= COUNTDOWN LABEL =================
        self.otp_timer_label = Label(self.root1,
                                     text="",
                                     font=('times new roman', 12, 'bold'),
                                     fg='blue2', bg='maroon1')
        self.otp_timer_label.place(x=85, y=430)

        # ================= ATTEMPTS LABEL =================
        self.attempts_label = Label(self.root1,
                                    text=f"OTP Attempts left: {self.max_otp_attempts}",
                                    font=('times new roman', 10, 'bold'),
                                    fg='blue2', bg='maroon1')
        self.attempts_label.place(x=110, y=460)

    def start_otp_countdown(self):
        try:
            if not self.root1.winfo_exists():
                return
        except:
            return

        if self.otp_time_left <= 0:
            self.otp_expired = True
            self.generated_otp = None
            self.otp_timer_label.config(text="OTP expired ❌")
            
            # Check if attempts are exhausted
            if self.otp_send_attempts >= self.max_otp_attempts:
                 messagebox.showerror('Max Attempts', 'Maximum OTP attempts reached. Window closing.', parent=self.root1)
                 self.root1.destroy()
            else:
                # Re-enable the button at the same place
                self.send_otp_btn.config(state=NORMAL, text='Resend OTP', bg='blue')
            return

        mins, secs = divmod(self.otp_time_left, 60)
        self.otp_timer_label.config(
            text=f"OTP expires in {mins:02}:{secs:02}"
        )
        self.otp_time_left -= 1
        self.root1.after(1000, self.start_otp_countdown)

    def show_shortcuts_info(self):
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "Available Shortcuts:\n\n"
            "Ctrl + Enter  → Login\n"
            "Ctrl + F  → Forgot Password\n"
            "Ctrl + R        → Register New User\n"
            "It should take about 35-40 seconds to load the main application and application will load after email confirmation"
            
        )

    def send_security_otp(self):
        """
        Called when the user clicks 'Send OTP'.
        Validates the email and security answer.
        If correct, generate a 4-digit OTP, save it in self.generated_otp, and send it via email.
        """
        # First check if we have attempts left
        if self.otp_send_attempts >= self.max_otp_attempts:
            messagebox.showerror('Error', 'Maximum OTP send attempts reached', parent=self.root1)
            self.root1.destroy()
            return

        email = self.txt.get()
        sec_q = self.security_q_combo.get()
        sec_a = self.security_a.get()

        if sec_q == 'Select' or sec_a == '':
            messagebox.showerror('Error', 'Please select a security question and provide the answer', parent=self.root1)
            return

        # Verify the answer in the database
        conn = get_db_connection()
        my_cursor = conn.cursor()
        query = 'select * from register where email=%s and securityq=%s and securitya=%s'
        my_cursor.execute(query, (self.txt.get(), sec_q, sec_a))
        row = my_cursor.fetchone()
        conn.close()
        if row is None:
            messagebox.showerror('Error', 'Incorrect security question or answer', parent=self.root1)
            return

        # Increment attempts counter
        self.otp_send_attempts += 1
        
        # Update attempts label
        left = self.max_otp_attempts - self.otp_send_attempts
        self.attempts_label.config(text=f"Attempts left: {left}")

        # Generate a random 4-digit OTP
        self.generated_otp = str(random.randint(1000, 9999))
        self.otp_expired = False
        self.otp_time_left = 60
        
        # Disable button during countdown
        self.send_otp_btn.config(state=DISABLED, text='Wait...', bg='gray')
        
        # Start countdown
        self.start_otp_countdown()

        try:
            # Read email credentials from credentials.txt
            with open(resource_path('credentials.txt')) as f:
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
                <p>This OTP is valid for 1 minute.</p>
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
            # Re-enable button if sending fails
            self.send_otp_btn.config(state=NORMAL, text='Send OTP', bg='blue')
            # Reset the counter if it failed to send (optional, but fair)
            self.otp_send_attempts -= 1
            left = self.max_otp_attempts - self.otp_send_attempts
            self.attempts_label.config(text=f"Attempts left: {left}")
            
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
            color = "bisque"
        elif (re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[0-9]', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
            strength = "Strong"
            color = "green"
        elif re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password):
            strength = "Medium"
            color = "cyan"
        else:
            strength = "Weak"
            color = "azure"

        self.strength_label_fp.config(text=f"Strength: {strength}", fg=color)

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
        if self.otp_expired:
            messagebox.showerror(
                'Error',
                'OTP has expired. Please request a new OTP.',
                parent=self.root1
            )
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

        conn = get_db_connection()
        my_cursor = conn.cursor()
        query = 'update register set password=%s where email=%s'
        value = (self.new_passw.get(), self.txt.get())
        my_cursor.execute(query, value)
        conn.commit()
        conn.close()
        messagebox.showinfo('Information', 'Your password has been successfully reset. Please login with your new password.', parent=self.root1)
        self.root1.destroy()

if __name__ == '__main__':
    # Initialize Database first
    try:
        from setup_database import setup_database
        setup_database()
    except Exception as e:
        print(f"Database setup warning: {e}")

    root = Tk()
    obj = login_window(root)
    root.mainloop()