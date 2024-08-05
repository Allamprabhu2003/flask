# custom_model_extension.py

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
import cv2
import importlib
from .utils import preprocess_image, resize_image, update_attendance

ALLOWED_EXTENSIONS = {'py'}
UPLOAD_FOLDER = 'custom_models'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_model():
    if 'model' not in request.files:
        return jsonify({'error': 'No model file provided'}), 400
    
    file = request.files['model']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({'message': 'Model uploaded successfully', 'model_path': file_path}), 200
    
    return jsonify({'error': 'Invalid file format'}), 400

def recognize(class_id):
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    if 'model_path' not in request.form:
        return jsonify({'error': 'No model path provided'}), 400
    
    image_file = request.files['image']
    model_path = request.form['model_path']
    
    if not os.path.exists(model_path):
        return jsonify({'error': 'Model file not found'}), 404
    
    # Read and preprocess the image
    image_bytes = image_file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image = resize_image(image)
    preprocessed_image = preprocess_image(image)
    
    # Load and use the custom model
    try:
        custom_model = load_custom_model(model_path)
        face_names = custom_model.recognize_faces(preprocessed_image)
        
        # Update attendance using the existing function
        update_attendance(face_names, class_id)
        
        return jsonify({'recognized_faces': face_names}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def load_custom_model(model_path):
    module_name = os.path.splitext(os.path.basename(model_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, model_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CustomModel()