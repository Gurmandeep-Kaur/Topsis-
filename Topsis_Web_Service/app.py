from flask import Flask, render_template, request
import os
import re
import subprocess
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def send_email(receiver_email, attachment_path):
    sender_email = "your_email"
    sender_password = "your_app_password"

    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result File"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Please find the attached TOPSIS result file.")

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="result.csv"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    file = request.files.get("file")
    weights = request.form.get("weights")
    impacts = request.form.get("impacts")
    email = request.form.get("email")

    if not file or not weights or not impacts or not email:
        return "All fields are required"

    if not valid_email(email):
        return "Invalid email format"

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(OUTPUT_FOLDER, "result.csv")

    file.save(input_path)

    command = [
        "python",
        "-m",
        "topsis_gurmandeep_102303764.topsis",
        input_path,
        weights,
        impacts,
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        return result.stderr

    send_email(email, output_path)

    return "TOPSIS result generated and emailed successfully"


if __name__ == "__main__":
    app.run(debug=True)
