from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, session
from camera import Camera
from qrScanner import QRScanner
import time
import threading
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Create camera instance
camera = Camera()
qr_scanner = QRScanner(camera)

# Start QR scanning in background
qr_thread = None
qr_scanning_active = False

def scan_for_qr():
    """Background thread function for QR code scanning"""
    global qr_scanning_active
    while qr_scanning_active:
        qr_data = qr_scanner.scan_qr_code()
        if qr_data:
            app.config['QR_DATA'] = qr_data
            time.sleep(0.5)  # Prevent multiple rapid detections

@app.route('/')
def index():
    """Video streaming home page - Reset QR data on every visit"""
    # Reset the QR data when accessing the landing page
    global last_qr_data
    last_qr_data = None
    qr_scanner.last_code = None  # Reset the scanner's last detected code
    
    # Pass a reset flag to template to ensure client-side reset
    return render_template('test_index.html', reset_timestamp=time.time())

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    def generate():
        while True:
            # Get a frame from the camera
            frame = camera.get_frame()
            
            # Yield the frame to the client
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.017)  # Adjust frame rate
    
    return Response(generate(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/scan_qr', methods=['GET'])
def scan_qr():
    """Endpoint to scan QR code"""
    global last_qr_data
    qr_data = qr_scanner.scan_qr_code()
    
    if qr_data:
        last_qr_data = qr_data
        return jsonify({'success': True, 'data': qr_data})
    else:
        return jsonify({'success': False, 'error': 'No QR code detected'})

@app.route('/reset_qr', methods=['POST'])
def reset_qr():
    """Explicitly reset QR data"""
    global last_qr_data
    last_qr_data = None
    qr_scanner.last_code = None  # Reset the scanner's last detected code
    return jsonify({'success': True, 'message': 'QR data reset successfully'})

@app.route('/check_qr_data')
def check_qr_data():
    """API endpoint to check if QR data is available"""
    qr_data = app.config.get('QR_DATA', None)
    if qr_data:
        # Clear the data so it's only used once
        app.config['QR_DATA'] = None
        return jsonify({'detected': True, 'data': qr_data})
    return jsonify({'detected': False})

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission"""
    qr_data = request.form.get('qr_data', '')
    
    # Store the QR data in session
    session['qr_data'] = qr_data
    
    # Generate timestamp for reference (could be used to look up specific reference images)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session['timestamp'] = timestamp
    
    return redirect(url_for('result'))

@app.route('/result')
def result():
    """Results page with camera feed and reference image"""
    qr_data = session.get('qr_data', '')
    timestamp = session.get('timestamp', '')
    
    # In a real application, you might use the QR data or timestamp 
    # to look up the specific reference image to display
    reference_image = f"Reference for: {qr_data}"
    # reference_image = 
    
    return render_template('test_result.html', 
                           qr_data=qr_data,
                           reference_image=reference_image,
                           timestamp=timestamp)

# def gen_frames():
#     """Generate camera frames"""
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     """Route for streaming video feed"""
#     return Response(gen_frames(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/scan_qr', methods=['GET'])
# def scan_qr():
#     """Endpoint to scan QR code"""
#     qr_data = qr_scanner.scan_qr_code()
#     if qr_data:
#         return jsonify({'success': True, 'data': qr_data})
#     else:
#         return jsonify({'success': False, 'error': 'No QR code detected'})

# @app.route('/start_scanning')
# def start_scanning():
#     """Start QR code scanning in background"""
#     global qr_thread, qr_scanning_active
    
#     if qr_thread is None or not qr_thread.is_alive():
#         qr_scanning_active = True
#         qr_thread = threading.Thread(target=scan_for_qr)
#         qr_thread.daemon = True
#         qr_thread.start()
    
#     return jsonify({'status': 'started'})

# @app.route('/stop_scanning')
# def stop_scanning():
#     """Stop QR code scanning"""
#     global qr_scanning_active
#     qr_scanning_active = False
#     return jsonify({'status': 'stopped'})

# Handle proper cleanup when the app is shutting down
def cleanup():
    print("Cleaning up resources...")
    qr_scanner.stop()
    camera.release()

if __name__ == '__main__':
    try:
        # Start with scanning active
        qr_scanning_active = True
        qr_thread = threading.Thread(target=scan_for_qr)
        qr_thread.daemon = True
        qr_thread.start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        # Ensure cleanup on exit
        qr_scanning_active = False
        if qr_thread and qr_thread.is_alive():
            qr_thread.join(timeout=1.0)
        cleanup()
        camera.release()