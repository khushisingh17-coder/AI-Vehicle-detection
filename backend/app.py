from flask import Flask, request, render_template, jsonify, send_from_directory
import os

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return "Welcome to AI Vehicle Intelligence Backend"


@app.route("/upload", methods=["POST"])
def upload():

    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image selected"})

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"success": False, "message": "No image selected"})

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(save_path)

    return jsonify({
        "success": True,
        "filename": image.filename,

        "plate": "UP32 AB 1234",
        "company": "Hyundai",
        "model": "Creta SX",
        "type": "SUV",
        "color": "White",
        "state": "Uttar Pradesh",
        "confidence": "98.7%",
        "owner": "Rahul Sharma",
        "status": "Valid"
    })


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)