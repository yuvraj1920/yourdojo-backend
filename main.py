from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(name)
CORS(app)

# Environment configs
API_KEY = os.getenv("AIzaSyDAzymZr0UE8YCcUMGkyaJ_K-fFYjP9rbI")
if not API_KEY:
    raise ValueError("Missing GOOGLE_GEMINI_API_KEY")

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.get_json()
        if not user_input:
            return jsonify({"error": "Missing JSON input"}), 400

        # Required fields
        required_fields = ["name", "age", "height", "weight", "experience", "preference", "fitness_goal", "diet", "motivation"]
        missing = [f for f in required_fields if not user_input.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Build AI prompt
        prompt = f"""
You are a professional MMA and fitness expert.

Based on the user's profile:
- Name: {user_input['name']}
- Age: {user_input['age']}
- Height: {user_input['height']} cm
- Weight: {user_input['weight']} kg
- Martial Arts Experience: {user_input['experience']}
- Preference: {user_input['preference']} (striking, grappling, or mixed)
- Fitness Goal: {user_input['fitness_goal']}
- Diet Type: {user_input['diet']}
- Motivation: {user_input['motivation']}

Please provide a full recommendation:
1. Best martial art suited for the user, and why.
2. A training schedule (beginner to advanced) with weekly breakdown.
3. A nutrition plan matching their training and dietary preference.
Keep the tone motivational, user-friendly, and expert-like.
"""

        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        # Send request
        response = requests.post(GEMINI_API_URL, headers=headers, json=body, timeout=15)
        response.raise_for_status()

        ai_reply = response.json()
        result_text = ai_reply.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")

        if not result_text:
            return jsonify({"error": "Gemini API gave empty response", "raw": ai_reply}), 500

        return jsonify({"result": result_text.strip()}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Gemini API connection failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if name == 'main':
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
