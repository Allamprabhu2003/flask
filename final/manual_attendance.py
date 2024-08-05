from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Attendance, Class, Student
from .extention import db
from datetime import datetime
from . import csrf

manual_attendance = Blueprint("manual_attendance", __name__)
@manual_attendance.route("/manual_attendance/<int:class_id>", methods=["GET", "POST"])
@login_required
@csrf.exempt
def manual_attendance_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    students = Student.query.filter_by(course_type=class_.course_type).all()

    # students = Student.query.filter(Student.classes.any(=class_id)).all()

    if request.method == "POST":
        present_count = 0
        absent_count = 0

        for student in students:
            status = request.form.get(f"status_{student.id}")
            if status == "present":
                present_count += 1
            elif status == "absent":
                absent_count += 1

        if present_count > absent_count:
            default_status = "present"
        else:
            default_status = "absent"

        for student in students:
            status = request.form.get(f"status_{student.id}")
            if status:
                attendance = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    timestamp=datetime.now(),
                    status=status
                )
            else:
                attendance = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    timestamp=datetime.now(),
                    status=default_status
                )
            db.session.add(attendance)

        db.session.commit()
        flash("Attendance marked successfully.", category="success")
        return redirect(url_for("manual_attendance.manual_attendance_class", class_id=class_id))

    return render_template("manual_attendance.html", class_=class_, students=students)
