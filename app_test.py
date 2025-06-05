from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, session
from camera import UnifiedCamera  # Import the new unified camera
import time
import os
from datetime import datetime
import atexit

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Single camera instance handles everything
camera = UnifiedCamera(width=640, height=480, jpeg_quality=70)

@app.route('/')
def index():
    """Video streaming home page"""
    # Clear any pending QR data for fresh start
    camera.clear_qr_queue()
    return render_template('test_index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route with built-in QR status overlay"""
    def generate():
        while True:
            frame = camera.get_frame()  # Already includes QR status overlay
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_qr_data')
def check_qr_data():
    """API endpoint to check for new QR detections"""
    qr_detection = camera.get_latest_qr()
    
    if qr_detection:
        return jsonify({
            'detected': True, 
            'data': qr_detection['data'],
            'timestamp': qr_detection['timestamp']
        })
    
    return jsonify({'detected': False})

@app.route('/scan_qr', methods=['GET'])
def scan_qr():
    """Manual QR scan endpoint (for compatibility)"""
    # Check if there's already detected QR data
    qr_detection = camera.get_latest_qr()
    
    if qr_detection:
        return jsonify({'success': True, 'data': qr_detection['data']})
    else:
        return jsonify({'success': False, 'error': 'No QR code detected'})

@app.route('/qr_settings', methods=['POST'])
def qr_settings():
    """Configure QR scanning settings"""
    data = request.get_json()
    
    if 'enabled' in data:
        camera.set_qr_scanning(data['enabled'])
    
    if 'cooldown' in data:
        camera.set_qr_cooldown(data['cooldown'])
    
    return jsonify({'status': 'updated'})

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission"""
    qr_data = request.form.get('qr_data', '')
    
    session['qr_data'] = qr_data
    session['timestamp'] = datetime.now().strftime("%Y%m%d%H%M%S")
    
    return redirect(url_for('result'))

@app.route('/result')
def result():
    """Results page"""
    qr_data = session.get('qr_data', '')
    timestamp = session.get('timestamp', '')
    reference_image = f"Reference for: {qr_data}"
    
    return render_template('test_result.html', 
                           qr_data=qr_data,
                           reference_image=reference_image,
                           timestamp=timestamp)

@app.route('/status')
def status():
    """Get camera and QR scanning status"""
    return jsonify({
        'qr_scanning_enabled': camera.qr_scanning_enabled,
        'qr_cooldown': camera.qr_cooldown,
        'has_qr_data': camera.has_qr_data(),
        'last_qr': camera.last_qr_data,
        'last_qr_time': camera.last_qr_time
    })

# Cleanup function
def cleanup():
    print("Cleaning up resources...")
    camera.release()

atexit.register(cleanup)

if __name__ == '__main__':
    try:
        print("Starting Flask app with unified camera...")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        cleanup()