import threading
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import webbrowser
from PIL import Image,ImageTk
from login import login_window
from student import students
from train import train
from face_recognition import face_recognition
from attendance import attendance
import os
import tkinter
from time import strftime
from datetime import datetime
from chatbot2 import ChatBot
import pyttsx3
from devloper import developer
from utils import resource_path



class face_recog:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+10")
        self.root.title("Face Recognition System")
        self.root.resizable(True, True)  # Make window resizable
        self.root.minsize(1024, 600)     # Set reasonable minimum size
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))
        
        # Initialize Audio
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        try:
            engine.setProperty('voice', voices[1].id)
        except:
            pass # Fallback if voice index out of bounds
            
        self.time_after_id = None
        self.slider_after_id = None
        
        # Initial greeting and warning
        # (Running in thread to not block UI startup if it takes time)
        threading.Thread(target=self.initial_voice_greeting, args=(engine,), daemon=True).start()
        
        # Debounce timer for resizing
        self.resize_timer = None

        # --- LOAD IMAGES (Store Originals for Resizing) ---
        self.org_img_h1 = Image.open(resource_path("college_images\\Stanford.jpg"))
        self.org_img_h2 = Image.open(resource_path("college_images\\facialrecognition.png"))
        self.org_img_h3 = Image.open(resource_path("college_images\\u.jpg"))
        self.org_img_bg = Image.open(resource_path("college_images\\wp2551980.jpg"))
        
        # Prepare UI Elements (Labels) empty first
        self.h_lbl1 = Label(self.root, borderwidth=0)
        self.h_lbl1.place(relx=0, rely=0, relwidth=0.333, relheight=0.191)
        
        self.h_lbl2 = Label(self.root, borderwidth=0)
        self.h_lbl2.place(relx=0.333, rely=0, relwidth=0.333, relheight=0.191)
        
        self.h_lbl3 = Label(self.root, borderwidth=0)
        self.h_lbl3.place(relx=0.666, rely=0, relwidth=0.334, relheight=0.191)
        
        self.bg_lbl = Label(self.root, borderwidth=0)
        self.bg_lbl.place(relx=0, rely=0.191, relwidth=1.0, relheight=0.809)

        # --- RESIZE BINDING ---
        self.root.bind("<Configure>", self.on_resize)

        
        self.title_lbl = Label(self.root, text='', font=('times new roman', 30, 'bold'), bg='white', fg='blue2', borderwidth=0)
        self.title_lbl.place(relx=0.09, rely=0.191, relwidth=0.82, relheight=0.065)
        
        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='green', borderwidth=0)
        self.time_lbl.place(relx=0, rely=0.191, relwidth=0.09, relheight=0.065)
        self.update_time()

        # Logout Button Container
        self.logout_frame = Frame(self.root, bg='white')
        self.logout_frame.place(relx=0.91, rely=0.191, relwidth=0.09, relheight=0.065)
        
        self.back_btn = Button(self.logout_frame, text="Log Out", cursor='hand2',
                            font=('times new roman', 10, 'bold'), bg='red', fg='white',
                            activebackground="green", command=self.logout)
        self.back_btn.pack(expand=True, fill=BOTH, padx=5, pady=5)


        # --- BUTTONS ---
       
        
        self.create_menu_button(
            "student.jpg", "Student Details", self.studuent_detail,
            0.073, 0.178, 0.147, 0.303, 0.071
        )
        self.create_menu_button(
            "face_detector1.jpg", "Face Recognition", self.face_data,
            0.294, 0.178, 0.147, 0.303, 0.071
        )
        self.create_menu_button(
            "report.jpg", "Attendance", self.attendance_details,
            0.514, 0.178, 0.147, 0.303, 0.071
        )
        self.create_menu_button(
            "chat.jpg", "HelpBot", self.chatbot,
            0.735, 0.178, 0.147, 0.303, 0.071
        )
        
        # Row 2
        self.create_menu_button(
            "Train.jpg", "Train Data", self.train_data,
            0.073, 0.589, 0.147, 0.303, 0.071
        )
        self.create_menu_button(
            "opencv_face_reco_more_data.jpg", "Photos", self.open_images,
            0.294, 0.589, 0.147, 0.303, 0.071
        )
        self.create_menu_button(
            "Team-Management-Software-Development.jpg", "Developers", self.devloper,
            0.514, 0.589, 0.147, 0.303, 0.071
        )
        self.create_menu_button(
            "exit.jpg", "Exit", self.iexit,
            0.735, 0.589, 0.147, 0.303, 0.071
        )

        # Shortcuts
        self.root.bind("<Control-l>", self.logout_shortcut)
        self.root.bind("<Control-L>", self.logout_shortcut)

        # Scrolling Text State
        self.text = ''
        self.count = 0
        self.s = "FACE RECOGNITION ATTENDANCE SYSTEM "
        self.slider()

    def initial_voice_greeting(self, engine):
        """Runs initial voice greeting in a thread to prevent UI freeze"""
        try:
            engine.say("welcome to facial recognition attendance system please put your internet on and you must have webcam and SQL Database!!")
            engine.runAndWait()
        except:
             pass
        # Note: Messagebox must be on main thread, so we schedule it
        self.root.after(0, lambda: tkinter.messagebox.showwarning('Note','This application required stable internet connection and webcam and SQL Database',parent=self.root))

    def create_menu_button(self, img_name, title, command, relx, rely, relw, relh, btn_h_rel):
        """
        Creates a responsive menu button with image and label.
        relx, rely: Position of the image
        relw, relh: Size of the image
        btn_h_rel: Height of the text button (placed relative to image bottom)
        """
        # Load and resize image once for initial 
        container = Frame(self.bg_lbl, bg='white', bd=0)
       
        
        # Let's place Image Button
        b_img = Button(self.bg_lbl, command=command, cursor='hand2', bg='white', bd=0)
        b_img.place(relx=relx, rely=rely, relwidth=relw, relheight=relh)
        
    
        
        text_rely = rely + relh - 0.015 # Slight overlap fix
        
        b_text = Button(self.bg_lbl, text=title, cursor='hand2',
                       font=('times new roman', 13, 'bold'), bg='#8B0000', fg='white',
                       activebackground="#B22222", activeforeground='white', command=command)
        b_text.place(relx=relx, rely=text_rely, relwidth=relw, relheight=btn_h_rel)
        
        # Hover effect functions
        def on_enter(e):
            b_text['bg'] = '#B22222'
        
        def on_leave(e):
            b_text['bg'] = '#8B0000'
            
        b_img.bind('<Enter>', on_enter)
        b_img.bind('<Leave>', on_leave)
        b_text.bind('<Enter>', on_enter)
        b_text.bind('<Leave>', on_leave)
        
        # Store reference to original image and widgets for resizing/lifting
        if not hasattr(self, 'btn_images'): self.btn_images = []
        original_img = Image.open(resource_path(f"college_images\\{img_name}"))
        self.btn_images.append({
            'widget': b_img,
            'text_widget': b_text,
            'orig': original_img,
            'aspect': original_img.width / original_img.height
        })
        
        # Add resizing capability to text font? Maybe too complex for now.

    def on_resize(self, event):
        """Variable delay to prevent lag while dragging"""
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_layout_images)

    def update_layout_images(self):
        """Resizes background and header images to fit current window size"""
        # Get current dimensions
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        if win_w < 100 or win_h < 100: return
        
        # 1. Header Images
        h_h = int(win_h * 0.191)
        h_w_1 = int(win_w * 0.333)
        h_w_3 = int(win_w * 0.334) # Remainder
        
        # Helper to update label image
        def update_img(lbl, orig, w, h):
            if w<=0 or h<=0: return
            resized = orig.resize((w, h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            lbl.config(image=photo)
            lbl.image = photo # Keep ref
            
        update_img(self.h_lbl1, self.org_img_h1, h_w_1, h_h)
        update_img(self.h_lbl2, self.org_img_h2, h_w_1, h_h)
        update_img(self.h_lbl3, self.org_img_h3, h_w_3, h_h)
        
        # 2. Background Image
        bg_h = int(win_h * 0.809)
        update_img(self.bg_lbl, self.org_img_bg, win_w, bg_h)
        
        # 3. Button Images
        # We need to calculate their actual size in pixels to resize the image properly
        for item in self.btn_images:
            btn = item['widget']
            txt = item['text_widget']
            
            # Lift both the image button and the text button
            btn.lift()
            txt.lift()
            
            # Get current size of button widget
            
            b_w = btn.winfo_width()
            b_h = btn.winfo_height()
            
            if b_w > 10 and b_h > 10:
                # Resize image to fit button
                resized = item['orig'].resize((b_w, b_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                btn.config(image=photo)
                btn.image = photo
        
       
        if hasattr(self, 'title_lbl'): self.title_lbl.lift()
        if hasattr(self, 'time_lbl'): self.time_lbl.lift()
        if hasattr(self, 'logout_frame'): self.logout_frame.lift()
        
        # Force a redraw to prevent glitches
        self.root.update_idletasks()

    def logout_shortcut(self, event=None):
        self.logout()

    def slider(self):
        if self.count == len(self.s):
            self.count = 0
            self.text = ''
        self.text += self.s[self.count]
        self.title_lbl.config(text=self.text)
        self.count += 1
        self.slider_after_id = self.title_lbl.after(300, self.slider)

    #####################Function button###########################
    def studuent_detail(self):
            self.new_window=Toplevel(self.root)
            self.app=students(self.new_window)
    
    def train_data(self):
            self.new_window=Toplevel(self.root)
            self.app=train(self.new_window)
 
    def face_data(self):
            self.new_window=Toplevel(self.root)
            self.app=face_recognition(self.new_window)
 
    def attendance_details(self):
            self.new_window=Toplevel(self.root)
            self.app=attendance(self.new_window)
 
    def chatbot(self):
         self.new_window=Toplevel(self.root)
         self.app=ChatBot(self.new_window)
        
    def devloper(self):
          self.new_window=Toplevel(self.root)
          self.app=developer(self.new_window)
 
    def logout(self):
        # Ask for confirmation
        confirm = tkinter.messagebox.askyesno("Logout", "Are you sure you want to logout?", parent=self.root)
        if not confirm:
            return

        # Cancel the scheduled after callbacks
        if self.time_after_id:
            self.time_lbl.after_cancel(self.time_after_id)
        if self.slider_after_id:
            self.title_lbl.after_cancel(self.slider_after_id)
        
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)

        # Start fade-out animation
        self.fade_out()

    def fade_out(self, alpha=1.0):
        if alpha > 0:
            alpha -= 0.05
            self.root.attributes("-alpha", alpha)
            self.root.after(50, self.fade_out, alpha)
        else:
            self.root.destroy()
            new_root = Tk()
            new_root.attributes("-alpha", 0)  # Start hidden
            app = login_window(new_root)

            def fade_in(alpha=0.0):
                if alpha < 1.0:
                    alpha += 0.05
                    new_root.attributes("-alpha", alpha)
                    new_root.after(50, fade_in, alpha)
                else:
                    new_root.attributes("-alpha", 1.0)

            fade_in()
            new_root.mainloop()

    def iexit(self):
            self.iexit=tkinter.messagebox.askyesno('Face Recognition','Are you sure you want to exit',parent=self.root)
            if self.iexit>0:
                  self.root.destroy()
            else:
                  return
 
    def open_images(self):
         os.startfile('data')

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        if hasattr(self, 'time_lbl') and self.time_lbl.winfo_exists():
            self.time_lbl.config(text=current_time)
            self.time_after_id = self.time_lbl.after(1000, self.update_time)



if __name__ == '__main__':
    root=Tk()
    obj=face_recog(root)
    root.mainloop() 