from flask import Flask, request, jsonify
from models.granite_model import generate_business_checklist, chat_with_ai, predict_business_growth
from config import GEMINI_API_KEY, GEMINI_API_URL

app = Flask(__name__)

# API Call Function to Gemini (if not already imported in the model)
import requests
import json

def call_gemini_api(prompt):
    """Call Gemini API to get AI response for a given prompt"""
    url = f"{GEMINI_API_URL}/v1/gemini/generative-models/gemini/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    data = {"messages": [{"role": "user", "content": prompt}]}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

# AI-powered Business Consultant Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    """Handles AI-driven business consulting chat."""
    data = request.get_json()
    user_message = data.get("message", "")
    checklist = data.get("checklist", [])
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    response, updated_checklist = chat_with_ai(user_message, checklist)
    
    return jsonify({
        "response": response,
        "updated_checklist": updated_checklist
    })

# Generate Business Checklist
@app.route("/generate-checklist", methods=["POST"])
def generate_checklist():
    """Generates an AI-driven business checklist based on user input."""
    data = request.get_json()
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "User input is required"}), 400
    
    checklist = generate_business_checklist(user_input)
    return jsonify({"checklist": checklist})

# Predict Business Growth
@app.route("/predict-growth", methods=["POST"])
def predict_growth():
    """Predicts business growth based on user input."""
    data = request.get_json()
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Business details are required"}), 400
    
    growth_rate = predict_business_growth(user_input)
    return jsonify({"growth_rate": growth_rate})

# Ensure the app is running on the appropriate host and port
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
