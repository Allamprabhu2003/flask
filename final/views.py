# # # import cProfile
# # # import time
# # # import cv2
# # # from .models import Attendance, Class, Face, Student
# # # from .utils import compute_face_embeding, run_face_recognition
from collections import defaultdict
from datetime import datetime, timedelta

# # # import numpy as np
import cv2
from flask_login import current_user, login_required
from sqlalchemy import func  # Import func from SQLAlchemy

from flask import (Blueprint, Response, current_app, flash, g, jsonify,
                   redirect, render_template, request, stream_with_context,
                   url_for)

from .extention import db
from .models import Attendance, Class, Face, Student, User

cv2.ocl.setUseOpenCL(True)
views = Blueprint("views", __name__)

# # # # @views.route("/register_student", methods=["GET", "POST"])
# # # # @login_required
# # # # def register_student():
# # # #     if request.method == "POST":
# # # #         first_name = request.form.get("first_name")
# # # #         last_name = request.form.get("last_name")
# # # #         email = request.form.get("email")

# # # #         # Check if a student with this email already exists
# # # #         existing_student = Student.query.filter_by(email=email).first()
# # # #         if existing_student:
# # # #             flash("A student with this email already exists.", "error")
# # # #             return redirect(url_for("views.register_student"))

# # # #         new_student = Student(first_name=first_name, last_name=last_name, email=email)
# # # #         db.session.add(new_student)
# # # #         db.session.commit()

# # # #         flash("Student registered successfully. You can now upload their face image.", "success")
# # # #         return redirect(url_for("views.upload_face", student_id=new_student.id))

# # # #     return render_template("register_student.html")

# # # @views.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
# # # @login_required
# # # def edit_student(student_id):
# # #     student = Student.query.get_or_404(student_id)

# # #     if request.method == "POST":
# # #         student.first_name = request.form.get("first_name")
# # #         student.last_name = request.form.get("last_name")
# # #         student.email = request.form.get("email")
# # #         db.session.commit()
# # #         flash("Student information updated successfully", "success")
# # #         return redirect(url_for("views.dashboard"))

# # #     return render_template("edit_student.html", student=student)

# # @views.route("/delete_class/<int:class_id>", methods=["POST"])
# # @login_required
# # def delete_class(class_id):
# #     class_ = Class.query.get_or_404(class_id)

# #     if current_user not in class_.teachers:
# #         flash("You do not have permission to delete this class", "danger")
# #         return redirect(url_for("views.dashboard"))

# #     db.session.delete(class_)
# #     db.session.commit()
# #     flash(f"Class '{class_.name}' has been deleted.", "success")

# #     return redirect(url_for('views.dashboard'))

# # @views.route("/delete_student_face/<int:student_id>", methods=["POST"])
# # @login_required
# # def delete_student_face(student_id):
# #     student = Student.query.get_or_404(student_id)
# #     face = Face.query.filter_by(student_id=student_id).first()

# #     if face:
# #         db.session.delete(face)
# #         db.session.commit()
# #         flash(f"Face data for {student.first_name} {student.last_name} has been deleted.", "success")
# #     else:
# #         flash(f"No face data found for {student.first_name} {student.last_name}.", "warning")

# #     return redirect(url_for('views.dashboard'))

# # @views.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
# # @login_required
# # def edit_student(student_id):
# #     student = Student.query.get_or_404(student_id)

# #     if request.method == "POST":
# #         student.first_name = request.form.get("first_name")
# #         student.last_name = request.form.get("last_name")
# #         student.email = request.form.get("email")

# #         db.session.commit()
# #         flash(f"Details for {student.first_name} {student.last_name} have been updated.", "success")
# #         return redirect(url_for('views.dashboard'))

# #     return render_template("edit_student.html", student=student)

# # # @views.route("/class/<int:class_id>/attendance_records")
# # # @login_required
# # # def attendance_records(class_id):
# # #     class_ = Class.query.get_or_404(class_id)
# # #     if current_user not in class_.teachers:
# # #         return redirect(url_for("views.dashboard"))
# # #     attendance_records = Attendance.query.filter_by(class_id=class_id).all()
# # #     return jsonify([
# # #         {
# # #             "student_name": f"{record.student.first_name} {record.student.last_name}",
# # #             "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
# # #             "status": record.status
# # #         }
# # #         for record in attendance_records
# # #     ])

