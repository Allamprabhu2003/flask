import csv
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import cv2
from flask import (Blueprint, flash, make_response, redirect, render_template,
                   url_for)
from flask_login import current_user, login_required
from sqlalchemy import func  # Import func from SQLAlchemy

from .extention import db
from .models import Attendance, Class, Student

cv2.ocl.setUseOpenCL(True)
views = Blueprint("views", __name__)


@views.route("/")
def index():
    return render_template("home.html")


# def analyze_class_data(class_data):
#     class_analysis = defaultdict(
#         lambda: {
#             "total_students": 0,
#             "total_classes": 0,
#             "avg_attendance": 0,
#             "top_students": [],
#             "bottom_students": [],
#             "recent_trend": [0] * 7,
#             "students": [],
#             "attendance_rate": 0,
#         })

#     class_attendance = defaultdict(lambda: defaultdict(lambda: {
#         "present": 0,
#         "late": 0,
#         "absent": 0
#     }))

#     now = datetime.now()
#     week_ago = now - timedelta(days=7)

#     for class_, student, status, attendance_count, last_attendance in class_data:
#         analysis = class_analysis[class_.id]
#         class_attendance[class_.id][student.id][status] += attendance_count

#         if student not in analysis["students"]:
#             analysis["students"].append(student)
#             analysis["total_students"] += 1

#         analysis["total_classes"] = max(
#             analysis["total_classes"],
#             sum(class_attendance[class_.id][student.id].values()),
#         )

#         if last_attendance and last_attendance >= week_ago:
#             day_index = (now.date() - last_attendance.date()).days
#             if 0 <= day_index < 7:
#                 analysis["recent_trend"][6 - day_index] += 1

#     for class_id, analysis in class_analysis.items():
#         student_counts = [
#             (student, sum(counts.values()))
#             for student, counts in class_attendance[class_id].items()
#         ]
#         if analysis["total_students"] > 0:
#             analysis["avg_attendance"] = (sum(count
#                                               for _, count in student_counts) /
#                                           analysis["total_students"])

#         analysis["top_students"] = sorted(student_counts,
#                                           key=lambda x: x[1],
#                                           reverse=True)[:5]
#         analysis["bottom_students"] = sorted(student_counts,
#                                              key=lambda x: x[1])[:3]

#         if analysis["total_students"] > 0 and analysis["total_classes"] > 0:
#             analysis["attendance_rate"] = (
#                 sum(count for _, count in student_counts) /
#                 (analysis["total_students"] * analysis["total_classes"])) * 100

#     return class_analysis, class_attendance


# @views.route("/dashboard")
# @login_required
# def dashboard():
#     students = Student.query.all()

#     if current_user.is_admin:
#         return redirect(url_for("admin.index"))

#     teacher_classes = Class.query.filter(
#         Class.teachers.any(id=current_user.id)).all()
#     class_data = get_class_data(teacher_classes)
#     class_analysis, class_attendance = analyze_class_data(class_data)

#     course_types = ["BCA", "BCS", "BA"]

#     courses_data = {}
#     for class_ in teacher_classes:
#         if class_.course_type not in courses_data:
#             courses_data[class_.course_type] = {
#                 "name": class_.course_type,
#                 "total_students": 0,
#             }
#         courses_data[class_.course_type]["total_students"] += (
#             db.session.query(func.count(Student.id)).filter(
#                 Student.classes.any(id=class_.id)).scalar())

#     return render_template(
#         "dashboard.html",
#         classes=teacher_classes,
#         class_analysis=class_analysis,
#         class_attendance=class_attendance,
#         course_types=course_types,
#         courses_data=courses_data,
#         students=students
#     )







from collections import defaultdict
from datetime import datetime, timedelta

from flask import jsonify, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from .extention import db
from .models import Attendance, Class, Student


@views.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.index"))
    
    course_types = ["BCA", "BCS", "BA"]

    teacher_classes = Class.query.filter(Class.teachers.any(id=current_user.id)).all()
    class_analysis = analyze_class_data(teacher_classes)

    return render_template(
        "dashboard.html",
        classes=teacher_classes,
        class_analysis=class_analysis,
        course_types=course_types,
    )

@views.route("/full-screen-plot/<int:class_id>")
@login_required
def full_screen_plot(class_id):
    class_ = Class.query.get_or_404(class_id)
    class_analysis = analyze_class_data([class_])
    return render_template("full_screen_plot.html", class_=class_, analysis=class_analysis[class_.id])

