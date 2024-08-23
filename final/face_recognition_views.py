import logging
import io
from flask import (Blueprint, Response, redirect, render_template, request,
                   session, stream_with_context, url_for, flash,
                   get_flashed_messages, json, jsonify)
from flask_login import login_required
import traceback

import cv2
import numpy as np
from . import csrf
from .Vision.utils import run_face_recognition, update_attendance, mark_absent_students

face_recognition = Blueprint('face_recognition', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


cv2.setUseOptimized(True)
cv2.ocl.setUseOpenCL(True)

### Routes

@face_recognition.route("/recognize_image/<int:class_id>", methods=["GET", "POST"])
@login_required
@csrf.exempt
def recognize_image(class_id):
    if request.method == "POST":
        logger.debug(f"Received POST request for class_id: {class_id}")
        
        if 'image' not in request.files:
            logger.error("No file part in the request")
            return jsonify({"error": "No file part", "flash_messages": get_flash_messages()}), 400

        file = request.files['image']

        if file.filename == '':
            logger.error("No selected file")
            return jsonify({"error": "No selected file", "flash_messages": get_flash_messages()}), 400

        if file:
            try:
                # Read the file directly into a numpy array
                file_bytes = np.frombuffer(file.read(), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                if image is None:
                    logger.error("Failed to decode image")
                    return jsonify({"error": "Failed to decode image", "flash_messages": get_flash_messages()}), 400

                # Run face recognition
                frame, attendance_records = run_face_recognition(image, class_id)
                print(attendance_records)
                print(attendance_records)
                print(attendance_records)

                # Update attendance
                update_attendance(attendance_records, class_id)

                # Encode the result image
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()

                logger.debug("Face recognition completed successfully")
                # flash("Face recognition completed successfully", "success")

                # Return both the image and flash messages
                response = Response(frame_bytes, mimetype="image/jpeg")
                response.headers['X-Flash-Messages'] = json.dumps(get_flash_messages())
                return response

            except Exception as e:
                logger.error(f"An error occurred during face recognition: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({"error": f"An error occurred: {str(e)}", "flash_messages": get_flash_messages()}), 500

        else:
            logger.error("Allowed file types are not supported")
            return jsonify({"error": "Allowed file types are not supported", "flash_messages": get_flash_messages()}), 400

    return render_template("recognize_image.html", class_id=class_id)

@face_recognition.route("/recognize/<int:class_id>")
@login_required
def recognize(class_id):
    return render_template("recognize.html", class_id=class_id)

@face_recognition.route("/video_feed/<int:class_id>")
@login_required
def video_feed(class_id):
    return Response(
        stream_with_context(generate_frames(class_id)),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

@face_recognition.route("/change_video_source/<int:class_id>", methods=["GET", "POST"])
@login_required
@csrf.exempt
def change_video_source(class_id):
    if request.method == "POST":
        video_source = request.form.get("video_source")
        session['video_source'] = "webcam" if video_source == "webcam" else request.form.get("custom_source")
        return redirect(url_for('views.dashboard'))
    return render_template("change_video_source.html", class_id=class_id)
import time

### Helper Functions
def get_flash_messages():
    return [{"category": category, "message": message} for category, message in get_flashed_messages(with_categories=True)]

def generate_frames(class_id):
    video_source = session.get('video_source', 'webcam')
    cap = cv2.VideoCapture(0 if video_source == 'webcam' else video_source)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        yield "data: error\n\n"
        return

    frame_skip_interval = 60
    frame_count = 0
    start_time = time.time()
    recognized_names = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            yield "data: video_end\n\n"
            break

        frame_count += 1
        if frame_count % frame_skip_interval == 0:
            frame, face_names = run_face_recognition(frame, class_id)
            recognized_names.update(face_names)
            update_attendance(face_names, class_id)

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Check if the time limit has been reached
        if time.time() - start_time >= 3000:  # 30 seconds for testing, change to 600 for 10 minutes
            mark_absent_students(class_id, recognized_names)
            break

    cap.release()
