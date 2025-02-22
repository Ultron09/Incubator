from flask import Flask, request, jsonify
from models.granite_model import chat_with_ai, call_gemini_api
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
