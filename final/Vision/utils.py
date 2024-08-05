
from datetime import datetime, timedelta

import cv2
import dlib

import numpy as np
from flask import current_app, flash, g
from sqlalchemy.orm import joinedload

from ..extention import db
from ..models import Attendance, Class, Face, Student

# # Enable optimizations
# cv2.setUseOptimized(True)
# cv2.ocl.setUseOpenCL(True)

# # Preload models (keep as is)
# face_detector = dlib.get_frontal_face_detector()
# shape_predictor = dlib.shape_predictor(
#     "Models/shape_predictor_68_face_landmarks_GTX.dat"
# )
# face_recognizer = dlib.face_recognition_model_v1(
#     "Models/dlib_face_recognition_resnet_model_v1.dat"
# )

# THRESH = 0.50
# IMAGE_SIZE = 400
# FACE_SIZE = 150
# MAX_FACES_TO_RECOGNIZE = 10

# # Face encoding cache (keep as is)
# face_encodings_cache = {}


# def preprocess_image(image):
#     if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
#         gray = image
#     else:
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     return cv2.GaussianBlur(cv2.equalizeHist(gray), (5, 5), 0)


# def resize_image(image, max_height=IMAGE_SIZE):
#     aspect_ratio = image.shape[1] / image.shape[0]
#     new_width = int(max_height * aspect_ratio)
#     return cv2.resize(image, (new_width, max_height))


# def compute_face_descriptor(image, face_location, num_jitters=1):
#     # Ensure image is a numpy array
#     if not isinstance(image, np.ndarray):
#         raise ValueError("Image must be a numpy array")

#     # Ensure face_location is a dlib rectangle
#     if not isinstance(face_location, dlib.rectangle):
#         raise ValueError("Face location must be a dlib rectangle")

#     shape = shape_predictor(image, face_location)
#     face_chip = dlib.get_face_chip(image, shape, size=FACE_SIZE)
#     return np.array(
#         face_recognizer.compute_face_descriptor(face_chip, num_jitters=num_jitters)
#     )


# # Replace with:
# def compute_face_encodings(image, face_locations):
#     encodings = []
#     for face in face_locations:
#         cache_key = (face.left(), face.top(), face.right(), face.bottom())
#         if cache_key in face_encodings_cache:
#             encoding = face_encodings_cache[cache_key]
#         else:
#             encoding = compute_face_descriptor(image, face)
#             face_encodings_cache[cache_key] = encoding
#         encodings.append(encoding)
#     return np.array(encodings)


# # Optimize database loading
# def load_from_database():
#     with current_app.app_context():
#         faces = Face.query.options(joinedload(Face.student)).all()
#         return {
#             face.student.first_name: np.frombuffer(
#                 face.face_encodings, dtype=np.float64
#             )
#             for face in faces
#         }


# def get_face_data():
#     if not hasattr(g, "face_data"):
#         g.face_data = load_from_database()
#     return g.face_data


# def recognize_faces(face_encodings):
#     face_data = get_face_data()
#     face_names_database = list(face_data.keys())
#     face_encodings_database = np.array(list(face_data.values()))

#     if len(face_encodings) == 0:
#         return []

#     distances = np.linalg.norm(
#         face_encodings_database[:, np.newaxis] - face_encodings, axis=2
#     )
#     min_distances = np.min(distances, axis=0)
#     min_indices = np.argmin(distances, axis=0)

#     return [
#         face_names_database[i] if d < THRESH else "Unknown"
#         for i, d in zip(min_indices, min_distances)
#     ]


# def run_face_recognition(frame):
#     small_frame = resize_image(frame)
#     preprocessed_frame = preprocess_image(small_frame)
#     rgb_small_frame = (
#         cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
#         if len(small_frame.shape) == 3 and small_frame.shape[2] == 3
#         else small_frame
#     )

#     face_locations = face_detector(preprocessed_frame, 1)

#     if not face_locations:
#         return (
#             frame,
#             [],
#         )  # Return the original frame and an empty list if no faces are detected

#     face_encodings = compute_face_encodings(rgb_small_frame, face_locations)
#     face_names = recognize_faces(face_encodings)
#     print(face_names)

#     scale_x, scale_y = (
#         frame.shape[1] / small_frame.shape[1],
#         frame.shape[0] / small_frame.shape[0],
#     )

#     for i, (face_location, name) in enumerate(
#         zip(
#             face_locations[:MAX_FACES_TO_RECOGNIZE], face_names[:MAX_FACES_TO_RECOGNIZE]
#         )
#     ):
#         left = int(face_location.left() * scale_x)
#         top = int(face_location.top() * scale_y)
#         right = int(face_location.right() * scale_x)
#         bottom = int(face_location.bottom() * scale_y)

#         color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
#         cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
#         cv2.putText(
#             frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
#         )

#     return frame, face_names


# def update_attendance(recognized_names, class_id):
#     with current_app.app_context():
#         class_ = Class.query.get(class_id)
#         if not class_:
#             flash("Class not found", "error")
#             print("Class not found")
#             return

#         # now = datetime.now()
#         now = datetime.utcnow()  # Use UTC time

#         two_hours_ago = now - timedelta(hours=2)  # Corrected to two hours

#         for name in set(recognized_names):
#             student = Student.query.filter_by(first_name=name).first()

#             if student:
#                 if student.course_type == class_.course_type:
#                     if student not in class_.students:
#                         class_.students.append(student)

