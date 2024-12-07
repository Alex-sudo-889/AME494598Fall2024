import face_recognition
import cv2
import numpy as np
import os
import csv
from datetime import datetime

# Load known faces and names
known_face_encodings = []
known_face_names = []

for filename in os.listdir('known_faces'):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        # Load an image
        image = face_recognition.load_image_file(f'known_faces/{filename}')
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            # Extract name from the filename
            known_face_names.append(os.path.splitext(filename)[0])
        else:
            print(f"Could not find a face in {filename}")

# Initialize variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Open CSV file for logging
csv_file = open('face_log.csv', 'a', newline='')
csv_writer = csv.writer(csv_file)
if os.stat('face_log.csv').st_size == 0:
    csv_writer.writerow(['Timestamp', 'Name'])

# Start video capture
video_capture = cv2.VideoCapture(0)

while True:
    # Grab a frame
    ret, frame = video_capture.read()
    if not ret:
        break

    # Resize frame for faster processing (optional)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert from BGR to RGB
    rgb_small_frame = small_frame[:, :, ::-1]

    # Process every other frame
    if process_this_frame:
        # Find all faces and face encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Compare face to known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown Individual"

            # Use the known face with the smallest distance
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if face_distances.size > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)

            # Log the name and timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            csv_writer.writerow([timestamp, name])
            csv_file.flush()
            print(f"{timestamp}: {name}")

    process_this_frame = not process_this_frame

    # Display the results (optional)
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw rectangle
        color = (0, 255, 0) if name != "Unknown Individual" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Label
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

    # Show the frame (optional)
    cv2.imshow('Video', frame)

    # Break on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
video_capture.release()
cv2.destroyAllWindows()
csv_file.close()
