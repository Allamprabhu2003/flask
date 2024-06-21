import time

import cv2
import numpy as np
from flask_login import current_user, login_required
from sympy import im
import cProfile

# from your_module import run_face_recognition


from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)

from . import db
from .models import Attendance, Class, Face, User
from .utils import compute_face_embeding, compute_face_encodings, run_face_recognition

views = Blueprint("views", __name__)


# face_encodings_cache = {}


def load_from_database():
    with current_app.app_context():
        faces = Face.query.all()
        # for face in faces:
            # face_encodings_cache[face.name] = face.face_encodings
        return [(face.name, face.face_encodings) for face in faces]


def handle_error(error):
    print(f"Error: {error}")
    return render_template("error.html", error=error)


def sanitize_input(input):
    return input.replace("'", "''")


def save_to_database(name, face_encodings):
    try:
        face = Face(name=name, face_encodings=face_encodings)
        db.session.add(face)
        db.session.commit()
    except Exception as e:
        return handle_error(e)


@views.route("/")
def index():
    return render_template("home.html")


# @views.route("/recognize_image", methods=["GET", "POST"])
# @login_required
# def recognize_image():
#     if request.method == "POST":
#         image_file = request.files["image"]
#         try:
#             image = np.fromfile(image_file, np.uint8)
#             image = cv2.imdecode(image, cv2.IMREAD_COLOR)
#             frame, attendance_records = run_face_recognition(image, None)
#             # cProfile.runctx('frame, attendance_records = run_face_recognition(image, None)', globals(), locals(), "Profile.prof")

#             ret, buffer = cv2.imencode(".jpg", frame)
#             frame = buffer.tobytes()
#             return Response(b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n", mimetype="multipart/x-mixed-replace; boundary=frame")
#         except Exception as e:
#             return handle_error(e)
#     return render_template("recognize_image.html")

@views.route("/recognize")
def recognize():
    return render_template("recognize.html")

