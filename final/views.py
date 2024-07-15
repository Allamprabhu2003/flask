# import cv2
# from .models import Attendance, Class, Student
# from collections import defaultdict
# from datetime import datetime, timedelta

# import cv2
# from flask_login import current_user, login_required
# from sqlalchemy import func  # Import func from SQLAlchemy

# from flask import (Blueprint, flash, redirect, render_template, url_for)

# from .extention import db
# from .models import Attendance, Class, Student

# cv2.ocl.setUseOpenCL(True)
# views = Blueprint("views", __name__)


# @views.route("/")
# def index():
#     return render_template("home.html")


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
#             sum(class_attendance[class_.id][student.id].values()))

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
#             analysis["avg_attendance"] = sum(
#                 count
#                 for _, count in student_counts) / analysis["total_students"]

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
#     if current_user.is_admin:
#         return redirect(url_for("admin.index"))

#     teacher_classes = Class.query.filter(Class.teachers.any(id=current_user.id)).all()
#     class_data = get_class_data(teacher_classes)
#     class_analysis, class_attendance = analyze_class_data(class_data)

#     course_types = ["BCA", "BCS", "BA"]  # Add this line

#     courses_data = {}
#     for class_ in teacher_classes:
#         if class_.course_type not in courses_data:
#             courses_data[class_.course_type] = {
#                 'name': class_.course_type,
#                 'total_students': 0
#             }
#         courses_data[class_.course_type]['total_students'] += db.session.query(func.count(Student.id)).filter(Student.classes.any(id=class_.id)).scalar()

#     return render_template(
#         "dashboard.html",
#         classes=teacher_classes,
#         class_analysis=class_analysis,
#         class_attendance=class_attendance,
#         course_types=course_types,  # Add this line
#         courses_data=courses_data

#     )

# def get_class_data(teacher_classes):
#     return (db.session.query(
#         Class,
#         Student,
#         Attendance.status,
#         func.count(Attendance.id).label("attendance_count"),
#         func.max(Attendance.timestamp).label("last_attendance"),
#     ).join(Attendance, Attendance.class_id == Class.id).join(
#         Student, Student.id == Attendance.student_id).filter(
#             Class.id.in_([c.id for c in teacher_classes
#                           ])).group_by(Class.id, Student.id,
#                                        Attendance.status).all())



# # from flask import Blueprint, render_template, url_for
# # from flask_login import current_user, login_required
# # from sqlalchemy import func
# # from .models import Class, Student, Attendance
# # from .extention import db


# # @views.route("/course/<string:course_type>/students")
# # @login_required
# # def student_list(course_type):
# #     print("Trigger")
# #     print(Student.query.join(Student.classes.).filter(course_type))
# #     students = Student.query.join(Student.classes).filter(Class.course_type == course_type).distinct().all()
# #     print(students)
# #     student_data = []
# #     for student in students:
# #         print(student)
# #         student_info = {
# #             'id': student.id,
# #             'name': f"{student.first_name} {student.last_name}",
# #             'email': student.email,
# #         }
# #         student_data.append(student_info)
    
# #     return render_template("student_list.html", course_type=course_type, students=student_data)


# # @views.route("/course/<string:course_type>/students")
# # @login_required
# # def student_list(course_type):
# #     try:
# #         students = Student.query.join(Student.classes).filter(Class.course_type == course_type).distinct().all()

# #         if not students:
# #             flash(f"No students found for course type '{course_type}'", "warning")
# #             print(f"No students found for course type {course_type}")

# #         student_data = []
# #         for student in students:
# #             student_info = {
# #                 'id': student.id,
# #                 'name': f"{student.first_name} {student.last_name}",
# #                 'email': student.email,
# #             }
# #             student_data.append(student_info)
        
# #         return render_template("student_list.html", course_type=course_type, students=student_data)

