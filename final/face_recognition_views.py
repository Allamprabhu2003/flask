
import cv2
import numpy as np
from flask_login import current_user, login_required

from flask import (Blueprint, Response, render_template, request, stream_with_context)

from .models import Class
from .utils import (run_face_recognition,
                    update_attendance)

face_recognition = Blueprint('face_recognition', __name__)

@face_recognition.route("/recognize_image/<int:class_id>", methods=["GET", "POST"])
@login_required
def recognize_image(class_id):
    if request.method == "POST":
        image_file = request.files["image"]
        try:
            image = cv2.imdecode(
                np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR
            )
            # frame, attendance_records = run_face_recognition(image, class_id)
            frame, attendance_records = run_face_recognition(image)
            update_attendance(attendance_records, class_id)
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            return Response(
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n",
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )
        except Exception as e:
            return render_template("error.html", error=str(e))
    return render_template("recognize_image.html", class_id=class_id)



# @face_recognition.route("/recognize_image/<int:class_id>", methods=["GET", "POST"])
# @login_required
# def recognize_image(class_id):
#     if request.method == "POST":
#         if 'image' not in request.files:
#             flash('No file part', 'error')
#             return redirect(request.url)
        
#         file = request.files['image']
#         if file.filename == '':
#             flash('No selected file', 'error')
#             return redirect(request.url)
        
#         if file:
#             # Read the image file
#             image_array = np.frombuffer(file.read(), np.uint8)
#             image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
#             # Convert the image to RGB (dlib expects RGB images)
#             rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
#             # Compute face encodings for the input image
#             input_encoding = compute_face_encodings(rgb_image)
            
#             if input_encoding is None:
#                 flash("No face detected in the image. Please try again.", "error")
#                 return redirect(request.url)
            
#             # Get all students in the class
#             class_ = Class.query.get_or_404(class_id)
#             students = class_.students
            
#             recognized_students = []
            
#             for student in students:
#                 face = Face.query.filter_by(student_id=student.id).first()
#                 if face:
#                     # Compare the input face encoding with the stored face encoding
#                     stored_encoding = np.frombuffer(face.face_encodings, dtype=np.float64)
#                     if compare_faces(input_encoding, stored_encoding):
#                         recognized_students.append(student)
            
#             # Draw rectangles and labels on the image
#             for student in recognized_students:
#                 # Here you would need to get the face location. For simplicity, let's assume it covers the whole image
#                 cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), (0, 255, 0), 2)
#                 cv2.putText(image, f"{student.first_name} {student.last_name}", (10, 30), 
#                             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
#             # Encode the image to send back to the client
#             _, buffer = cv2.imencode('.jpg', image)
#             response = Response(buffer.tobytes(), mimetype='image/jpeg')
            
#             # Update attendance for recognized students
#             for student in recognized_students:
#                 # Here you would call a function to update attendance
#                 # update_attendance(student.id, class_id)
#                 pass
            
#             flash(f"Recognized {len(recognized_students)} students", "success")
#             return response

#     return render_template('recognize_image.html', class_id=class_id)




@face_recognition.route("/recognize")
@login_required
def recognize():
    classes = Class.query.filter(Class.teachers.any(id=current_user.id)).all()
    return render_template("recognize.html", classes=classes)

@face_recognition.route("/video_feed/<int:class_id>")
@login_required
def video_feed(class_id):
    return Response(
        stream_with_context(generate_frames(class_id)),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def generate_frames(class_id):
    cap = cv2.VideoCapture("C:\\Users\\Aallamprabhu\\Desktop\\CV\\DSC_0313.MOV")

    # cap = cv2.VideoCapture(0)  # Use 0 for webcam or provide a video file path
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    if not cap.isOpened():
        yield "data: error\n\n"
        return

    frame_skip_interval = 30  # Process every 30th frame
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            yield "data: video_end\n\n"
            break

        frame_count += 1
        if frame_count % frame_skip_interval == 0:
            frame, face_names = run_face_recognition(frame)
            update_attendance(face_names, class_id)

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# Add other face recognition-related routes here