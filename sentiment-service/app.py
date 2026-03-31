from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")
LANGUAGE_KEY = os.getenv("LANGUAGE_KEY")

API_ENDPOINT = "language/:analyze-text?api-version=2023-04-01"

headers = {
    "Ocp-Apim-Subscription-Key": LANGUAGE_KEY,
    "Content-Type": "application/json"
}


@app.route("/sentiment", methods=["POST"])
def analyze_sentiment():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Missing text"}), 400

    body = {
        "kind": "SentimentAnalysis",
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
        return jsonify({"error": response.text}), 500

    result = response.json()

    sentiment = result["results"]["documents"][0]

    return jsonify({
        "sentiment": sentiment["sentiment"],
        "confidence": sentiment["confidenceScores"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)