# #     except Exception as e:
# #         flash(f"An error occurred while retrieving the student list: {str(e)}", "danger")
# #         print(f"An error occurred while retrieving the student list: {str(e)}")
# #         return redirect(url_for('views.dashboard'))



# @views.route("/course/<string:course_type>/students")
# @login_required
# def student_list(course_type):
#     try:
#         # Fetch students based on the course type
#         students = Student.query.filter_by(course_type=course_type).all()

#         # Check if there are any students found
#         if not students:
#             flash(f"No students found for course type '{course_type}'", "warning")
#             return redirect(url_for('views.dashboard'))

#         # Prepare student data for the template
#         student_data = []
#         for student in students:
#             student_info = {
#                 'id': student.id,
#                 'name': f"{student.first_name} {student.last_name}",
#                 'email': student.email,
#             }
#             student_data.append(student_info)

#         return render_template("student_list.html", course_type=course_type, students=student_data)

#     except Exception as e:
#         flash(f"An error occurred while retrieving the student list: {str(e)}", "danger")
#         return redirect(url_for('views.dashboard'))








# # @views.route("/course/<string:course_type>/students")
# # @login_required
# # def student_list(course_type):
#     # Check if the current user teaches any class of this course type
#     # teacher_classes = Class.query.filter(Class.teachers.any(id=current_user.id), Class.course_type == course_type).all()
#     # if not teacher_classes:
#     #     abort(403)  # Forbidden
    
#     # students = Student.query.join(Student.classes).filter(Class.course_type == course_type).distinct().all()
    
#     # student_data = []
#     # for student in students:
#     #     # Calculate attendance across all classes of this course type
#     #     attendance_count = Attendance.query.join(Class).filter(
#     #         Attendance.student_id == student.id,
#     #         Class.course_type == course_type
#     #     ).count()
        
#     #     # total_sessions = sum(class_.total_sessions for class_ in teacher_classes)
#     #     # attendance_rate = (attendance_count / total_sessions) * 100 if total_sessions > 0 else 0
        
#     #     student_info = {s
#     #         'id': student.id,
#     #         'name': student.first_name,
#     #         'email': student.email,
#     #         # 'attendance_count': attendance_count,
#     #         # 'attendance_rate': round(attendance_rate, 2)
#     #     }
#     #     student_data.append(student_info)
    
#     # return render_template("student_list.html", course_type=course_type, students=student_data)
    
    
    
    
#     from flask import send_file
# from io import BytesIO
# import pdfkit

# @views.route('/download_pdf/<int:class_id>')
# @login_required
# def download_pdf(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     rendered = render_template('pdf_template.html', class_=class_)
#     pdf = pdfkit.from_string(rendered, False)

#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = f'attachment; filename={class_.name}_analysis.pdf'
#     return response


# import csv

# @views.route('/download_csv/<int:class_id>')
# @login_required
# def download_csv(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     attendance_data = get_attendance_data(class_id)  # Fetch your attendance data here

#     si = BytesIO()
#     cw = csv.writer(si)
#     cw.writerow(['Student Name', 'Present', 'Late', 'Absent'])  # Add your CSV header here
#     for student in attendance_data:
#         cw.writerow([student.name, student.present, student.late, student.absent])  # Add your CSV data here

#     response = make_response(si.getvalue())
#     response.headers['Content-Disposition'] = f'attachment; filename={class_.name}_attendance.csv'
#     response.headers['Content-type'] = 'text/csv'
#     return response

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import cv2
import pdfkit
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

# @views.route("/dashboard")
# @login_required
# def dashboard():
#     if current_user.is_admin:
#         return redirect(url_for("admin.index"))

#     teacher_classes = Class.query.filter(Class.teachers.any(id=current_user.id)).all()
#     class_data = get_class_data(teacher_classes)
#     class_analysis, class_attendance = analyze_class_data(class_data)

#     course_types = ["BCA", "BCS", "BA"]