def analyze_class_data(classes):
    class_analysis = {}
    for class_ in classes:
        analysis = {
            "total_students": 0,
            "avg_attendance": 0,
            "attendance_rate": 0,
            "top_students": [],
            "bottom_students": [],
            "dates": [],
            "attendance_counts": [],
            
        }

        # Get all students in this class
        students = Student.query.filter(Student.classes.any(id=class_.id)).all()
        analysis["total_students"] = len(students)

        # Get attendance data for the last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=129)
        attendances = Attendance.query.filter(
            Attendance.class_id == class_.id,
            Attendance.timestamp >= start_date,
            Attendance.timestamp <= end_date + timedelta(days=1)  # Include the entire last day
        ).order_by(Attendance.timestamp).all()

        # Process attendance data
        date_attendance = defaultdict(int)
        student_attendance = defaultdict(int)
        for attendance in attendances:
            attendance_date = attendance.timestamp.date()
            date_attendance[attendance_date] += 1
            student_attendance[attendance.student_id] += 1

        # Calculate average attendance and attendance rate
        total_attendance = sum(date_attendance.values())
        num_days = len(date_attendance)
        total_possible_attendances = analysis["total_students"] * num_days

        if num_days > 0:
            analysis["avg_attendance"] = total_attendance / num_days
        else:
            analysis["avg_attendance"] = 0

        if total_possible_attendances > 0:
            analysis["attendance_rate"] = (total_attendance / total_possible_attendances) * 100
        else:
            analysis["attendance_rate"] = 0

        # Prepare data for the attendance trend chart
        for date in (start_date + timedelta(n) for n in range(30)):
            analysis["dates"].append(date.strftime('%Y-%m-%d'))
            analysis["attendance_counts"].append(date_attendance[date])

        # Get top and bottom students
        student_attendance_list = [(Student.query.get(student_id), count) for student_id, count in student_attendance.items()]
        analysis["top_students"] = sorted(student_attendance_list, key=lambda x: x[1], reverse=True)[:5]
        analysis["bottom_students"] = sorted(student_attendance_list, key=lambda x: x[1])[:5]

        class_analysis[class_.id] = analysis

    return class_analysis















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

















@views.route("/course/<string:course_type>/students")
@login_required
def student_list(course_type: str) -> None:
    try:
        # students = (Student.query.join(Student.classes).filter(
        #     Class.course_type == course_type).distinct().all())
        # students = (Student.query
        #     .join(Student.classes)
        #     .filter(Class.course_type == course_type)
        #     .distinct()
        #     .all())
        students = (
            Student.query.join(Class, Student.course_type == Class.course_type)
            .filter(Class.course_type == course_type)
            .distinct()
            .all()
        )

        if not students:
            flash(f"No students found for course type '{course_type}'", "warning")
            return redirect(url_for("views.dashboard"))

        student_data = []
        for student in students:
            student_info = {
                "id": student.id,
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email,
            }
            student_data.append(student_info)

        return render_template(
            "student_list.html", course_type=course_type, students=student_data
        )

    except Exception as e:
        flash(
            f"An error occurred while retrieving the student list: {str(e)}", "danger"
        )
        return redirect(url_for("views.dashboard"))

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO, StringIO

import matplotlib.pyplot as plt
from flask import (Blueprint, flash, make_response, redirect, render_template,
                   send_file, url_for)
from flask_login import current_user, login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Table,
                                TableStyle)
from sqlalchemy import func  # Import func from SQLAlchemy

from .extention import db
from .models import Attendance, Class, Student
from .student_views import get_course_types_from_db


