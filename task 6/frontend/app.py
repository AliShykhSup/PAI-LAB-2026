import os

import requests
from flask import Flask, render_template, request


API_BASE_URL = os.getenv("FACE_API_URL", "http://127.0.0.1:8000")

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        uploaded = request.files.get("image")
        if not uploaded or uploaded.filename == "":
            error = "Please choose an image file."
        else:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/analyze",
                    files={
                        "image": (
                            uploaded.filename,
                            uploaded.read(),
                            uploaded.mimetype or "application/octet-stream",
                        )
                    },
                    timeout=60,
                )
                if response.ok:
                    result = response.json()
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    error = error_data.get("detail", f"API error: {response.status_code}")
            except Exception as exc:
                error = f"Could not connect to API: {exc}"

    return render_template("index.html", result=result, error=error, api_url=API_BASE_URL)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
