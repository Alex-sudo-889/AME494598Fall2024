# recognize_faces.py
import face_recognition
import cv2
import numpy as np
import pickle
import os
from datetime import datetime
import csv

# Load known face encodings and names
with open('encodings.pickle', 'rb') as f:
    data = pickle.load(f)
    known_face_encodings = data['encodings']
    known_face_names = data['names']

# Initialize variables
face_locations = []
face_encodings = []
face_names = []
process_every_n_frames = 2  # Adjust for performance
frame_count = 0

# Open CSV file for logging
csv_file = open('face_log.csv', 'a', newline='')
csv_writer = csv.writer(csv_file)
if os.stat('face_log.csv').st_size == 0:
    csv_writer.writerow(['Timestamp', 'Name'])

# Start video capture
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Error: Unable to access the camera.")
    exit()

while True:
    # Grab a single frame
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1

    # Resize frame for faster processing (optional)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB

    # Only process every nth frame to save time
    if frame_count % process_every_n_frames == 0:
        # Find all face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Compare to known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown Individual"

            # Use the known face with the smallest distance if a match was found
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if face_distances.size > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)

            # Log the recognized face with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            csv_writer.writerow([timestamp, name])
            csv_file.flush()
            print(f"{timestamp}: {name}")

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 0.5
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
video_capture.release()
cv2.destroyAllWindows()
csv_file.close()
