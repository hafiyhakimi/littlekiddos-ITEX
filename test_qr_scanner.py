"""
This is to do functional test to QR scanner ability of the camera

@author
Salman H.
"""

import unittest
import numpy as np
import cv2
from qrScanner import QRScanner

class TestQRScanner(unittest.TestCase):
    def setUp(self):
        """Initialize QR scanner before each test"""
        self.qr_scanner = QRScanner(use_camera=False)

    # def test_detect_qr_code(self):
    #     result = self.qr_scanner.scan_from_camera()
    #     if result:
    #         print(f"📜 Final QR Code Data: {result}")
    #     else:
    #         print("⚠️ No QR code detected.")

    def test_detect_qr_code(self):
        """Test QR code detection from a sample image"""

        sample_qr_code = cv2.imread("test_qr.png")
        self.assertIsNotNone(sample_qr_code, "❌ Error: Test image not found!")

        decoded_text = self.qr_scanner.decode_qr_from_frame(sample_qr_code)
        
        # Expected output from the QR code
        expected_text = "Lfgggggggg!!!"  # Change this based on your actual QR code
        self.assertEqual(decoded_text, expected_text, "❌ QR code was not correctly decoded!")

    def test_no_qr_code(self):
        """Test when no QR code is present in an image"""

        blank_image = np.zeros((500, 500, 3), dtype=np.uint8)

        # Run the QR scanner
        decoded_text = self.qr_scanner.decode_qr_from_frame(blank_image)

        # Expect no QR code to be detected
        self.assertIsNone(decoded_text, "❌ QR scanner detected a QR code when none was present!")

if __name__ == "__main__":
    unittest.main()