# # from datetime import timezone

# # @views.route("/class/<int:class_id>/attendance_records")
# # @login_required
# # def attendance_records(class_id):
# #     class_ = Class.query.get_or_404(class_id)
# #     if current_user not in class_.teachers:
# #         return redirect(url_for("views.dashboard"))

# #     attendance_records = Attendance.query.filter_by(class_id=class_id).all()

# #     records = []
# #     for record in attendance_records:
# #         student = Student.query.get(record.student_id)
# #         student_name = f"{student.first_name} {student.last_name}"

# #         timestamp = record.timestamp.replace(tzinfo=timezone.utc).isoformat()  # Ensure UTC time

# #         # timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
# #         records.append({"student_name": student_name, "timestamp": timestamp})

# #     return jsonify(records)

# # # Clear face data cache before each request
# # @views.before_request
# # def clear_face_data_cache():
# #     if hasattr(g, 'face_data'):
# #         delattr(g, 'face_data')

# # @views.route("/delete_face_embedding/<int:student_id>", methods=["POST"])
# # @login_required
# # def delete_face_embedding(student_id):
# #     student = Student.query.get_or_404(student_id)
# #     face = Face.query.filter_by(student_id=student_id).first()

# #     if face:
# #         db.session.delete(face)
# #         db.session.commit()
# #         flash(f"Face embedding for {student.first_name} {student.last_name} has been deleted.", "success")
# #     else:
# #         flash(f"No face embedding found for {student.first_name} {student.last_name}.", "warning")

# #     return redirect(url_for('views.dashboard'))

# cv2.setUseOptimized(True)
# cv2.ocl.setUseOpenCL(True)

# # compute_face_embeding,
# from sqlalchemy import func
# from . import db
# from .models import Attendance, Class, Face, Student, User
# from collections import defaultdict
# from datetime import datetime, timedelta

views = Blueprint("views", __name__)

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_admin:
#             flash("You need admin privileges to access this page.", "error")
#             return redirect(url_for('views.dashboard'))
#         return f(*args, **kwargs)
#     return decorated_function


@views.route("/")
def index():
    return render_template("home.html")


# # @views.route("/upload", methods=["POST", "GET"])
# # @login_required
# # def upload():
# #     if request.method == "POST":
# #         first_name = request.form["first_name"]
# #         last_name = request.form["last_name"]
# #         email = request.form["email"]
# #         image_file = request.files["image"]
# #         try:
# #             student = Student.query.filter_by(email=email).first()
# #             if not student:
# #                 student = Student(
# #                     first_name=first_name, last_name=last_name, email=email
# #                 )
# #                 db.session.add(student)
# #                 db.session.flush()

# #             # Read the image file
# #             image_array = np.frombuffer(image_file.read(), np.uint8)
# #             image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

# #             # Convert the image to RGB (dlib expects RGB images)
# #             rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# #             # Detect faces in the image
# #             face_locations = face_detector(rgb_image)

# #             if not face_locations:
# #                 flash("No face detected in the image. Please try again.", "error")
# #                 return redirect(url_for("views.upload"))

# #             # Compute face encodings
# #             face_encodings = compute_face_encodings(rgb_image, face_locations)

# #             if len(face_encodings) == 0:
# #                 flash("Failed to compute face encodings. Please try again.", "error")
# #                 return redirect(url_for("views.upload"))

# #             # Use the first face encoding if multiple faces are detected
# #             face_encoding = face_encodings[0]

# #             face = Face.query.filter_by(student_id=student.id).first()
# #             if face:
# #                 face.face_encodings = face_encoding.tobytes()
# #             else:
# #                 face = Face(
# #                     student_id=student.id, face_encodings=face_encoding.tobytes()
# #                 )
# #                 db.session.add(face)

# #             db.session.commit()
# #             flash("Student registered and face uploaded successfully", "success")
# #             return redirect(url_for("views.dashboard"))
# #         except Exception as e:
# #             db.session.rollback()
# #             flash(f"An error occurred: {str(e)}", "error")
# #             return redirect(url_for("views.upload"))
# #     return render_template("upload.html")

