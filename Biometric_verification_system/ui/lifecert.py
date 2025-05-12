import os
import sys
import subprocess
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QFrame
)
from db.database import get_connection
from cert.generate_certificate import generate_pdf_for_user

class LifeCertWindow(QWidget):
    def __init__(self, aadhaar):
        super().__init__()
        self.aadhaar = aadhaar
        self.name = ""
        self.setWindowTitle("Life Certificate")
        self.resize(450, 250)

        self.layout = QVBoxLayout()

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")

        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: darkblue; font-weight: bold; margin-bottom: 15px;")

        self.download_btn = QPushButton("📄 Download Life Certificate PDF")
        self.download_btn.setStyleSheet("padding: 8px; font-size: 14px;")
        self.download_btn.clicked.connect(self.on_download)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.download_btn)
        self.setLayout(self.layout)

        self.populate_user_info()
        self.check_eligibility()

    def populate_user_info(self):
        """Fetch user's name from DB using Aadhaar."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT name
            FROM users
            WHERE aadhaar_number = %s
        """, (self.aadhaar,))
        row = cur.fetchone()
        conn.close()

        if row:
            self.name = row[0]
        else:
            self.name = "User"

        self.title_label.setText(f"Welcome, {self.name}!")
        self.message_label.setText(f"Aadhaar Number: {self.aadhaar}")

    def check_eligibility(self):
        """Check if the user has already been certified this month."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT last_verified
            FROM users
            WHERE aadhaar_number = %s
        """, (self.aadhaar,))
        row = cur.fetchone()
        conn.close()

        if row and row[0]:
            last = row[0]
            today = date.today()
            if last.year == today.year and last.month == today.month:
                self.status_label.setText(f"✅ Certificate already issued on {last}")
                self.download_btn.setEnabled(False)
                return

        self.status_label.setText("❗ You have not been certified this month.")
        self.download_btn.setEnabled(True)

    def on_download(self):
        """Generate certificate PDF, update DB, and disable button."""
        try:
            pdf_path = generate_pdf_for_user(self.aadhaar)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"PDF generation failed:\n{e}")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE users
                   SET last_verified = CURRENT_DATE
                 WHERE aadhaar_number = %s
            """, (self.aadhaar,))
            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Could not update certification date:\n{e}")
            return

        self.check_eligibility()

        QMessageBox.information(self, "Success", f"✅ Life Certificate saved to:\n{pdf_path}")

        try:
            if sys.platform == "win32":
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", pdf_path])
            else:
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            QMessageBox.warning(self, "Open PDF Failed", f"Could not open the PDF:\n{e}")
