import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
import pytesseract
from PIL import Image
import re
from flask_cors import CORS

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Tesseract path (modify if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Load YOLOv8 model
model = YOLO("best.pt")

# Indian plate regex
plate_regex = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$'

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(plate_img):
    pre = preprocess(plate_img)
    text = pytesseract.image_to_string(pre, config='--psm 7')
    return re.sub(r'[^A-Z0-9]', '', text.upper())

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/api/detect", methods=["POST"])
def detect():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    file = request.files['file']
    img = Image.open(file.stream).convert('RGB')
    frame = np.array(img)

    results = model(frame)[0]
    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        cropped = frame[y1:y2, x1:x2]
        text = extract_text(cropped)
        confidence = float(box.conf[0])
        detections.append({
            'plate': text,
            'confidence': round(confidence * 100, 1),
            'validity': 'Valid' if re.match(plate_regex, text) else 'Invalid'
        })

    return jsonify({'success': True, 'detections': detections})

@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_msg = data.get("message", "")
    return jsonify({"reply": f"You asked about '{user_msg}', but I am still learning!"})

if __name__ == '__main__':
    app.run(debug=True)
