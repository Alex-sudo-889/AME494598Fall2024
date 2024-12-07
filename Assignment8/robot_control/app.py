# app.py

from flask import Flask, render_template, Response, request
import motor_control  # Ensure motor_control.py is in the same directory
import atexit
import cv2
import face_recognition
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# =========================
# Configuration and Setup
# =========================

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Define the path to the 'known_faces' directory
known_faces_dir = os.path.join(script_dir, 'known_faces')

# Verify that the 'known_faces' directory exists
if not os.path.exists(known_faces_dir):
    logging.error(f"The directory '{known_faces_dir}' does not exist. Please create it and add known face images.")
    raise FileNotFoundError(f"The directory '{known_faces_dir}' does not exist. Please create it and add known face images.")

# Load known faces
known_face_encodings = []
known_face_names = []

# Supported image formats
supported_formats = ('.jpg', '.jpeg', '.png')

# Iterate through each file in the 'known_faces' directory
for filename in os.listdir(known_faces_dir):
    if filename.lower().endswith(supported_formats):
        image_path = os.path.join(known_faces_dir, filename)
        try:
            # Load the image file
            image = face_recognition.load_image_file(image_path)
            
            # Get the face encodings for any faces in the image
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                # Assume the first face in the image is the intended one
                encoding = encodings[0]
                known_face_encodings.append(encoding)
                
                # Extract the name from the filename (without extension)
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)
                logging.info(f"Loaded encoding for {name} from {filename}")
            else:
                logging.warning(f"No faces found in {filename}. Skipping this file.")
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

# Initialize video capture
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    logging.error("Failed to open video capture device.")
    raise IOError("Cannot open webcam")

# =========================
# Cleanup Function
# =========================

def cleanup_func():
    """Release resources when the app exits."""
    video_capture.release()
    cv2.destroyAllWindows()
    motor_control.cleanup()
    logging.info("Cleaned up resources.")

# Register the cleanup function to be called on exit
atexit.register(cleanup_func)

# =========================
# Flask Routes
# =========================

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')  # Ensure you have an 'index.html' in the 'templates' folder

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
        logging.info(f"Received command: {command}")
        try:
            if command == 'forward':
                motor_control.forward()
            elif command == 'backward':
                motor_control.backward()
            elif command == 'left':
                motor_control.leftrotation()
            elif command == 'right':
                motor_control.rightrotation()
            elif command == 'stop':
                motor_control.stop()
            else:
                logging.warning(f"Invalid command received: {command}")
                return 'Invalid command', 400  # Bad Request
            return '', 204  # No Content
        except Exception as e:
            logging.error(f"Error executing command '{command}': {e}")
            return 'Error executing command', 500  # Internal Server Error
    else:
        logging.warning("No command provided in the request.")
        return 'No command provided', 400  # Bad Request

# =========================
# Frame Generation
# =========================

def gen_frames():
    """Generate video frames with facial recognition annotations."""
    while True:
        # Capture a single frame of video
        success, frame = video_capture.read()
        if not success:
            logging.error("Failed to capture video frame.")
            break
        else:
            # Resize the frame to 1/4 size for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Detect face locations in the resized frame
            face_locations = face_recognition.face_locations(rgb_small_frame)

            # Compute face encodings based on the face locations
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # Compare face encodings with known faces
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # Use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if face_distances.size > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                face_names.append(name)

            # Scale face locations back to the original frame size
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logging.error("Failed to encode frame.")
                continue
            frame_bytes = buffer.tobytes()

            # Yield the frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# =========================
# Run the Flask App
# =========================

if __name__ == '__main__':
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)
