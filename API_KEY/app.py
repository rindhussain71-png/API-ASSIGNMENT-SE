from flask import Flask, request, jsonify
import secrets

app = Flask(__name__)

API_KEYS = {
    "Consumer 1": secrets.token_urlsafe(32),
    "Consumer 2": secrets.token_urlsafe(32),
    "Consumer 3": secrets.token_urlsafe(32)
}

print("\n===== ROOTSOFTWARE API KEYS =====")
for consumer, key in API_KEYS.items():
    print(f"{consumer}: {key}")
print("=================================\n")


@app.route("/process", methods=["POST"])
def process_text():

    api_key = request.headers.get("X-API-Key")

    if not api_key or api_key not in API_KEYS.values():
        return jsonify({
            "error": "Invalid or missing API key"
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON object required"
        }), 400

    text = data.get("text")

    if not isinstance(text, str):
        return jsonify({
            "error": "Text must be a string"
        }), 400

    processed_text = text.upper()

    return jsonify({
        "message": "Text processed successfully",
        "processed_text": processed_text
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)