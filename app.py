from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Metadata Checker API is running"

@app.route("/check", methods=["POST"])
def check_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        result = subprocess.run(
            ["python3", "metadata_checker.py", filepath],
            capture_output=True,
            text=True
        )

        return jsonify({
            "output": result.stdout,
            "error": result.stderr
        })

    finally:
        os.remove(filepath)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
