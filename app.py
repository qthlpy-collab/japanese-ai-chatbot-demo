from flask import Flask, request, jsonify, send_from_directory
import os
import requests

app = Flask(__name__, static_folder="static")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not OPENAI_API_KEY:
        return jsonify({"error": "Server is missing OPENAI_API_KEY"}), 500

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    try:
        payload = {
            "model": "gpt-4o-mini",
            "input": messages
        }

        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        result = response.json()

        if response.status_code != 200:
            return jsonify({
                "error": result.get("error", {}).get("message", "OpenAI request failed"),
                "raw": result
            }), response.status_code

        reply_text = ""
        for item in result.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        reply_text += content.get("text", "")

        if not reply_text:
            return jsonify({"error": "No reply text returned", "raw": result}), 500

        return jsonify({"reply": reply_text})

    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)