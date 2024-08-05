# Import necessary modules
import os

import cv2
import numpy as np
from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from . import csrf
from .extention import db
from .models import Attendance, Class, Face, Student
from .Vision.utils import compute_face_encodings, face_detector

# Create a Blueprint for student routes
student = Blueprint("student", __name__)


# Define a function to get course types from the database
def get_course_types_from_db():
    class_course_types = db.session.query(Class.course_type).distinct().all()
    student_course_types = db.session.query(Student.course_type).distinct().all()
    course_types = list(
        set([c[0] for c in class_course_types] + [s[0] for s in student_course_types])
    )
    return course_types


# Define a function to check if a file is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Define a function to save an image
def save_image(image_file):
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_path = os.path.join("", filename)
        image_file.save(image_path)
        return image_path
    return None


# Student Routes
@student.route("/register_student", methods=["GET", "POST"])
@login_required
def register_student():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")

        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash("A student with this email already exists.", "error")
            return redirect(url_for("student.register_student"))

        new_student = Student(first_name=first_name, last_name=last_name, email=email)
        db.session.add(new_student)
        db.session.commit()

        flash(
            "Student registered successfully. You can now upload their face image.",
            "success",
        )
        return redirect(url_for("student.upload_face", student_id=new_student.id))

    return render_template("register_student.html")


@student.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
@csrf.exempt
def edit(student_id):
    course_types = (
        get_course_types_from_db()
    )  # You might want to fetch this from the database
    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        roll_number = request.form.get("roll_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        course_type = request.form.get("course_type")
        new_course_type = request.form.get("new_course_type")
        image_file = request.files.get("image")

        if not all(
            [roll_number, first_name, last_name, email, course_type or new_course_type]
        ):
            flash("All fields are required except the image.", "error")
            return redirect(url_for("student.edit", student_id=student_id))

        if new_course_type:
            course_type = new_course_type
            if course_type not in course_types:
                course_types.append(course_type)

        try:
            # Check for duplicate roll number
            existing_student = Student.query.filter(
                Student.roll_number == roll_number, Student.id != student_id
            ).first()
            if existing_student:
                flash(
                    f"A student with roll number {roll_number} already exists.", "error"
                )
                return redirect(url_for("student.edit", student_id=student_id))

            # Check for duplicate email
            existing_student = Student.query.filter(
                Student.email == email, Student.id != student_id
            ).first()
            if existing_student:
                flash(f"A student with email {email} already exists.", "error")
                return redirect(url_for("student.edit", student_id=student_id))

            # Update student information
            student.roll_number = roll_number
            student.first_name = first_name
            student.last_name = last_name
            student.email = email
            student.course_type = course_type

            if image_file:
                # Read and process the image
                image_array = np.frombuffer(image_file.read(), np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                if image is None:
                    flash("Invalid image file. Please upload a valid image.", "error")
                    return redirect(url_for("student.edit", student_id=student_id))

                # Convert the image to RGB (dlib expects RGB images)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Detect faces
                face_locations = face_detector(rgb_image, 1)

                if not face_locations:
                    flash("No face detected in the image. Please try again.", "error")
                    return redirect(url_for("student.edit", student_id=student_id))

                # Compute face encodings
                face_encoding = compute_face_encodings(rgb_image, face_locations)[
                    0
                ]  # Get the first face encoding

                # Save or update the face encoding
                face = Face.query.filter_by(student_id=student.id).first()
                if face:
                    face.face_encodings = face_encoding.tobytes()
                else:
                    face = Face(
                        student_id=student.id, face_encodings=face_encoding.tobytes()
                    )
                    db.session.add(face)

            # Update the class
            class_ = Class.query.filter_by(
                name=course_type, course_type=course_type
            ).first()
            if not class_:
                class_ = Class(name=course_type, course_type=course_type)
                db.session.add(class_)

            if student not in class_.students:
                class_.students.append(student)

            db.session.commit()
            flash("Student information updated successfully", "success")
            return redirect(url_for("views.dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("student.edit", student_id=student_id))

    return render_template("std.html", course_types=course_types, student=student)


def get_course_types_from_db():
    class_course_types = db.session.query(Class.course_type).distinct().all()
    student_course_types = db.session.query(Student.course_type).distinct().all()

    # Combine the two lists and remove duplicates
    course_types = list(
        set([c[0] for c in class_course_types] + [s[0] for s in student_course_types])
    )
    return course_types


# Student Routes
@student.route("/upload", methods=["GET", "POST"])
@login_required
@csrf.exempt
def upload():
    course_types = get_course_types_from_db()
    print(course_types)
    if request.method == "POST":
        roll_number = request.form.get("roll_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        course_type = request.form.get("course_type")
        new_course_type = request.form.get("new_course_type")
        image_file = request.files.get("image")

        if not all(
            [
                roll_number,
                first_name,
                last_name,
                email,
                course_type or new_course_type,
                image_file,
            ]
        ):
            flash("All fields are required.", "error")
            return redirect(url_for("student.upload"))

        if new_course_type:
            course_type = new_course_type
            if course_type not in course_types:
                course_types.append(course_type)

        try:
            # Check for duplicate roll number
            if Student.query.filter_by(roll_number=roll_number).first():
                flash(
                    f"A student with roll number {roll_number} already exists.", "error"
                )
                return redirect(url_for("student.upload"))

            # Check for duplicate email
            if Student.query.filter_by(email=email).first():
                flash(f"A student with email {email} already exists.", "error")
                return redirect(url_for("student.upload"))

            # Save and process the image
            image_path = save_image(image_file)
            if not image_path:
                flash("Invalid image file. Please upload a valid image.", "error")
                return redirect(url_for("student.upload"))

            image = cv2.imread(image_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Here you would typically use a face detection library
            # For this example, we'll assume the face is detected successfully
            face_encoding = np.random.rand(128)  # Placeholder for face encoding

            # Save the student data
            student = Student(
                roll_number=roll_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                course_type=course_type,
            )
            db.session.add(student)
            db.session.flush()

            # Save the face encoding
            face = Face(student_id=student.id, face_encodings=face_encoding.tobytes())
            db.session.add(face)

            # Create or update the class
            class_ = Class.query.filter_by(
                name=course_type, course_type=course_type
            ).first()
            if not class_:
                class_ = Class(name=course_type, course_type=course_type)
                db.session.add(class_)

            class_.students.append(student)

            db.session.commit()
            flash("Student registered and face uploaded successfully", "success")
            return redirect(url_for("views.dashboard"))

        except IntegrityError:
            db.session.rollback()
            flash("A database error occurred. Please try again.", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")

    return render_template("upload.html", course_types=course_types)


@student.route("/delete_student", methods=["POST"])
@login_required
@csrf.exempt  # Exempting CSRF protection for the API endpoint
def delete_student():
    data = request.get_json()
    student_id = data.get("id")

    if not student_id:
        return jsonify({"success": False, "error": "Student ID is required."}), 400

    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"success": False, "error": "Student not found."}), 404

        # Delete related attendance records
        Attendance.query.filter_by(student_id=student.id).delete()

        # Delete related face data
        Face.query.filter_by(student_id=student.id).delete()

        # Remove the student from any classes
        for class_ in student.classes:
            class_.students.remove(student)

        # Delete the student
        db.session.delete(student)
        db.session.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
