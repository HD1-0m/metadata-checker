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
        return "<h3>No file uploaded</h3>"

    file = request.files["file"]

    if file.filename == "":
        return "<h3>No file selected</h3>"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        result = subprocess.run(
            ["python3", "metadata_checker.py", filepath],
            capture_output=True,
            text=True,
            timeout=15
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if error:
            return f"<h3>Error:</h3><pre>{error}</pre>"

        if not output:
            return "<h3>No metadata found or script returned no output.</h3>"

        return f"<h3>Result:</h3><pre>{output}</pre>"

    except subprocess.TimeoutExpired:
        return "<h3>Error: Script took too long (timeout)</h3>"

    except Exception as e:
        return f"<h3>Unexpected error:</h3><pre>{str(e)}</pre>"

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
