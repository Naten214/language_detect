from flask import Flask, render_template, request
import requests

app = Flask(__name__)

LANGUAGE_URL = "http://language-service:5000/detect"
SENTIMENT_URL = "http://sentiment-service:5000/sentiment"

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        text = request.form["text"]

        # Call language service
        lang_res = requests.post(LANGUAGE_URL, json={"text": text}).json()

        # Call sentiment service
        sent_res = requests.post(SENTIMENT_URL, json={"text": text}).json()

        result = {
            "text": text,
            "language": lang_res.get("language"),
            "confidence": lang_res.get("confidence"),
            "sentiment": sent_res.get("sentiment")
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)