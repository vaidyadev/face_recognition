from time import strftime
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
import cv2
import webbrowser  # For clickable links

class developer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        self.title_lbl = Label(self.root, text='DEVLOPERS', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        back_btn = Button(self.title_lbl, text="Back", width=22, cursor='hand2', font=('times new roman', 10, 'bold'),
                          bg='red', fg='white', activebackground="green", command=self.back)
        back_btn.place(x=1150, y=10, height=25)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red', borderwidth=0,
                              highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()  # start the clock

        img_top = Image.open("college_images\\dev.jpg")
        img_top = img_top.resize((1360, 650), Image.Resampling.LANCZOS)
        self.photoimg_top = ImageTk.PhotoImage(img_top)

        f_lbl = Label(self.root, image=self.photoimg_top)
        f_lbl.place(x=0, y=45, width=1360, height=650)

        dev1_frame = Frame(f_lbl, bd=2,bg='pink')
        dev1_frame.place(x=10, y=10, width=500, height=620)

        dev1_img = Image.open("college_images\\dev_2.png")
        dev1_img = dev1_img.resize((160, 160), Image.Resampling.LANCZOS)
        self.dev1_photoimg = ImageTk.PhotoImage(dev1_img)

        dev1_lbl = Label(dev1_frame, image=self.dev1_photoimg, bg='pink')
        dev1_lbl.place(x=200, y=0, width=160, height=160)

        dev1_info_lbl = Label(dev1_frame,
                              text='Hello my name is Harsh Makhija, I am a 3rd year BCA Student. Know Java, PHP, Kotlin, MERN, Python Basics.',
                              font=('times new roman', 20, 'bold'), bg='pink', fg='blue', wraplength=400)
        dev1_info_lbl.place(x=70, y=180)

        dev1_info1_lbl = Label(dev1_frame,
                               text='You can contact me at following platforms:',
                               font=('times new roman', 18, 'bold'), bg='pink', fg='purple', wraplength=400)
        dev1_info1_lbl.place(x=70, y=370)

        img1 = Image.open("college_images\\facebook.png")
        img1 = img1.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        l1 = Label(dev1_frame, image=self.photoimg1, cursor='hand2', bg='pink')
        l1.place(x=150, y=460, width=35, height=35)

        img2 = Image.open("college_images\\snap.png")
        img2 = img2.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        l2 = Label(dev1_frame, image=self.photoimg2, cursor='hand2', bg='pink')
        l2.place(x=220, y=460, width=35, height=35)

        img3 = Image.open("college_images\\github.png")
        img3 = img3.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        l3 = Label(dev1_frame, image=self.photoimg3, cursor='hand2', bg='pink')
        l3.place(x=300, y=460, width=35, height=35)

        img = Image.open("college_images\\insta.png")
        img = img.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        l4 = Label(dev1_frame, image=self.photoimg, cursor='hand2', bg='pink')
        l4.place(x=370, y=460, width=35, height=35)

        dev1_info2_lbl = Label(dev1_frame,
                               text='To know more about me scan QR code:',
                               font=('times new roman', 15, 'bold'), bg='pink', fg='purple', wraplength=300)
        dev1_info2_lbl.place(x=70, y=520)

        img9 = Image.open("college_images\\pdf_qr_code1.png")
        img9 = img9.resize((100, 100), Image.Resampling.LANCZOS)
        self.photoimg9 = ImageTk.PhotoImage(img9)
        l5 = Label(dev1_frame, image=self.photoimg9, bg='pink')
        l5.place(x=370, y=520, width=100, height=100)

        # # ========== Link Functions ==========
        def open_facebook(event):
            webbrowser.open("https://www.facebook.com/harsh.makhija.399")

        def open_snap(event):
            webbrowser.open("https://www.snapchat.com/add/h_makhija5437")  
        def open_github(event):
            webbrowser.open("https://github.com/makhijaharsh197")

        def open_insta(event):
            webbrowser.open("https://www.instagram.com/harsh_makhija_007/")

        # Bind events
        l1.bind("<Button-1>", open_facebook)
        l2.bind("<Button-1>", open_snap)
        l3.bind("<Button-1>", open_github)
        l4.bind("<Button-1>", open_insta)


        dev2_frame = Frame(f_lbl, bd=2, bg='aqua')
        dev2_frame.place(x=850, y=10, width=500, height=620)

        

        dev2_img = Image.open("college_images\\dev_1.png")
        dev2_img = dev2_img.resize((160, 160), Image.Resampling.LANCZOS)
        self.dev2_photoimg = ImageTk.PhotoImage(dev2_img)

        dev2_lbl = Label(dev2_frame, image=self.dev2_photoimg, bg='aqua')
        dev2_lbl.place(x=200, y=0, width=160, height=160)

        dev2_info_lbl = Label(dev2_frame,
                              text='Hello my name is Dev Vaidya, I am a 3rd year BCA Student. Know Java, Python, HTML, CSS, C and Javascript Basics.',
                              font=('times new roman', 20, 'bold'), bg='aqua', fg='red', wraplength=400)
        dev2_info_lbl.place(x=70, y=180)

        dev2_info1_lbl = Label(dev2_frame,
                               text='You can contact me at following platforms:',
                               font=('times new roman', 18, 'bold'), bg='aqua', fg='green', wraplength=400)
        dev2_info1_lbl.place(x=70, y=370)

        img4 = Image.open("college_images\\facebook.png")
        img4 = img4.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg4 = ImageTk.PhotoImage(img4)
        l1 = Label(dev2_frame, image=self.photoimg4, cursor='hand2', bg='aqua')
        l1.place(x=150, y=460, width=35, height=35)

        img5 = Image.open("college_images\\x.png")
        img5 = img5.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg5 = ImageTk.PhotoImage(img5)
        l2 = Label(dev2_frame, image=self.photoimg5, cursor='hand2', bg='aqua')
        l2.place(x=220, y=460, width=35, height=35)

        img6 = Image.open("college_images\\github.png")
        img6 = img6.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg6 = ImageTk.PhotoImage(img6)
        l3 = Label(dev2_frame, image=self.photoimg6, cursor='hand2', bg='aqua')
        l3.place(x=300, y=460, width=35, height=35)

        img7 = Image.open("college_images\\insta.png")
        img7 = img7.resize((35, 35), Image.Resampling.LANCZOS)
        self.photoimg7 = ImageTk.PhotoImage(img7)
        l4 = Label(dev2_frame, image=self.photoimg7, cursor='hand2', bg='aqua')
        l4.place(x=370, y=460, width=35, height=35)

        dev2_info2_lbl = Label(dev2_frame,
                               text='To know more about me scan QR code:',
                               font=('times new roman', 15, 'bold'), bg='aqua', fg='green', wraplength=300)
        dev2_info2_lbl.place(x=70, y=520)

        img8 = Image.open("college_images\\pdf_qr_code.png")
        img8 = img8.resize((100, 100), Image.Resampling.LANCZOS)
        self.photoimg8 = ImageTk.PhotoImage(img8)
        l5 = Label(dev2_frame, image=self.photoimg8, bg='aqua')
        l5.place(x=370, y=520, width=100, height=100)

        # ========== Link Functions ==========
        def open_facebook(event):
            webbrowser.open("https://www.facebook.com/dev.vaidya.526")

        def open_x(event):
            webbrowser.open("https://x.com/vaidyadev2")  # or twitter.com

        def open_github(event):
            webbrowser.open("https://github.com/vaidyadev")

        def open_insta(event):
            webbrowser.open("https://www.instagram.com/devv6688/")

        # Bind events
        l1.bind("<Button-1>", open_facebook)
        l2.bind("<Button-1>", open_x)
        l3.bind("<Button-1>", open_github)
        l4.bind("<Button-1>", open_insta)

    def back(self):
        self.root.destroy()

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)


if __name__ == '__main__':
    root = Tk()
    obj = developer(root)
    root.mainloop()
