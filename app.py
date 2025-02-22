from flask import Flask, request, jsonify
import os
from granite_model import generate_business_checklist, chat_with_ai, predict_business_growth

app = Flask(__name__)

@app.route("/generate-checklist", methods=["POST"])
def generate_checklist():
    """Generates an AI-driven business checklist based on user input."""
    data = request.get_json()
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "User input is required"}), 400
    
    checklist = generate_business_checklist(user_input)
    return jsonify({"checklist": checklist})

@app.route("/chat", methods=["POST"])
def chat():
    """Handles AI-driven business consulting chat."""
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    response = chat_with_ai(user_message)
    return jsonify({"response": response})

@app.route("/predict-growth", methods=["POST"])
def predict_growth():
    """Predicts business growth based on user input."""
    data = request.get_json()
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Business details are required"}), 400
    
    growth_rate = predict_business_growth(user_input)
    return jsonify({"growth_rate": growth_rate})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
