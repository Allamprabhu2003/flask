
# from datetime import datetime

# import cv2
# import dlib
# import numpy as np
# from sqlalchemy.orm import joinedload

# from flask import current_app, g

# from . import db
# from .models import Attendance, Class, Face, Student

# cv2.setUseOptimized(True)
# cv2.ocl.setUseOpenCL = True

# # Preload models
# face_detector = dlib.get_frontal_face_detector()
# shape_predictor = dlib.shape_predictor('Models/shape_predictor_68_face_landmarks.dat')
# face_recognizer = dlib.face_recognition_model_v1('Models/dlib_face_recognition_resnet_model_v1.dat')

# THRESH = 0.55
# IMAGE_SIZE = 400
# FACE_SIZE = 150
# MAX_FACES_TO_RECOGNIZE = 10

# # Face encoding cache
# face_encodings_cache = {}

# def preprocess_image(image):
#     if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
#         gray = image
#     else:
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
#     equalized = cv2.equalizeHist(gray)
#     return cv2.GaussianBlur(equalized, (5, 5), 0)

# def resize_image(image, max_height=IMAGE_SIZE):
#     aspect_ratio = image.shape[1] / image.shape[0]
#     new_width = int(max_height * aspect_ratio)
#     return cv2.resize(image, (new_width, max_height))

# def compute_face_descriptor(image, face_location, num_jitters=1):
#     face_chip = dlib.get_face_chip(image, shape_predictor(image, face_location), size=FACE_SIZE)
#     return np.array(face_recognizer.compute_face_descriptor(face_chip, num_jitters=num_jitters))

# def compute_face_encodings(image, face_locations):
#     face_encodings = []
#     for face_location in face_locations:
#         location_key = (face_location.left(), face_location.top(), face_location.right(), face_location.bottom())
#         if location_key in face_encodings_cache:
#             face_encodings.append(face_encodings_cache[location_key])
#         else:
#             face_encoding = compute_face_descriptor(image, face_location)
#             face_encodings_cache[location_key] = face_encoding
#             face_encodings.append(face_encoding)
#     return np.array(face_encodings)

# def load_from_database():
#     with current_app.app_context():
#         faces = Face.query.options(joinedload(Face.student)).all()
#         return [(face.student.first_name, np.frombuffer(face.face_encodings, dtype=np.float64)) for face in faces]

# def get_face_data():
#     if not hasattr(g, 'face_data'):
#         g.face_data = load_from_database()
#     return g.face_data

# def recognize_faces(face_encodings):
#     face_data = get_face_data()
#     face_encodings_database = np.array([face[1] for face in face_data])
#     face_names_database = [face[0] for face in face_data]
    
#     face_names = []
#     for face_encoding in face_encodings:
#         distances = np.linalg.norm(face_encodings_database - face_encoding, axis=1)
#         min_distance = np.min(distances)
#         min_index = np.argmin(distances)
        
#         if min_distance < THRESH:
#             face_names.append(face_names_database[min_index])
#         else:
#             face_names.append("Unknown")
    
#     return face_names

# def run_face_recognition(frame):
#     small_frame = resize_image(frame)
#     preprocessed_frame = preprocess_image(small_frame)

#     if len(small_frame.shape) == 3 and small_frame.shape[2] == 3:
#         rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
#     else:
#         rgb_small_frame = small_frame

#     face_locations = face_detector(preprocessed_frame, 1)
#     face_encodings = compute_face_encodings(rgb_small_frame, face_locations)
#     face_names = recognize_faces(face_encodings)

#     scale_x = frame.shape[1] / small_frame.shape[1]
#     scale_y = frame.shape[0] / small_frame.shape[0]

#     recognized_faces = 0
#     for i, (face_location, name) in enumerate(zip(face_locations, face_names)):
#         if recognized_faces >= MAX_FACES_TO_RECOGNIZE:
#             break

#         top = int(face_location.top() * scale_y)
#         right = int(face_location.right() * scale_x)
#         bottom = int(face_location.bottom() * scale_y)
#         left = int(face_location.left() * scale_x)

#         color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
#         cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
#         cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#         recognized_faces += 1

#     return frame, face_names


# from flask import flash


# def update_attendance(recognized_names, class_id):
#     with current_app.app_context():
#         class_ = Class.query.get(class_id)
#         if not class_:
#             print(class_)
#             flash("Class not found", "error")
#             return

#         for name in set(recognized_names):  # Use set to avoid duplicates
#             student = Student.query.filter_by(first_name=name).first()
#             if student and student in class_.students:
#                 # Check if attendance already exists for today
#                 existing_attendance = Attendance.query.filter(
#                     Attendance.student_id == student.id,
#                     Attendance.class_id == class_id,
#                     func.date(Attendance.timestamp) == func.current_date()
#                 ).first()

#                 if not existing_attendance:
#                     attendance = Attendance(
#                         student_id=student.id,
#                         class_id=class_id,
#                         status="present"
#                     )
#                     db.session.add(attendance)
#                     flash(f"Attendance marked for {student.first_name} {student.last_name}", "success")
#                 else:
#                     flash(f"Attendance already marked for {student.first_name} {student.last_name}", "info")
#             elif student:
#                 flash(f"{student.first_name} {student.last_name} is not a member of this class", "warning")
#             else:
#                 flash(f"Student {name} not found in the database", "warning")

#         db.session.commit()


from datetime import datetime
import cv2
import dlib
import numpy as np
from sqlalchemy.orm import joinedload
from flask import current_app, g, flash
from sqlalchemy import func
from . import db
from .models import Attendance, Class, Face, Student