# # @views.route("/upload", methods=["POST", "GET"])
# # @login_required
# # def upload():
# #     course_types = ["BCA", "BCS", "BA"]  # Define the course types

# #     if request.method == "POST":
# #         first_name = request.form["first_name"]
# #         last_name = request.form["last_name"]
# #         email = request.form["email"]
# #         course_type = request.form["course_type"]
# #         new_course_type = request.form.get("new_course_type")
# #         image_file = request.files["image"]

# #         if new_course_type:
# #             course_type = new_course_type
# #             if course_type not in course_types:
# #                 course_types.append(course_type)

# #         try:
# #             student = Student.query.filter_by(email=email).first()
# #             if not student:
# #                 student = Student(
# #                     first_name=first_name,
# #                     last_name=last_name,
# #                     email=email,
# #                     course_type=course_type
# #                 )
# #                 db.session.add(student)
# #                 db.session.flush()

# #             # Read the image file
# #             image_array = np.frombuffer(image_file.read(), np.uint8)
# #             image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

# #             # Convert the image to RGB (dlib expects RGB images)
# #             rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# #             # Detect faces in the image
# #             face_locations = face_detector(rgb_image)

# #             if not face_locations:
# #                 flash("No face detected in the image. Please try again.", "error")
# #                 return redirect(url_for("views.upload"))

# #             # Compute face encodings
# #             face_encodings = compute_face_encodings(rgb_image, face_locations)

# #             if len(face_encodings) == 0:
# #                 flash("Failed to compute face encodings. Please try again.", "error")
# #                 return redirect(url_for("views.upload"))

# #             # Use the first face encoding if multiple faces are detected
# #             face_encoding = face_encodings[0]

# #             face = Face.query.filter_by(student_id=student.id).first()
# #             if face:
# #                 face.face_encodings = face_encoding.tobytes()
# #             else:
# #                 face = Face(
# #                     student_id=student.id, face_encodings=face_encoding.tobytes()
# #                 )
# #                 db.session.add(face)

# #             # Create or update the class
# #             class_ = Class.query.filter_by(name=course_type, course_type=course_type).first()
# #             if not class_:
# #                 class_ = Class(name=course_type, course_type=course_type)
# #                 db.session.add(class_)

# #             if student not in class_.students:
# #                 class_.students.append(student)

# #             db.session.commit()
# #             flash("Student registered and face uploaded successfully", "success")
# #             return redirect(url_for("views.dashboard"))
# #         except Exception as e:
# #             db.session.rollback()
# #             flash(f"An error occurred: {str(e)}", "error")
# #             return redirect(url_for("views.upload"))

# #     return render_template("upload.html", course_types=course_types)

# @views.route("/upload", methods=["POST", "GET"])
# @login_required
# def upload():
#     course_types = ["BCA", "BCS", "BA"]  # Define the course types

#     if request.method == "POST":
#         first_name = request.form["first_name"]
#         last_name = request.form["last_name"]
#         email = request.form["email"]
#         course_type = request.form["course_type"]
#         new_course_type = request.form.get("new_course_type")
#         image_file = request.files["image"]

#         if new_course_type:
#             course_type = new_course_type
#             if course_type not in course_types:
#                 course_types.append(course_type)

#         try:
#             student = Student.query.filter_by(email=email).first()
#             if not student:
#                 student = Student(
#                     first_name=first_name,
#                     last_name=last_name,
#                     email=email,
#                     course_type=course_type
#                 )
#                 db.session.add(student)
#                 db.session.flush()

#             # Read the image file
#             image_array = np.frombuffer(image_file.read(), np.uint8)
#             image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

#             # Convert the image to RGB (dlib expects RGB images)
#             rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#             # Detect faces in the image
#             face_locations = face_detector(rgb_image)

#             if not face_locations:
#                 flash("No face detected in the image. Please try again.", "error")
#                 return redirect(url_for("views.upload"))

#             # Compute face encodings
#             face_encodings = compute_face_encodings(rgb_image, face_locations)

