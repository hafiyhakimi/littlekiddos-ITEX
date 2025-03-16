"""
This is to do functional test to QR scanner ability of the camera

@author
Salman H.
"""

import unittest
import numpy as np
from qrScanner import QRScanner  # Ensure we are actually testing this module

class TestQRScanner(unittest.TestCase):
    def setUp(self):
        """Initialize QR scanner before each test"""
        self.qr_scanner = QRScanner()

    def test_detect_qr_code(self):
        result = self.qr_scanner.scan_from_camera()
        if result:
            print(f"📜 Final QR Code Data: {result}")
        else:
            print("⚠️ No QR code detected.")

    def test_no_qr_code(self):
        """Test when no QR code is present in an image"""
        # Create a blank image (no QR code)
        blank_image = np.zeros((500, 500, 3), dtype=np.uint8)

        # Run the QR scanner
        decoded_text = self.qr_scanner.scan_qr_code(blank_image)

        # Expect no QR code to be detected
        self.assertIsNone(decoded_text, "❌ QR scanner detected a QR code when none was present!")

if __name__ == "__main__":
    unittest.main()
