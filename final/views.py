import cv2
import numpy as np

from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .models import Face
from .utils import compute_face_encodings, run_face_recognition

views = Blueprint("views", __name__)


# Error handling
def handle_error(error):
    # Log the error and display a user-friendly message
    print(f"Error: {error}")
    return render_template("error.html", error=error)


# Security
def sanitize_input(input):
    # Sanitize user input to prevent SQL injection attacks
    return input.replace("'", "''")


# Database operations
def save_to_database(name, face_encodings):
    try:
        face = Face(name=name, face_encodings=face_encodings)
        db.session.add(face)
        db.session.commit()
    except Exception as e:
        return handle_error(e)


# User interface
@views.route("/")
def index():
    return render_template("index.html")


@views.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        name = sanitize_input(request.form["name"])
        image_file = request.files["image"]
        try:
            image = np.fromfile(image_file, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            face_encodings = compute_face_encodings(image)
            save_to_database(name, face_encodings)
            return redirect(url_for("views.index"))

        except Exception as e:
            return handle_error(e)


# Face recognition
@views.route("/recognize")
def recognize():
    cap = cv2.VideoCapture(0)  # Change to '0' for webcam or provide video file path
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame.size == 0:
            continue
        frame = run_face_recognition(frame)
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    return render_template("recognize.html")
