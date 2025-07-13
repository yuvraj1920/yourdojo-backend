from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "AIzaSyDAzymZr0UE8YCcUMGkyaJ_K-fFYjP9rbI"  
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + API_KEY

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.get_json()

    prompt = f"""
You are an expert martial arts and fitness coach.

Based on the user's profile:
- Name: {user_input.get("name")}
- Age: {user_input.get("age")}
- Height: {user_input.get("height")} cm
- Weight: {user_input.get("weight")} kg
- Experience: {user_input.get("experience")}
- Preference: {user_input.get("preference")} (e.g., striking, grappling, or mixed)
- Fitness Goal: {user_input.get("fitness_goal")}
- Diet Type: {user_input.get("diet")}
- Motivation: {user_input.get("motivation")}

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

    response = requests.post(GEMINI_API_URL, headers=headers, json=body)
    ai_reply = response.json()

    try:
        output_text = ai_reply["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"result": output_text}), 200
    except:
        return jsonify({"error": "Something went wrong", "raw": ai_reply}), 500

if __name__ == '__main__':
    app.run()
