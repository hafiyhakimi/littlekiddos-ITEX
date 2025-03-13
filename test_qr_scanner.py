"""
This is to do functional test to QR scanner ability of the camera

@author
Salman H.
"""

import cv2
import unittest
from pyzbar.pyzbar import decode
from qrScanner import scan  # Import the function from your QR scanner module

class TestQRScanner(unittest.TestCase):
    def test_qr_scanner(self):
        """Test if the QR scanner correctly detects and decodes a QR code."""
        # Load a test image with a known QR code
        test_image = cv2.imread('test_qr.png')  # Replace with a real QR code image

        # Ensure the image is loaded
        self.assertIsNotNone(test_image, "Test QR image could not be loaded.")

        # Decode QR code from the image
        decoded_objects = decode(test_image)

        # Ensure at least one QR code is detected
        self.assertGreater(len(decoded_objects), 0, "No QR codes detected.")

        # Extract the decoded text
        qr_text = decoded_objects[0].data.decode('utf-8')

        # Expected QR code content (change this to match your test QR)
        expected_text = "Lfgggggggg!!!"

        # Assert the decoded text is correct
        self.assertEqual(qr_text, expected_text, "QR code content does not match expected value.")

if __name__ == '__main__':
    unittest.main()
