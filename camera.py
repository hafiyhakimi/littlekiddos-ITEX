"""
This file is for handling the live feed from the camera

@author
Salman H.
"""

import cv2

class Camera:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)

    def get_frame(self):
        success, frame = self.cap.read()
        if success:
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        return None

    def release(self):
        self.cap.release()
