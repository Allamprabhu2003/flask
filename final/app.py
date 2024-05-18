import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from face import Face, compute_face_encodings, load_from_database
from face_recognition import run_face_recognition
import numpy as np
import cv2

# Initialize Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/face_rec'
db = SQLAlchemy(app)



# Database operations
def save_to_database(name, face_encodings):
    try:
        face = Face(name=name, face_encodings=face_encodings)
        db.session.add(face)
        db.session.commit()
    except Exception as e:
        return handle_error(e)

# User interface
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        name = sanitize_input(request.form['name'])
        image_file = request.files['image']
        try:
            image = np.fromfile(image_file, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            face_encodings = compute_face_encodings(image)
            save_to_database(name, face_encodings)
            return redirect(url_for('index'))
            
        except Exception as e:
            return handle_error(e)

# Face recognition
@app.route('/recognize')
def recognize():
    cap = cv2.VideoCapture(0)  # Change to '0' for webcam or provide video file path
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame.size == 0:
            continue
        frame = run_face_recognition(frame)
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    return render_template('recognize.html')


# if __name__ == "__main__":
#     app.run(debug=True)