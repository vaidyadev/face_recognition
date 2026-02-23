from time import strftime
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
import cv2
import webbrowser  # For clickable links
from utils import resource_path

class developer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(True, True)
        self.root.minsize(1024, 600)
        self.root.state('zoomed')
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))
        self.resize_timer = None

        # ================== Header ==================
        self.title_lbl = Label(self.root, text='DEVLOPERS', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(relx=0, rely=0, relwidth=1, relheight=0.07)

        self.back_btn = Button(self.root, text="Back", width=22, cursor='hand2', font=('times new roman', 10, 'bold'),
                          bg='red', fg='white', activebackground="green", command=self.back)
        self.back_btn.place(relx=1.0, rely=0.015, x=-20, width=80, height=30, anchor="ne")

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red', borderwidth=0,
                              highlightthickness=0)
        self.time_lbl.place(relx=0, rely=0, width=120, relheight=0.07)
        self.update_time()  # start the clock

        # ================== Background Image ==================
        self.org_img_top = Image.open(resource_path("college_images\\dev.jpg"))
        self.f_lbl = Label(self.root)
        self.f_lbl.place(relx=0, rely=0.07, relwidth=1, relheight=0.93)
        
        # ================== Developer 1 Frame (Left) ==================
        # Reparent to root to ensure visibility over background image
        self.dev1_frame = Frame(self.root, bd=2, bg='pink')
        self.dev1_frame.place(relx=0.02, rely=0.12, relwidth=0.47, relheight=0.85)

        # Profile Image (Centered in frame) - Reduced size
        dev1_img = Image.open(resource_path("college_images\\dev_2.png"))
        dev1_img = dev1_img.resize((130, 130), Image.Resampling.LANCZOS)
        self.dev1_photoimg = ImageTk.PhotoImage(dev1_img)

        dev1_lbl = Label(self.dev1_frame, image=self.dev1_photoimg, bg='pink')
        dev1_lbl.pack(pady=5)

        # Reduced font and padding
        dev1_info_lbl = Label(self.dev1_frame,
                              text='Hello my name is Harsh Makhija, I am a 3rd year BCA Student. Know Java, PHP, Kotlin, MERN, Python Basics.',
                              font=('times new roman', 16, 'bold'), bg='pink', fg='blue', wraplength=500, justify=CENTER)
        dev1_info_lbl.pack(fill=X, padx=10, pady=5)

        dev1_info1_lbl = Label(self.dev1_frame,
                               text='You can contact me at following platforms:',
                               font=('times new roman', 14, 'bold'), bg='pink', fg='purple', wraplength=400, justify=CENTER)
        dev1_info1_lbl.pack(fill=X, padx=10, pady=5)

        # Social Icons Frame
        icons_frame1 = Frame(self.dev1_frame, bg='pink')
        icons_frame1.pack(pady=5)

        img1 = Image.open(resource_path("college_images\\facebook.png"))
        img1 = img1.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        l1 = Label(icons_frame1, image=self.photoimg1, cursor='hand2', bg='pink')
        l1.pack(side=LEFT, padx=10)

        img2 = Image.open(resource_path("college_images\\snap.png"))
        img2 = img2.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        l2 = Label(icons_frame1, image=self.photoimg2, cursor='hand2', bg='pink')
        l2.pack(side=LEFT, padx=10)

        img3 = Image.open(resource_path("college_images\\github.png"))
        img3 = img3.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        l3 = Label(icons_frame1, image=self.photoimg3, cursor='hand2', bg='pink')
        l3.pack(side=LEFT, padx=10)

        img = Image.open(resource_path("college_images\\insta.png"))
        img = img.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        l4 = Label(icons_frame1, image=self.photoimg, cursor='hand2', bg='pink')
        l4.pack(side=LEFT, padx=10)

        dev1_info2_lbl = Label(self.dev1_frame,
                               text='To know more about me scan QR code:',
                               font=('times new roman', 12, 'bold'), bg='pink', fg='purple', wraplength=300, justify=CENTER)
        dev1_info2_lbl.pack(fill=X, padx=10, pady=5)

        # Reduced QR code size
        img9 = Image.open(resource_path("college_images\\pdf_qr_code1.png"))
        img9 = img9.resize((80, 80), Image.Resampling.LANCZOS)
        self.photoimg9 = ImageTk.PhotoImage(img9)
        l5 = Label(self.dev1_frame, image=self.photoimg9, bg='pink')
        l5.pack(pady=5)

        # Bind events
        l1.bind("<Button-1>", lambda e: webbrowser.open("https://www.facebook.com/harsh.makhija.399"))
        l2.bind("<Button-1>", lambda e: webbrowser.open("https://www.snapchat.com/add/h_makhija5437"))  
        l3.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/makhijaharsh197"))
        l4.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/harsh_makhija_007/"))


        # ================== Developer 2 Frame (Right) ==================
        # Reparent to root
        self.dev2_frame = Frame(self.root, bd=2, bg='aqua')
        self.dev2_frame.place(relx=0.51, rely=0.12, relwidth=0.47, relheight=0.85)

        dev2_img = Image.open(resource_path("college_images\\dev_1.png"))
        dev2_img = dev2_img.resize((130, 130), Image.Resampling.LANCZOS)
        self.dev2_photoimg = ImageTk.PhotoImage(dev2_img)

        dev2_lbl = Label(self.dev2_frame, image=self.dev2_photoimg, bg='aqua')
        dev2_lbl.pack(pady=5)

        dev2_info_lbl = Label(self.dev2_frame,
                              text='Hello my name is Dev Vaidya, I am a 3rd year BCA Student. Know Java, Python, HTML, CSS, C and Javascript Basics.',
                              font=('times new roman', 16, 'bold'), bg='aqua', fg='red', wraplength=500, justify=CENTER)
        dev2_info_lbl.pack(fill=X, padx=10, pady=5)

        dev2_info1_lbl = Label(self.dev2_frame,
                               text='You can contact me at following platforms:',
                               font=('times new roman', 14, 'bold'), bg='aqua', fg='green', wraplength=400, justify=CENTER)
        dev2_info1_lbl.pack(fill=X, padx=10, pady=5)

        # Social Icons Frame
        icons_frame2 = Frame(self.dev2_frame, bg='aqua')
        icons_frame2.pack(pady=5)

        img4 = Image.open(resource_path("college_images\\facebook.png"))
        img4 = img4.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg4 = ImageTk.PhotoImage(img4)
        l1_2 = Label(icons_frame2, image=self.photoimg4, cursor='hand2', bg='aqua')
        l1_2.pack(side=LEFT, padx=10)

        img5 = Image.open(resource_path("college_images\\x.png"))
        img5 = img5.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg5 = ImageTk.PhotoImage(img5)
        l2_2 = Label(icons_frame2, image=self.photoimg5, cursor='hand2', bg='aqua')
        l2_2.pack(side=LEFT, padx=10)

        img6 = Image.open(resource_path("college_images\\github.png"))
        img6 = img6.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg6 = ImageTk.PhotoImage(img6)
        l3_2 = Label(icons_frame2, image=self.photoimg6, cursor='hand2', bg='aqua')
        l3_2.pack(side=LEFT, padx=10)

        img7 = Image.open(resource_path("college_images\\insta.png"))
        img7 = img7.resize((30, 30), Image.Resampling.LANCZOS)
        self.photoimg7 = ImageTk.PhotoImage(img7)
        l4_2 = Label(icons_frame2, image=self.photoimg7, cursor='hand2', bg='aqua')
        l4_2.pack(side=LEFT, padx=10)

        dev2_info2_lbl = Label(self.dev2_frame,
                               text='To know more about me scan QR code:',
                               font=('times new roman', 12, 'bold'), bg='aqua', fg='green', wraplength=300, justify=CENTER)
        dev2_info2_lbl.pack(fill=X, padx=10, pady=5)

        img8 = Image.open(resource_path("college_images\\pdf_qr_code.png"))
        img8 = img8.resize((80, 80), Image.Resampling.LANCZOS)
        self.photoimg8 = ImageTk.PhotoImage(img8)
        l5_2 = Label(self.dev2_frame, image=self.photoimg8, bg='aqua')
        l5_2.pack(pady=5)

        # Bind events
        l1_2.bind("<Button-1>", lambda e: webbrowser.open("https://www.facebook.com/dev.vaidya.526"))
        l2_2.bind("<Button-1>", lambda e: webbrowser.open("https://x.com/vaidyadev2"))  
        l3_2.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/vaidyadev"))
        l4_2.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/devv6688/"))
        
        # Bind Resize Event
        self.root.bind('<Configure>', self.on_resize)
        self.update_layout_images() 

    def on_resize(self, event):
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_layout_images)

    def update_layout_images(self):
        """Resizes background image"""
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        if win_w < 100: win_w = 1360
        if win_h < 100: win_h = 680

        # Background Image (93% height)
        h_bg = int(win_h * 0.93)
        w_bg = win_w
        if h_bg > 0 and w_bg > 0:
            try:
                resized_bg = self.org_img_top.resize((w_bg, h_bg), Image.Resampling.LANCZOS)
                self.photoimg_top = ImageTk.PhotoImage(resized_bg)
                self.f_lbl.config(image=self.photoimg_top)
            except Exception:
                pass
        
        # Ensure Z-Order
        self.title_lbl.lift()
        self.time_lbl.lift()
        self.back_btn.lift()
        # Lift frames explicitly
        self.dev1_frame.lift()
        self.dev2_frame.lift()

    def back(self):
        self.root.destroy()

    def update_time(self):
        try:
            current_time = strftime('%I:%M:%S %p')
            self.time_lbl.config(text=current_time)
            self.time_lbl.after(1000, self.update_time)
        except:
            pass

if __name__ == '__main__':
    root = Tk()
    obj = developer(root)
    root.mainloop()
