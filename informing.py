from time import strftime
from utils import resource_path
from tkinter import *
from PIL import Image,ImageTk
from tkinter import messagebox
from send_email import emailsender
from send_whatsapp import msgsender
from send_telegram import TelegramBotSender
class Inform:
    def __init__(self,root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(True, True) # Enabled Resizing
        self.root.minsize(1024, 600)
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))

        # --- Header Images ---
        # 46% Left, 54% Right split roughly matches original 625/735 split
        self.org_img_left = Image.open(resource_path("college_images\\com.jpg"))
        self.org_img_right = Image.open(resource_path("college_images\\_com2.webp"))
        
        # Placeholders
        self.photoimg = ImageTk.PhotoImage(self.org_img_left.resize((625, 170)))
        self.photoimg1 = ImageTk.PhotoImage(self.org_img_right.resize((735, 170)))
        
        self.f_lbl = Label(self.root, image=self.photoimg)
        self.f_lbl.place(relx=0, rely=0, relwidth=0.46, relheight=0.25)
        
        self.f_lbl1 = Label(self.root, image=self.photoimg1)
        self.f_lbl1.place(relx=0.46, rely=0, relwidth=0.54, relheight=0.25)

        # --- Background Image ---
        self.org_img_bg = Image.open(resource_path("college_images\\wp2551980.jpg"))
        self.photoimg3 = ImageTk.PhotoImage(self.org_img_bg.resize((1360, 560)))
        
        self.bg_img = Label(self.root, image=self.photoimg3)
        self.bg_img.place(relx=0, rely=0.25, relwidth=1.0, relheight=0.75)

        # --- Overlays (Title & Time) ---
        # Reparented to root so they stay on top of background
        self.title_lbl = Label(self.root, text='INFORMING MESSAGE  CENTER', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(relx=0, rely=0.25, relwidth=1.0, relheight=0.07) # height ~45px/680

        self.time_lbl = Label(self.root, font=('times new roman', 17, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(relx=0, rely=0.25, relwidth=0.11, relheight=0.07)
        self.update_time()

        # --- Back Button ---
        # Reparented to root, positioned top-right of the title bar area
        self.back_btn=Button(self.root,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        self.back_btn.place(relx=0.85, rely=0.26, relwidth=0.1, relheight=0.05)

        # --- Action Buttons (Mail, Whatsapp, Telegram) ---
        # These will be children of bg_img or root? 
        # Using root for easier z-order management, positioned relative to window
        
        # Load Original Images for resizing
        self.org_img_mail = Image.open(resource_path("college_images\\mail.jpg"))
        self.org_img_what = Image.open(resource_path("college_images\\what.jpg"))
        self.org_img_tel = Image.open(resource_path("college_images\\tel.jpg"))
        
        # Initial placeholders
        self.photoimg4 = ImageTk.PhotoImage(self.org_img_mail.resize((400,410)))
        self.photoimg5 = ImageTk.PhotoImage(self.org_img_what.resize((400,410)))
        self.photoimg6 = ImageTk.PhotoImage(self.org_img_tel.resize((400,410)))

        def bind_hover(btn, normal_bg, hover_bg):
            btn.bind('<Enter>', lambda e: btn.config(bg=hover_bg))
            btn.bind('<Leave>', lambda e: btn.config(bg=normal_bg))

        # 1. MAIL
        self.btn_mail_img = Button(self.root, image=self.photoimg4, cursor='hand2', command=self.email)
        self.btn_mail_img.place(relx=0.03, rely=0.35, relwidth=0.29, relheight=0.50)
        
        self.btn_mail_txt = Button(self.root, text="Inform Via Mail", cursor='hand2', font=('times new roman', 20, 'bold'), bg='#2B2B52', fg='white', activebackground="#483D8B", activeforeground='white', command=self.email)
        self.btn_mail_txt.place(relx=0.03, rely=0.86, relwidth=0.29, relheight=0.08)
        bind_hover(self.btn_mail_txt, '#2B2B52', '#483D8B')

        # 2. WHATSAPP
        self.btn_what_img = Button(self.root, image=self.photoimg5, cursor='hand2', command=self.whatsapp)
        self.btn_what_img.place(relx=0.35, rely=0.35, relwidth=0.29, relheight=0.50)
        
        self.btn_what_txt = Button(self.root, text="Inform Via Whatsapp", cursor='hand2', font=('times new roman', 20, 'bold'), bg='#228B22', fg='white', activebackground="#32CD32", activeforeground='white', command=self.whatsapp)
        self.btn_what_txt.place(relx=0.35, rely=0.86, relwidth=0.29, relheight=0.08)
        bind_hover(self.btn_what_txt, '#228B22', '#32CD32')

        # 3. TELEGRAM
        self.btn_tel_img = Button(self.root, image=self.photoimg6, cursor='hand2', command=self.telegram)
        self.btn_tel_img.place(relx=0.67, rely=0.35, relwidth=0.29, relheight=0.50)
        
        self.btn_tel_txt = Button(self.root, text="Inform Via Telegram", cursor='hand2', font=('times new roman', 20, 'bold'), bg='slateblue2', fg='white', activebackground="slateblue1", activeforeground='white', command=self.telegram)
        self.btn_tel_txt.place(relx=0.67, rely=0.86, relwidth=0.29, relheight=0.08)
        bind_hover(self.btn_tel_txt, 'slateblue2', 'slateblue1')

        # Resize Binding
        self.resize_timer = None
        self.root.bind("<Configure>", self.on_resize)

    def back(self):
        self.root.destroy()
  
    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)

    def email(self):
       self.new_window=Toplevel(self.root)
       self.app=emailsender(self.new_window)

    def whatsapp(self):
       self.new_window=Toplevel(self.root)
       self.app=msgsender(self.new_window)
   
    def telegram(self):
        self.new_window = Toplevel(self.root)
        self.app = TelegramBotSender(self.new_window)

    # ================== RESIZING LOGIC ==================
    def on_resize(self, event):
        """Variable delay to prevent lag while dragging"""
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_layout_images)

    def update_layout_images(self):
        """Resizes images and handles Z-order"""
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        if win_w < 100 or win_h < 100: return
        
        # 1. Header (25% height)
        header_h = int(win_h * 0.25)
        
        # Left (46%)
        w_left = int(win_w * 0.46)
        try:
            resized = self.org_img_left.resize((w_left, header_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            self.f_lbl.config(image=photo)
            self.f_lbl.image = photo
        except: pass
        
        # Right (54%)
        w_right = win_w - w_left
        try:
            resized = self.org_img_right.resize((w_right, header_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            self.f_lbl1.config(image=photo)
            self.f_lbl1.image = photo
        except: pass
        
        # 2. Background (75% height)
        bg_h = int(win_h * 0.75)
        try:
            resized_bg = self.org_img_bg.resize((win_w, bg_h), Image.Resampling.LANCZOS)
            photo_bg = ImageTk.PhotoImage(resized_bg)
            self.bg_img.config(image=photo_bg)
            self.bg_img.image = photo_bg
        except: pass

        # 3. Action Images (Mail, Whatsapp, Telegram)
        # They take roughly 50% height and 29% width
        btn_w = int(win_w * 0.29)
        btn_h = int(win_h * 0.50)
        
        # Helper for resizing
        def resize_btn_img(org_img, btn_widget):
            try:
                resized = org_img.resize((btn_w, btn_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                btn_widget.config(image=photo)
                btn_widget.image = photo
            except: pass
            
        resize_btn_img(self.org_img_mail, self.btn_mail_img)
        resize_btn_img(self.org_img_what, self.btn_what_img)
        resize_btn_img(self.org_img_tel, self.btn_tel_img)

        # 4. Lift Overlays
        self.title_lbl.lift()
        self.time_lbl.lift()
        self.back_btn.lift()
        
        # Lift buttons to be sure
        self.btn_mail_img.lift()
        self.btn_mail_txt.lift()
        self.btn_what_img.lift()
        self.btn_what_txt.lift()
        self.btn_tel_img.lift()
        self.btn_tel_txt.lift()


if __name__ == '__main__':
    root=Tk()
    obj=Inform(root)
    root.mainloop()

