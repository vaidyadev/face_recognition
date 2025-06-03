from time import strftime
import numpy as np 
import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import os

# open source computer vision librabry full form of opencv

''' Here we are using LBPH(Local Binary Pattern Histogram) algorithm 

Note that face recognition is different of face detection:

Face Detection: it has the objective of finding the faces (location and size) in an image and probably extract them to be used by the face recognition algorithm.

Face Recognition: with the facial images already extracted, cropped, resized and usually converted to grayscale, the face recognition algorithm is responsible for finding characteristics which best describe the image.
                    Introduction
Local Binary Pattern (LBP) is a simple yet very efficient texture operator which labels the pixels of an image by thresholding the neighborhood of each pixel and considers the result as a binary number.

you can further read on it by here :
https://medium.com/data-science/face-recognition-how-lbph-works-90ec258c3d6b
'''


class train:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        self.title_lbl = Label(self.root, text='TRAIN DATA SET', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        back_btn=Button(self.title_lbl,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        back_btn.place(x=1150,y=10,height=25)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()  # start the clock

        img_top = Image.open("college_images\\facialrecognition.png")
        img_top = img_top.resize((1360,300), Image.Resampling.LANCZOS)
        self.photoimg_top = ImageTk.PhotoImage(img_top)

        f_lbl = Label(self.root, image=self.photoimg_top)
        f_lbl.place(x=0, y=45, width=1360, height=300)

        b1=Button(self.root,text='TRAIN DATA',cursor='hand2',font=('times new roman',35,'bold'),activebackground='red',activeforeground='green',bg='darkblue',fg='white',command=self.train_classifier)
        b1.place(x=0,y=345,width=1360,height=55)

        img_bottom = Image.open("college_images\\opencv_face_reco_more_data.jpg")
        img_bottom = img_bottom.resize((1360,300), Image.Resampling.LANCZOS)
        self.photoimg_bottom = ImageTk.PhotoImage(img_bottom)

        f_lbl1 = Label(self.root, image=self.photoimg_bottom)
        f_lbl1.place(x=0, y=400, width=1360, height=280)

    def train_classifier(self):
        data_dir=('data')
        path=[os.path.join(data_dir,file)for file in os.listdir(data_dir)]
        faces=[]
        ids=[]
        

        for image in path:
            img=Image.open(image).convert('L')# convert image into gray scale
            imagenp=np.array(img,'uint8')
            id=int(os.path.split(image)[1].split('.')[1])
            faces.append(imagenp)
            ids.append(id)

            cv2.imshow('Training Frame',imagenp)
            cv2.waitKey(1)==13
        ids=np.array(ids)

        ################################Train the Classifier and Save############
        clf=cv2.face.LBPHFaceRecognizer.create()
        clf.train(faces,ids)
        clf.write('classifier.xml')
        cv2.destroyAllWindows()
        messagebox.showinfo('Result','Training Datasets Completed!!',parent=self.root)
    def back(self):
        self.root.destroy()
    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)  # call again after 1 second



   
    

       

if __name__ == '__main__':
    root=Tk()
    obj=train(root)
    root.mainloop() 