#             if len(face_encodings) == 0:
#                 flash("Failed to compute face encodings. Please try again.", "error")
#                 return redirect(url_for("views.upload"))

#             # Use the first face encoding if multiple faces are detected
#             face_encoding = face_encodings[0]

#             face = Face.query.filter_by(student_id=student.id).first()
#             if face:
#                 face.face_encodings = face_encoding.tobytes()
#             else:
#                 face = Face(
#                     student_id=student.id, face_encodings=face_encoding.tobytes()
#                 )
#                 db.session.add(face)

#             # Create or update the class
#             class_ = Class.query.filter_by(name=course_type, course_type=course_type).first()
#             if not class_:
#                 class_ = Class(name=course_type, course_type=course_type)
#                 db.session.add(class_)

#             if student not in class_.students:
#                 class_.students.append(student)

#             db.session.commit()
#             flash("Student registered and face uploaded successfully", "success")
#             return redirect(url_for("views.dashboard"))
#         except Exception as e:
#             db.session.rollback()
#             flash(f"An error occurred: {str(e)}", "error")
#             return redirect(url_for("views.upload"))

#     return render_template("upload.html", course_types=course_types)


def analyze_class_data(class_data):
    class_analysis = defaultdict(
        lambda: {
            "total_students": 0,
            "total_classes": 0,
            "avg_attendance": 0,
            "top_students": [],
            "bottom_students": [],
            "recent_trend": [0] * 7,
            "students": [],
            "attendance_rate": 0,
        })

    class_attendance = defaultdict(lambda: defaultdict(lambda: {
        "present": 0,
        "late": 0,
        "absent": 0
    }))

    now = datetime.now()
    week_ago = now - timedelta(days=7)

    for class_, student, status, attendance_count, last_attendance in class_data:
        analysis = class_analysis[class_.id]
        class_attendance[class_.id][student.id][status] += attendance_count

        if student not in analysis["students"]:
            analysis["students"].append(student)
            analysis["total_students"] += 1

        analysis["total_classes"] = max(
            analysis["total_classes"],
            sum(class_attendance[class_.id][student.id].values()))

        if last_attendance and last_attendance >= week_ago:
            day_index = (now.date() - last_attendance.date()).days
            if 0 <= day_index < 7:
                analysis["recent_trend"][6 - day_index] += 1

    for class_id, analysis in class_analysis.items():
        student_counts = [
            (student, sum(counts.values()))
            for student, counts in class_attendance[class_id].items()
        ]
        if analysis["total_students"] > 0:
            analysis["avg_attendance"] = sum(
                count
                for _, count in student_counts) / analysis["total_students"]

        analysis["top_students"] = sorted(student_counts,
                                          key=lambda x: x[1],
                                          reverse=True)[:5]
        analysis["bottom_students"] = sorted(student_counts,
                                             key=lambda x: x[1])[:3]

        if analysis["total_students"] > 0 and analysis["total_classes"] > 0:
            analysis["attendance_rate"] = (
                sum(count for _, count in student_counts) /
                (analysis["total_students"] * analysis["total_classes"])) * 100

    return class_analysis, class_attendance


# @views.route("/class/<int:class_id>/attendance")
# @login_required
# def class_attendance(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     if current_user not in class_.teachers:
#         return redirect(url_for("views.dashboard"))
#     attendance_records = Attendance.query.filter_by(class_id=class_id).all()
#     print(attendance_records)
#     return render_template(
#         "class_attendance.html", class_=class_, attendance_records=attendance_records
#     )


@views.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.index"))

    teacher_classes = Class.query.filter(
        Class.teachers.any(id=current_user.id)).all()
    class_data = get_class_data(teacher_classes)
    class_analysis, class_attendance = analyze_class_data(class_data)

    course_types = ["BCA", "BCS", "BA"]  # Add this line

    return render_template(
        "dashboard.html",
        classes=teacher_classes,
        class_analysis=class_analysis,
        class_attendance=class_attendance,
        course_types=course_types  # Add this line
    )


# @views.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
# @login_required
# def edit_class(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     if current_user not in class_.teachers:
#         flash("You do not have permission to edit this class", "danger")
#         return redirect(url_for("views.dashboard"))

