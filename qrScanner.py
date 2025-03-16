"""
This file is for scanning QR code from the camera, and returning the decoded value

@author
Salman H.
"""

import cv2
from pyzbar.pyzbar import decode
from camera import Camera
import os
import time

class QRScanner:
    def __init__(self):
        """Initialize the QR scanner and camera."""
        self.camera = Camera()

    def is_display_available(self):
        """Check if a display is available (for headless systems)."""
        return "DISPLAY" in os.environ or os.environ.get('WAYLAND_DISPLAY') is not None

    def scan_qr_code(self, frame):
        """
        Detects and decodes a QR code from a given frame.
        :param frame: Image frame from which to detect QR code.
        :return: Decoded QR code text if found, else None.
        """
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
                break  # Exit once a QR code is found

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # time.sleep(max(0, 0.1 - (time.time() - start_time)))

        self.camera.release()  # Release camera properly
        cv2.destroyAllWindows()
        return qr_data
