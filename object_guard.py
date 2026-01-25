# object_guard.py
from ultralytics import YOLO
import torch
import numpy as np

class ObjectGuard:
    def __init__(self):
        # Configure torch threads for efficiency
        torch.set_num_threads(4)

        # Load model once during initialization
        print("Loading Object Guard Model...")
        self.model = YOLO("yolov8n.pt")
        self.model.fuse()

        # Run a dummy inference to warm up the model (prevents lag on first real frame)
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        self.model(dummy, verbose=False)
        print("Object Guard Model Loaded and Ready.")

        # BLOCKED OBJECTS (COCO IDs)
        # 67: cell phone, 63: laptop, 73: book, 62: tv/monitor
        self.blocked_classes = {
             67: "mobile phone",
             63: "laptop",
             62: "computer monitor / screen",
             73: "book/paper"
        }

    def scan(self, frame):
        """
        Scans a single frame and returns the name of a blocked object if found.
        Returns None if safe.
        """
        results = self.model(frame, conf=0.45, iou=0.5, device="cpu", verbose=False)

        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls_id = int(box.cls[0])
                if cls_id in self.blocked_classes:
                    # Return the first blocked object found
                    return self.blocked_classes[cls_id]
        
        return None