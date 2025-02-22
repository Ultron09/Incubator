from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import requests

app = Flask(__name__)

# Configure IBM Granite API
genai.configure(api_key=os.getenv("GRANITE_API_KEY"))

def get_granite_response(prompt: str):
    """Get AI response from IBM Granite"""
    model = genai.GenerativeModel("gemini-pro")  # Replace this if using a different Granite model
    response = model.generate_content(prompt)
    return response.text if response else "Error generating response"

@app.route("/generate", methods=["POST"])
def generate():
    """Generates AI response for a given prompt."""
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    response = get_granite_response(prompt)
    return jsonify({"response": response})

@app.route("/analyze-trends", methods=["GET"])
def analyze_trends():
    """Fetches trending hashtags or topics."""
    # Dummy response – integrate with a social media API if needed
    trends = ["#AI", "#MachineLearning", "#StartupGrowth"]
    return jsonify({"trends": trends})

@app.route("/schedule-post", methods=["POST"])
def schedule_post():
    """Schedules a post with AI-optimized content."""
    data = request.get_json()
    content = data.get("content", "")
    time = data.get("time", "")

    if not content or not time:
        return jsonify({"error": "Content and time are required"}), 400

    # Normally, you'd store this in a DB or queue system
    return jsonify({"status": "Post scheduled", "content": content, "time": time})

@app.route("/generate-cv", methods=["POST"])
def generate_cv():
    """Generates a CV based on provided user data."""
    data = request.get_json()
    name = data.get("name", "")
    skills = data.get("skills", [])
    experience = data.get("experience", [])

    if not name or not skills or not experience:
        return jsonify({"error": "Incomplete data"}), 400

    cv_template = f"Name: {name}\nSkills: {', '.join(skills)}\nExperience:\n"
    for job in experience:
        cv_template += f"- {job}\n"

    return jsonify({"cv": cv_template})

@app.route("/generate-business-plan", methods=["POST"])
def generate_business_plan():
    """Generates a business plan for startups using AI."""
    data = request.get_json()
    idea = data.get("idea", "")
    
    if not idea:
        return jsonify({"error": "Business idea is required"}), 400

    response = get_granite_response(f"Create a business plan for: {idea}")
    return jsonify({"business_plan": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
