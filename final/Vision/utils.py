import cv2
import dlib
import numpy as np
from flask import current_app, flash, g
from sqlalchemy.orm import joinedload
from ..extention import db
from ..models import Attendance, Class, Face, Student
from datetime import datetime, timedelta
from functools import lru_cache

# Enable optimizations
cv2.setUseOptimized(True)
cv2.ocl.setUseOpenCL(True)

# Preload models
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("Models/shape_predictor_68_face_landmarks_GTX.dat")
face_recognizer = dlib.face_recognition_model_v1("Models/dlib_face_recognition_resnet_model_v1.dat")

THRESH = 0.44
IMAGE_SIZE = 800
FACE_SIZE = 150
MAX_FACES_TO_RECOGNIZE = 10

# Face encoding cache
face_encodings_cache = {}

def preprocess_image(image):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return cv2.equalizeHist(gray)

def resize_image(image, max_height=IMAGE_SIZE):
    aspect_ratio = image.shape[1] / image.shape[0]
    new_width = int(max_height * aspect_ratio)
    return cv2.resize(image, (new_width, max_height), interpolation=cv2.INTER_AREA)

@lru_cache(maxsize=1000)
def compute_face_descriptor(face_chip_bytes, num_jitters=1):
    face_chip = np.frombuffer(face_chip_bytes, dtype=np.uint8).reshape((FACE_SIZE, FACE_SIZE, 3))
    return np.array(face_recognizer.compute_face_descriptor(face_chip, num_jitters=num_jitters))

def compute_face_encodings(image, face_locations):
    encodings = []
    for face in face_locations:
        shape = shape_predictor(image, face)
        face_chip = dlib.get_face_chip(image, shape, size=FACE_SIZE)
        face_chip_bytes = face_chip.tobytes()
        encoding = compute_face_descriptor(face_chip_bytes)
        encodings.append(encoding)
    return np.array(encodings)

@lru_cache(maxsize=1)
def load_from_database():
    with current_app.app_context():
        faces = Face.query.options(joinedload(Face.student)).all()
        return {face.student.first_name: np.frombuffer(face.face_encodings, dtype=np.float64) for face in faces}

def get_face_data():
    if not hasattr(g, "face_data"):
        g.face_data = load_from_database()
    return g.face_data

def recognize_faces(face_encodings):
    face_data = get_face_data()
    face_names_database = list(face_data.keys())
    face_encodings_database = np.array(list(face_data.values()))

    if len(face_encodings) == 0:
        return []

    distances = np.linalg.norm(face_encodings_database[:, np.newaxis] - face_encodings, axis=2)
    min_distances = np.min(distances, axis=0)
    min_indices = np.argmin(distances, axis=0)

    return [face_names_database[i] if d < THRESH else "Unknown" for i, d in zip(min_indices, min_distances)]

def run_face_recognition(frame, class_id):
    small_frame = resize_image(frame)
    preprocessed_frame = preprocess_image(small_frame)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_detector(preprocessed_frame, 1)

    if not face_locations:
        return frame, []

    face_encodings = compute_face_encodings(rgb_small_frame, face_locations)
    face_names = recognize_faces(face_encodings)

    scale_x, scale_y = frame.shape[1] / small_frame.shape[1], frame.shape[0] / small_frame.shape[0]

    with current_app.app_context():
        class_ = Class.query.get(class_id)
        if not class_:
            flash("Class not found", "error")
            return frame, []

        recognized_students = {student.first_name: student for student in class_.students}

        for i, (face_location, name) in enumerate(zip(face_locations[:MAX_FACES_TO_RECOGNIZE], face_names[:MAX_FACES_TO_RECOGNIZE])):
            if name in recognized_students:
                left = int(face_location.left() * scale_x)
                top = int(face_location.top() * scale_y)
                right = int(face_location.right() * scale_x)
                bottom = int(face_location.bottom() * scale_y)

                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame, face_names

from sqlalchemy import func 

def update_attendance(recognized_names, class_id):
    with current_app.app_context():
        class_ = Class.query.get(class_id)
        if not class_:
            flash("Class not found", "error")
            return
        
        now = datetime.utcnow()
        two_hours_ago = now - timedelta(hours=2)
        
        # Case-insensitive matching and trimming spaces
        recognized_names_cleaned = [name.strip().lower() for name in recognized_names]
     
        
        # Fetch students matching recognized names and associated with the class
        students = Student.query.join(Class.students).filter(
            Class.id == class_id,
            func.lower(Student.first_name).in_(recognized_names_cleaned)
        ).all()
        
        if not students:
            flash("No students found matching recognized names", "warning")
            return
        
        # Fetch existing attendances for these students in the class within the last two hours
        existing_attendances = Attendance.query.filter(
            Attendance.student_id.in_([s.id for s in students]),
            Attendance.class_id == class_id,
            Attendance.timestamp >= two_hours_ago,
            Attendance.timestamp <= now
        ).all()
        
        existing_attendance_set = set((att.student_id, att.class_id) for att in existing_attendances)
        
        new_attendances = []
        for student in students:
            if student.course_type == class_.course_type:
                if (student.id, class_id) not in existing_attendance_set:
                    # Check if attendance already exists (prevent duplicate attendance)
                    existing_attendance = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        Attendance.class_id == class_id,
                        Attendance.timestamp >= two_hours_ago,
                        Attendance.timestamp <= now
                    ).first()
                    if not existing_attendance:
                        # Mark attendance as present
                        new_attendances.append(Attendance(
                            student_id=student.id,
                            class_id=class_id,
                            status="present",
                            timestamp=now
                        ))
                        flash(f"Attendance marked for {student.first_name} {student.last_name}", "success")
                    else:
                        flash(f"Attendance already marked for {student.first_name} {student.last_name}", "info")
                else:
                    flash(f"Attendance already marked for {student.first_name} {student.last_name}", "info")
            else:
                flash(f"Student {student.first_name} is not enrolled in this course type", "warning")
        
        if new_attendances:
            db.session.bulk_save_objects(new_attendances)
            db.session.commit()



def mark_absent_students(class_id, recognized_names):
    with current_app.app_context():
        class_ = Class.query.get(class_id)
        if not class_:
            flash("Class not found", "error")
            return

        now = datetime.utcnow()
        two_hours_ago = now - timedelta(hours=2)

        # Fetch all students in the class
        students = class_.students

        # Fetch existing attendances for these students in the class within the last two hours
        existing_attendances = Attendance.query.filter(
            Attendance.student_id.in_([s.id for s in students]),
            Attendance.class_id == class_id,
            Attendance.timestamp >= two_hours_ago,
            Attendance.timestamp <= now
        ).all()

        existing_attendance_set = set((att.student_id, att.class_id) for att in existing_attendances)

        new_attendances = []
        for student in students:
            if student.course_type == class_.course_type:
                if (student.id, class_id) not in existing_attendance_set and student.first_name not in recognized_names:
                    # Mark attendance as absent
                    new_attendances.append(Attendance(
                        student_id=student.id,
                        class_id=class_id,
                        status="absent",
                        timestamp=now
                    ))
                    flash(f"Attendance marked as absent for {student.first_name} {student.last_name}", "warning")

        if new_attendances:
            db.session.bulk_save_objects(new_attendances)
            db.session.commit()

