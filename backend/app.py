from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import cv2
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
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# About Page
@app.route("/about")
def about():
    return "Welcome to AI Vehicle Intelligence Backend"


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
        detected_vehicles = detect_vehicles(save_path)
    except Exception:
        if os.path.exists(save_path):
            os.remove(save_path)
        app.logger.exception("Vehicle detection failed")
        return jsonify({
            "success": False,
            "message": "Vehicle detection failed. Please try another image."
        }), 500

    return jsonify({
        "success": True,
        "filename": filename,
        "detections": detected_vehicles
    })

# Show uploaded image
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)