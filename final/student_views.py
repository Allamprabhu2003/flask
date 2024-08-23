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


# Helper functions
def get_course_types_from_db():
    class_course_types = db.session.query(Class.course_type).distinct().all()
    student_course_types = db.session.query(
        Student.course_type).distinct().all()
    course_types = list(
        set([c[0] for c in class_course_types] +
            [s[0] for s in student_course_types]))
    return course_types


def process_image(image_file):
    image_array = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        return None, "Invalid image file. Please upload a valid image."

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_detector(rgb_image, 1)

    if not face_locations:
        return None, "No face detected in the image. Please try again."

    face_encodings = compute_face_encodings(rgb_image, face_locations)[0]
    return face_encodings, None


# Student Routes
@student.route("/upload", methods=["GET", "POST"])
@login_required
@csrf.exempt
def upload():
    course_types = get_course_types_from_db()
    if request.method == "POST":
        roll_number = request.form.get("roll_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        course_type = request.form.get("course_type")
        new_course_type = request.form.get("new_course_type")
        image_file = request.files.get("image")

        if not all([
                roll_number, first_name, last_name, email, course_type
                or new_course_type, image_file
        ]):
            flash("All fields are required.", "error")
            return redirect(url_for("student.upload"))

        if new_course_type:
            course_type = new_course_type
            if course_type not in course_types:
                course_types.append(course_type)

        try:
            # Check for duplicate roll number and email
            if Student.query.filter_by(roll_number=roll_number).first():
                flash(
                    f"A student with roll number {roll_number} already exists.",
                    "error")
                return redirect(url_for("student.upload"))
            if Student.query.filter_by(email=email).first():
                flash(f"A student with email {email} already exists.", "error")
                return redirect(url_for("student.upload"))

            # Process the image
            face_encodings, error_message = process_image(image_file)
            if error_message:
                flash(error_message, "error")
                return redirect(url_for("student.upload"))

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
            face = Face(student_id=student.id,
                        face_encodings=face_encodings.tobytes())
            db.session.add(face)

            # Find all classes with the same course type
            classes = Class.query.filter_by(course_type=course_type).all()

            # If no classes exist with this course type, create a new one
            if not classes:
                new_class = Class(name=course_type, course_type=course_type)
                db.session.add(new_class)
                classes = [new_class]

            # Add the student to all matching classes
            for class_ in classes:
                class_.students.append(student)

            db.session.commit()
            flash(
                "Student registered and mapped to all relevant classes successfully",
                "success")
            return redirect(url_for("views.dashboard"))

        except IntegrityError:
            db.session.rollback()
            flash("A database error occurred. Please try again.", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")

    return render_template("upload.html", course_types=course_types)


@student.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
@csrf.exempt
def edit(student_id):
    course_types = get_course_types_from_db()
    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        roll_number = request.form.get("roll_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        course_type = request.form.get("course_type")
        new_course_type = request.form.get("new_course_type")
        image_file = request.files.get("image")

        if not all([
                roll_number, first_name, last_name, email, course_type
                or new_course_type
        ]):
            flash("All fields are required except the image.", "error")
            return redirect(url_for("student.edit", student_id=student_id))

        if new_course_type:
            course_type = new_course_type
            if course_type not in course_types:
                course_types.append(course_type)

        try:
            # Check for duplicate roll number and email
            existing_student = Student.query.filter(
                Student.roll_number == roll_number, Student.id
                != student_id).first()
            if existing_student:
                flash(
                    f"A student with roll number {roll_number} already exists.",
                    "error")
                return redirect(url_for("student.edit", student_id=student_id))

            existing_student = Student.query.filter(Student.email == email,
                                                    Student.id
                                                    != student_id).first()
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
                # Process the new image
                face_encodings, error_message = process_image(image_file)
                if error_message:
                    flash(error_message, "error")
                    return redirect(
                        url_for("student.edit", student_id=student_id))

                # Update or create face encoding
                face = Face.query.filter_by(student_id=student.id).first()
                if face:
                    face.face_encodings = face_encodings.tobytes()
                else:
                    face = Face(student_id=student.id,
                                face_encodings=face_encodings.tobytes())
                    db.session.add(face)

            # Remove student from all current classes
            for class_ in student.classes:
                class_.students.remove(student)

            # Find all classes with the new course type
            classes = Class.query.filter_by(course_type=course_type).all()

            # If no classes exist with this course type, create a new one
            if not classes:
                new_class = Class(name=course_type, course_type=course_type)
                db.session.add(new_class)
                classes = [new_class]

            # Add the student to all matching classes
            for class_ in classes:
                class_.students.append(student)

            db.session.commit()
            flash(
                "Student information updated and mapped to all relevant classes successfully",
                "success")
            return redirect(url_for("views.dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("student.edit", student_id=student_id))

    return render_template("std.html",
                           course_types=course_types,
                           student=student)


@student.route("/delete_student", methods=["POST"])
@login_required
@csrf.exempt  # Exempting CSRF protection for the API endpoint
def delete_student():
    data = request.get_json()
    student_id = data.get("id")

    if not student_id:
        return jsonify({
            "success": False,
            "error": "Student ID is required."
        }), 400

    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({
                "success": False,
                "error": "Student not found."
            }), 404

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
