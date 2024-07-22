import cv2
import numpy as np
from flask_login import login_required

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .models import Class, Face, Student, Attendance
from .utils import compute_face_encodings

student = Blueprint('student', __name__)

import cv2
import numpy as np
from flask_login import login_required

from flask import (Blueprint, flash, redirect, render_template,
                   request, url_for)
from . import csrf
from .extention import db
from .models import Class, Face, Student
from .utils import compute_face_encodings, face_detector

student = Blueprint('student', __name__)

@student.route("/register_student", methods=["GET", "POST"])
@login_required
# @admin_required
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

        flash("Student registered successfully. You can now upload their face image.", "success")
        return redirect(url_for("student.upload_face", student_id=new_student.id))

    return render_template("register_student.html")

# @student.route("/upload", methods=["GET", "POST"])
# @login_required
# def upload():
#     course_types = ["BCA", "BCS", "BA"]  # You might want to fetch this from the database
    
#     if request.method == "POST":
#         first_name = request.form.get("first_name")
#         last_name = request.form.get("last_name")
#         email = request.form.get("email")
#         course_type = request.form.get("course_type")
#         new_course_type = request.form.get("new_course_type")
#         image_file = request.files.get("image")
        
#         if not all([first_name, last_name, email, course_type or new_course_type, image_file]):
#             flash("All fields are required.", "error")
#             print("All fields are required.", "error")
#             return redirect(url_for("student.upload"))
        
#         if new_course_type:
#             course_type = new_course_type
#             if course_type not in course_types:
#                 course_types.append(course_type)
        
#         try:
#             # Read and process the image
#             image_array = np.frombuffer(image_file.read(), np.uint8)
#             image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
#             if image is None:
#                 flash("Invalid image file. Please upload a valid image.", "error")
#                 print("Invalid image file. Please upload a valid image.", "error")
#                 return redirect(url_for("student.upload"))
            
#             # Convert the image to RGB (dlib expects RGB images)
#             rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
#             # Detect faces
#             face_locations = face_detector(rgb_image, 1)
            
#             if not face_locations:
#                 flash("No face detected in the image. Please try again.", "error")
#                 print("No face detected in the image. Please try again.", "error")
#                 return redirect(url_for("student.upload"))
            
#             # Compute face encodings
#             face_encoding = compute_face_encodings(rgb_image, face_locations)[0]  # Get the first face encoding
            
#             # Save the student data
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
            
#             # Save or update the face encoding
#             face = Face.query.filter_by(student_id=student.id).first()
#             if face:
#                 face.face_encodings = face_encoding.tobytes()
#             else:
#                 face = Face(
#                     student_id=student.id,
#                     face_encodings=face_encoding.tobytes()
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
#             print("Student registered and face uploaded successfully", "success")
#             return redirect(url_for("views.dashboard"))
        
#         except Exception as e:
#             db.session.rollback()
#             flash(f"An error occurred: {str(e)}", "error")
#             print(f"An error occurred: {str(e)}", "error")
#             return redirect(url_for("student.upload"))
    
#     return render_template("upload.html", course_types=course_types)

# # Add other student-related routes here
from . import csrf
@student.route("/upload", methods=["GET", "POST"])
@login_required
# @csrf.exempt
def upload():
    course_types = ["BCA", "BCS", "BA"]  # You might want to fetch this from the database
    
    if request.method == "POST":
        roll_number = request.form.get("roll_number")
        print(roll_number)
        first_name = request.form.get("first_name")
        print(first_name)
        last_name = request.form.get("last_name")
        print(last_name)
        email = request.form.get("email")
        print(email)
        course_type = request.form.get("course_type")
        print(course_type)
        new_course_type = request.form.get("new_course_type")
        image_file = request.files.get("image")
        print(image_file)
        
        if not all([roll_number, first_name, last_name, email, course_type or new_course_type, image_file]):
            flash("All fields are required.", "error")
            print("All fields are required.", "error")
            print("All fields are required.", "error")
            print("All fields are required.", "error")
            print("All fields are required.", "error")
            return redirect(url_for("student.upload"))
        
        if new_course_type:
            course_type = new_course_type
            if course_type not in course_types:
                course_types.append(course_type)
        
        try:
            # Read and process the image
            image_array = np.frombuffer(image_file.read(), np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                flash("Invalid image file. Please upload a valid image.", "error")
                print("Invalid image file. Please upload a valid image.", "error")
                return redirect(url_for("student.upload"))
            
            # Convert the image to RGB (dlib expects RGB images)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_detector(rgb_image, 1)
            
            if not face_locations:
                flash("No face detected in the image. Please try again.", "error")
                print("No face detected in the image. Please try again.", "error")
                return redirect(url_for("student.upload"))
            
            # Compute face encodings
            face_encoding = compute_face_encodings(rgb_image, face_locations)[0]  # Get the first face encoding
            
            # Save the student data
            student = Student.query.filter_by(email=email).first()
            if not student:
                student = Student(
                    roll_number=roll_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    course_type=course_type
                )
                db.session.add(student)
                db.session.flush()
            
            # Save or update the face encoding
            face = Face.query.filter_by(student_id=student.id).first()
            if face:
                face.face_encodings = face_encoding.tobytes()
            else:
                face = Face(
                    student_id=student.id,
                    face_encodings=face_encoding.tobytes()
                )
                db.session.add(face)
            
            # Create or update the class
            class_ = Class.query.filter_by(name=course_type, course_type=course_type).first()
            if not class_:
                class_ = Class(name=course_type, course_type=course_type)
                db.session.add(class_)
            
            if student not in class_.students:
                class_.students.append(student)
            
            db.session.commit()
            flash("Student registered and face uploaded successfully", "success")
            print("Student registered and face uploaded successfully", "success")
            return redirect(url_for("views.dashboard"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            print(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("student.upload"))
    
    return render_template("upload.html", course_types=course_types)



from flask import jsonify

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






@student.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit(student_id):
    course_types = ["BCA", "BCS", "BA"]  # You might want to fetch this from the database
    student = Student.query.get_or_404(student_id)
    
    if request.method == "POST":
        roll_number = request.form.get("roll_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        course_type = request.form.get("course_type")
        new_course_type = request.form.get("new_course_type")
        image_file = request.files.get("image")
        
        if not all([roll_number, first_name, last_name, email, course_type or new_course_type]):
            flash("All fields are required except the image.", "error")
            return redirect(url_for("student.edit", student_id=student_id))
        
        if new_course_type:
            course_type = new_course_type
            if course_type not in course_types:
                course_types.append(course_type)
        
        try:
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
                face_encoding = compute_face_encodings(rgb_image, face_locations)[0]  # Get the first face encoding
                
                # Save or update the face encoding
                face = Face.query.filter_by(student_id=student.id).first()
                if face:
                    face.face_encodings = face_encoding.tobytes()
                else:
                    face = Face(
                        student_id=student.id,
                        face_encodings=face_encoding.tobytes()
                    )
                    db.session.add(face)
            
            # Update the class
            class_ = Class.query.filter_by(name=course_type, course_type=course_type).first()
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
