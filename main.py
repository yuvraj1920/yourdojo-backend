import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def detect_supported_model(api_key):
    for version in ["v1", "v1beta"]:
        try:
            resp = requests.get(
                f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}",
                timeout=10,
            )
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                # Filter out deprecated and vision models
                candidates = [
                    m.get("name", "").split("/")[-1]
                    for m in models
                    if (
                        "vision" not in m.get("name", "")
                        and not m.get("name", "").endswith("-vision")
                        and not m.get("name", "").endswith("-vision-latest")
                        and "generateContent" in m.get("supportedGenerationMethods", [])
                        and not m.get("name", "").startswith("deprecated")
                    )
                ]
                # Prioritize 1.5-flash, then 1.5-pro, then gemini-pro
                for model_choice in ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-pro"]:
                    if model_choice in candidates:
                        return version, model_choice
                # Fallback to first model
                if candidates:
                    return version, candidates[0]
        except Exception:
            continue
    return None, None

API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
API_VERSION, GEMINI_MODEL = detect_supported_model(API_KEY) if API_KEY else (None, None)

@app.route("/", methods=["GET"])
def home():
    if not API_KEY:
        return jsonify({"status": "error", "message": "No API key set in environment"}), 500
    if not GEMINI_MODEL:
        return jsonify({"status": "error", "message": "No usable Gemini model found for your API key. Go to https://aistudio.google.com/app/apikey and create a new key."}), 500
    return jsonify({
        "status": "OK",
        "message": "API is live!",
        "model_used": GEMINI_MODEL,
        "api_version": API_VERSION
    }), 200

@app.route("/recommend", methods=["POST"])
def recommend():
    if not API_KEY:
        return jsonify({"error": "GOOGLE_GEMINI_API_KEY environment variable not set in Render."}), 500
    if not GEMINI_MODEL:
        return jsonify({"error": "No usable Gemini model found for your API key. Go to https://aistudio.google.com/app/apikey and create a new key."}), 500

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

    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            try:
                gemini_error = resp.json()
            except Exception:
                gemini_error = resp.text
            return jsonify({
                "error": "Gemini API error",
                "detail": gemini_error,
                "model_used": GEMINI_MODEL,
                "api_version": API_VERSION
            }), 502
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
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