# Enable optimizations
cv2.setUseOptimized(True)
cv2.ocl.setUseOpenCL(True)

# Preload models (keep as is)
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor('Models/shape_predictor_68_face_landmarks_GTX.dat')
face_recognizer = dlib.face_recognition_model_v1('Models/dlib_face_recognition_resnet_model_v1.dat')

THRESH = 0.55
IMAGE_SIZE = 400
FACE_SIZE = 150
MAX_FACES_TO_RECOGNIZE = 10

# Face encoding cache (keep as is)
face_encodings_cache = {}

def preprocess_image(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(cv2.equalizeHist(gray), (5, 5), 0)

def resize_image(image, max_height=IMAGE_SIZE):
    aspect_ratio = image.shape[1] / image.shape[0]
    new_width = int(max_height * aspect_ratio)
    return cv2.resize(image, (new_width, max_height))

# Optimize face descriptor computation
# @np.vectorize
# def compute_face_descriptor(image, face_location, num_jitters=1):
#     face_chip = dlib.get_face_chip(image, shape_predictor(image, face_location), size=FACE_SIZE)
#     return face_recognizer.compute_face_descriptor(face_chip, num_jitters=num_jitters)

# def compute_face_encodings(image, face_locations):
#     return np.array([
#         face_encodings_cache.get(
#             (face.left(), face.top(), face.right(), face.bottom()),
#             compute_face_descriptor(image, face)
#         )
#         for face in face_locations
#     ])



def compute_face_descriptor(image, face_location, num_jitters=1):
    # Ensure image is a numpy array
    if not isinstance(image, np.ndarray):
        raise ValueError("Image must be a numpy array")
    
    # Ensure face_location is a dlib rectangle
    if not isinstance(face_location, dlib.rectangle):
        raise ValueError("Face location must be a dlib rectangle")
    
    shape = shape_predictor(image, face_location)
    face_chip = dlib.get_face_chip(image, shape, size=FACE_SIZE)
    return np.array(face_recognizer.compute_face_descriptor(face_chip, num_jitters=num_jitters))

# Remove the @np.vectorize decorator
# def compute_face_encodings(image, face_locations):
#     return np.array([
#         face_encodings_cache.get(
#             (face.left(), face.top(), face.right(), face.bottom()),
#             compute_face_descriptor(image, face)
#         )
#         for face in face_locations
#     ])

# Replace with:
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


# Optimize database loading
def load_from_database():
    with current_app.app_context():
        faces = Face.query.options(joinedload(Face.student)).all()
        return {face.student.first_name: np.frombuffer(face.face_encodings, dtype=np.float64) for face in faces}

def get_face_data():
    if not hasattr(g, 'face_data'):
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
        return frame, []  # Return the original frame and an empty list if no faces are detected
    
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


from datetime import datetime
from flask import current_app, flash
from sqlalchemy import func
from .extention import db
from .models import Attendance, Class, Student

def update_attendance(recognized_names, class_id):
    with current_app.app_context():
        class_ = Class.query.get(class_id)
        if not class_:
            flash("Class not found", "error")
            return

        today = datetime.now().date()

        for name in set(recognized_names):
            # Find the student by first name
            student = Student.query.filter_by(first_name=name).first()
            
            if student:
                # Check if the student's course type matches the class course type
                if student.course_type == class_.course_type:
                    # Check if the student is already in the class
                    if student not in class_.students:
                        class_.students.append(student)
                    
                    # Check for existing attendance
                    existing_attendance = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        Attendance.class_id == class_id,
                        func.date(Attendance.timestamp) == today
                    ).first()

                    if not existing_attendance:
                        new_attendance = Attendance(
                            student_id=student.id,
                            class_id=class_id,
                            status="present"
                        )
                        db.session.add(new_attendance)
                        flash(f"Attendance marked for {student.first_name} {student.last_name}", "success")
                        print(f"Attendance marked for {student.first_name} {student.last_name}")
                    else:
                        flash(f"Attendance already marked for {student.first_name} {student.last_name}", "info")
                        print(f"Attendance already marked for {student.first_name} {student.last_name}")
                else:
                    flash(f"Student {name} is not enrolled in this course type", "warning")
                    print(f"Student {name} is not enrolled in this course type")
            else:
                flash(f"Student {name} not found", "warning")
                print(f"Student {name} not found")

        db.session.commit()



# def update_attendance(recognized_names, class_id):
    with current_app.app_context():
        class_ = Class.query.get(class_id)
        if not class_:
            flash("Class not found", "error")
            return

        students = {s.first_name: s for s in class_.students}
        today = datetime.now().date()

        existing_attendances = {
            a.student_id: a for a in Attendance.query.filter(
                Attendance.class_id == class_id,
                func.date(Attendance.timestamp) == today
            )
        }

        new_attendances = []
        for name in set(recognized_names):
            student = students.get(name)
            if student:
                if student.id not in existing_attendances:
                    new_attendances.append(Attendance(
                        student_id=student.id,
                        class_id=class_id,
                        status="present"
                    ))
                    flash(f"Attendance marked for {student.first_name} {student.last_name}", "success")
                    print(f"Attendance marked for {student.first_name} {student.last_name}")
                else:
                    flash(f"Attendance already marked for {student.first_name} {student.last_name}", "info")
                    print(f"Attendance already marked for {student.first_name} {student.last_name}")
            else:
                flash(f"Student {name} not found in this class", "warning")
                print(f"Student {name} not found in this class")

        if new_attendances:
            db.session.bulk_save_objects(new_attendances)
            db.session.commit()