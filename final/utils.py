import cv2
import dlib
import numpy as np

from .models import load_from_database

face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("C:\\Users\\Aallamprabhu\\anaconda3\\envs\\vs22\\Lib\\site-packages\\face_recognition_models\\models\\shape_predictor_68_face_landmarks.dat")
face_recognizer = dlib.face_recognition_model_v1("C:\\Users\\Aallamprabhu\\anaconda3\\envs\\vs22\\Lib\\site-packages\\face_recognition_models\\models\\dlib_face_recognition_resnet_model_v1.dat")


def sanitize_input(input):
    return input.replace("'", "''")

def compute_face_encodings(image):
    face_locations = face_detector(image, 1)
    if not face_locations:
        return None
    landmarks = shape_predictor(image, face_locations[0])
    face_encoding = np.array(face_recognizer.compute_face_descriptor(image, landmarks))
    return face_encoding



def run_face_recognition(frame):
    loaded_faces = load_from_database()
    face_encodings_database = [face[1] for face in loaded_faces]
    face_names = [face[0] for face in loaded_faces]

    face_locations = face_detector(frame, 1)
    if face_locations:
        for face_location in face_locations:
            landmarks = shape_predictor(frame, face_location)
            face_encoding = np.array(face_recognizer.compute_face_descriptor(frame, landmarks))
            distances = [np.linalg.norm(face_encoding - enc) for enc in face_encodings_database]
            min_distance_index = np.argmin(distances)
            min_distance = distances[min_distance_index]
            if min_distance < 0.45:
                name = face_names[min_distance_index]
            else:
                name = "Unknown"
            top, right, bottom, left = face_location.top(), face_location.right(), face_location.bottom(), face_location.left()
            color = (0, 255, 0) if min_distance < 0.45 else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

