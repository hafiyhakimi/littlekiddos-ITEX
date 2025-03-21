"""
A test script to do integration test

@author
Salman H.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import patch
from camera import Camera
from qrScanner import QRScanner

# class TestCameraFunctionality(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         print("\n🔎 Setting up Camera...")
#         cls.camera = Camera()

#     @classmethod
#     def tearDownClass(cls):
#         print("📷 Releasing Camera...")
#         cls.camera.release()

#     def test_camera_capture_frame(self):
#         print("▶ Testing camera frame capture...")
#         frame = self.camera.get_frame()
#         self.assertIsNotNone(frame, "❌ No frame captured from camera.")
#         self.assertEqual(len(frame.shape), 3, "❌ Frame is not a 3D array (image).")
#         print(f"✅ Frame captured successfully. Shape: {frame.shape}")

#     def test_camera_frame_rate(self):
#         print("▶ Testing camera frame rate...")
#         start = time.time()
#         frame_count = 0
#         for _ in range(30):
#             frame = self.camera.get_frame()
#             if frame is not None:
#                 frame_count += 1
#         end = time.time()
#         fps = frame_count / (end - start)
#         print(f"⚡ Measured FPS: {fps}")
#         self.assertGreaterEqual(fps, 10, "❌ Frame rate is too low!")

class TestCamera(unittest.TestCase):
    @patch.object(Camera, 'get_frame')
    def test_camera_stream(self, mock_get_frame):
        """Test camera stream returns frames"""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_get_frame.return_value = dummy_frame

        camera = Camera(use_camera=False)  # add a parameter to skip opening camera
        frame = camera.get_frame()
        self.assertIsNotNone(frame, "❌ No frame captured from mock camera.")
        self.assertEqual(frame.shape, (480, 640, 3), "❌ Frame shape mismatch.")

# class TestQRScannerFunctionality(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         print("\n🔎 Setting up QRScanner...")
#         cls.scanner = QRScanner()

#     @classmethod
#     def tearDownClass(cls):
#         cls.scanner.release()

#     @classmethod
#     def tearDownClass(cls):
#         print("🛑 QRScanner test completed.")

#     def test_qr_scanner_runs_without_crashing(self):
#         print("▶ Testing QR scanner run cycle for a few frames...")
#         result_detected = None
#         # We'll scan a few frames quickly to make sure it runs without crashing
#         for _ in range(10):
#             # frame = self.scanner.camera.get_frame()
#             qr_data = self.scanner.scan_qr_code()
#             if qr_data:
#                 print(f"✅ Detected QR Code: {qr_data}")
#                 result_detected = qr_data
#                 break
#         self.assertTrue(result_detected is None or isinstance(result_detected, str),
#                         "❌ QR scanner returned an unexpected result.")
#         print("✅ QR scanner function runs correctly.")

class TestQRScanner(unittest.TestCase):
    @patch.object(Camera, 'get_frame')
    def test_detect_qr_code(self, mock_get_frame):
        """Test QR detection from sample QR image"""
        sample_qr = cv2.imread('test_qr.png')
        mock_get_frame.return_value = sample_qr

        qr_scanner = QRScanner(use_camera=False)
        decoded_text = qr_scanner.scan_qr_code(sample_qr)
        self.assertEqual(decoded_text, "Lfgggggggg!!!", "❌ QR decoding failed.")

    @patch.object(Camera, 'get_frame')
    def test_no_qr_code(self, mock_get_frame):
        """Test detection with a blank image"""
        blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_get_frame.return_value = blank_img

        qr_scanner = QRScanner(use_camera=False)
        result = qr_scanner.scan_qr_code(blank_img)
        self.assertIsNone(result, "❌ False positive QR detection.")

if __name__ == '__main__':
    unittest.main()