from flask import Flask, request, jsonify
from models.granite_model import get_granite_response
from models.gemini_model import get_gemini_response
from database.progress_model import update_progress, get_user_progress
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route("/business_insights/<ai_type>", methods=["GET"])
def business_insights(ai_type):
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 400

    if ai_type == "granite":
        response = get_granite_response(query)
    elif ai_type == "gemini":
        response = get_gemini_response(query)
    else:
        return jsonify({"error": "Invalid AI type. Use 'granite' or 'gemini'."}), 400

    return jsonify({"generated_text": response})

@app.route("/progress/update", methods=["POST"])
def update_progress_route():
    data = request.get_json()
    if not data or not all(k in data for k in ["user_id", "task", "status"]):
        return jsonify({"error": "Missing required fields (user_id, task, status)"}), 400

    update_progress(data["user_id"], data["task"], data["status"])
    return jsonify({"message": "Progress updated successfully"})

@app.route("/progress/get", methods=["GET"])
def get_progress_route():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    progress = get_user_progress(user_id)
    return jsonify({"progress": progress})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
