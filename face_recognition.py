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
from object_guard import ObjectGuard
import threading

class face_recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        self.title_lbl = Label(self.root, text='FACE RECOGNITION', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()

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

        # --- PRE-LOAD MODELS HERE ---
        # 1. Load Object Guard immediately so it's ready before button click
        self.object_guard = ObjectGuard()
        self.liveness_detector = LivenessDetector()

    ######################### Attendance (MySQL) #############################
    def mark_attendance(self, i, r, n, d):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3307,
                username='root',
                password='1582',
                database='face_recognizer'
            )
            my_cursor = conn.cursor()

            now = datetime.now()
            date_today = now.strftime('%d/%m/%Y')
            time_now = now.strftime('%H:%M:%S')

            my_cursor.execute("SELECT * FROM attendance WHERE Student_id=%s AND Date=%s", (i, date_today))
            row = my_cursor.fetchone()

            if row is not None:
                print(f"Attendance already marked for {n} today.")
            else:
                my_cursor.execute(
                    "INSERT INTO attendance (Student_id, Student_name, Roll, Dep, Time, Date, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (i, n, r, d, time_now, date_today, "Present")
                )
                conn.commit()
                print(f"Attendance marked successfully for {n} at {time_now}")

            conn.close()

        except Exception as e:
            print(f"Error in marking attendance: {e}")

    ########################## Face recognition #######################
    def face_recog(self):
        def draw_boundry(img, classifier, scalefactor, minNeighbors, color, text, clf):
            gray_images = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray_images, scalefactor, minNeighbors)
            coord = []
            face_recognized = False 

            for (x, y, w, h) in features:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                id, predict = clf.predict(gray_images[y:y + h, x:x + w])
                confidence = int((100 * (1 - predict / 300)))

                try:
                    conn = mysql.connector.connect(host='localhost',port=3307, username='root', password='1582', database='face_recognizer')
                    my_cursor = conn.cursor()

                    my_cursor.execute('select Student_name from student where Student_id=' + str(id))
                    n = my_cursor.fetchone()
                    n = '+'.join(n)

                    my_cursor.execute('select Roll from student where Student_id=' + str(id))
                    r = my_cursor.fetchone()
                    r = '+'.join(r)

                    my_cursor.execute('select Dep from student where Student_id=' + str(id))
                    d = my_cursor.fetchone()
                    d = '+'.join(d)

                    my_cursor.execute('select Student_id from student where Student_id=' + str(id))
                    i = my_cursor.fetchone()
                    i = '+'.join(i)
                    
                    conn.close()

                    if confidence > 77:
                        cv2.putText(img, f'ID : {i}', (x, y - 75), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                        cv2.putText(img, f'Name : {n}', (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                        cv2.putText(img, f'Roll No : {r}', (x, y - 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                        cv2.putText(img, f'Department : {d}', (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                        self.mark_attendance(i, r, n, d)
                        face_recognized = True
                    else:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                        cv2.putText(img, f'Unknown Face', (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                except Exception as e:
                    pass

                coord = [x, y, w, h]
            return coord, face_recognized

        def recognize(img, clf, faceCascade):
            coord, face_recognized = draw_boundry(img=img, classifier=faceCascade, scalefactor=1.1, minNeighbors=10, color=(255, 25, 255), text='Face', clf=clf)
            return img, face_recognized

        # --- SETUP ---
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        clf = cv2.face.LBPHFaceRecognizer.create()
        clf.read('classifier.xml')
        
        # Use 0 for default camera, 1 for external
        video_cap = cv2.VideoCapture(1)

        window_name = "Face Recognition System"
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, 600, 100)

        # --- OBJECT GUARD & SPOOF RECORDING VARIABLES ---
        frame_counter = 0
        consecutive_threat_frames = 0
        threat_threshold = 5
        check_frequency = 1 # Check every  frames normally

        # Recording state
        is_recording_spoof = False
        spoof_writer = None
        spoof_rec_start_time = 0
        closing_pending = False # Flag to close after recording is done

        while True: # ================= OUTER LOOP =================
            
            # Reset checks for the new student cycle
            live_verified = False
            liveness_start_time = time.time()
            
            # --- PHASE 1: LIVENESS & OBJECT GUARD ---
            while not live_verified:
                ret, img = video_cap.read()
                if not ret: break
                
                frame_counter += 1
                current_time = time.time()

                # --- 1. HANDLE SPOOF RECORDING (Always runs if active) ---
                if is_recording_spoof:
                    if spoof_writer is not None:
                        spoof_writer.write(img)
                        # Visual REC indicator
                        h, w, _ = img.shape
                        cv2.circle(img, (w - 50, 50), 10, (0, 0, 255), -1)
                        cv2.putText(img, "REC", (w - 35, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                    # Stop after 2 seconds
                    if current_time - spoof_rec_start_time >= 2:
                        print("Spoof recording saved.")
                        is_recording_spoof = False
                        if spoof_writer is not None:
                            spoof_writer.release()
                            spoof_writer = None
                        
                        # If the alarm triggered a close, we execute it now that video is saved
                        if closing_pending:
                            video_cap.release()
                            cv2.destroyAllWindows()
                            return # EXIT

                # Admin Exit Check (Enter Key) - Only if not in critical closing mode
                if not closing_pending and cv2.waitKey(1) == 13: 
                    video_cap.release()
                    cv2.destroyAllWindows()
                    if spoof_writer: spoof_writer.release()
                    return

                # --- 2. SMART OBJECT GUARD CHECK ---
                # Check every 30 frames OR if we are currently suspicious (threat > 0)
                # If closing is pending, we skip scanning and just finish recording
                should_check = not closing_pending and ((frame_counter % check_frequency == 0) or (consecutive_threat_frames > 0))

                if should_check:
                    blocked_obj = self.object_guard.scan(img)
                    
                    if blocked_obj:
                        consecutive_threat_frames += 1
                        print(f"Warning: {blocked_obj} detected. Strike {consecutive_threat_frames}/5")
                        
                        # A. Start Recording IMMEDIATELY on first suspicion
                        if not is_recording_spoof:
                            is_recording_spoof = True
                            spoof_rec_start_time = current_time
                            if not os.path.exists("spoofing_recordings"):
                                os.makedirs("spoofing_recordings")
                            h, w, _ = img.shape
                            fourcc = cv2.VideoWriter_fourcc(*'XVID')
                            timestamp = int(current_time)
                            spoof_writer = cv2.VideoWriter(f"spoofing_recordings/spoof_{timestamp}.avi", fourcc, 20.0, (w, h))

                        # B. Visual Warning
                        cv2.putText(img, f"WARNING: {blocked_obj}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        # C. ALARM & CLOSE CONDITION (5 Continuous Frames)
                        if consecutive_threat_frames >= threat_threshold:
                            print("CRITICAL: Blocked object confirmed. Alarm triggered.")
                            
                            # Trigger Alarm
                            threading.Thread(target=self.play_alarm, daemon=True).start()
                            
                            # Set flag to close window AFTER recording finishes
                            closing_pending = True
                            
                            # Show Access Denied UI
                            cv2.putText(img, "ACCESS DENIED - CLOSING", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                            
                    else:
                        # Reset if check passed (and we aren't already closing)
                        consecutive_threat_frames = 0
                
                # If closing is pending, show the denial screen and loop until recording finishes
                if closing_pending:
                    cv2.putText(img, "ACCESS DENIED - SYSTEM LOCKED", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow(window_name, img)
                    # We continue the loop; the recording logic at the top will handle the exit
                    continue

                # --- 3. LIVENESS CHECK (Only if safe) ---
                is_live, face_rect, message = self.liveness_detector.detect_liveness(img)
                
                # Timeout logic for Liveness
                if time.time() - liveness_start_time > 20: 
                    cv2.putText(img, "Time Limit - Resetting...", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow(window_name, img)
                    cv2.waitKey(2000)
                    break 

                if is_live:
                    live_verified = True
                    cv2.putText(img, "Liveness Verified.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow(window_name, img)
                    cv2.waitKey(500) 
                else:
                    if face_rect is not None:
                        x, y, w, h = face_rect
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(img, "Please Blink/Move for Liveness", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(img, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow(window_name, img)

            if closing_pending: return # Double check exit
            if not live_verified: continue

            # --- PHASE 2: RECOGNITION ---
            recog_start_time = time.time()
            student_processed = False

            while not student_processed:
                ret, img = video_cap.read()
                if not ret: break

                img, face_recognized = recognize(img, clf, faceCascade)
                
                cv2.putText(img, "Admin: Press Enter to Exit", (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                if face_recognized:
                    cv2.putText(img, "ATTENDANCE MARKED", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                    cv2.imshow(window_name, img)
                    cv2.waitKey(2000) # Show success for 2 seconds
                    student_processed = True 
                
                else:
                    cv2.imshow(window_name, img)

                # Timeout logic for Recognition
                if time.time() - recog_start_time > 10:
                    cv2.putText(img, "Timeout - Resetting", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow(window_name, img)
                    cv2.waitKey(1000)
                    student_processed = True 

                # Admin Exit
                if cv2.waitKey(1) == 13: 
                    video_cap.release()
                    cv2.destroyAllWindows()
                    return

        video_cap.release()
        cv2.destroyAllWindows()

    def play_alarm(self):
        try:
            import winsound
            winsound.Beep(1200, 1000)
        except ImportError:
            print("Alarm triggered! (winsound not available)")

    def back(self):
        self.root.destroy()

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time) 

       
if __name__ == '__main__':
    root=Tk()
    obj=face_recognition(root)
    root.mainloop()