from time import strftime
import cv2.face
import numpy as np 
import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import os
from utils import resource_path

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
        self.root.minsize(800, 600)
        self.root.title("Face Recognition System")
        self.root.resizable(True, True)
        self.root.state('zoomed')
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))
        self.resize_timer = None

        # ================== Title Section ==================
        # Reparented to root for Z-order handling
        self.title_lbl = Label(self.root, text='TRAIN DATA SET', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(relx=0, rely=0, relwidth=1, relheight=0.07)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(relx=0, rely=0, width=120, relheight=0.07)
        self.update_time()

        # Back Button - Reparented to root, positioned top-right
        self.back_btn=Button(self.root,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), 
                             bg='red', fg='white',activebackground="green",command=self.back)
        self.back_btn.place(relx=1.0, rely=0.015, x=-20, width=80, height=30, anchor="ne")

        # ================== Top Image ==================
        # Load and keep original for resizing
        self.org_img_top = Image.open(resource_path("college_images\\facialrecognition.png"))
        self.f_lbl = Label(self.root)
        self.f_lbl.place(relx=0, rely=0.07, relwidth=1, relheight=0.38)

        def bind_hover(btn, normal_bg, hover_bg):
            btn.bind('<Enter>', lambda e: btn.config(bg=hover_bg))
            btn.bind('<Leave>', lambda e: btn.config(bg=normal_bg))

        # ================== Train Button ==================
        self.b1=Button(self.root,text='TRAIN DATA',cursor='hand2',font=('times new roman',35,'bold'),
                       activebackground='#FF6347',activeforeground='white',bg='#B22222',fg='white',command=self.train_classifier)
        self.b1.place(relx=0, rely=0.45, relwidth=1, relheight=0.10)
        bind_hover(self.b1, '#B22222', '#FF6347')

        # ================== Bottom Image ==================
        # Load and keep original
        self.org_img_bottom = Image.open(resource_path("college_images\\opencv_face_reco_more_data.jpg"))
        self.f_lbl1 = Label(self.root)
        self.f_lbl1.place(relx=0, rely=0.55, relwidth=1, relheight=0.45)

        # Bind Resize Event
        self.root.bind('<Configure>', self.on_resize)
        self.update_layout_images() # Initial call
    
    def on_resize(self, event):
        """Variable delay to prevent lag while dragging"""
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_layout_images)

    def update_layout_images(self):
        """Resizes images to fit current window dimensions"""
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        # Guard against startup zero-size
        if win_w < 100: win_w_final = 1360
        else: win_w_final = win_w
            
        if win_h < 100: win_h_final = 680
        else: win_h_final = win_h

        # Top Image (38% height)
        h_top = int(win_h_final * 0.38)
        w_top = win_w_final
        if h_top > 0 and w_top > 0:
            try:
                resized_top = self.org_img_top.resize((w_top, h_top), Image.Resampling.LANCZOS)
                self.photoimg_top = ImageTk.PhotoImage(resized_top)
                self.f_lbl.config(image=self.photoimg_top)
            except Exception as e:
                pass # print(f"Resize error top: {e}")

        # Bottom Image (45% height)
        h_bot = int(win_h_final * 0.45)
        w_bot = win_w_final
        if h_bot > 0 and w_bot > 0:
             try:
                resized_bot = self.org_img_bottom.resize((w_bot, h_bot), Image.Resampling.LANCZOS)
                self.photoimg_bottom = ImageTk.PhotoImage(resized_bot)
                self.f_lbl1.config(image=self.photoimg_bottom)
             except Exception as e:
                pass # print(f"Resize error bot: {e}")
        
        # Ensure Z-Order (overlays on top)
        self.title_lbl.lift()
        self.time_lbl.lift()
        self.back_btn.lift() # Lift Button

    def train_classifier(self):
        # Bug 11 Fix: Run training in a separate thread to prevent UI freeze
        import threading
        t = threading.Thread(target=self._train_thread)
        t.start()

    def _train_thread(self):
        try:
            # Bug 1 & 10 Fix: Check data directory and use dynamic path if needed (defaulting to 'data')
            data_dir = resource_path('data')
            if not os.path.exists(data_dir):
                messagebox.showerror("Error", "Data directory not found!", parent=self.root)
                return

            path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]
            faces = []
            ids = []
            
            # Initialize CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            
            # Bug 8 & 9 Fix: Face Detection & Resizing
            try:
                face_cascade = cv2.CascadeClassifier(resource_path("haarcascade_frontalface_default.xml"))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load haarcascade: {str(e)}", parent=self.root)
                return

            valid_image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}

            for image in path:
                # Bug 2 Fix: Validate file extension
                _, ext = os.path.splitext(image)
                if ext.lower() not in valid_image_extensions:
                    continue

                try:
                    img = Image.open(image).convert('L') # convert image into gray scale
                    imagenp = np.array(img, 'uint8')
                    
                    # Apply CLAHE
                    imagenp = clahe.apply(imagenp)
                    
                    # Bug 3 Fix: Robust ID extraction
                    base_name = os.path.basename(image)
                    try:
                        # Assumes format: user.ID.Count.jpg
                        parts = base_name.split('.')
                        if len(parts) < 3:
                            continue # Skip files that don't match format
                        id = int(parts[1])
                    except ValueError:
                        continue # Skip files with non-integer IDs

                    # Face Detection on training image to ensure quality
                    faces_detected = face_cascade.detectMultiScale(imagenp, scaleFactor=1.3, minNeighbors=5)
                    
                    if len(faces_detected) < 1:
                        # Fallback: Use entire image if no face detected (or skip?)
                        # Better to use the image if it was already cropped, but re-verifying is safer.
                        # For this specific app, images in 'data' are likely already cropped by student.py.
                        # However, ensuring consistency is good.
                        # Using center crop or resizing to standard size is safer if detection fails but we trust the source.
                        # Let's resize to standard size (450x450) to match student.py output
                        img_resized = cv2.resize(imagenp, (450, 450))
                        faces.append(img_resized)
                        ids.append(id)
                    else:
                        for (x, y, w, h) in faces_detected:
                            face_roi = imagenp[y:y+h, x:x+w]
                            face_resized = cv2.resize(face_roi, (450, 450))
                            faces.append(face_resized)
                            ids.append(id)
                            break # Only use the first face found

                    # Visual feedback (User requested to keep this effect)
                    cv2.imshow('Training Frame', imagenp)
                    # Bug 5 Fix: Correct waitKey usage
                    if cv2.waitKey(1) == 13:
                        break
                except Exception as ex:
                    print(f"Skipping corrupt image {image}: {ex}")
                    continue
            
            cv2.destroyAllWindows() 
            
            # Bug 4 Fix: Check for empty dataset
            if len(faces) == 0:
                messagebox.showerror("Error", "No valid training data found!", parent=self.root)
                return

            ids = np.array(ids)

            # Train the Classifier
            clf = cv2.face.LBPHFaceRecognizer.create(radius=1, neighbors=8, grid_x=8, grid_y=8)
            clf.train(faces, ids)
            
            # Bug 6 Fix: Safe classifier path
            clf_path = resource_path('classifier.xml') # Saving to current working dir is usually fine for this app structure
            clf.write(clf_path)
            
            messagebox.showinfo('Result', 'Training Datasets Completed!!', parent=self.root)

        except Exception as e:
            # Bug 7 Fix: Exception Handling
            messagebox.showerror("Error", f"Training failed: {str(e)}", parent=self.root)
        
    def back(self):
        self.root.destroy()
        
    def update_time(self):
        try:
            current_time = strftime('%I:%M:%S %p')
            self.time_lbl.config(text=current_time)
            self.time_lbl.after(1000, self.update_time)  # call again after 1 second
        except:
            pass 

if __name__ == '__main__':
    root=Tk()
    obj=train(root)
    root.mainloop() 