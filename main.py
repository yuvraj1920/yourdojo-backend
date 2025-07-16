from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(name)
# Restrict CORS to specific origins in production (update as needed)
CORS(app, resources={r"/recommend": {"origins": "*"}})  # Replace "*" with specific origins in production

# Get API key from environment variable
API_KEY = os.getenv("AIzaSyDAzymZr0UE8YCcUMGkyaJ_K-fFYjP9rbI")
if not API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY environment variable is not set")

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Validate JSON input
        user_input = request.get_json()
        if not user_input:
            return jsonify({"error": "Invalid or missing JSON data"}), 400

        # Required fields
        required_fields = ["name", "age", "height", "weight", "experience", "preference", "fitness_goal", "diet", "motivation"]
        missing_fields = [field for field in required_fields if field not in user_input or user_input[field] is None]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Construct prompt with sanitized input
        prompt = f"""
You are an expert martial arts and fitness coach.

Based on the user's profile:
- Name: {user_input.get("name", "Unknown")}
- Age: {user_input.get("age", "N/A")}
- Height: {user_input.get("height", "N/A")} cm
- Weight: {user_input.get("weight", "N/A")} kg
- Experience: {user_input.get("experience", "N/A")}
- Preference: {user_input.get("preference", "N/A")} (e.g., striking, grappling, or mixed)
- Fitness Goal: {user_input.get("fitness_goal", "N/A")}
- Diet Type: {user_input.get("diet", "N/A")}
- Motivation: {user_input.get("motivation", "N/A")}

Give a detailed AI response including:
1. The best martial art for this user and why it suits them.
2. A training schedule tailored to their experience level (beginner/intermediate/master) with weekly breakdown.
3. A diet plan based on their diet type and training goals (vegetarian allowed).
Make the response simple, motivating, and professional.
"""

        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Make request to Gemini API with timeout
        response = requests.post(GEMINI_API_URL, headers=headers, json=body, timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes

        ai_reply = response.json()

        # Safely extract the response text
        try:
            output_text = ai_reply.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not output_text:
                return jsonify({"error": "Empty response from Gemini API"}), 500
            return jsonify({"result": output_text}), 200
        except (IndexError, KeyError) as e:
            return jsonify({
                "error": "Unexpected response structure from Gemini API",
                "raw_response": ai_reply
            }), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to Gemini API: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"error": "Invalid JSON input"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if name == 'main':
    # Run with debug=False for production
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
