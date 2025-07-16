from flask import Flask, request, jsonify from flask_cors import CORS import requests import os from dotenv import load_dotenv
Load environment variables from .env file
load_dotenv()
Initialize Flask app
app = Flask(name) CORS(app)
Load Gemini API key
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY") if not API_KEY: raise EnvironmentError("GOOGLE_GEMINI_API_KEY not found in environment variables")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
@app.route("/recommend", methods=["POST"]) def recommend(): try: user_input = request.get_json(force=True)
required_fields = [ "name", "age", "height", "weight", "experience", "preference", "fitness_goal", "diet", "motivation" ] missing_fields = [f for f in required_fields if not user_input.get(f)] if missing_fields: return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400 prompt = f""" 
You are an expert martial arts and fitness coach.
Based on the user's profile:
Name: {user_input['name']}
Age: {user_input['age']}
Height: {user_input['height']} cm
Weight: {user_input['weight']} kg
Experience: {user_input['experience']}
Preference: {user_input['preference']}
Fitness Goal: {user_input['fitness_goal']}
Diet Type: {user_input['diet']}
Motivation: {user_input['motivation']}
Give a detailed AI response including:
The best martial art for this user and why it suits them.
A training schedule tailored to their experience level (beginner/intermediate/master) with weekly breakdown.
A diet plan based on their diet type and training goals (vegetarian allowed). Make the response simple, motivating, and professional. """
body = { "contents": [{ "parts": [{"text": prompt}] }] } headers = { "Content-Type": "application/json" } response = requests.post(GEMINI_API_URL, headers=headers, json=body, timeout=10) response.raise_for_status() ai_reply = response.json() try: output_text = ai_reply["candidates"][0]["content"]["parts"][0]["text"] return jsonify({"result": output_text}), 200 except (IndexError, KeyError): return jsonify({"error": "Unexpected Gemini response format", "raw": ai_reply}), 500 
except requests.RequestException as e: return jsonify({"error": f"Gemini API error: {str(e)}"}), 502 except Exception as e: return jsonify({"error": f"Server error: {str(e)}"}), 500
Ensure this block runs only if the script is executed directly
if name == "main": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