#                     existing_attendance = Attendance.query.filter(
#                         Attendance.student_id == student.id,
#                         Attendance.class_id == class_id,
#                         Attendance.timestamp >= two_hours_ago,
#                         Attendance.timestamp <= now,
#                     ).first()

#                     if not existing_attendance:
#                         new_attendance = Attendance(
#                             student_id=student.id,
#                             class_id=class_id,
#                             status="present",
#                             timestamp=now,
#                         )
#                         db.session.add(new_attendance)
#                         flash(
#                             f"Attendance marked for {student.first_name} {student.last_name}",
#                             "success",
#                         )
#                         print(
#                             f"Attendance marked for {student.first_name} {student.last_name}"
#                         )
#                     else:
#                         flash(
#                             f"Attendance already marked for {student.first_name} {student.last_name}",
#                             "info",
#                         )
#                         print(
#                             f"Attendance already marked for {student.first_name} {student.last_name} within the last 2 hours"
#                         )
#                 else:
#                     flash(f"Student {name} not found in this class", "warning")
#                     print(f"Student {name} is not enrolled in this course type")
#             else:
#                 print(f"Student {name} not found")

#         db.session.commit()



import cv2
import dlib
import numpy as np
from flask import current_app, flash, g
from sqlalchemy.orm import joinedload

from ..extention import db
from ..models import Attendance, Class, Face, Student

# Enable optimizations
cv2.setUseOptimized(True)
cv2.ocl.setUseOpenCL(True)

# Preload models
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("Models/shape_predictor_68_face_landmarks_GTX.dat")
face_recognizer = dlib.face_recognition_model_v1("Models/dlib_face_recognition_resnet_model_v1.dat")

THRESH = 0.50
IMAGE_SIZE = 600
FACE_SIZE = 150
MAX_FACES_TO_RECOGNIZE = 12

# Face encoding cache
face_encodings_cache = {}

def preprocess_image(image):
    # Convert to grayscale if necessary
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply histogram equalization
    equalized = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise
    # blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
    
    # # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Perform morphological operations to remove small noise
    # kernel = np.ones((3,3), np.uint8)
    # morph = cv2.morphologyEx(THRESH, cv2.MORPH_OPEN, kernel)
    
    # return morph
    return thresh

def resize_image(image, max_height=IMAGE_SIZE):
    aspect_ratio = image.shape[1] / image.shape[0]
    new_width = int(max_height * aspect_ratio)
    return cv2.resize(image, (new_width, max_height), interpolation=cv2.INTER_AREA)

def compute_face_descriptor(image, face_location, num_jitters=5):
    if not isinstance(image, np.ndarray):
        raise ValueError("Image must be a numpy array")
    if not isinstance(face_location, dlib.rectangle):
        raise ValueError("Face location must be a dlib rectangle")

    shape = shape_predictor(image, face_location)
    face_chip = dlib.get_face_chip(image, shape, size=FACE_SIZE)
    return np.array(face_recognizer.compute_face_descriptor(face_chip, num_jitters=num_jitters))

def compute_face_encodings(image, face_locations):
    encodings = []
    for face in face_locations:
        cache_key = (face.left(), face.top(), face.right(), face.bottom())
        if cache_key in face_encodings_cache:
            encoding = face_encodings_cache[cache_key]
        else:
            encoding = compute_face_descriptor(image, face)
            face_encodings_cache[cache_key] = encoding
        encodings.append(encoding)
    return np.array(encodings)

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

def run_face_recognition(frame):
    small_frame = resize_image(frame)
    preprocessed_frame = preprocess_image(small_frame)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB) if len(small_frame.shape) == 3 and small_frame.shape[2] == 3 else small_frame

    face_locations = face_detector(preprocessed_frame, 1)

    if not face_locations:
        return frame, []

    face_encodings = compute_face_encodings(rgb_small_frame, face_locations)
    face_names = recognize_faces(face_encodings)
    print(face_names)

    scale_x, scale_y = frame.shape[1] / small_frame.shape[1], frame.shape[0] / small_frame.shape[0]

    for i, (face_location, name) in enumerate(zip(face_locations[:MAX_FACES_TO_RECOGNIZE], face_names[:MAX_FACES_TO_RECOGNIZE])):
        left = int(face_location.left() * scale_x)
        top = int(face_location.top() * scale_y)
        right = int(face_location.right() * scale_x)
        bottom = int(face_location.bottom() * scale_y)

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame, face_names

# The rest of the code (update_attendance function) remains unchanged



def update_attendance(recognized_names, class_id):
    with current_app.app_context():
        class_ = Class.query.get(class_id)
        if not class_:
            flash("Class not found", "error")
            print("Class not found")
            return

        # now = datetime.now()
        now = datetime.utcnow()  # Use UTC time

        two_hours_ago = now - timedelta(hours=2)  # Corrected to two hours

        for name in set(recognized_names):
            student = Student.query.filter_by(first_name=name).first()

            if student:
                if student.course_type == class_.course_type:
                    if student not in class_.students:
                        class_.students.append(student)

                    existing_attendance = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        Attendance.class_id == class_id,
                        Attendance.timestamp >= two_hours_ago,
                        Attendance.timestamp <= now,
                    ).first()

                    if not existing_attendance:
                        new_attendance = Attendance(
                            student_id=student.id,
                            class_id=class_id,
                            status="present",
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
                else:
                    flash(f"Student {name} not found in this class", "warning")
                    print(f"Student {name} is not enrolled in this course type")
            else:
                print(f"Student {name} not found")

        db.session.commit()
