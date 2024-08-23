from cmath import e
from exceptiongroup import catch
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from pytz import timezone
from .models import Attendance, Class, Student
from .extention import db
from datetime import datetime, timedelta
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
        
        try:
            for student in students:
                status = request.form.get(f"status_{student.id}")        

                now = datetime.utcnow()  # Use UTC time
                two_hours_ago = now - timedelta(hours=2)  # Corrected to two hours
                existing_attendance = Attendance.query.filter(
                    Attendance.student_id == student.id,
                    Attendance.class_id == class_id,
                    Attendance.timestamp >= two_hours_ago,
                    Attendance.timestamp <= now,
                ).first()
                
                if status == 'present':
                    if not existing_attendance:
                        new_attendance = Attendance(
                            student_id=student.id,
                            class_id=class_id,
                            status=status,
                            timestamp=now,
                        )
                        db.session.add(new_attendance)
                        flash(
                            f"Attendance marked for {student.first_name} {student.last_name}",
                            "success",
                        )
                        print(
                            f"Attendance marked for {student.first_name} {student.last_name}"
                        )
                    else:
                        flash(
                            f"Attendance already marked for {student.first_name} {student.last_name}",
                            "info",
                        )
                    print(
                            f"Attendance already marked for {student.first_name} {student.last_name} within the last 2 hours"
                        )
                        
                
                elif status == None:
                    print("//////////////000")
                    print("//////////////000")
                    print("//////////////000")
                    print("//////////////000")
                    print("//////////////000")
                    print("//////////////000")

                else:
                    flash(
                            f"Attendance already marked for {student.first_name} {student.last_name}",
                            "info",
                        )
                    print(
                            f"Attendance already marked for {student.first_name} {student.last_name} within the last 2 hours"
                        )
             
        except Exception as e:
            print("Errpr ", str(e))


        db.session.commit()
        flash("Attendance marked successfully.", category="success")
        # return redirect(url_for("views.dashboard"))
        return redirect(url_for("manual_attendance.manual_attendance_class", class_id=class_id))

    return render_template("manual_attendance.html", class_=class_, students=students)
