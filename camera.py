"""
This file is for handling the live feed from the camera
@author
Salman H.
"""
import cv2
import time
import threading
import numpy as np
import subprocess
import tempfile
import os
# from picamera2 import Picamera2

class Camera:
    def __init__(self, width=640, height=480, jpeg_quality=70):
        """Initialize camera using libcamera via subprocess with specified quality
        
        Args:
            width: Width to resize frames to (default: 320)
            height: Height to resize frames to (default: 240)
            jpeg_quality: JPEG compression quality (0-100, default: 70)
        """
        print(f"Initializing camera with size {width}x{height}, quality {jpeg_quality}...")

        # Store quality settings
        self.width = width
        self.height = height
        self.jpeg_quality = jpeg_quality

        # Create a lock for thread-safe access to camera
        self.frame_lock = threading.Lock()
        self.current_frame = None
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "temp_frame.jpg")

        # Start frame capture thread
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        # Wait a moment for first frame
        time.sleep(2)

        print("Camera initialization complete")

    def _capture_frames(self):
        """Continuously capture frames in a background thread using rpicam-jpeg"""
        while self.running:
            try:
                # Use rpicam-jpeg to capture a frame with specified width and height
                subprocess.run([
                    "rpicam-jpeg",
                    "--output", self.temp_file,
                    "--nopreview",
                    "--timeout", "1",
                    "--width", str(self.width * 2),  # Capture at higher res for better QR reading
                    "--height", str(self.height * 2),
                    "--quality", "85"  # Moderate quality for source image
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Read the captured frame
                frame = cv2.imread(self.temp_file)

                if frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame
                    print("Frame captured successfully:", frame.shape)
                else:
                    print("Failed to read captured frame")
            except Exception as e:
                print(f"Error capturing frame: {e}")

            time.sleep(0.017)  # Capture at ~10 FPS to avoid overloading the system

    def get_frame(self):
        """Get the latest frame from the camera, resized and compressed"""
        with self.frame_lock:
            if self.current_frame is None:
                # Return a blank frame if no frame is available
                blank = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                # Add text to indicate no camera feed
                cv2.putText(blank, "No Camera Feed", (int(self.width/4), int(self.height/2)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                _, buffer = cv2.imencode('.jpg', blank, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
                return buffer.tobytes()

            # Return a resized copy of the current frame
            frame = self.current_frame.copy()

        # Resize the frame to the specified dimensions
        frame = cv2.resize(frame, (self.width, self.height))

        # Encode the frame with specified quality
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        return buffer.tobytes()

    def get_raw_frame(self):
        """Get the raw frame for processing (not encoded)"""
        with self.frame_lock:
            if self.current_frame is None:
                return None
            return self.current_frame.copy()

    def release(self):
        """Release the camera resources"""
        print("Releasing camera resources...")
        self.running = False
        if self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)

        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning temporary directory: {e}")