#     courses_data = {}
#     for class_ in teacher_classes:
#         if class_.course_type not in courses_data:
#             courses_data[class_.course_type] = {
#                 'name': class_.course_type,
#                 'total_students': 0
#             }
#         courses_data[class_.course_type]['total_students'] += db.session.query(func.count(Student.id)).filter(Student.classes.any(id=class_.id)).scalar()

#     return render_template(
#         "dashboard.html",
#         classes=teacher_classes,
#         class_analysis=class_analysis,
#         class_attendance=class_attendance,
#         course_types=course_types,
#         courses_data=courses_data
#     )

@views.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.index"))

    teacher_classes = Class.query.filter(Class.teachers.any(id=current_user.id)).all()
    class_data = get_class_data(teacher_classes)
    class_analysis, class_attendance = analyze_class_data(class_data)

    course_types = ["BCA", "BCS", "BA"]

    courses_data = {}
    for class_ in teacher_classes:
        if class_.course_type not in courses_data:
            courses_data[class_.course_type] = {
                'name': class_.course_type,
                'total_students': 0
            }
        courses_data[class_.course_type]['total_students'] += db.session.query(func.count(Student.id)).filter(Student.classes.any(id=class_.id)).scalar()

    return render_template(
        "dashboard.html",
        classes=teacher_classes,
        class_analysis=class_analysis,
        class_attendance=class_attendance,
        course_types=course_types,
        courses_data=courses_data
    )



def get_class_data(teacher_classes):
    return (db.session.query(
        Class,
        Student,
        Attendance.status,
        func.count(Attendance.id).label("attendance_count"),
        func.max(Attendance.timestamp).label("last_attendance"),
    ).join(Attendance, Attendance.class_id == Class.id).join(
        Student, Student.id == Attendance.student_id).filter(
            Class.id.in_([c.id for c in teacher_classes])
    ).group_by(Class.id, Student.id, Attendance.status).all())

@views.route("/course/<string:course_type>/students")
@login_required
def student_list(course_type):
    try:
        students = Student.query.join(Student.classes).filter(Class.course_type == course_type).distinct().all()

        if not students:
            flash(f"No students found for course type '{course_type}'", "warning")
            return redirect(url_for('views.dashboard'))

        student_data = []
        for student in students:
            student_info = {
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email,
            }
            student_data.append(student_info)

        return render_template("student_list.html", course_type=course_type, students=student_data)

    except Exception as e:
        flash(f"An error occurred while retrieving the student list: {str(e)}", "danger")
        return redirect(url_for('views.dashboard'))

# @views.route('/download_pdf/<int:class_id>')
# @login_required
# def download_pdf(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     rendered = render_template('pdf_template.html', class_=class_)
#     pdf = pdfkit.from_string(rendered, False)

#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = f'attachment; filename={class_.name}_analysis.pdf'
#     return response


# @views.route('/download_pdf/<int:class_id>')
# @login_required
# def download_pdf(class_id):
#     class_ = Class.query.get_or_404(class_id)
    
#     # Get the class data and analyze it
#     class_data = get_class_data([class_])
#     class_analysis, _ = analyze_class_data(class_data)
    
#     # Prepare the recent trend data
#     recent_trend = {
#         (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'): class_analysis[class_.id]['recent_trend'][6-i]
#         for i in range(7)
#     }
    
#     rendered = render_template('pdf_template.html', 
#                                class_=class_, 
#                                class_analysis=class_analysis,
#                                recent_trend=recent_trend)
#     pdf = pdfkit.from_string(rendered, False)

#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = f'attachment; filename={class_.name}_analysis.pdf'
#     return response


from io import BytesIO

from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from .models import Student  # Make sure to import the Student model

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from .models import Student
import matplotlib.pyplot as plt
import numpy as np

