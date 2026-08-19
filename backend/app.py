from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import cv2
import uuid
from collections import Counter
from werkzeug.utils import secure_filename
from detector import detect_vehicles

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../frontend/templates"),
    static_folder=os.path.join(BASE_DIR, "../frontend/static")
)

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# About Page
@app.route("/about")
def about():
    return "Welcome to AI Vehicle Intelligence Backend"


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "message": "Image is too large. Please choose an image under 10 MB."
    }), 413


# Upload Image
@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image selected"
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "success": False,
            "message": "No image selected"
        }), 400

    filename = secure_filename(image.filename)
    file_extension = os.path.splitext(filename)[1].lower()

    if not filename or file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({
            "success": False,
            "message": "Please upload a supported image file"
        }), 400

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(save_path):
        name, extension = os.path.splitext(filename)
        filename = f"{name}_{uuid.uuid4().hex[:8]}{extension}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    processed_filename = f"{os.path.splitext(filename)[0]}_processed.jpg"
    processed_path = os.path.join(app.config["UPLOAD_FOLDER"], processed_filename)

    try:
        image.save(save_path)

        if cv2.imread(save_path) is None:
            os.remove(save_path)
            return jsonify({
                "success": False,
                "message": "The uploaded file is not a valid image"
            }), 400

        print("IMAGE SAVED AT :", save_path)

        # Call vehicle detection
        detected_vehicles = detect_vehicles(save_path, processed_path)
    except Exception:
        for file_path in (save_path, processed_path):
            if os.path.exists(file_path):
                os.remove(file_path)
        app.logger.exception("Vehicle detection or image processing failed")
        return jsonify({
            "success": False,
            "message": "Vehicle detection failed. Please try another image."
        }), 500

    vehicle_counts = Counter(detection["vehicle"] for detection in detected_vehicles)
    total_vehicles = len(detected_vehicles)
    average_confidence = (
        sum(detection["confidence"] for detection in detected_vehicles) / total_vehicles
        if total_vehicles else 0
    )

    return jsonify({
        "success": True,
        "filename": filename,
        "processed_filename": processed_filename,
        "detections": detected_vehicles,
        "statistics": {
            "total": total_vehicles,
            "car": vehicle_counts.get("car", 0),
            "truck": vehicle_counts.get("truck", 0),
            "bus": vehicle_counts.get("bus", 0),
            "motorcycle": vehicle_counts.get("motorcycle", 0),
            "average_confidence": round(average_confidence, 2)
        }
    })

# Show uploaded image
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)