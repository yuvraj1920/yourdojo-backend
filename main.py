import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "OK", "message": "API is live!"}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GOOGLE_GEMINI_API_KEY environment variable not set!"}), 500

    try:
        user_input = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid or missing JSON data."}), 400

    required_fields = [
        "name", "age", "height", "weight", "experience",
        "preference", "fitness_goal", "diet", "motivation"
    ]
    missing = [f for f in required_fields if f not in user_input or user_input[f] in [None, "", []]]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    prompt = (
        "You are an expert martial arts and fitness coach.\n"
        f"User's Profile:\n"
        f"Name: {user_input['name']}\n"
        f"Age: {user_input['age']}\n"
        f"Height: {user_input['height']} cm\n"
        f"Weight: {user_input['weight']} kg\n"
        f"Martial Arts Experience: {user_input['experience']}\n"
        f"Preference: {user_input['preference']}\n"
        f"Fitness Goal: {user_input['fitness_goal']}\n"
        f"Diet: {user_input['diet']}\n"
        f"Motivation: {user_input['motivation']}\n"
        "Provide:\n"
        "- Best martial art for this user and why.\n"
        "- Weekly training schedule based on their level.\n"
        "- Diet plan based on their input.\n"
        "Keep it detailed, helpful, and professional."
    )

    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    )
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        resp = requests.post(gemini_url, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            return jsonify({"error": f"Gemini API error: {resp.text}"}), 502
        data = resp.json()
        output = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        if not output:
            return jsonify({"error": "Empty response from Gemini API"}), 500
        return jsonify({"result": output}), 200
    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Failed to connect to Gemini API: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
