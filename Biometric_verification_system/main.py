from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from ui.register import RegistrationForm
from face.verify import authenticate_face
from ui.lifecert import LifeCertWindow
import sys

class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Social Security Verification System")
        self.setGeometry(100, 50, 800, 600)  # Increase window size

        apply_gradient_background(self)

        layout = QVBoxLayout()
        layout.setSpacing(30)  # Increased spacing for better readability
        layout.setAlignment(Qt.AlignCenter)

        # Header with Emblems
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)

        # Tamil Nadu Government Emblem
        tn_emblem_label = QLabel()
        tn_emblem_pixmap = QPixmap("tn.png").scaled(80, 80, Qt.KeepAspectRatio)  # Increased size of emblems
        tn_emblem_label.setPixmap(tn_emblem_pixmap)

        # Government of India Emblem
        emblem_label = QLabel()
        emblem_pixmap = QPixmap("indiapng.jpg").scaled(80, 80, Qt.KeepAspectRatio)  # Increased size of emblems
        emblem_label.setPixmap(emblem_pixmap)

        # Title Label
        title_label = QLabel("Social Security Verification System")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #003366;")  # Larger title font
        
        # Add images and title to header
        header_layout.addWidget(tn_emblem_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(emblem_label)

        layout.addLayout(header_layout)


        # Buttons
        btn_register = QPushButton("Register New User")
        btn_authenticate = QPushButton("Authenticate User")

        # Apply styles
        style_main_button(btn_register)
        style_main_button(btn_authenticate)

        # Signals
        btn_register.clicked.connect(self.open_registration)
        btn_authenticate.clicked.connect(self.authenticate_and_open_cert)

        # Layout setup
        layout.addWidget(btn_register)
        layout.addWidget(btn_authenticate)

        self.setLayout(layout)

    def open_registration(self):
        self.registration_form = RegistrationForm()
        self.registration_form.show()

    def authenticate_and_open_cert(self):
        aadhaar = authenticate_face()
        print("Authenticated:", aadhaar)

        if aadhaar:
            self.cert_win = LifeCertWindow(aadhaar)
            self.cert_win.show()
        else:
            QMessageBox.warning(
                self,
                "Authentication Failed",
                "Face not recognized. Please try again or register."
            )

# ========== STYLE HELPERS ==========

def apply_gradient_background(widget: QWidget):
    widget.setStyleSheet("""
        QWidget {
            background-color: white;
        }
    """)

def style_main_button(button: QPushButton):
    button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    set_font(button, size=16, bold=True)

def set_font(widget: QWidget, size=12, bold=False):
    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)
    widget.setFont(font)

# Run app
def run_app():
    app = QApplication(sys.argv)
    window = HomeScreen()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    print("Starting app...")
    run_app()