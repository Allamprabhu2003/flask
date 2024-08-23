from collections import defaultdict
import csv
from datetime import datetime, timezone, timedelta
from io import StringIO
from flask import Blueprint, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Attendance, Class, Student
from . import csrf
from .extention import db

attendance = Blueprint('attendance', __name__)

@attendance.route("/<int:class_id>/attendance")
@login_required
def class_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()

    return render_template("class_attendance.html",
                           class_=class_,
                           attendance_records=attendance_records)


@attendance.route("/<int:class_id>/attendance_records")
@login_required
def attendance_records(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))

    date_str = request.args.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = datetime.combine(selected_date, datetime.min.time())
        end_date = datetime.combine(selected_date + timedelta(days=1),
                                    datetime.min.time())
        attendance_records = Attendance.query.filter(
            Attendance.class_id == class_id, Attendance.timestamp
            >= start_date, Attendance.timestamp < end_date).all()
    else:
        attendance_records = Attendance.query.filter_by(
            class_id=class_id).all()

    records = []
    for record in attendance_records:
        student = Student.query.get(record.student_id)
        student_name = f"{student.first_name} {student.last_name}"
        roll_number = student.roll_number  # Fetch the roll number

        timestamp = record.timestamp.replace(tzinfo=timezone.utc).isoformat()
        records.append({
            "student_name": student_name,
            "roll_number": roll_number,
            "timestamp": timestamp,
            "status": record.status
        })

    return jsonify(records)




# Import necessary modules
from collections import defaultdict
import csv
from datetime import datetime, timezone, timedelta
from io import StringIO

from flask import Blueprint, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .models import Attendance, Class, Student

# Create a Blueprint for attendance routes
attendance = Blueprint('attendance', __name__)


# Define a function to get attendance records for a class
def get_attendance_records(class_id, date_str=None):
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = datetime.combine(selected_date, datetime.min.time())
        end_date = datetime.combine(selected_date + timedelta(days=1),
                                    datetime.min.time())
        return Attendance.query.filter(Attendance.class_id == class_id,
                                       Attendance.timestamp >= start_date,
                                       Attendance.timestamp < end_date).all()
    else:
        return Attendance.query.filter_by(class_id=class_id).all()


# Define a route for class attendance
@attendance.route("/<int:class_id>/attendance")
@login_required
def class_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))
    attendance_records = get_attendance_records(class_id)
    return render_template("class_attendance.html",
                           class_=class_,
                           attendance_records=attendance_records)

@attendance.route("/<int:class_id>/attendance_records")
@login_required
def attendance_records(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))

    date_str = request.args.get('date')
    attendance_records = get_attendance_records(class_id, date_str)

    records = []
    for record in attendance_records:
        student = Student.query.get(record.student_id)
        student_name = f"{student.first_name} {student.last_name}"
        roll_number = student.roll_number

        timestamp = record.timestamp.replace(tzinfo=timezone.utc).isoformat()

        records.append({
            "id": record.id,  # Include attendance_id here
            "student_name": student_name,
            "roll_number": roll_number,
            "timestamp": timestamp,
            "status": record.status
        })

    return jsonify(records)


# Define a function to generate CSV data
def generate_csv_data(attendance_records):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Student Name", "Roll Number", "Present", "Late", "Absent"])

    student_data = defaultdict(lambda: {
        "present": 0,
        "absent": 0,
        "roll_number": ""
    })

    for record in attendance_records:
        student = Student.query.get(record.student_id)
        student_name = f"{student.first_name} {student.last_name}"
        student_data[student_name]["roll_number"] = student.roll_number
        student_data[student_name][record.status.lower()] += 1

    for student_name, counts in student_data.items():
        cw.writerow([
            student_name, counts["roll_number"], counts["present"],
             counts["absent"]
        ])

    return si.getvalue()


# Define a route to download CSV data
@attendance.route("/<int:class_id>/download_csv")
@login_required
def download_csv(class_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return redirect(url_for("views.dashboard"))

    date_str = request.args.get('date')
    attendance_records = get_attendance_records(class_id, date_str)

    csv_data = generate_csv_data(attendance_records)

    output = make_response(csv_data)
    output.headers["Content-Disposition"] = (
        f"attachment; filename={class_.name}_attendance.csv")
    output.headers["Content-type"] = "text/csv"
    return output


@attendance.route("/<int:class_id>/get_attendance/<int:attendance_id>",
                  methods=['GET'])
@login_required
@csrf.exempt
def get_attendance(class_id, attendance_id):
    class_ = Class.query.get_or_404(class_id)
    if current_user not in class_.teachers:
        return jsonify({"error": "Unauthorized"}), 403

    attendance_record = Attendance.query.get(attendance_id)
    if not attendance_record or attendance_record.class_id != class_id:
        return jsonify({"error": "Attendance record not found"}), 404

    return jsonify({"status": attendance_record.status}), 200


@attendance.route("/<int:class_id>/edit_attendance", methods=['POST'])
@login_required
@csrf.exempt
def edit_attendance(class_id):
    try:
        class_ = Class.query.get_or_404(class_id)
        if current_user not in class_.teachers:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        new_status = data.get('status')

        # Get the attendance_id from the query string
        attendance_id = request.args.get('attendance_id')

        if not attendance_id or new_status not in ['Present', 'Absent']:
            return jsonify({"error": "Invalid data"}), 400

        attendance_record = Attendance.query.get(attendance_id)
        if not attendance_record or attendance_record.class_id != class_id:
            return jsonify({"error": "Attendance record not found"}), 404

        attendance_record.status = new_status
        db.session.commit()

        return jsonify({"message": "Attendance updated successfully"}), 200

    except Exception as e:
        print(f"Error occurred: {e}")  # This will print the error in your logs
        return jsonify({"error": "Internal Server Error"}), 500
