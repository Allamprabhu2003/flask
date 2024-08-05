from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import csrf

# Configuration for email
EMAIL_ADDRESS = "allamprabhuhiremath2003@gmail.com"
EMAIL_PASSWORD = "mfqa ufqt ziah qjfp"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

email_blueprint = Blueprint("email", __name__)

@email_blueprint.route("/send-email", methods=["POST"])
@csrf.exempt
def send_email():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"error": "Missing required fields"}), 400

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = f"New message from {name}"

    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    msg.attach(MIMEText(body, "plain"))

    try:
        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
