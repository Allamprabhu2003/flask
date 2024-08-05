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
from .Vision.utils import run_face_recognition, update_attendance

face_recognition = Blueprint('face_recognition', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

### Routes


@face_recognition.route("/recognize_image/<int:class_id>",
                        methods=["GET", "POST"])
@login_required
@csrf.exempt
def recognize_image(class_id):
    if request.method == "POST":
        logger.debug(f"Received POST request for class_id: {class_id}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request files: {request.files}")
        logger.debug(f"Request form: {request.form}")

        # Check if the post request has the file part
        if 'image' not in request.files:
            logger.error("No file part in the request")
            flash("No file part in the request", "error")
            return jsonify({
                "error": "No file part",
                "flash_messages": get_flash_messages()
            }), 400

        file = request.files['image']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            logger.error("No selected file")
            flash("No selected file", "error")
            return jsonify({
                "error": "No selected file",
                "flash_messages": get_flash_messages()
            }), 400

        if file:
            try:
                # Read the file into a byte stream
                file_bytes = io.BytesIO(file.read())

                # Use numpy to construct an array from the byte stream
                file_bytes_np = np.asarray(bytearray(file_bytes.read()),
                                           dtype=np.uint8)

                # Use cv2 to decode the image
                image = cv2.imdecode(file_bytes_np, cv2.IMREAD_COLOR)

                if image is None:
                    logger.error("Failed to decode image")
                    flash("Failed to decode image", "error")
                    return jsonify({
                        "error": "Failed to decode image",
                        "flash_messages": get_flash_messages()
                    }), 400

                logger.debug(f"Image shape: {image.shape}")
                logger.debug(f"Image dtype: {image.dtype}")

                # Run face recognition
                frame, attendance_records = run_face_recognition(image)

                # Update attendance
                update_attendance(attendance_records, class_id)

                # Encode the result image
                _, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()

                logger.debug("Face recognition completed successfully")
                flash("Face recognition completed successfully", "success")

                # Return both the image and flash messages
                response = Response(frame_bytes, mimetype="image/jpeg")
                response.headers['X-Flash-Messages'] = json.dumps(
                    get_flash_messages())
                return response

            except Exception as e:
                logger.error(
                    f"An error occurred during face recognition: {str(e)}")
                logger.error(traceback.format_exc())
                flash(f"An error occurred: {str(e)}", "error")
                return jsonify({
                    "error": f"An error occurred: {str(e)}",
                    "flash_messages": get_flash_messages()
                }), 500

        else:
            logger.error("Allowed file types are not supported")
            flash("Allowed file types are not supported", "error")
            return jsonify({
                "error": "Allowed file types are not supported",
                "flash_messages": get_flash_messages()
            }), 400

    return render_template("recognize_image.html", class_id=class_id)


@face_recognition.route("/recognize/<int:class_id>")
@login_required
def recognize(class_id):
    # classes = Class.query.filter(Class.teachers.any(id=current_user.id)).all()
    return render_template("recognize.html", class_id=class_id)


@face_recognition.route("/video_feed/<int:class_id>")
@login_required
def video_feed(class_id):
    return Response(
        stream_with_context(generate_frames(class_id)),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@face_recognition.route("/change_video_source/<int:class_id>",
                        methods=["GET", "POST"])
@login_required
@csrf.exempt
def change_video_source(class_id):
    if request.method == "POST":
        video_source = request.form.get("video_source")
        if video_source == "webcam":
            session['video_source'] = "webcam"
        else:
            custom_source = request.form.get("custom_source")
            session['video_source'] = custom_source
        return redirect(url_for('views.dashboard'))
    return render_template("change_video_source.html", class_id=class_id)



### Helper Functions
def get_flash_messages():
    return [{
        "category": category,
        "message": message
    } for category, message in get_flashed_messages(with_categories=True)]


def process_frame(frame, class_id, app):
    with app.app_context():
        frame, face_names = run_face_recognition(frame)
        update_attendance(face_names, class_id)
        ret, buffer = cv2.imencode('.jpg', frame,
                                   [cv2.IMWRITE_JPEG_QUALITY, 50])
        return buffer.tobytes()


def generate_frames(class_id):
    video_source = session.get('video_source', 'webcam')
    if video_source == 'webcam':
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_source)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        yield "data: error\n\n"
        return

    frame_skip_interval = 30
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

        ret, buffer = cv2.imencode('.jpg', frame,
                                   [cv2.IMWRITE_JPEG_QUALITY, 50])
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    return render_template("change_video_source.html", class_id=class_id)
