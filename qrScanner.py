"""
This file is for scanning QR code from the camera, and returning the decoded value

@author
Salman H.
"""

import cv2
from pyzbar.pyzbar import decode
from camera import Camera

def scan():
    cam = Camera()
    qr_text = None

    while True:
        frame = cam.get_frame()
        if frame is None:
            continue

        # Decode QR code
        decoded_objects = decode(cv2.imdecode(frame, cv2.IMREAD_COLOR))
        for obj in decoded_objects:
            qr_text = obj.data.decode('utf-8')
            cam.release()  # Release camera after scanning
            return qr_text

    cam.release()
    return None
