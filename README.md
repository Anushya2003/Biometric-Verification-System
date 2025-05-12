Schema

CREATE DATABASE life_certification_db;
\c life_certification_db

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    aadhaar_number VARCHAR(12) UNIQUE NOT NULL,
    name VARCHAR(100),
    dob DATE,
    mobile VARCHAR(15),
    address TEXT,
    photo_path TEXT,
    face_encoding BYTEA,
    is_alive BOOLEAN DEFAULT TRUE,
    last_verified DATE
);

connection
5. Database Connection File: db/database.py
python
Copy
Edit
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname='life_certification_db',
        user='postgres',
        password='your_password',
        host='localhost',
        port='5432'
    )


   

pip install pyqt5
pip install opencv-python
pip install numpy
pip install psycopg2-binary
pip install face_recognition
pip install pillow
pip install reportlab  

# for generating PDF life certificates

error pip uninstall face_recognition face_recognition_models -y
pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition

solution:

Clone the face recognition models to your project manually:

bash
Copy
Edit
git clone https://github.com/ageitgey/face_recognition_models.git

cd face_recognition_models
pip install setuptools
python setup.py install
pip list | findstr face
face-recognition           1.3.0
face-recognition-models    0.3.0

