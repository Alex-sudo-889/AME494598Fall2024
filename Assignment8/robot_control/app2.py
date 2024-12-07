# app2.py

from flask import Flask, render_template, Response, request
import motor_control
import atexit
import cv2

app = Flask(__name__)

# Initialize the video capture object (0 for the default camera)
video_capture = cv2.VideoCapture(0)

def cleanup_func():
    """Release resources when the app exits."""
    video_capture.release()
    cv2.destroyAllWindows()
    motor_control.cleanup()
    print("Cleaned up resources.")

# Register the cleanup function to be called on exit
atexit.register(cleanup_func)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    """Control endpoint to handle motor commands."""
    command = request.form.get('command')
    if command:
        if command == 'forward':
            motor_control.forward()
        elif command == 'backward':
            motor_control.backward()
        elif command == 'left':
            motor_control.left()
        elif command == 'right':
            motor_control.right()
        elif command == 'stop':
            motor_control.stop()
        elif command == 'set_speed':
            speed = int(request.form.get('speed', 100))
            motor_control.set_speed(speed)
        else:
            return 'Invalid command', 400
        return '', 204
    else:
        return 'No command provided', 400

def gen_frames():
    """Generate video frames for streaming."""
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
