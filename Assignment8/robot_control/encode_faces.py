import face_recognition
import os
import pickle

# Path to known faces directory
KNOWN_FACES_DIR = 'known_faces'

# Lists to store encodings and names
known_face_encodings = []
known_face_names = []

for person_name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
    if not os.path.isdir(person_dir):
        continue

    for filename in os.listdir(person_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(person_dir, filename)
            print(f"Processing image: {image_path}")

            try:
                # Load the image
                image = face_recognition.load_image_file(image_path)

                # Detect and encode faces
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(person_name)
                    print(f"Face encoded successfully for {person_name}.")
                else:
                    print(f"No face detected in {image_path}. Skipping...")

            except Exception as e:
                print(f"Error processing {image_path}: {e}")

# Save encodings and names
with open('encodings.pickle', 'wb') as f:
    pickle.dump({'encodings': known_face_encodings, 'names': known_face_names}, f)

print("Encoding complete. Data saved to encodings.pickle.")