@views.route("/download_pdf/<int:class_id>")
@login_required
def download_pdf(class_id):
    class_ = Class.query.get_or_404(class_id)

    # Get the class data and analyze it
    class_data = get_class_data([class_])
    classes = [i[0] for i in class_data]
    class_analysis = analyze_class_data(classes)

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Create the elements to add to the PDF
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    elements.append(Paragraph(f"{class_.name} - Analysis", styles["Title"]))

    # Add general statistics
    elements.append(Paragraph("General Statistics", styles["Heading2"]))
    general_stats = [
        ["Total Students", str(class_analysis[class_.id]["total_students"])],
        ["Average Attendance", f"{class_analysis[class_.id]['avg_attendance']:.2f}"],
        ["Attendance Rate", f"{class_analysis[class_.id]['attendance_rate']:.2f}%"],
    ]
    t = Table(general_stats)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)

    # Add top performers
    elements.append(Paragraph("Top Performers", styles["Heading2"]))
    top_performers = [["Student", "Attendances"]]
    for student, count in class_analysis[class_.id]["top_students"][:5]:
        top_performers.append([f"{student.first_name} {student.last_name}", str(count)])
    t = Table(top_performers)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)

    # Add attendance trend chart
    elements.append(Paragraph("Attendance Trend (Last 30 Days)", styles["Heading2"]))

    # Create the chart using matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(class_analysis[class_.id]["dates"][-30:], class_analysis[class_.id]["attendance_counts"][-30:], marker="o")
    plt.title("Attendance Trend (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Attendance Count")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True)

    # Save the chart to a BytesIO object
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format="png")
    chart_buffer.seek(0)

    # Add the chart to the PDF
    chart_image = Image(chart_buffer)
    chart_image.drawHeight = 300
    chart_image.drawWidth = 500
    elements.append(chart_image)

    # Build the PDF
    doc.build(elements)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{class_.name}_analysis.pdf",
        mimetype="application/pdf",
    )

















@views.route("/download_csv/<int:class_id>")
@login_required
def download_csv(class_id):
    class_ = Class.query.get_or_404(class_id)
    attendance_data = get_class_attendance_data(class_id)

    # Use StringIO instead of BytesIO for text data
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Student Name", "Present", "Late", "Absent"])

    student_data = defaultdict(lambda: {"present": 0, "late": 0, "absent": 0})
    for first_name, last_name, status, count in attendance_data:
        student_name = f"{first_name} {last_name}"
        student_data[student_name][status] += count

    for student_name, counts in student_data.items():
        cw.writerow([student_name, counts["present"], counts["late"], counts["absent"]])

    # Create the response and set headers
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = (
        f"attachment; filename={class_.name}_attendance.csv"
    )
    output.headers["Content-type"] = "text/csv"
    return output


@views.route("/functionalities/<int:class_id>")
@login_required
def functionalities(class_id):
    class_ = Class.query.get_or_404(class_id)
    if not current_user.is_admin and class_ not in current_user.classes:
        flash("You do not have permission to access this class.", "danger")
        print("You do not have permission to access this class.", "danger")
        return redirect(url_for("views.dashboard"))
    return render_template("Attendance.html", class_=class_)


# Helper functions
# def analyze_class_data(classes):
#     class_analysis = {}
#     for class_ in classes:
#         print(class_)
#         analysis = {
#             "total_students": 0,
#             "avg_attendance": 0,
#             "attendance_rate": 0,
#             "top_students": [],
#             "bottom_students": [],
#             "dates": [],
#             "attendance_counts": [],
#         }

#         # Get all students in this class
#         students = Student.query.filter(
#             Student.classes.any(id=class_.id)).all()
#         print("Class students", students)
#         print("length of students", len(students))
#         analysis["total_students"] = len(students)

#         # Get attendance data for the last 30 days
#         end_date = datetime.now().date()
#         start_date = end_date - timedelta(days=20)
#         print(start_date, end_date)
#         attendances = Attendance.query.filter(
#             Attendance.class_id == class_.id, Attendance.timestamp
#             >= start_date, Attendance.timestamp
#             <= end_date).order_by(Attendance.timestamp).all()
#         print(f"Class ID: {class_.id}, Attendances: {attendances}")

#         # Process attendance data
#         date_attendance = defaultdict(int)
#         student_attendance = defaultdict(int)
#         for attendance in attendances:
#             date_attendance[attendance.timestamp.date()] += 1
#             student_attendance[attendance.student_id] += 1

#         # Calculate average attendance and attendance rate
#         total_attendance = sum(date_attendance.values())
#         num_days = (end_date - start_date).days + 1
#         if num_days > 0:
#             analysis["avg_attendance"] = total_attendance / num_days
#         if analysis["total_students"] * num_days > 0:
#             analysis["attendance_rate"] = (
#                 total_attendance /
#                 (analysis["total_students"] * num_days)) * 100

#         # Prepare data for the attendance trend chart
#         for date in (start_date + timedelta(n) for n in range(30)):
#             analysis["dates"].append(date.strftime('%Y-%m-%d'))
#             analysis["attendance_counts"].append(date_attendance[date])

