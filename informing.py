from time import strftime
from tkinter import *
from PIL import Image,ImageTk
from tkinter import messagebox
from send_email import emailsender
from send_whatsapp import msgsender
class Inform:
   def __init__(self,root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        # self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        img = Image.open("college_images\\com.jpg")
        img = img.resize((625, 170), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=0, width=625, height=170)

        img1 = Image.open("college_images\\_com2.webp")
        img1 = img1.resize((735, 170), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        f_lbl1 = Label(self.root, image=self.photoimg1)
        f_lbl1.place(x=625, y=0, width=735, height=170)

        #background
        img3 = Image.open("college_images\\wp2551980.jpg")
        img3 = img3.resize((1360, 560), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=170, width=1360, height=510)

        self.title_lbl = Label(bg_img, text='INFORMING MESSAGE  CENTER', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        self.time_lbl = Label(bg_img, font=('times new roman', 17, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=150, height=45)
        self.update_time()  # start the clock

        back_btn=Button(self.title_lbl,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        back_btn.place(x=1160,y=8,height=25)

        img4 = Image.open("college_images\\mail.jpg")
        img4 = img4.resize((660,410), Image.Resampling.LANCZOS)
        self.photoimg4 = ImageTk.PhotoImage(img4)

        b1=Button(bg_img,image=self.photoimg4,cursor='hand2',command=self.email)
        b1.place(x=10,y=50,width=660,height=410)

        b1_1=Button(bg_img,text="Inform Via Mail",cursor='hand2',font=('times new roman', 20, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.email)
        b1_1.place(x=10,y=460,width=660,height=60)

        img5 = Image.open("college_images\\what.jpg")
        img5 = img5.resize((670,410), Image.Resampling.LANCZOS)
        self.photoimg5 = ImageTk.PhotoImage(img5)

        b2=Button(bg_img,image=self.photoimg5,cursor='hand2',command=self.whatsapp)
        b2.place(x=680,y=50,width=670,height=410)

        b1_2=Button(bg_img,text="Inform Via Whatsapp",cursor='hand2',font=('times new roman', 20, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.whatsapp)
        b1_2.place(x=680,y=460,width=670,height=60)


   def back(self):
        self.root.destroy()
   def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)  # call again after 1 second

   def email(self):
       self.new_window=Toplevel(self.root)
       self.app=emailsender(self.new_window)
   def whatsapp(self):
       self.new_window=Toplevel(self.root)
       self.app=msgsender(self.new_window)
       


        
        

if __name__ == '__main__':
    root=Tk()
    obj=Inform(root)
    root.mainloop()

