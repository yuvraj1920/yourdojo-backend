from flask import Flask, request, jsonify from flask_cors import CORS import requests import os from dotenv import load_dotenv
Load environment variables from .env file
load_dotenv()
app = Flask(name) CORS(app) # Allow CORS for all domains temporarily for testing
Get API key from environment variables
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY") if not API_KEY: raise EnvironmentError("Missing GOOGLE_GEMINI_API_KEY in environment variables")
Google Gemini API endpoint
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={AIzaSyDAzymZr0UE8YCcUMGkyaJ_K-fFYjP9rbI}"
@app.route('/recommend', methods=['POST']) def recommend(): try: user_input = request.get_json()
if not user_input: return jsonify({"error": "Invalid or missing JSON data"}), 400 required_fields = [ "name", "age", "height", "weight", "experience", "preference", "fitness_goal", "diet", "motivation" ] missing = [field for field in required_fields if not user_input.get(field)] if missing: return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400 # Generate prompt based on user input prompt = f""" 
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
Best martial art for this user and why.
Weekly training schedule based on their level.
Diet plan based on their input. Keep it detailed, helpful, and professional. """
headers = {"Content-Type": "application/json"} body = { "contents": [ {"parts": [{"text": prompt}]} ] } response = requests.post(GEMINI_API_URL, headers=headers, json=body, timeout=10) response.raise_for_status() data = response.json() output_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "") if not output_text: return jsonify({"error": "Empty response from Gemini API"}), 500 return jsonify({"result": output_text}), 200 
except requests.exceptions.RequestException as e: return jsonify({"error": f"Failed to connect to Gemini API: {str(e)}"}), 500 except Exception as e: return jsonify({"error": f"Internal server error: {str(e)}"}), 500
if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port, debug=False)
