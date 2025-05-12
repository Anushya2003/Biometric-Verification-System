# cert/generate_certificate.py


import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from db.database import get_connection
from datetime import date

OUTPUT_DIR = "certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf_for_user(aadhaar_number: str) -> str:
    # Fetch user details
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, dob, mobile, address, photo_path
          FROM users
         WHERE aadhaar_number = %s
    """, (aadhaar_number,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise ValueError("User not found")

    name, dob, mobile, address, photo_path = row

    # Build filename
    today = date.today().strftime("%Y%m%d")
    filename = f"life_cert_{aadhaar_number}_{today}.pdf"
    out_path = os.path.join(OUTPUT_DIR, filename)

    # Create PDF
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 50, "Digital Life Certificate")

    # User info
    c.setFont("Helvetica", 12)
    text_y = height - 100
    for label, value in [
        ("Name", name),
        ("Aadhaar No.", aadhaar_number),
        ("DOB", dob.strftime("%Y-%m-%d")),
        ("Mobile", mobile),
        ("Address", address.replace("\n", " "))
    ]:
        c.drawString(50, text_y, f"{label}: {value}")
        text_y -= 20

    # Certification date
    c.drawString(50, text_y - 10, f"Certified on: {date.today().isoformat()}")

    # Optionally draw photo
    if os.path.exists(photo_path):
        c.drawImage(photo_path, width - 150, height - 200, 100, 100)

    c.showPage()
    c.save()

    return out_path
