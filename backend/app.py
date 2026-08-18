from flask import Flask, request, render_template, jsonify, send_from_directory
import os
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
        })

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "success": False,
            "message": "No image selected"
        })

    filename = image.filename

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    image.save(save_path)

    print("IMAGE SAVED AT :", save_path)

    # Call vehicle detection
    detected_vehicles = detect_vehicles(save_path)

    return jsonify({
        "success": True,
        "filename": image.filename,
        "detections": detected_vehicles
    })

# Show uploaded image
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)