#         # Get top and bottom students
#         student_attendance_list = [
#             (Student.query.get(student_id), count)
#             for student_id, count in student_attendance.items()
#         ]
#         analysis["top_students"] = sorted(student_attendance_list,
#                                           key=lambda x: x[1],
#                                           reverse=True)
#         analysis["bottom_students"] = sorted(student_attendance_list,
#                                              key=lambda x: x[1])

#         class_analysis[class_.id] = analysis
#         # print(class_analysis)
#     return class_analysis

from sqlalchemy.orm import aliased


def analyze_class_data(classes):
    class_analysis = {}
    print("***************************")
    print("Data Type of classes: ", type(classes))
    print()
    print("printing the list classes :", classes)
    print()
    print("***************************")
    print()
    print("Printing Classes: ", classes)
    print()
    for class_ in classes:
        # print(f"Processing class: {class_.id}")
        print("printing thet type of class_ :", type(class_))
        print()
        print("class_ :", class_)
        print()
        print()
        print()
        print("++++++++++++++++++++++++++++++++++")
        print("class id ===== ", class_.id)
        print("+++++++++++++++++++++++++++++++++")
        print()
        print()
        print()
        # print("class id ===== ", class_.id)
        print()
        print()
        print()
        analysis = {
            "total_students": 0,
            "avg_attendance": 0,
            "attendance_rate": 0,
            "top_students": [],
            "bottom_students": [],
            "dates": [],
            "attendance_counts": [],
        }

        # Get all students in this class
        students = Student.query.filter(Student.classes.any(id=class_.id)).all()
        print(f"Class students: {students}")
        print(f"Length of students: {len(students)}")
        analysis["total_students"] = len(students)

        # Get attendance data for the last 30 days
        end_date = datetime.now().date() + +timedelta(days=2)
        start_date = end_date - timedelta(days=28)
        print(f"Start date: {start_date}, End date: {end_date}")

        attendances = (
            Attendance.query.filter(
                Attendance.class_id == class_.id,
                Attendance.timestamp >= start_date,
                Attendance.timestamp <= end_date,
            )
            .order_by(Attendance.timestamp)
            .all()
        )
        print(Attendance.class_id)
        print(f"Class ID: {class_.id}, Attendances: {attendances}")

        # Process attendance data
        date_attendance = defaultdict(int)
        student_attendance = defaultdict(int)
        for attendance in attendances:
            date_attendance[attendance.timestamp.date()] += 1
            student_attendance[attendance.student_id] += 1

        # Calculate average attendance and attendance rate
        total_attendance = sum(date_attendance.values())
        num_days = (end_date - start_date).days + 1
        if num_days > 0:
            analysis["avg_attendance"] = total_attendance / num_days
        if analysis["total_students"] * num_days > 0:
            analysis["attendance_rate"] = (
                total_attendance / (analysis["total_students"] * num_days)
            ) * 100

        # Prepare data for the attendance trend chart
        for date in (start_date + timedelta(n) for n in range(30)):
            analysis["dates"].append(date.strftime("%Y-%m-%d"))
            analysis["attendance_counts"].append(date_attendance[date])

        # Get top and bottom students
        student_attendance_list = [
            (Student.query.get(student_id), count)
            for student_id, count in student_attendance.items()
        ]
        analysis["top_students"] = sorted(
            student_attendance_list, key=lambda x: x[1], reverse=True
        )
        analysis["bottom_students"] = sorted(
            student_attendance_list, key=lambda x: x[1]
        )

        class_analysis[class_.id] = analysis
        # print(class_analysis)
    return class_analysis


def get_class_data(teacher_classes):
    return (
        db.session.query(
            Class,
            Student,
            Attendance.status,
            func.count(Attendance.id).label("attendance_count"),
            func.max(Attendance.timestamp).label("last_attendance"),
        )
        .join(Attendance, Attendance.class_id == Class.id)
        .join(Student, Student.id == Attendance.student_id)
        .filter(Class.id.in_([c.id for c in teacher_classes]))
        .group_by(Class.id, Student.id, Attendance.status)
        .all()
    )


def get_class_attendance_data(class_id):
    return (
        db.session.query(
            Student.first_name,
            Student.last_name,
            Attendance.status,
            func.count(Attendance.id).label("attendance_count"),
        )
        .join(Attendance, Attendance.student_id == Student.id)
        .filter(Attendance.class_id == class_id)
        .group_by(Student.id, Attendance.status)
        .all()
    )
    