@views.route("/recognize_image/<int:class_id>", methods=["GET", "POST"])
@login_required
def recognize_image(class_id):
    if request.method == "POST":
        image_file = request.files["image"]
        try:
            image = np.fromfile(image_file, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            frame, attendance_records = run_face_recognition(image, class_id)
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            return Response(
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n",
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )
        except Exception as e:
            return handle_error(e)
    return render_template("recognize_image.html", class_id=class_id)


# @views.route("/upload", methods=["POST"])

# @login_required
# def upload():
#     if not current_user.is_admin:
#         teacher_classes = Class.query.filter_by(teacher_id=current_user.id).all()

#     if request.method == "POST":
#         name = sanitize_input(request.form["name"])
#         image_file = request.files["image"]
#         try:
#             image = np.fromfile(image_file, np.uint8)
#             image = cv2.imdecode(image, cv2.IMREAD_COLOR)
#             # face_encodings = compute_face_encodings(image)
#             face_encodings = compute_face_embeding(image, 100)
#             save_to_database(name, face_encodings)
#             # return redirect(url_for("views.index"))
#             return redirect("index.html", classes=teacher_classes)
#         except Exception as e:
#             return handle_error(e)


@views.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        name = sanitize_input(request.form["name"])
        image_file = request.files["image"]
        try:
            image = np.fromfile(image_file, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            face_encodings = compute_face_embeding(image, 100)
            save_to_database(name, face_encodings)
            return redirect(url_for("views.dashboard"))
        except Exception as e:
            return handle_error(e)
    return render_template("upload.html")


# @views.route("/dashboard")
# @login_required
# def dashboard():
#     if not current_user.is_admin:
#         teacher_classes = Class.query.filter_by(teacher_id=current_user.id).all()

#         return render_template("dashboard.html", classes=teacher_classes)
#     return redirect(url_for("admin.index"))

# @views.route("/dashboard")
# @login_required
# def dashboard():
#     if not current_user.is_admin:
#         teacher_classes = Class.query.filter_by(teacher_id=current_user.id).all()

#         # Calculate the average attendance for each student in each class
#         average_attendance = {}
#         for class_ in teacher_classes:
#             attendance_records = Attendance.query.filter_by(class_id=class_.id).all()
#             student_attendance = {}
#             for record in attendance_records:
#                 if record.student_name in student_attendance:
#                     student_attendance[record.student_name] += 1
#                 else:
#                     student_attendance[record.student_name] = 1
#             total_records = len(attendance_records)
#             student_average_attendance = {name: count / total_records for name, count in student_attendance.items()}
#             average_attendance[class_.name] = student_average_attendance

#         # Identify the student with the least average attendance in each class
#         least_attended_students = {}
#         for class_name, student_attendance in average_attendance.items():
#             least_attended_student = min(student_attendance, key=student_attendance.get)
#             least_attended_students[class_name] = {
#                 "name": least_attended_student,
#                 "average_attendance": average_attendance[class_name][least_attended_student]
#             }

#         return render_template("dashboard.html", classes=teacher_classes, least_attended_students=least_attended_students)
#     return redirect(url_for("admin.index"))


@views.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        teacher_classes = Class.query.filter_by(teacher_id=current_user.id).all()

        # Calculate the average attendance for each student in each class
        # average_attendance = {}
        # for class_ in teacher_classes:
        #     attendance_records = Attendance.query.filter_by(class_id=class_.id).all()
        #     student_attendance = {}
        #     for record in attendance_records:
        #         if record.student_name in student_attendance:
        #             student_attendance[record.student_name] += 1
        #         else:
        #             student_attendance[record.student_name] = 1
        #     total_records = len(attendance_records)
        #     student_average_attendance = {
        #         name: count / total_records
        #         for name, count in student_attendance.items()
        #     }
        #     average_attendance[class_.name] = student_average_attendance

        # Identify the 5 students with the least average attendance in each class
        # least_attended_students = {}
        # for class_name, student_attendance in average_attendance.items():
        #     sorted_students = sorted(student_attendance.items(), key=lambda x: x[1])
        #     least_attended_students[class_name] = sorted_students[:5]

        return render_template(
            "dashboard.html",
            classes=teacher_classes
            # least_attended_students=least_attended_students,
        )
    return redirect(url_for("admin.index"))


@views.route("/class/add", methods=["POST"])
@login_required
def add_class():
    class_name = request.form.get("class_name")
    new_class = Class(name=class_name, teacher_id=current_user.id)
    db.session.add(new_class)
    db.session.commit()
    return redirect(url_for("views.dashboard"))


@views.route("/class/<int:class_id>/edit")
@login_required
def edit_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        return redirect(url_for("views.dashboard"))

    return render_template("edit_class.html", class_=class_)


@views.route("/class/<int:class_id>/update", methods=["POST"])
@login_required
def update_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        return redirect(url_for("views.dashboard"))
    class_.name = request.form.get("class_name")
    db.session.commit()
    return redirect(url_for("views.dashboard"))


@views.route("/class/<int:class_id>/attendance")
@login_required
def class_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)  # Use class_ instead of class
    if class_.teacher_id != current_user.id:
        return redirect(url_for("views.dashboard"))
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()
    return render_template(
        "class_attendence.html", class_=class_, attendance_records=attendance_records
    )


@views.route("/class/<int:class_id>/attendance_records")
@login_required
def attendance_records(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        return redirect(url_for("views.dashboard"))
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()
    return jsonify(
        [
            {
                "student_name": record.student_name,
                "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for record in attendance_records
        ]
    )


# @views.route("/recognize")
# def recognize():
#     return render_template("recognize.html")


@stream_with_context
def generate_frames(class_id):
    # cap = cv2.VideoCapture("C:\\Users\\Aallamprabhu\\Desktop\\CV\\Pro_vid.mp4")  # Change to '0' for webcam or provide video file path
    cap = cv2.VideoCapture(0)  # Change to '0' for webcam or provide video file path
    recognizeed_names = []
    # cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return
    frame_count = 0
    processing_interval = 60
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret or frame.size == 0:
            break
        if frame_count % processing_interval == 0:
            frame = cv2.resize(frame, (600, 400))
            frame_start_time = time.time()
            frame, attendance_records = run_face_recognition(frame, class_id)
            recognizeed_names.extend(attendance_records)
            frame_processing_time = time.time() - frame_start_time
            ret, buffer = cv2.imencode(".jpg", frame)  # Use H.264 codec with
            frame = buffer.tobytes()
            frame_count += 1
            total_time = time.time() - start_time
            fps = frame_count / total_time
            print(
                f"Frame {frame_count}: Processing Time = {frame_processing_time:.2f} s, FPS = {fps:.2f}"
            )
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

            # yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        frame_count += 1
    # After the loop, mark attendance for unique names
    mark_attendance(set(recognizeed_names), class_id)


# cProfile.run('generate_frames(class_id)')


def mark_attendance(names, class_id):
    for name in names:
        attendance = Attendance(student_name=name, class_id=class_id)
        db.session.add(attendance)
    db.session.commit()


# @views.route("/video_feed")
# @views.route("/video_feed/<int:class_id>")
# def video_feed(class_id):
#     return Response(generate_frames(class_id), mimetype="multipart/x-mixed-replace; boundary=frame")


@views.route("/video_feed/<int:class_id>")
@login_required
def video_feed(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        return redirect(url_for("views.dashboard"))
    return Response(generate_frames(class_id), mimetype="multipart/x-mixed-replace; boundary=frame")
