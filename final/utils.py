# import cv2
# import dlib
# import numpy as np
# from flask import current_app, g
# from .models import Face, Attendance, Class
# from datetime import datetime
# from . import db


# def compute_face_embeding(image, num_jitters):
#     # image = cv2.imread(image)

#     face_locations = face_detector(image, 1)

#     if not face_locations:
#         return "Hello"

#     landmarks = shape_predictor(image, face_locations[0])

#     # Create multiple encodings with jittering
#     jittered_encodings = []
#     for _ in range(num_jitters):
#         face_encoding = np.array(
#             face_recognizer.compute_face_descriptor(image, landmarks)
#         )
#         jittered_encodings.append(face_encoding)

#     # Average the jittered encodings
#     average_encoding = np.median(jittered_encodings, axis=0)
#     # face_encodings_database[name] = average_encoding

#     return average_encoding


# # face_encodings_database = fun()


# # Preload models outside the function
# face_detector = dlib.get_frontal_face_detector()
# shape_predictor = dlib.shape_predictor("Models\shape_predictor_68_face_landmarks.dat")
# face_recognizer = dlib.face_recognition_model_v1(
#     "Models\dlib_face_recognition_resnet_model_v1.dat"
# )


# def sanitize_input(input):
#     return input.replace("'", "''")


# def compute_face_encodings(image, face_locations):
#     face_encodings = []
#     for face_location in face_locations:
#         landmarks = shape_predictor(image, face_location)
#         face_encoding = np.array(
#             face_recognizer.compute_face_descriptor(image, landmarks)
#         )
#         face_encodings.append(face_encoding)
#     return face_encodings


# def load_from_database():
#     with current_app.app_context():
#         faces = Face.query.all()
#     return [(face.name, face.face_encodings) for face in faces]


# def get_face_data():
#     if "face_data" not in g:
#         g.face_data = load_from_database()
#     return g.face_data


# # Initialize an empty list to store attendance records
# def run_face_recognition(frame, class_id):
#     attendance_records = []
#     loaded_faces = get_face_data()
#     face_encodings_database = [face[1] for face in loaded_faces]
#     face_names = [face[0] for face in loaded_faces]

#     # Detect faces in the frame
#     face_locations = face_detector(frame, 1)

#     # Compute face encodings for all detected faces
#     face_encodings = compute_face_encodings(frame, face_locations)

#     if face_encodings:
#         # Compute distances between detected faces and database faces
#         distances = np.array(
#             [
#                 [np.linalg.norm(encoding - enc) for enc in face_encodings_database]
#                 for encoding in face_encodings
#             ]
#         )

#         # Find the closest match for each detected face
#         min_distances = np.min(distances, axis=1)
#         min_indices = np.argmin(distances, axis=1)

#         # Draw bounding boxes and labels
#         for i, face_location in enumerate(face_locations):
#             min_distance = min_distances[i]
#             min_index = min_indices[i]
#             name = face_names[min_index] if min_distance < 0.7 else "Unknown"
#             print(name)
#             top, right, bottom, left = (
#                 face_location.top(),
#                 face_location.right(),
#                 face_location.bottom(),
#                 face_location.left(),
#             )
#             color = (0, 255, 0) if min_distance < 0.45 else (0, 0, 255)
#             cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
#             cv2.putText(
#                 frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
#             )

#             # Mark attendance if the face is recognized
#             if name != "Unknown":
#                 attendance_records.append(name)

#     return frame, attendance_records

import cv2
import dlib
import numpy as np
from flask import current_app, g
from .models import Face, Attendance, Class
from datetime import datetime
from . import db


def compute_face_embeding(image, num_jitters):
    # image = cv2.imread(image)

    face_locations = face_detector(image, 1)

    if not face_locations:
        return "Hello"

    landmarks = shape_predictor(image, face_locations[0])

    # Create multiple encodings with jittering
    jittered_encodings = []
    for _ in range(num_jitters):
        face_encoding = np.array(
            face_recognizer.compute_face_descriptor(image, landmarks)
        )
        jittered_encodings.append(face_encoding)

    # Average the jittered encodings
    average_encoding = np.mean(jittered_encodings, axis=0)
    # face_encodings_database[name] = average_encoding

    return average_encoding


# face_encodings_database = fun()


# Preload models outside the function
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(
    "Models\shape_predictor_68_face_landmarks.dat")
face_recognizer = dlib.face_recognition_model_v1(
    "Models\dlib_face_recognition_resnet_model_v1.dat")


def sanitize_input(input):
    return input.replace("'", "''")


def compute_face_encodings(image, face_locations):
    face_encodings = []
    for face_location in face_locations:
        landmarks = shape_predictor(image, face_location)
        face_encoding = np.array(
            face_recognizer.compute_face_descriptor(image, landmarks)
        )
        face_encodings.append(face_encoding)
    return face_encodings


def load_from_database():
    with current_app.app_context():
        faces = Face.query.all()
    return [(face.name, face.face_encodings) for face in faces]


def get_face_data():
    if "face_data" not in g:
        g.face_data = load_from_database()
    return g.face_data


# Initialize an empty list to store attendance records
def run_face_recognition(frame, class_id):
    attendance_records = []
    loaded_faces = get_face_data()
    face_encodings_database = [face[1] for face in loaded_faces]
    face_names = [face[0] for face in loaded_faces]

    # Detect faces in the frame
    face_locations = face_detector(frame, 1)

    # Compute face encodings for all detected faces
    face_encodings = compute_face_encodings(frame, face_locations)

    if face_encodings:
        # Compute distances between detected faces and database faces
        distances = np.array(
            [
                [np.linalg.norm(encoding - enc) for enc in face_encodings_database]
                for encoding in face_encodings
            ]
        )

        # Find the closest match for each detected face
        min_distances = np.min(distances, axis=1)
        min_indices = np.argmin(distances, axis=1)

        # Draw bounding boxes and labels
        for i, face_location in enumerate(face_locations):
            min_distance = min_distances[i]
            min_index = min_indices[i]
            name = face_names[min_index] if min_distance < 0.45 else "Unknown"
            print(name)
            top, right, bottom, left = (
                face_location.top(),
                face_location.right(),
                face_location.bottom(),
                face_location.left(),
            )
            color = (0, 255, 0) if min_distance < 0.45 else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

            # Mark attendance if the face is recognized
            if name != "Unknown":
                attendance_records.append(name)

    return frame, attendance_records