@views.route('/download_pdf/<int:class_id>')
@login_required
def download_pdf(class_id):
    class_ = Class.query.get_or_404(class_id)
    
    # Get the class data and analyze it
    class_data = get_class_data([class_])
    class_analysis, class_attendance = analyze_class_data(class_data)
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Create the elements to add to the PDF
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    elements.append(Paragraph(f"{class_.name} - Analysis", styles['Title']))

    # Add general statistics
    elements.append(Paragraph("General Statistics", styles['Heading2']))
    general_stats = [
        ["Total Students", str(class_analysis[class_.id]['total_students'])],
        ["Average Attendance", f"{class_analysis[class_.id]['avg_attendance']:.2f}"],
        ["Attendance Rate", f"{class_analysis[class_.id]['attendance_rate']:.2f}%"]
    ]
    t = Table(general_stats)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
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
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)

    # Add top performers
    elements.append(Paragraph("Top Performers", styles['Heading2']))
    top_performers = [["Student", "Attendances"]]
    for student_id, count in class_analysis[class_.id]['top_students']:
        student = Student.query.get(student_id)
        if student:
            top_performers.append([f"{student.first_name} {student.last_name}", str(count)])
    t = Table(top_performers)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
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
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)

    # Add attendance trend chart
    elements.append(Paragraph("Attendance Trend (Last 7 Days)", styles['Heading2']))
    
    # Create the chart using matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(range(7), class_analysis[class_.id]['recent_trend'], marker='o')
    plt.title('Attendance Trend (Last 7 Days)')
    plt.xlabel('Days Ago')
    plt.ylabel('Attendance Count')
    plt.xticks(range(7), ['7', '6', '5', '4', '3', '2', '1'])
    plt.grid(True)
    
    # Save the chart to a BytesIO object
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png')
    chart_buffer.seek(0)
    
    # Add the chart to the PDF
    chart_image = Image(chart_buffer)
    chart_image.drawHeight = 300
    chart_image.drawWidth = 500
    elements.append(chart_image)

    # Add attendance details
    elements.append(Paragraph("Attendance Details", styles['Heading2']))
    attendance_data = [["Student", "Present", "Late", "Absent"]]
    for student_id, counts in class_attendance[class_.id].items():
        student = Student.query.get(student_id)
        if student:
            attendance_data.append([
                f"{student.first_name} {student.last_name}",
                str(counts['present']),
                str(counts['late']),
                str(counts['absent'])
            ])
    t = Table(attendance_data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
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
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)

    # Build the PDF
    doc.build(elements)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'{class_.name}_analysis.pdf', mimetype='application/pdf')


# @views.route('/download_pdf/<int:class_id>')
# @login_required
# def download_pdf(class_id):
#     class_ = Class.query.get_or_404(class_id)
    
#     # Get the class data and analyze it
#     class_data = get_class_data([class_])
#     class_analysis, _ = analyze_class_data(class_data)
    
#     # Prepare the recent trend data
#     recent_trend = [
#         [
#             (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
#             class_analysis[class_.id]['recent_trend'][6-i]
#         ]
#         for i in range(7)
#     ]

#     # Create a file-like buffer to receive PDF data
#     buffer = BytesIO()

#     # Create the PDF object, using the buffer as its "file."
#     doc = SimpleDocTemplate(buffer, pagesize=letter)

#     # Create the elements to add to the PDF
#     elements = []
#     styles = getSampleStyleSheet()

#     # Add title
#     elements.append(Paragraph(f"{class_.name} - Analysis", styles['Title']))

#     # Add general statistics
#     elements.append(Paragraph("General Statistics", styles['Heading2']))
#     general_stats = [
#         ["Total Students", str(class_analysis[class_.id]['total_students'])],
#         ["Average Attendance", f"{class_analysis[class_.id]['avg_attendance']:.2f}"],
#         ["Attendance Rate", f"{class_analysis[class_.id]['attendance_rate']:.2f}%"]
#     ]
#     t = Table(general_stats)
#     t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                            ('FONTSIZE', (0, 0), (-1, 0), 14),
#                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                            ('FONTSIZE', (0, 1), (-1, -1), 12),
#                            ('TOPPADDING', (0, 1), (-1, -1), 6),
#                            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
#                            ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
#     elements.append(t)

