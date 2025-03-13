"""
This file is for handling the live feed from the camera

@author
Salman H.
"""

import cv2
import threading
import time

class Camera:
    def __init__(self, camera_index=0):
        """Initialize the camera."""
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            raise Exception("❌ Error: Could not open camera.")

        self.frame = None
        self.running = True

        # Wait up to 5 seconds for the first frame
        for _ in range(10):  
            ret, self.frame = self.cap.read()
            if ret:
                print("✅ First frame captured!")
                break
            time.sleep(0.5)  # Wait 500ms between retries
        else:
            raise Exception("❌ Error: No frame received after 5 seconds.")

        # Start background thread
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        """Continuously capture frames in a separate thread."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            else:
                print("❌ No frame captured!")

    def get_frame(self):
        """Return the latest frame as a JPEG byte array."""
        if self.frame is None:
            print("⚠️ Warning: No frame available yet!")
            return None  

        print(f"📷 Original Frame shape: {self.frame.shape}")

        # Ensure the frame is resized to a fixed resolution
        resized_frame = cv2.resize(self.frame, (640, 480))

        print(f"📷 Resized Frame shape: {resized_frame.shape}")

        success, buffer = cv2.imencode('.jpg', resized_frame)  
        if not success:
            print("❌ Error: Frame encoding failed!")
            return None  

        return buffer.tobytes()

    def release(self):
        """Release the camera."""
        self.running = False
        self.thread.join()
        self.cap.release()
        print("Camera released.")
