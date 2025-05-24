import cv2
import numpy as np
import time
import random

class LivenessDetector:
    def __init__(self):
        # Load face detector
        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Load eye detector
        self.eye_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        # Load smile detector
        self.smile_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Challenge states
        self.challenge_active = False
        self.challenge_completed = False
        self.challenge_type = None 
        self.challenge_start_time = None
        self.challenge_timeout = 5  # seconds
        
        # Tracking variables
        self.prev_eyes_count = 0
        self.current_eyes_count = 0
        self.blink_detected = False
        self.blink_count = 0
        self.prev_face_center = None
        self.movement_threshold = 15
        self.prev_smile_count = 0
    
    def detect_blink(self, frame, face_rect):
        """Detect eye blinks by tracking eye presence"""
        x, y, w, h = face_rect
        face_roi = frame[y:y+h, x:x+w]
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Detect eyes
        eyes = self.eye_detector.detectMultiScale(gray_roi, 1.1, 5, minSize=(30, 30))
        
        # Update eye count
        self.prev_eyes_count = self.current_eyes_count
        self.current_eyes_count = len(eyes)
        
        # Logic for blink detection
        # If we had eyes before, but now we don't (or have fewer), then likely a blink occurred
        if (self.prev_eyes_count >= 2 and self.current_eyes_count < self.prev_eyes_count):
            self.blink_detected = True
            self.blink_count += 1
            return True
        
        return False
    
    def detect_head_movement(self, face_rect):
        """Detect if the head has moved significantly"""
        if face_rect is None or self.prev_face_center is None:
            if face_rect is not None:
                x, y, w, h = face_rect
                self.prev_face_center = (x + w//2, y + h//2)
            return False
        
        # Calculate current face center
        x, y, w, h = face_rect
        current_center = (x + w//2, y + h//2)
        
        # Calculate distance moved
        distance = np.sqrt((current_center[0] - self.prev_face_center[0])**2 + 
                          (current_center[1] - self.prev_face_center[1])**2)
        
        # Update previous center
        self.prev_face_center = current_center
        
        # Return true if movement exceeds threshold
        return distance > self.movement_threshold
    
    def detect_smile(self, frame, face_rect):
        """Detect if the person is smiling"""
        x, y, w, h = face_rect
        face_roi = frame[y:y+h, x:x+w]
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Lower part of the face
        smile_roi = gray_roi[int(h/2):h, :]
        
        # Detect smiles
        smiles = self.smile_detector.detectMultiScale(
            smile_roi, 
            scaleFactor=1.1,
            minNeighbors=10,
            minSize=(25, 15),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Logic to prevent constant smile detection
        current_smile_count = len(smiles)
        smile_detected = current_smile_count > self.prev_smile_count
        self.prev_smile_count = current_smile_count
        
        return smile_detected and current_smile_count > 0
    
    def check_texture_variation(self, face_region):
        """Check for texture variation in the face region (real faces have more variation than printed photos)"""
        # Convert to grayscale
        if len(face_region.shape) > 2:
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray_face = face_region
            
        # Apply Laplacian for edge detection
        laplacian = cv2.Laplacian(gray_face, cv2.CV_64F)
        
        # Calculate variance of Laplacian (higher for real faces with more texture)
        variance = laplacian.var()
        
        # Threshold for texture variation (adjust based on testing)
        return variance > 120  # Higher threshold for clearer distinction
    
    def detect_reflections(self, face_region):
        """Detect light reflections that would be present on a real face but not on a photo"""
        # Convert to HSV for better handling of brightness
        hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
        
        # Extract value channel (brightness)
        _, _, v = cv2.split(hsv)
        
        # Threshold to find bright regions (reflections)
        _, thresh = cv2.threshold(v, 200, 255, cv2.THRESH_BINARY)
        
        # Count white pixels (reflections)
        reflection_pixels = cv2.countNonZero(thresh)
        
        # Calculate percentage of reflection pixels
        total_pixels = face_region.shape[0] * face_region.shape[1]
        reflection_percentage = reflection_pixels / total_pixels * 100
        
        # Real faces typically have some natural light reflections
        return 0.1 < reflection_percentage <18  # Adjust thresholds as needed
    
    def issue_challenge(self):
        """Issue a random liveness challenge to the user"""
        challenges = ["blink", "move_head", "smile"]
        self.challenge_type = random.choice(challenges)
        self.challenge_active = True
        self.challenge_completed = False
        self.challenge_start_time = time.time()
        
        # Reset tracking variables based on challenge
        if self.challenge_type == "blink":
            self.blink_detected = False
            self.blink_count = 0
        elif self.challenge_type == "move_head":
            # We'll keep the previous face center to detect movement
            pass
        elif self.challenge_type == "smile":
            self.prev_smile_count = 0
            
        return self.challenge_type
    
    def check_challenge_completion(self, frame, face_rect):
        """Check if the user has completed the active challenge"""
        if not self.challenge_active or face_rect is None:
            return False
            
        # Check for timeout
        if time.time() - self.challenge_start_time > self.challenge_timeout:
            self.challenge_active = False
            return False
            
        # Check based on challenge type
        if self.challenge_type == "blink":
            if self.detect_blink(frame, face_rect):
                self.challenge_completed = True
                self.challenge_active = False
                return True
                
        elif self.challenge_type == "move_head":
            if self.detect_head_movement(face_rect):
                self.challenge_completed = True
                self.challenge_active = False
                return True
                
        elif self.challenge_type == "smile":
            if self.detect_smile(frame, face_rect):
                self.challenge_completed = True
                self.challenge_active = False
                return True
                
        return False
    
    def detect_liveness(self, frame):
        """Main liveness detection function
        
        Args:
            frame: BGR image from camera
            
        Returns:
            is_live: Boolean indicating if a live person is detected
            face_rect: Rectangle coordinates of detected face
            message: Status message for display
        """
        # Initialize variables
        is_live = False
        message = "No face detected"
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return is_live, None, message
        
        # Use the largest face detected
        face_rect = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = face_rect
        
        # Extract face region
        face_region = frame[y:y+h, x:x+w]
        
        # Run static checks first
        texture_check = self.check_texture_variation(face_region)
        reflection_check = self.detect_reflections(face_region)
        
        # If static checks pass, proceed to challenges
        if texture_check and reflection_check:
            if not self.challenge_active and not self.challenge_completed:
                # Issue a new challenge
                challenge = self.issue_challenge()
                challenge_text = challenge.replace('_', ' ')
                message = f"Please {challenge_text} to verify liveness"
            elif self.challenge_active:
                # Check if challenge is completed
                if self.check_challenge_completion(frame, face_rect):
                    is_live = True
                    message = "Liveness confirmed!"
                else:
                    challenge_text = self.challenge_type.replace('_', ' ')
                    message = f"Continue to {challenge_text}"
            elif self.challenge_completed:
                # Challenge was already completed
                is_live = True
                message = "Liveness confirmed!"
        else:
            if not texture_check and not reflection_check:
                message = "Failed texture and reflection checks - likely a photo"
            elif not texture_check:
                message = "Failed texture check - likely a photo"
            else:
                message = "Failed reflection check - likely a photo"
        
        return is_live, face_rect, message


def main():
    """Main function to run the liveness detection demo"""
    detector = LivenessDetector()
    cap = cv2.VideoCapture(1)

    # start_time = time.time()  # Start the timer

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Check if 10 seconds have passed
        # if time.time() - start_time > 30:
        #     print("Time limit reached. Exiting...")
        #     break

        is_live, face_rect, message = detector.detect_liveness(frame)

        if face_rect is not None:
            x, y, w, h = face_rect
            color = (0, 255, 0) if is_live else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        cv2.putText(frame, 'Liveness Detection', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Liveness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exit key pressed. Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
