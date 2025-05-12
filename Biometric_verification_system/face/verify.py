import cv2
import face_recognition
import numpy as np
from db.database import get_connection
import psycopg2

def get_all_face_encodings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT aadhaar_number, face_encoding FROM users")
    users = cur.fetchall()
    conn.close()

    # Convert byte data to numpy array
    encoded_users = []
    for aadhaar, encoding in users:
        encoding_array = np.frombuffer(encoding, dtype=np.float64)
        encoded_users.append((aadhaar, encoding_array))
    return encoded_users

def authenticate_face():
    known_encodings = get_all_face_encodings()

    cap = cv2.VideoCapture(0)
    print("Press 's' to scan face or 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Face Authentication", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

        elif key == ord('s'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for unknown_encoding in face_encodings:
                for aadhaar, known_encoding in known_encodings:
                    match = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.45)
                    if match[0]:
                        cap.release()
                        cv2.destroyAllWindows()
                        print(f"✅ Face matched with Aadhaar: {aadhaar}")
                        return aadhaar

            print("❌ No match found.")

    cap.release()
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    result = authenticate_face()
    if result:
        print(f"Authentication success: {result}")
    else:
        print("Authentication failed.")
