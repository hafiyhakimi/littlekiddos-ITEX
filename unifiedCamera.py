"""
Unified camera module with built-in QR scanning capability
@author Salman H.
"""
import cv2
import time
import threading
import numpy as np
from pyzbar.pyzbar import decode
from collections import deque
import queue
from picamera2 import Picamera2

class UnifiedCamera:
    def __init__(self, width=640, height=480, jpeg_quality=70):
        """Initialize camera with integrated QR scanning"""
        print(f"Initializing unified camera with size {width}x{height}...")

        self.width = width
        self.height = height
        self.jpeg_quality = jpeg_quality

        # Frame management
        self.frame_lock = threading.Lock()
        self.current_frame = None
        self.qr_frame = None

        # QR scanning state
        self.qr_data_queue = queue.Queue(maxsize=5)  # Store recent QR detections
        self.last_qr_data = None
        self.last_qr_time = 0
        self.qr_cooldown = 10.0  # 10 second cooldown
        self.qr_scanning_enabled = True

        # Initialize camera
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(
            main={"size": (width * 2, height * 2)},  # High res for display
            lores={"size": (640, 480), "format": "YUV420"},  # Optimized for QR
            controls={
                "FrameRate": 30,
                "ExposureTime": 8000,
                "AnalogueGain": 2.0
            }
        )
        self.picam2.configure(config)
        self.picam2.start()

        # Start unified processing thread
        self.running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.daemon = True
        self.process_thread.start()

        time.sleep(1)
        print("Unified camera initialized successfully")

    def _process_loop(self):
        """Single thread handling both frame capture and QR detection"""
        frame_count = 0

        while self.running:
            try:
                # Capture both streams
                request = self.picam2.capture_request()

                # Main frame for display
                main_frame = request.make_array("main")
                main_frame = cv2.cvtColor(main_frame, cv2.COLOR_RGB2BGR)

                # QR frame (grayscale, optimized)
                lores_frame = request.make_array("lores")
                qr_frame = cv2.cvtColor(lores_frame, cv2.COLOR_YUV420p2GRAY)

                request.release()

                # Update frames
                with self.frame_lock:
                    self.current_frame = main_frame
                    self.qr_frame = qr_frame

                # QR detection (every 3rd frame to balance performance)
                frame_count += 1
                if frame_count % 3 == 0 and self._should_scan_qr():
                    self._detect_qr(qr_frame)

                time.sleep(1/30)  # 30 FPS

            except Exception as e:
                print(f"Error in processing loop: {e}")
                time.sleep(0.1)

    def _should_scan_qr(self):
        """Check if we should scan for QR codes (respects cooldown)"""
        if not self.qr_scanning_enabled:
            return False

        current_time = time.time()
        return (current_time - self.last_qr_time) >= self.qr_cooldown

    def _detect_qr(self, frame):
        """Detect QR codes in the given frame"""
        try:
            # Multiple processing techniques for better detection
            detection_frames = [
                frame,  # Original
                cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
                cv2.GaussianBlur(frame, (3, 3), 0)
            ]

            for processed_frame in detection_frames:
                qr_codes = decode(processed_frame)
                if qr_codes:
                    for qr in qr_codes:
                        qr_data = qr.data.decode('utf-8')
                        self._handle_qr_detection(qr_data)
                        return  # Stop after first successful detection
 
        except Exception as e:
            print(f"QR detection error: {e}")

    def _handle_qr_detection(self, qr_data):
        """Handle a successful QR code detection"""
        current_time = time.time()

        # Avoid duplicate detections
        if qr_data == self.last_qr_data and (current_time - self.last_qr_time) < 1.0:
            return

        print(f"QR Code detected: {qr_data}")

        # Update state
        self.last_qr_data = qr_data
        self.last_qr_time = current_time

        # Add to queue (thread-safe)
        try:
            self.qr_data_queue.put_nowait({
                'data': qr_data,
                'timestamp': current_time
            })
        except queue.Full:
            # Remove oldest item and add new one
            try:
                self.qr_data_queue.get_nowait()
                self.qr_data_queue.put_nowait({
                    'data': qr_data,
                    'timestamp': current_time
                })
            except queue.Empty:
                pass

    def get_frame(self):
        """Get frame for web streaming with status overlay"""
        with self.frame_lock:
            if self.current_frame is None:
                blank = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                cv2.putText(blank, "No Camera Feed", (self.width//4, self.height//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                _, buffer = cv2.imencode('.jpg', blank, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
                return buffer.tobytes()

            frame = self.current_frame.copy()

        # Resize for display
        frame = cv2.resize(frame, (self.width, self.height))

        # Add status overlay
        self._add_status_overlay(frame)

        # Encode
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        return buffer.tobytes()

    def _add_status_overlay(self, frame):
        """Add QR scanning status to frame"""
        current_time = time.time()

        if not self.qr_scanning_enabled:
            status = "QR Scanning: Disabled"
            color = (0, 0, 255)  # Red
        elif (current_time - self.last_qr_time) < self.qr_cooldown:
            remaining = self.qr_cooldown - (current_time - self.last_qr_time)
            status = f"QR Cooldown: {remaining:.1f}s"
            color = (0, 165, 255)  # Orange
        else:
            status = "QR Scanning: Active"
            color = (0, 255, 0)  # Green

        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Show last detected QR
        if self.last_qr_data:
            qr_text = f"Last QR: {self.last_qr_data[:20]}..."
            cv2.putText(frame, qr_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def get_latest_qr(self):
        """Get the most recent QR detection (non-blocking)"""
        try:
            return self.qr_data_queue.get_nowait()
        except queue.Empty:
            return None

    def has_qr_data(self):
        """Check if there's QR data available"""
        return not self.qr_data_queue.empty()

    def clear_qr_queue(self):
        """Clear all pending QR detections"""
        while not self.qr_data_queue.empty():
            try:
                self.qr_data_queue.get_nowait()
            except queue.Empty:
                break

    def set_qr_scanning(self, enabled):
        """Enable/disable QR scanning"""
        self.qr_scanning_enabled = enabled
        if not enabled:
            self.clear_qr_queue()
        print(f"QR scanning {'enabled' if enabled else 'disabled'}")

    def set_qr_cooldown(self, seconds):
        """Set QR detection cooldown period"""
        self.qr_cooldown = seconds
        print(f"QR cooldown set to {seconds} seconds")

    def get_raw_frame(self):
        """Get raw frame for other processing"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None

    def release(self):
        """Clean up resources"""
        print("Releasing unified camera resources...")
        self.running = False

        if self.process_thread.is_alive():
            self.process_thread.join(timeout=2.0)

        try:
            self.picam2.stop()
            self.picam2.close()
        except Exception as e:
            print(f"Error closing camera: {e}")

        self.clear_qr_queue()
        print("Unified camera released")
