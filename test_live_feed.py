"""
A test script to do funtional test on the live feed feature

@author
Salman H.
"""

import unittest
import cv2
from camera import Camera

class TestLiveFeed(unittest.TestCase):
    
    def test_camera_stream(self):
        cam = Camera()

        frame =cam.get_frame()

        self.assertIsNotNone(frame, "No frame received from the camera.")

        self.assertGreater(len(frame), 0, "Captured frame is empty.")

        cam.release() 

if __name__ == '__main__':
    unittest.main()
