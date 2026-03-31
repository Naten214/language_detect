from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")
LANGUAGE_KEY = os.getenv("LANGUAGE_KEY")

API_ENDPOINT = "language/:analyze-text?api-version=2023-04-01"

headers = {
    "Ocp-Apim-Subscription-Key": LANGUAGE_KEY,
    "Content-Type": "application/json"
}

# -----------------------------
# API ROUTE
# -----------------------------
@app.route("/detect", methods=["POST"])
def detect_language():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing text"}), 400

        body = {
            "kind": "LanguageDetection",
            "analysisInput": {
                "documents": [
                    {"id": "1", "text": data["text"]}
                ]
            }
        }

        response = requests.post(
            LANGUAGE_ENDPOINT + API_ENDPOINT,
            headers=headers,
            json=body
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Azure API failed",
                "details": response.text
            }), 500

        result = response.json()

        language = result["results"]["documents"][0]["detectedLanguage"]

        return jsonify({
            "language": language["name"],
            "code": language["iso6391Name"],
            "confidence": language["confidenceScore"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# FRONTEND ROUTE
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# -----------------------------
# HEALTH CHECK (VERY IMPORTANT 🔥)
# -----------------------------
@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)