#     if request.method == "POST":
#         class_.name = request.form.get("class_name")
#         db.session.commit()
#         flash("Class updated successfully", "success")
#         return redirect(url_for("views.dashboard"))

#     return render_template("edit_class.html", class_=class_)

# # @views.route("/class/add", methods=["GET", "POST"])
# # @login_required
# # # @admin_required
# # # def add_class():

# #     if request.method == "POST":
# #         class_name = request.form.get("class_name")
# #         new_class = Class(name=class_name)
# #         new_class.teachers.append(current_user)
# #         db.session.add(new_class)
# #         db.session.commit()
# #         flash("Class created successfully", "success")
# #         print("Class created successfully")
# #         return redirect(url_for("views.dashboard"))
# #     return render_template("add_class.html")

# @views.route("/class/add", methods=["GET", "POST"])
# @login_required
# def add_class():
#     course_types = ["BCA", "BCS", "BA"]
#     if request.method == "POST":
#         class_name = request.form.get("class_name")
#         course_type = request.form.get("course_type")
#         new_class = Class(name=class_name, course_type=course_type)
#         new_class.teachers.append(current_user)
#         db.session.add(new_class)
#         db.session.commit()
#         flash("Class created successfully", "success")
#         return redirect(url_for("views.dashboard"))

#     return render_template("dashboard.html", course_types=course_types)

# @views.route("/register_student", methods=["GET", "POST"])
# @login_required
# @admin_required
# def register_student():
#     if request.method == "POST":
#         first_name = request.form.get("first_name")
#         last_name = request.form.get("last_name")
#         email = request.form.get("email")

#         existing_student = Student.query.filter_by(email=email).first()
#         if existing_student:
#             flash("A student with this email already exists.", "error")
#             return redirect(url_for("views.register_student"))

#         new_student = Student(first_name=first_name, last_name=last_name, email=email)
#         db.session.add(new_student)
#         db.session.commit()

#         flash("Student registered successfully. You can now upload their face image.", "success")

#         return redirect(url_for("views.upload_face", student_id=new_student.id))

#     return render_template("register_student.html")

# @views.route("/delete_student_face/<int:student_id>", methods=["POST"])
# @login_required
# def delete_student_face(student_id):
#     student = Student.query.get_or_404(student_id)
#     face = Face.query.filter_by(student_id=student_id).first()

#     if face:
#         db.session.delete(face)
#         db.session.commit()
#         flash(
#             f"Face data for {student.first_name} {student.last_name} has been deleted.",
#             "success",
#         )
#     else:
#         flash(
#             f"No face data found for {student.first_name} {student.last_name}.",
#             "warning",
#         )

#     return redirect(url_for("views.dashboard"))

# @views.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
# @login_required
# def edit_student(student_id):
#     student = Student.query.get_or_404(student_id)

#     if request.method == "POST":
#         student.first_name = request.form.get("first_name")
#         student.last_name = request.form.get("last_name")
#         student.email = request.form.get("email")

#         db.session.commit()
#         flash(
#             f"Details for {student.first_name} {student.last_name} have been updated.",
#             "success",
#         )
#         return redirect(url_for("views.dashboard"))

#     return render_template("edit_student.html", student=student)

# from datetime import timezone

# @views.route("/class/<int:class_id>/attendance_records")
# @login_required
# def attendance_records(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     if current_user not in class_.teachers:
#         return redirect(url_for("views.dashboard"))

#     attendance_records = Attendance.query.filter_by(class_id=class_id).all()

#     records = []
#     for record in attendance_records:
#         student = Student.query.get(record.student_id)
#         student_name = f"{student.first_name} {student.last_name}"

#         timestamp = record.timestamp.replace(
#             tzinfo=timezone.utc
#         ).isoformat()  # Ensure UTC time

#         # timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
#         records.append({"student_name": student_name, "timestamp": timestamp})

#     return jsonify(records)


