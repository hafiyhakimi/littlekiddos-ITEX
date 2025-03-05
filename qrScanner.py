"""
This file is for scanning QR code from the camera, and returning the decoded value

@author
Salman H.
"""

import cv2
from pyzbar.pyzbar import decode

def scan():
    cap = cv2.VideoCapture(0)
    qr_text = None

    while True:
        _, frame = cap.read()
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            qr_text = obj.data.decode('utf-8')
            cap.release()
            return qr_text

    cap.release()
    return None
