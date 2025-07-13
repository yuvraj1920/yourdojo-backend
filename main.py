from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://your-flutterflow-app.web.app"}},supports_credentials=True)

@app.route('/')
def home():
    return "✅ MMA AI Backend is running!"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()

    name = data.get('name')
    weight = data.get('weight')
    height = data.get('height')
    experience = data.get('experience')
    preference = data.get('preference')
    age = data.get('age')
    diet = data.get('diet')
    goal = data.get('goal')
    motivation = data.get('motivation')

    prompt = f"""
    Based on the following user data, suggest:

    1. The most suitable martial art for them and why.
    2. A complete weekly training plan based on their fitness goal and experience.
    3. A vegetarian or non-vegetarian diet plan based on their goal.

    User Data:
    - Name: {name}
    - Weight: {weight} kg
    - Height: {height} cm
    - Martial Arts Experience: {experience}
    - Martial Arts Preference: {preference}
    - Age: {age}
    - Diet: {diet}
    - Fitness Goal: {goal}
    - Motivation: {motivation}
    """

    genai.configure(api_key="AIzaSyDAzymZr0UE8YCcUMGkyaJ_K-fFYjP9rbI")  # 👈 Your API Key

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return jsonify({"result": response.text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
