from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2.face
from student import students
from train import train
from config import get_db_connection
import os
import cv2
import time
from time import strftime
from datetime import datetime
from liveness import LivenessDetector
from object_guard import ObjectGuard
import threading
from utils import resource_path

class face_recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(True, True)
        self.root.minsize(1024, 600)
        self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))

        self.title_lbl = Label(self.root, text='FACE RECOGNITION', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(relx=0, rely=0, relwidth=1.0, relheight=0.065)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red', borderwidth=0, highlightthickness=0)
        self.time_lbl.place(relx=0, rely=0, relwidth=0.09, relheight=0.065)
        self.update_time()

        # Back Button
        self.back_btn = Button(self.root, text="Back", width=22, cursor='hand2', font=('times new roman', 10, 'bold'), bg='red', fg='white', activebackground="green", command=self.back)
        self.back_btn.place(relx=0.85, rely=0.013, relwidth=0.12, relheight=0.039)

        # Left Image
        self.org_img_top = Image.open(resource_path("college_images\\face_detector1.jpg"))
        self.photoimg_top = ImageTk.PhotoImage(self.org_img_top.resize((560, 635), Image.Resampling.LANCZOS))
        
        self.f_lbl = Label(self.root, image=self.photoimg_top)
        self.f_lbl.place(relx=0, rely=0.065, relwidth=0.41, relheight=0.935)

        # Right Image
        self.org_img_bottom = Image.open(resource_path("college_images\\register.jpg"))
        self.photoimg_bottom = ImageTk.PhotoImage(self.org_img_bottom.resize((800, 635), Image.Resampling.LANCZOS))

        self.f_lbl1 = Label(self.root, image=self.photoimg_bottom)
        self.f_lbl1.place(relx=0.41, rely=0.065, relwidth=0.59, relheight=0.935)

        # Buttons
        self.b1 = Button(self.root, text='FACE RECOGNITION', cursor='hand2', font=('times new roman', 15, 'bold'), activebackground='yellow', activeforeground='blue', bg='green', fg='red', command=self.face_recog)
        self.b1.place(relx=0.622, rely=0.897, relwidth=0.153, relheight=0.056)

        self.b2 = Button(self.root, text='Recordings', cursor='hand2', font=('times new roman', 15, 'bold'), activebackground='yellow', activeforeground='blue', bg='blue', fg='white', command=self.open_recordings)
        self.b2.place(relx=0.435, rely=0.897, relwidth=0.153, relheight=0.056)

        # Resize Binding
        self.resize_timer = None
        self.root.bind("<Configure>", self.on_resize)

        # --- BUG FIX #3: Initialize Cache ---
        self.student_cache = {}
        self.load_student_data_cache()

        # --- PRE-LOAD MODELS ---
        from loading import LoadingSplash
        self.loading_splash = LoadingSplash(self.root, "Initializing Security Models...")
        
        # Load heavy models in a background thread so splash spinner keeps animating
        threading.Thread(target=self.init_models_in_background, daemon=True).start()

    def init_models_in_background(self):
        try:
            self.object_guard = ObjectGuard()
            self.loading_splash.update_message("Loading Liveness Detector...")
            self.liveness_detector = LivenessDetector()
        except Exception as e:
            print(f"Error loading models: {e}")
        finally:
            self.root.after(0, self._destroy_splash)

    def _destroy_splash(self):
        if hasattr(self, 'loading_splash'):
            self.loading_splash.destroy()

    # --- BUG FIX #3: Cache Loading Function ---
    def load_student_data_cache(self):
        """Fetches all students once to prevent DB lag during recognition."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Student_id, Student_name, Roll, Dep FROM student")
            rows = cursor.fetchall()
            for row in rows:
                # Key: Student_id (string), Value: Dict of details
                self.student_cache[str(row[0])] = {
                    "name": row[1],
                    "roll": row[2],
                    "dep": row[3]
                }
            conn.close()
            print("Student data cached successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not cache student data: {e}")

    # --- BUG FIX #2: Corrected Parameter Order ---
    def mark_attendance(self, i, n, r, d):
        try:
            conn = get_db_connection()
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
            # --- BUG FIX #4: No silent exceptions ---
            print(f"Error in marking attendance: {e}")

    def open_recordings(self):
        try:
            # --- BUG FIX #10: Robust Path handling ---
            path = resource_path("spoofing_recordings")
            if not os.path.exists(path):
                os.makedirs(path)
            os.startfile(os.path.abspath(path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open recordings folder: {e}")

    def face_recog(self):
        # Refresh cache on start to get new students
        self.load_student_data_cache()
        
        self.session_marked = set()
        self.face_tracks = {}
        self.next_track_id = 0
        self.current_frame = 0
        
        IOU_THRESHOLD = 0.3
        REQUIRED_FRAMES = 7
        CONFIDENCE_THRESHOLD = 80
        TRACK_TIMEOUT = 10
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        def calculate_iou(box1, box2):
            x1, y1, w1, h1 = box1
            x2, y2, w2, h2 = box2
            xi1 = max(x1, x2)
            yi1 = max(y1, y2)
            xi2 = min(x1 + w1, x2 + w2)
            yi2 = min(y1 + h1, y2 + h2)
            
            if xi2 <= xi1 or yi2 <= yi1: return 0.0
            
            inter_area = (xi2 - xi1) * (yi2 - yi1)
            union_area = (w1 * h1) + (w2 * h2) - inter_area
            return inter_area / union_area if union_area > 0 else 0.0
        
        def get_majority_vote(predictions):
            if not predictions: return None
            
            id_counts = {}
            id_data = {}
            
            for pred_id, name, roll, dep, conf in predictions:
                if pred_id not in id_counts:
                    id_counts[pred_id] = 0
                    id_data[pred_id] = {'name': name, 'roll': roll, 'dep': dep, 'total_conf': 0}
                id_counts[pred_id] += 1
                id_data[pred_id]['total_conf'] += conf
            
            sorted_ids = sorted(id_counts.keys(), 
                key=lambda x: (id_counts[x], id_data[x]['total_conf'] / id_counts[x]), 
                reverse=True)
            
            if not sorted_ids: return None
            
            best_id = sorted_ids[0]
            best_count = id_counts[best_id]
            best_avg_conf = id_data[best_id]['total_conf'] / best_count
            
            is_ambiguous = False
            if len(sorted_ids) > 1:
                second_id = sorted_ids[1]
                second_count = id_counts[second_id]
                if best_count - second_count <= 2 and best_count > 0:
                    is_ambiguous = True
            
            return (best_id, id_data[best_id]['name'], id_data[best_id]['roll'], 
                    id_data[best_id]['dep'], best_count, best_avg_conf, is_ambiguous)
        
        def find_matching_track(bbox):
            best_track_id = None
            best_iou = IOU_THRESHOLD
            for track_id, track_data in self.face_tracks.items():
                iou = calculate_iou(bbox, track_data['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_track_id = track_id
            return best_track_id

        def draw_boundry(img, classifier, scalefactor, minNeighbors, color, text, clf):
            gray_images = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray_images, scalefactor, minNeighbors)
            detected_track_ids = set()
            coord = []
            faces_in_frame = 0

            for (x, y, w, h) in features:
                bbox = (x, y, w, h)
                
                # --- BUG FIX #7: ROI Size Validation ---
                face_roi = gray_images[y:y + h, x:x + w]
                if face_roi.size == 0 or w < 20 or h < 20:
                    continue

                face_roi_normalized = clahe.apply(face_roi)
                
                try:
                    id, predict = clf.predict(face_roi_normalized)
                    
                    # --- BUG FIX #6: Clamp Confidence ---
                    raw_conf = 100 * (1 - predict / 300)
                    confidence = int(max(0, min(100, raw_conf)))

                    # --- BUG FIX #3: Use Cache instead of DB ---
                    str_id = str(id)
                    if str_id in self.student_cache:
                        data = self.student_cache[str_id]
                        n = data['name']
                        r = data['roll']
                        d = data['dep']
                        i = str_id
                    else:
                        n = "Unknown"
                        r = ""
                        d = ""
                        i = str_id

                    if confidence > CONFIDENCE_THRESHOLD:
                        track_id = find_matching_track(bbox)
                        if track_id is None:
                            track_id = self.next_track_id
                            self.next_track_id += 1
                            self.face_tracks[track_id] = {
                                'bbox': bbox,
                                'predictions': [],
                                'last_seen': self.current_frame
                            }
                        
                        self.face_tracks[track_id]['bbox'] = bbox
                        self.face_tracks[track_id]['predictions'].append((i, n, r, d, confidence))
                        self.face_tracks[track_id]['last_seen'] = self.current_frame
                        detected_track_ids.add(track_id)
                        
                        vote_result = get_majority_vote(self.face_tracks[track_id]['predictions'])
                        if vote_result:
                            display_id, display_name, display_roll, display_dep, vote_count, avg_conf, is_ambiguous = vote_result
                            
                            if is_ambiguous:
                                box_color = (0, 255, 255)
                                status_text = "Verifying..."
                            else:
                                box_color = (0, 255, 0)
                                status_text = f"[{vote_count}/{REQUIRED_FRAMES}]"
                            
                            cv2.rectangle(img, (x, y), (x + w, y + h), box_color, 2)
                            cv2.putText(img, f'ID : {display_id}', (x, y - 75), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                            cv2.putText(img, f'Name : {display_name}', (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                            cv2.putText(img, f'Roll : {display_roll}', (x, y - 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                            cv2.putText(img, f'Dept : {display_dep} {status_text}', (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                            
                            if vote_count >= REQUIRED_FRAMES and not is_ambiguous:
                                if display_id not in self.session_marked:
                                    total_preds = len(self.face_tracks[track_id]['predictions'])
                                    required_ratio = 0.7
                                    if vote_count / total_preds >= required_ratio:
                                        # --- BUG FIX #2: Fixed parameter order in call ---
                                        self.mark_attendance(display_id, display_name, display_roll, display_dep)
                                        self.session_marked.add(display_id)
                                        print(f"✓ Marked: {display_name}")
                        faces_in_frame += 1
                    else:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                        cv2.putText(img, f'Unknown Face', (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                
                except Exception as e:
                    # --- BUG FIX #4: Log exceptions ---
                    print(f"Prediction Error: {e}")

                coord = [x, y, w, h]
            
            stale_tracks = [tid for tid, data in self.face_tracks.items() 
                          if self.current_frame - data['last_seen'] > TRACK_TIMEOUT]
            for tid in stale_tracks:
                del self.face_tracks[tid]
            
            return coord, faces_in_frame, detected_track_ids

        def recognize(img, clf, faceCascade):
            coord, count, ids = draw_boundry(img=img, classifier=faceCascade, scalefactor=1.1, minNeighbors=10, color=(255, 25, 255), text='Face', clf=clf)
            return img, count, ids

        # --- SETUP ---
        # --- BUG FIX #10: Resource Path ---
        faceCascade = cv2.CascadeClassifier(resource_path('haarcascade_frontalface_default.xml'))
        clf = cv2.face.LBPHFaceRecognizer.create()
        clf.read(resource_path('classifier.xml'))
        
        video_cap = cv2.VideoCapture(1) # Try 0 if 1 fails

        window_name = "Face Recognition System"
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, 600, 100)

        frame_counter = 0
        consecutive_threat_frames = 0
        threat_threshold = 5
        check_frequency = 1 

        is_recording_spoof = False
        spoof_writer = None
        spoof_rec_start_time = 0
        closing_pending = False 

        while True: 
            live_verified = False
            liveness_start_time = time.time()
            
            # --- PHASE 1: LIVENESS & OBJECT GUARD ---
            while not live_verified:
                ret, img = video_cap.read()
                if not ret: break
                
                frame_counter += 1
                current_time = time.time()
                
                # --- BUG FIX #5: Single waitKey call ---
                key_input = cv2.waitKey(1) & 0xFF

                if is_recording_spoof:
                    if spoof_writer is not None:
                        spoof_writer.write(img)
                        h, w, _ = img.shape
                        cv2.circle(img, (w - 50, 50), 10, (0, 0, 255), -1)
                        cv2.putText(img, "REC", (w - 35, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                    if current_time - spoof_rec_start_time >= 2:
                        print("Spoof recording saved.")
                        is_recording_spoof = False
                        if spoof_writer is not None:
                            spoof_writer.release()
                            spoof_writer = None
                        if closing_pending:
                            video_cap.release()
                            cv2.destroyAllWindows()
                            return 

                if not closing_pending and key_input == 13: 
                    video_cap.release()
                    cv2.destroyAllWindows()
                    if spoof_writer: spoof_writer.release()
                    return

                should_check = not closing_pending and ((frame_counter % check_frequency == 0) or (consecutive_threat_frames > 0))

                if should_check:
                    blocked_obj = self.object_guard.scan(img)
                    if blocked_obj:
                        consecutive_threat_frames += 1
                        if not is_recording_spoof:
                            is_recording_spoof = True
                            spoof_rec_start_time = current_time
                            save_path = resource_path("spoofing_recordings")
                            if not os.path.exists(save_path): os.makedirs(save_path)
                            h, w, _ = img.shape
                            fourcc = cv2.VideoWriter_fourcc(*'XVID')
                            timestamp = int(current_time)
                            spoof_writer = cv2.VideoWriter(os.path.join(save_path, f"spoof_{timestamp}.avi"), fourcc, 20.0, (w, h))

                        cv2.putText(img, f"WARNING: {blocked_obj}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        if consecutive_threat_frames >= threat_threshold:
                            threading.Thread(target=self.play_alarm, daemon=True).start()
                            closing_pending = True
                            cv2.putText(img, "ACCESS DENIED - CLOSING", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    else:
                        consecutive_threat_frames = 0
                
                if closing_pending:
                    cv2.putText(img, "ACCESS DENIED - SYSTEM LOCKED", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow(window_name, img)
                    continue

                is_live, face_rect, message = self.liveness_detector.detect_liveness(img)
                
                # --- BUG FIX #9: Liveness Timeout Feedback ---
                if time.time() - liveness_start_time > 20: 
                    cv2.putText(img, "Timeout!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow(window_name, img)
                    cv2.waitKey(1000)
                    messagebox.showwarning("Timeout", "Liveness check failed due to timeout.")
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

            if closing_pending: return 
            if not live_verified: continue

            # --- PHASE 2: RECOGNITION (Continuous) ---
            last_face_seen_time = time.time()
            
            # --- BUG FIX #8: Session reset hint ---
            # session_marked is local to this function, so it resets every time 'face_recog' is called.
            # However, if we want a timeout reset within the loop:
            session_start_time = time.time()

            while (time.time() - last_face_seen_time < 10):
                ret, img = video_cap.read()
                if not ret: break
                
                self.current_frame += 1

                img, count, current_ids = recognize(img, clf, faceCascade)
                
                if count > 0:
                    last_face_seen_time = time.time()
                    cv2.putText(img, f"Faces: {count}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, f"Session Marks: {len(self.session_marked)}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                     cv2.putText(img, "Scanning...", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                cv2.putText(img, "Admin: Press Enter to Exit", (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.imshow(window_name, img)

                # --- BUG FIX #5: Single waitKey call ---
                key_input = cv2.waitKey(1) & 0xFF
                if key_input == 13: 
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

    def on_resize(self, event):
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_layout_images)

    def update_layout_images(self):
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        if win_w < 100 or win_h < 100: return
        
        img_h = int(win_h * 0.935)
        w_left = int(win_w * 0.41)
        
        if hasattr(self, 'f_lbl') and hasattr(self, 'org_img_top'):
            try:
                resized = self.org_img_top.resize((w_left, img_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                self.f_lbl.config(image=photo)
                self.f_lbl.image = photo 
            except: pass
            
        w_right = win_w - w_left
        if hasattr(self, 'f_lbl1') and hasattr(self, 'org_img_bottom'):
             try:
                resized = self.org_img_bottom.resize((w_right, img_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                self.f_lbl1.config(image=photo)
                self.f_lbl1.image = photo 
             except: pass

        if hasattr(self, 'title_lbl'): self.title_lbl.lift()
        if hasattr(self, 'time_lbl'): self.time_lbl.lift()
        if hasattr(self, 'back_btn'): self.back_btn.lift()
        if hasattr(self, 'b1'): self.b1.lift()
        if hasattr(self, 'b2'): self.b2.lift()
        
        self.root.update_idletasks()

if __name__ == '__main__':
    root = Tk()
    obj = face_recognition(root)
    root.mainloop()