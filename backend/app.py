from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import cv2
import uuid
import json
import tempfile
from datetime import datetime, timezone
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
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
MAX_HISTORY_RECORDS = 20


def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as history_file:
            records = json.load(history_file)
        return [record for record in records if isinstance(record, dict)] if isinstance(records, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_history_record(record):
    records = (load_history() + [record])[-MAX_HISTORY_RECORDS:]
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=BASE_DIR,
            delete=False
        ) as temporary_file:
            json.dump(records, temporary_file, indent=2)
            temporary_path = temporary_file.name
        os.replace(temporary_path, HISTORY_FILE)
    except OSError:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise


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
    statistics = {
        "total": total_vehicles,
        "car": vehicle_counts.get("car", 0),
        "truck": vehicle_counts.get("truck", 0),
        "bus": vehicle_counts.get("bus", 0),
        "motorcycle": vehicle_counts.get("motorcycle", 0),
        "average_confidence": round(average_confidence, 2)
    }

    try:
        save_history_record({
            "filename": filename,
            "processed_filename": processed_filename,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": statistics,
            "detections": detected_vehicles
        })
    except OSError:
        app.logger.exception("Unable to save detection history")

    return jsonify({
        "success": True,
        "filename": filename,
        "processed_filename": processed_filename,
        "detections": detected_vehicles,
        "statistics": statistics
    })


@app.route("/history", methods=["GET"])
def history():
    records = []
    for record in load_history():
        filename = record.get("filename", "")
        processed_filename = record.get("processed_filename", "")
        timestamp = record.get("timestamp", "")
        statistics = record.get("statistics", {})
        statistic_names = ("total", "car", "truck", "bus", "motorcycle", "average_confidence")
        if (
            not isinstance(filename, str)
            or not isinstance(processed_filename, str)
            or not isinstance(timestamp, str)
            or not isinstance(statistics, dict)
            or any(
                not isinstance(statistics.get(name), (int, float))
                or statistics.get(name) < 0
                for name in statistic_names
            )
            or not filename
            or not processed_filename
            or secure_filename(filename) != filename
            or secure_filename(processed_filename) != processed_filename
        ):
            continue
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        record = dict(record)
        record["files"] = {
            "original": os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename)),
            "processed": os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], processed_filename))
        }
        records.append(record)
    records.sort(key=lambda record: record["timestamp"], reverse=True)
    return jsonify({"success": True, "history": records})


@app.route("/history", methods=["DELETE"])
def clear_history():
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=BASE_DIR,
            delete=False
        ) as temporary_file:
            json.dump([], temporary_file)
            temporary_path = temporary_file.name
        os.replace(temporary_path, HISTORY_FILE)
    except OSError:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
        app.logger.exception("Unable to clear detection history")
        return jsonify({
            "success": False,
            "message": "Detection history could not be cleared."
        }), 500

    return jsonify({"success": True, "history": []})

# Show uploaded image
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)