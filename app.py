from flask import Flask, request, render_template_string
import subprocess
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Metadata Checker</title>
</head>
<body>
    <h2>Upload Image</h2>
    <form action="/check" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Check</button>
    </form>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/check", methods=["POST"])
def check_image():
    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        result = subprocess.run(
            ["python3", "metadata_checker.py", filepath],
            capture_output=True,
            text=True
        )
        return f"<pre>{result.stdout}</pre>"
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
