"""
A test script to do funtional test on the live feed feature

@author
Salman H.
"""

import unittest
import cv2
import time
from camera import Camera

class TestLiveFeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the camera before running tests"""
        cls.camera = Camera()
        time.sleep(2)  # Allow the camera to warm up

    @classmethod
    def tearDownClass(cls):
        """Release the camera after tests"""
        cls.camera.release()
        cv2.destroyAllWindows()

    def test_camera_stream(self):
        """Test if camera is capturing valid frames"""
        frame = self.camera.get_frame()
        self.assertIsNotNone(frame, "No frame received from the camera.")
        self.assertGreater(len(frame), 0, "Frame data is empty.")
        # self.assertGreater(frame.shape[0], 0, "Frame height is 0.")
        # self.assertGreater(frame.shape[1], 0, "Frame width is 0.")

    def test_frame_rate(self):
        """Test if the frame rate is reasonable (at least 10 FPS)"""
        start_time = time.time()
        frame_count = 0

        for _ in range(240):
            frame = self.camera.get_frame()
            if frame is not None:
                frame_count += 1

                cv2.imshow("Live Stream Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit preview early
                    break

        end_time = time.time()
        elapsed_time = end_time - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        print(f"🎥 Measured FPS: {fps:.2f}")
        self.assertGreaterEqual(fps, 10, "FPS is too low!")

if __name__ == "__main__":
    unittest.main()
