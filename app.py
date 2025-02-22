from flask import Flask, request, jsonify
from models.granite_model import chat_with_ai, predict_business_growth

app = Flask(__name__)

# AI-powered Business Consultant Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    """Handles AI-driven business consulting chat."""
    data = request.get_json()
    user_message = data.get("message")
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
    user_input = data.get("user_input")

    if not user_input:
        return jsonify({"error": "User input is required"}), 400

    checklist = generate_business_checklist(user_input)
    return jsonify({"checklist": checklist})

# Predict Business Growth
@app.route("/predict-growth", methods=["POST"])
def predict_growth():
    """Predicts business growth based on user input."""
    data = request.get_json()
    user_input = data.get("user_input")

    if not user_input:
        return jsonify({"error": "Business details are required"}), 400

    growth_rate = predict_business_growth(user_input)
    return jsonify({"growth_rate": growth_rate})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
