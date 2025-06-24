from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image,ImageTk
import cv2.face
from student import students
from train import train
import mysql.connector
import os
import cv2
import time
from time import strftime
from datetime import datetime
from liveness import LivenessDetector


class face_recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        # self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        self.title_lbl = Label(self.root, text='FACE RECOGNITION', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()  # start the clock


        back_btn=Button(self.title_lbl,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        back_btn.place(x=1150,y=10,height=25)

        img_top = Image.open("college_images\\face_detector1.jpg")
        img_top = img_top.resize((560,635), Image.Resampling.LANCZOS)
        self.photoimg_top = ImageTk.PhotoImage(img_top)

        f_lbl = Label(self.root, image=self.photoimg_top)
        f_lbl.place(x=0, y=45, width=560, height=635)

        img_bottom = Image.open("college_images\\register.jpg")
        img_bottom = img_bottom.resize((800,635), Image.Resampling.LANCZOS)
        self.photoimg_bottom = ImageTk.PhotoImage(img_bottom)

        f_lbl1 = Label(self.root, image=self.photoimg_bottom)
        f_lbl1.place(x=560, y=45, width=800, height=635)

        b1=Button(f_lbl1,text='FACE RECOGNITION',cursor='hand2',font=('times new roman',15,'bold'),activebackground='yellow',activeforeground='blue',bg='green',fg='red',command=self.face_recog)
        b1.place(x=290,y=565,width=210,height=40)
    #########################Attendance#############################
    def mark_attendance(self, i, r, n, d):
        with open('attendance.csv', 'r+', newline='\n') as f:
            mydata = f.readlines()
            now = datetime.now()
            date_today = now.strftime('%d/%m/%Y')
            time_now = now.strftime('%H:%M:%S')

            already_present_today = False
            for line in mydata:
                entry = line.strip().split(',')
                # print(entry)
                if len(entry) > 0 and entry[0] == i and entry[5] == date_today:
                    already_present_today = True
                    break

            if not already_present_today:
                f.writelines(f'\n{i},{n},{r},{d},{time_now},{date_today},Present')





    ##########################Face recognition#######################
    def face_recog(self):
        def draw_boundry(img,classifier,scalefactor,minNeighbors,color,text,clf):
            gray_images=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            features=classifier.detectMultiScale(gray_images,scalefactor,minNeighbors)
            coord=[]

            for(x,y,w,h) in features:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                id,predict=clf.predict(gray_images[y:y+h,x:x+w])
                confidence=int((100*(1-predict/300)))

                
                conn=mysql.connector.connect(host='localhost',username='root',password='1582',database='face_recognizer')
                my_cursor=conn.cursor()

                my_cursor.execute('select Student_name from student where Student_id='+str(id))
                n=my_cursor.fetchone()
                n='+'.join(n)

                my_cursor.execute('select Roll from student where Student_id='+str(id))
                r=my_cursor.fetchone()
                r='+'.join(r)

                my_cursor.execute('select Dep from student where Student_id='+str(id))
                d=my_cursor.fetchone()
                d='+'.join(d)

                my_cursor.execute('select Student_id from student where Student_id='+str(id))
                i=my_cursor.fetchone()
                i='+'.join(i)

                if confidence>77:
                    cv2.putText(img,f'ID : {i}',(x,y-75),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                    cv2.putText(img,f'Name : {n}',(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                    cv2.putText(img,f'Roll No : {r}',(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                    cv2.putText(img,f'Department : {d}',(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                    self.mark_attendance(i,r,n,d)
                else:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
                    cv2.putText(img,f'Unknown Face',(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                coord=[x,y,w,h]
            return coord
        def recognize(img,clf,faceCascade):
            coord=draw_boundry(img=img,classifier=faceCascade,scalefactor=1.1,minNeighbors=10,color=(255,25,255),text='Face',clf=clf)
            return img
            
        

        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        clf = cv2.face.LBPHFaceRecognizer.create()
        clf.read('classifier.xml')
        detector = LivenessDetector()
        video_cap = cv2.VideoCapture(1)

        # Step 1: Require live face BEFORE recognition
        live_verified = False
        start_time = time.time()  # Start the timer
        messagebox.showinfo('Authentication','Detecting Liveness :',parent=self.root)
        while not live_verified:
            ret, img = video_cap.read()
            is_live, face_rect, message = detector.detect_liveness(img)
            if time.time() - start_time > 30:
                messagebox.showerror('Exiting','Time Limit Reached',parent=self.root)
                video_cap.release()
                cv2.destroyAllWindows()
                break
            
            if is_live:
                live_verified = True
                cv2.putText(img, "Liveness Detection Test:", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(img, "Liveness Verified. Starting Recognition...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Liveness Detection", img)
                cv2.waitKey(1500)  # Wait for 1.5 seconds
                break
            else:
                if face_rect is not None:
                    x, y, w, h = face_rect
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(img, "Liveness Detection Test:", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(img, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Liveness Detection", img)
                if cv2.waitKey(1) == 13:
                    video_cap.release()
                    cv2.destroyAllWindows()
                    return  # Exit if Enter key is pressed

        cv2.destroyWindow("Liveness Detection")

        
        
        
        while True:
            ret,img=video_cap.read()
            img=recognize(img,clf,faceCascade)
            cv2.imshow("Welcome To Face Recognition",img)
            if cv2.waitKey(1)==13:
                break
        video_cap.release()
        cv2.destroyAllWindows()
    def back(self):
        self.root.destroy()

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)  # call again after 1 second


       
if __name__ == '__main__':
    root=Tk()
    obj=face_recognition(root)
    root.mainloop() 