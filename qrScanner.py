"""
This file is for scanning QR code from the camera, and returning the decoded value
@author
Salman H.
"""
import cv2
import time
from pyzbar.pyzbar import decode
import threading

class QRScanner:
    def __init__(self, camera):
        """Initialize the QR scanner with a camera instance"""
        self.camera = camera
        self.last_scan_time = 0
        self.scan_cooldown = 0.5  # Reduced cooldown for more frequent scans
        self.last_code = None

        # Start scanning thread for continuous detection
        self.running = True
        self.scan_thread = threading.Thread(target=self._continuous_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def _continuous_scan(self):
        """Continuously scan QR codes in a background thread"""
        while self.running:
            result = self._process_frame()
            if result:
                self.last_code = result
            time.sleep(0.1)  # Check every 100ms

    def _process_frame(self):
        """Process a frame to detect QR codes with enhanced detection"""
        # Get the current frame
        frame = self.camera.get_raw_frame()
        if frame is None:
            return None

        # Apply image processing to improve QR detection
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # Try multiple processing methods
            detection_images = [
                gray,                          # Original grayscale
                thresh,                         # Thresholded
                cv2.GaussianBlur(gray, (5, 5), 0)  # Blurred to reduce noise
            ]

            # Try to detect QR in each processed image
            for img in detection_images:
                # Scan for QR codes
                qr_codes = decode(img)

                if qr_codes:
                    for qr in qr_codes:
                        # Update last scan time
                        self.last_scan_time = time.time()

                        # Return the QR code data
                        return qr.data.decode('utf-8')

            # If we reach here, no QR code was found in any processed image
            return None

        except Exception as e:
            print(f"Error in QR processing: {e}")
            return None

    def scan_qr_code(self):
        """Return last detected QR code, with cooldown"""
        current_time = time.time()

        # If we're in cooldown and have a code, return it
        if current_time - self.last_scan_time < self.scan_cooldown and self.last_code:
            return self.last_code

        # Otherwise, force a new scan
        result = self._process_frame()
        if result:
            self.last_code = result
            self.last_scan_time = current_time

        return self.last_code

    def stop(self):
        """Stop the scanning thread"""
        self.running = False
        if self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1.0)