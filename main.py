from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Allow all origins for FlutterFlow; restrict origins in production for security!
CORS(app, resources={r"/*": {"origins": "*"}})

# Retrieve Gemini API Key from environment variables
API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GOOGLE_GEMINI_API_KEY environment variable not set!")

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

@app.route("/")
def home():
    return jsonify({"message": "API is running!"})

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.get_json(force=True)
        required_fields = [
            "name", "age", "height", "weight", "experience",
            "preference", "fitness_goal", "diet", "motivation"
        ]
        missing = [field for field in required_fields if field not in user_input or user_input[field] in [None, "", []]]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        prompt = f"""
You are an expert martial arts and fitness coach.
User's Profile:
Name: {user_input['name']}
Age: {user_input['age']}
Height: {user_input['height']} cm
Weight: {user_input['weight']} kg
Martial Arts Experience: {user_input['experience']}
Preference: {user_input['preference']}
Fitness Goal: {user_input['fitness_goal']}
Diet: {user_input['diet']}
Motivation: {user_input['motivation']}
Provide:
- Best martial art for this user and why.
- Weekly training schedule based on their level.
- Diet plan based on their input.

Keep it detailed, helpful, and professional.
"""

        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        response = requests.post(GEMINI_API_URL, headers=headers, json=body, timeout=30)
        if response.status_code != 200:
            return jsonify({"error": f"Gemini API error: {response.text}"}), 502

        data = response.json()
        output_text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        if not output_text:
            return jsonify({"error": "Empty response from Gemini API"}), 500

        return jsonify({"result": output_text}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