#     # Add top performers
#     elements.append(Paragraph("Top Performers", styles['Heading2']))
#     top_performers = [["Student", "Attendances"]]
#     for student_id, count in class_analysis[class_.id]['top_students']:
#         student = Student.query.get(student_id)
#         if student:
#             top_performers.append([f"{student.first_name} {student.last_name}", str(count)])
#     t = Table(top_performers)
#     t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                            ('FONTSIZE', (0, 0), (-1, 0), 14),
#                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                            ('FONTSIZE', (0, 1), (-1, -1), 12),
#                            ('TOPPADDING', (0, 1), (-1, -1), 6),
#                            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
#                            ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
#     elements.append(t)

#     # Add attendance trend
#     elements.append(Paragraph("Attendance Trend (Last 7 Days)", styles['Heading2']))
#     t = Table([["Date", "Attendance"]] + recent_trend)
#     t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                            ('FONTSIZE', (0, 0), (-1, 0), 14),
#                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                            ('FONTSIZE', (0, 1), (-1, -1), 12),
#                            ('TOPPADDING', (0, 1), (-1, -1), 6),
#                            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
#                            ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
#     elements.append(t)

#     # Build the PDF
#     doc.build(elements)

#     # FileResponse sets the Content-Disposition header so that browsers
#     # present the option to save the file.
#     buffer.seek(0)
#     return send_file(buffer, as_attachment=True, download_name=f'{class_.name}_analysis.pdf', mimetype='application/pdf')


def get_class_attendance_data(class_id):
    return (db.session.query(
        Student.first_name,
        Student.last_name,
        Attendance.status,
        func.count(Attendance.id).label("attendance_count")
    ).join(Attendance, Attendance.student_id == Student.id).filter(
        Attendance.class_id == class_id
    ).group_by(Student.id, Attendance.status).all())

# @views.route('/download_csv/<int:class_id>')
# @login_required
# def download_csv(class_id):
#     class_ = Class.query.get_or_404(class_id)
#     attendance_data = get_class_attendance_data(class_id)

#     si = BytesIO()
#     cw = csv.writer(si)
#     cw.writerow(['Student Name', 'Present', 'Late', 'Absent'])

#     student_data = defaultdict(lambda: {"present": 0, "late": 0, "absent": 0})
#     for first_name, last_name, status, count in attendance_data:
#         student_name = f"{first_name} {last_name}"
#         student_data[student_name][status] += count

#     for student_name, counts in student_data.items():
#         cw.writerow([student_name, counts['present'], counts['late'], counts['absent']])

#     response = make_response(si.getvalue())
#     response.headers['Content-Disposition'] = f'attachment; filename={class_.name}_attendance.csv'
#     response.headers['Content-type'] = 'text/csv'
#     return response


from io import StringIO
import csv
from flask import make_response

@views.route('/download_csv/<int:class_id>')
@login_required
def download_csv(class_id):
    class_ = Class.query.get_or_404(class_id)
    attendance_data = get_class_attendance_data(class_id)

    # Use StringIO instead of BytesIO for text data
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Present', 'Late', 'Absent'])

    student_data = defaultdict(lambda: {"present": 0, "late": 0, "absent": 0})
    for first_name, last_name, status, count in attendance_data:
        student_name = f"{first_name} {last_name}"
        student_data[student_name][status] += count

    for student_name, counts in student_data.items():
        cw.writerow([student_name, counts['present'], counts['late'], counts['absent']])

    # Create the response and set headers
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={class_.name}_attendance.csv"
    output.headers["Content-type"] = "text/csv"
    return output