from tkinter import *
from tkinter import ttk
import tkinter.messagebox
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



class face_recog:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+10")
        # self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition System")
        # self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate',150) 
        engine.setProperty('volume', 1.0)  
        engine.setProperty('voice',voices[1].id)
        self.time_after_id = None
        self.slider_after_id = None
        # engine.say("welcome to facial recognition attendance system please put your internet on and you must have webcam and SQL Database!!")
        # engine.runAndWait()
        # tkinter.messagebox.showwarning('Note','This application required stable internet connection and webcam and SQL Database',parent=self.root)
        

        # Define the scrolling text string here
        self.text = ''
        self.count = 0
        self.s = "FACE RECOGNITION ATTENDENCE SYSTEM "

        # Proceed with images and title label setup
        img = Image.open("college_images\\Stanford.jpg")
        img = img.resize((450, 130), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=0, width=450, height=130)

        img1 = Image.open("college_images\\facialrecognition.png")
        img1 = img1.resize((450, 130), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        f_lbl1 = Label(self.root, image=self.photoimg1)
        f_lbl1.place(x=450, y=0, width=450, height=130)

        img2 = Image.open("college_images\\u.jpg")
        img2 = img2.resize((460, 130), Image.Resampling.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        f_lbl2 = Label(self.root, image=self.photoimg2)
        f_lbl2.place(x=900, y=0, width=460, height=130)
    #background image
        img3 = Image.open("college_images\\wp2551980.jpg")
        img3 = img3.resize((1360, 560), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=130, width=1360, height=560)


        
        self.time_lbl = Label(bg_img, font=('times new roman', 15, 'bold'), bg='white', fg='green',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()  # start the clock

        self.title_lbl = Label(bg_img, text='', font=('times new roman', 35, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.title_lbl.place(x=120, y=0, width=1140, height=45)

        # New frame for logout button
        logout_frame = Frame(bg_img, bg='white')
        logout_frame.place(x=1240, y=0, width=120, height=45)

        self.back_btn = Button(logout_frame, text="Log Out", width=10, cursor='hand2',
                            font=('times new roman', 10, 'bold'), bg='red', fg='white',
                            activebackground="green", command=self.logout)
        self.back_btn.pack(pady=10)





    #student button
    #1 Student Details 
        img4 = Image.open("college_images\\student.jpg")
        img4 = img4.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg4 = ImageTk.PhotoImage(img4)

        b1=Button(bg_img,image=self.photoimg4,cursor='hand2',command=self.studuent_detail)
        b1.place(x=100,y=100,width=200,height=170)

        b1_1=Button(bg_img,text="Student Details",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.studuent_detail)
        b1_1.place(x=100,y=260,width=200,height=40)

    #2 Face Recognition
        img5 = Image.open("college_images\\face_detector1.jpg")
        img5 = img5.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg5 = ImageTk.PhotoImage(img5)

        b2=Button(bg_img,image=self.photoimg5,cursor='hand2',command=self.face_data)
        b2.place(x=400,y=100,width=200,height=170)

        b1_2=Button(bg_img,text="Face Recognition",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.face_data)
        b1_2.place(x=400,y=260,width=200,height=40)
    # 3 Attendence
        img6 = Image.open("college_images\\report.jpg")
        img6 = img6.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg6 = ImageTk.PhotoImage(img6)

        b3=Button(bg_img,image=self.photoimg6,cursor='hand2',command=self.attendance_details)
        b3.place(x=700,y=100,width=200,height=170)
        b1_3=Button(bg_img,text="Attendence",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.attendance_details)
        b1_3.place(x=700,y=260,width=200,height=40)
    #4 ChatBot
        img7 = Image.open("college_images\\chat.jpg")
        img7 = img7.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg7 = ImageTk.PhotoImage(img7)

        b4=Button(bg_img,image=self.photoimg7,cursor='hand2',command=self.chatbot)
        b4.place(x=1000,y=100,width=200,height=170)
        b1_4=Button(bg_img,text="HelpBot",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.chatbot)
        b1_4.place(x=1000,y=260,width=200,height=40)
    # 5 Train
        img8 = Image.open("college_images\\Train.jpg")
        img8 = img8.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg8 = ImageTk.PhotoImage(img8)

        b5=Button(bg_img,image=self.photoimg8,cursor='hand2',command=self.train_data)
        b5.place(x=100,y=330,width=200,height=170)

        b1_5=Button(bg_img,text="Train Data",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.train_data)
        b1_5.place(x=100,y=480,width=200,height=40)

    # 6 Photos
        img9 = Image.open("college_images\\opencv_face_reco_more_data.jpg")
        img9 = img9.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg9 = ImageTk.PhotoImage(img9)

        b6=Button(bg_img,image=self.photoimg9,cursor='hand2',command=self.open_images)
        b6.place(x=400,y=330,width=200,height=170)
        b1_6=Button(bg_img,text="Photos",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.open_images)
        b1_6.place(x=400,y=480,width=200,height=40)

    # 7 Devlopers
        img10 = Image.open("college_images\\Team-Management-Software-Development.jpg")
        img10 = img10.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg10 = ImageTk.PhotoImage(img10)

        b7=Button(bg_img,image=self.photoimg10,cursor='hand2',command=self.devloper)
        b7.place(x=700,y=330,width=200,height=170)
        b1_7=Button(bg_img,text="Devlopers",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.devloper)
        b1_7.place(x=700,y=480,width=200,height=40)
    #8 Exit
        img11 = Image.open("college_images\\exit.jpg")
        img11 = img11.resize((200,170), Image.Resampling.LANCZOS)
        self.photoimg11 = ImageTk.PhotoImage(img11)

        b11=Button(bg_img,image=self.photoimg11,cursor='hand2',command=self.iexit)
        b11.place(x=1000,y=330,width=200,height=170)
        b1_11=Button(bg_img,text="Exit",cursor='hand2',font=('times new roman', 15, 'bold'), bg='darkblue', fg='white'
                    ,activebackground="red",activeforeground='green',command=self.iexit)
        b1_11.place(x=1000,y=480,width=200,height=40)


       
       

        # Start the slider after initializing everything
        self.slider()

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
        # Cancel the scheduled after callbacks before destroying the root
        if self.time_after_id:
            self.time_lbl.after_cancel(self.time_after_id)
        if self.slider_after_id:
            self.title_lbl.after_cancel(self.slider_after_id)

        self.root.destroy()  # Destroy the current main window
        new_root = Tk()
        app = login_window(new_root)
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
        self.time_lbl.config(text=current_time)
        self.time_after_id = self.time_lbl.after(1000, self.update_time)



if __name__ == '__main__':
    root=Tk()
    obj=face_recog(root)
    root.mainloop() 