def get_class_data(teacher_classes):
    return (db.session.query(
        Class,
        Student,
        Attendance.status,
        func.count(Attendance.id).label("attendance_count"),
        func.max(Attendance.timestamp).label("last_attendance"),
    ).join(Attendance, Attendance.class_id == Class.id).join(
        Student, Student.id == Attendance.student_id).filter(
            Class.id.in_([c.id for c in teacher_classes
                          ])).group_by(Class.id, Student.id,
                                       Attendance.status).all())


# # @views.route("/upload_face/<int:student_id>", methods=["GET", "POST"])
# # @login_required
# # def upload_face(student_id):
# #     student = Student.query.get_or_404(student_id)

# #     if request.method == "POST":
# #         if "image" not in request.files:
# #             flash("No file part", "error")
# #             return redirect(request.url)

# #         file = request.files["image"]

# #         if file.filename == "":
# #             flash("No selected file", "error")
# #             return redirect(request.url)

# #         if file:
# #             try:
# #                 image = cv2.imdecode(
# #                     np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR
# #                 )
# #                 face_encodings = compute_face_embedding(image)
# #                 # face_encodings = compute_face_descriptor(image)

# #                 if face_encodings is None:
# #                     flash("No face detected in the image. Please try again.", "error")
# #                     return redirect(request.url)

# #                 existing_face = Face.query.filter_by(student_id=student.id).first()
# #                 if existing_face:
# #                     existing_face.face_encodings = face_encodings.tobytes()
# #                 else:
# #                     new_face = Face(
# #                         student_id=student.id, face_encodings=face_encodings.tobytes()
# #                     )
# #                     db.session.add(new_face)

# #                 db.session.commit()
# #                 flash("Face image uploaded successfully", "success")
# #                 return redirect(url_for("views.dashboard"))
# #             except Exception as e:
# #                 flash(f"Error processing image: {str(e)}", "error")
# #                 return redirect(request.url)

# #     return render_template("upload_face.html", student=student)

# # from multiprocessing import Pool

# # def encode_frame(frame):
# #     return cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])[1].tobytes()

# # # Initialize the pool outside your main loop
# # pool = Pool(processes=4)  # Adjust based on your CPU cores

# def update_attendance(recognized_names, class_id):
#     with current_app.app_context():
#         class_ = Class.query.get(class_id)
#         print(class_)
#         if not class_:
#             print(class_)
#             flash("Class not found", "error")
#             return

#         for name in set(recognized_names):  # Use set to avoid duplicates
#             student = Student.query.filter_by(first_name=name).first()

#             print(student)
#             if student and student in class_.students:
#                 # Check if attendance already exists for today
#                 existing_attendance = Attendance.query.filter(
#                     Attendance.student_id == student.id,
#                     Attendance.class_id == class_id,
#                     func.date(Attendance.timestamp) == func.current_date()
#                 ).first()

#                 if not existing_attendance:
#                     attendance = Attendance(
#                         student_id=student.id,
#                         class_id=class_id,
#                         status="present"
#                     )
#                     db.session.add(attendance)
#                     flash(f"Attendance marked for {student.first_name} {student.last_name}", "success")
#                 else:
#                     flash(f"Attendance already marked for {student.first_name} {student.last_name}", "info")
#             elif student:
#                 print("Not from this class ")
#                 flash(f"{student.first_name} {student.last_name} is not a member of this class", "warning")
#             else:
#                 flash(f"Student {name} not found in the database", "warning")
#                 print(f"Student {name} not found in the database")

#         db.session.commit()

# # Clear face data cache before each request
# @views.before_request
# def clear_face_data_cache():
#     if hasattr(g, "face_data"):
#         delattr(g, "face_data")

# @views.route("/delete_face_embedding/<int:student_id>", methods=["POST"])
# @login_required
# def delete_face_embedding(student_id):
#     student = Student.query.get_or_404(student_id)
#     face = Face.query.filter_by(student_id=student_id).first()

#     if face:
#         db.session.delete(face)
#         db.session.commit()
#         flash(
#             f"Face embedding for {student.first_name} {student.last_name} has been deleted.",
#             "success",
#         )
#     else:
#         flash(
#             f"No face embedding found for {student.first_name} {student.last_name}.",
#             "warning",
#         )

#     return redirect(url_for("views.dashboard"))
