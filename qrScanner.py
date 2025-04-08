"""
This file is for scanning QR code from the camera, and returning the decoded value

@author
Salman H.
"""

import cv2
from pyzbar.pyzbar import decode
from camera import Camera, DummyCamera
import os
import time

class QRScanner:
    def __init__(self, use_camera=True):
        """Initialize the QR scanner and camera."""
        try:
            self.camera = Camera() if use_camera else None
        except Exception:
            print("⚠️ Camera not available, switching to DummyCamera.")
            self.camera = DummyCamera()

    def is_display_available(self):
        """Check if a display is available (for headless systems)."""
        return "DISPLAY" in os.environ or os.environ.get('WAYLAND_DISPLAY') is not None

    def scan_qr_code(self, frame=None):
        """
        Detects and decodes a QR code from a given frame.
        :param frame: Image frame from which to detect QR code.
        :return: Decoded QR code text if found, else None.
        """
        if frame is None and self.camera:
            frame = self.camera.get_frame()

        if frame is None:
            return None

        if len(frame.shape) == 3:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_frame = frame
        qr_codes = decode(gray_frame)  # Detect QR codes

        if qr_codes:
            qr_data = qr_codes[0].data.decode('utf-8')
            print(f"✅ QR Code Detected: {qr_data}")
            return qr_data  # Return the first detected QR code text

        return None  # No QR code detected

    @staticmethod
    def decode_qr_from_frame(frame):
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            return obj.data.decode("utf-8")
        return None

    def scan_from_camera(self):
        """Continuously scans QR codes from the live camera feed."""
        print("🎥 Starting QR Scanner... Press 'q' to quit.")

        while True:
            start_time = time.time()
            frame = self.camera.get_frame_raw()
            if frame is None:
                print("❌ Error: No frame received!")
                continue  # Try again

            qr_data = self.scan_qr_code(frame)

            display_frame = cv2.resize(frame, (640, 480))

            # Display the frame
            if self.is_display_available():
                cv2.imshow("QR Scanner", display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            if qr_data:
                print(f"✅ Scanned QR Code: {qr_data}")
                return qr_data

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(max(0, 0.1 - (time.time() - start_time)))

    def release(self):
        if self.camera:
            self.camera.release()
