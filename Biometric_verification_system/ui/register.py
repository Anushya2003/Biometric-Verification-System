import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox, QDateEdit
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, QDate

import os
from face_recognition import face_encodings, load_image_file # type: ignore
import numpy as np
from db.database import get_connection

IMAGE_DIR = 'images'
ENCODING_DIR = 'encodings'

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(ENCODING_DIR, exist_ok=True)

class RegistrationForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Registration")
        self.image_path = None

        self.init_ui()
        self.setup_camera()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.aadhaar_input = QLineEdit()
        self.name_input = QLineEdit()
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        self.mobile_input = QLineEdit()
        self.address_input = QTextEdit()

        form_layout.addRow("Aadhaar Number:", self.aadhaar_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("DOB:", self.dob_input)
        form_layout.addRow("Mobile:", self.mobile_input)
        form_layout.addRow("Address:", self.address_input)

        layout.addLayout(form_layout)

        # Webcam preview
        self.camera_label = QLabel()
        layout.addWidget(self.camera_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Photo")
        self.submit_btn = QPushButton("Submit")
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.submit_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Signals
        self.capture_btn.clicked.connect(self.capture_photo)
        self.submit_btn.clicked.connect(self.submit_data)

    def setup_camera(self):
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(
                rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0],
                QImage.Format_RGB888
            )
            self.camera_label.setPixmap(QPixmap.fromImage(image))
            self.current_frame = frame

    def capture_photo(self):
        aadhaar = self.aadhaar_input.text()
        if not aadhaar:
            QMessageBox.warning(self, "Missing Aadhaar", "Please enter Aadhaar number first.")
            return

        filename = f"{aadhaar}.jpg"
        path = os.path.join(IMAGE_DIR, filename)
        cv2.imwrite(path, self.current_frame)
        self.image_path = path
        QMessageBox.information(self, "Captured", "Photo captured successfully.")

    def submit_data(self):
        if not self.image_path:
            QMessageBox.warning(self, "No Photo", "Please capture photo first.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            aadhaar = self.aadhaar_input.text()
            name = self.name_input.text()
            dob = self.dob_input.date().toPyDate()
            mobile = self.mobile_input.text()
            address = self.address_input.toPlainText()

            # Generate face encoding
            image = load_image_file(self.image_path)
            encoding_list = face_encodings(image)

            if not encoding_list:
                QMessageBox.warning(self, "Face Error", "No face detected in photo.")
                return

            face_encoding = encoding_list[0]
            cur.execute("""
                INSERT INTO users (aadhaar_number, name, dob, mobile, address, photo_path, face_encoding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (aadhaar, name, dob, mobile, address, self.image_path, face_encoding.tobytes()))

            conn.commit()
            QMessageBox.information(self, "Success", "User registered successfully.")
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        finally:
            if conn:
                conn.close()

    def clear_form(self):
        self.aadhaar_input.clear()
        self.name_input.clear()
        self.mobile_input.clear()
        self.address_input.clear()
        self.image_path = None



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistrationForm() # type: ignore
    window.show()
    sys.exit(app.exec_())
