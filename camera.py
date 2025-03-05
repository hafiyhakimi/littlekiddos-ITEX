"""
This file is for handling the live feed from the camera

@author
Salman H.
"""

import cv2

class Camera:
    def __init__(self, src=0):
        """Initialize the camera."""
        self.cap = cv2.VideoCapture(src)

    def get_frame(self):
        """Capture a single frame and return it as a JPEG-encoded byte stream."""
        success, frame = self.cap.read()
        if success:
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        return None

    def release(self):
        """Release the camera resource when done."""
        self.cap.release()
