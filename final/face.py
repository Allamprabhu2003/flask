import numpy as np
from flask_sqlalchemy import SQLAlchemy
import dlib
import cv2
from app import db

# Load face detection, shape prediction, and face recognition models

face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("C:\\Users\\Aallamprabhu\\anaconda3\\envs\\vs22\\Lib\\site-packages\\face_recognition_models\\models\\shape_predictor_68_face_landmarks.dat")
face_recognizer = dlib.face_recognition_model_v1("C:\\Users\\Aallamprabhu\\anaconda3\\envs\\vs22\\Lib\\site-packages\\face_recognition_models\\models\\dlib_face_recognition_resnet_model_v1.dat")


class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    face_encodings = db.Column(db.PickleType, nullable=False)

def compute_face_encodings(image):
    # Import face_detector, shape_predictor, and face_recognizer here
    face_locations = face_detector(image, 1)
    if not face_locations:
        return None
    landmarks = shape_predictor(image, face_locations[0])
    face_encoding = np.array(face_recognizer.compute_face_descriptor(image, landmarks))
    return face_encoding

def load_from_database():
    faces = Face.query.all()
    return [(face.name, face.face_encodings) for face in faces]
