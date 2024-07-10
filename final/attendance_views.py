from flask import Blueprint, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Class, Attendance, Student
from sqlalchemy import func
from datetime import timezone
print("dnkjadsfkll")

attendance = Blueprint('attendance', __name__)

@attendance.route("/class/<int:class_id>/attendance")
@login_required
def class_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()
    return render_template("class_attendance.html", class_=class_, attendance_records=attendance_records)

@attendance.route("/class/<int:class_id>/attendance_records")
@login_required
def attendance_records(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))

    attendance_records = Attendance.query.filter_by(class_id=class_id).all()

    records = []
    for record in attendance_records:
        student = Student.query.get(record.student_id)
        student_name = f"{student.first_name} {student.last_name}"
        timestamp = record.timestamp.replace(tzinfo=timezone.utc).isoformat()
        records.append({"student_name": student_name, "timestamp": timestamp})

    return jsonify(records)

# Add other attendance-related routes here