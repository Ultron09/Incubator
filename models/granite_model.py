import json
from datetime import datetime, timedelta
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini API Key
genai.configure(api_key=GEMINI_API_KEY)

# Function to call Gemini API
def call_gemini_api(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if response and hasattr(response, "text"):  # Ensure it's a string
            return response.text.strip()
        elif response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip() if response.candidates[0].content.parts else "No response"
        else:
            return "No response from Gemini API."
    except Exception as e:
        print(f"Error while calling Gemini API: {e}")
        return json.dumps({"error": "Error calling Gemini API", "details": str(e)})

# AI-powered Business Consultant Chatbot
def chat_with_ai(user_message, checklist=None):
    prompt = f"""
    The user is running a business and has the following query: {user_message}
    - Provide business guidance on the next step they should take.
    - Suggest any updates to their current checklist.
    - If necessary, modify task deadlines based on new priorities.
    - Respond as a strategic business consultant.
    Format output strictly as a valid JSON object containing:
    - `response` (string): AI's advice
    - `updated_checklist` (list): Updated checklist

    Example JSON response:
    {{
        "response": "Your next step is to secure funding...",
        "updated_checklist": [
            {{"id": 1, "task": "Register business", "priority": "high"}}
        ]
    }}
    """
    
    response = call_gemini_api(prompt)
    
    try:
        response_data = json.loads(response)
        return response_data.get("response", ""), response_data.get("updated_checklist", [])
    except json.JSONDecodeError:
        return "Error parsing AI response", []

# AI-generated Business Checklist
def generate_business_checklist(user_input):
    prompt = f"""
    The user is starting a business with the following details: {user_input}
    Generate a step-by-step checklist covering:
    - Legal requirements
    - Product development
    - Marketing
    - Funding & Finance
    - Scaling & growth
    Each task should have a category, priority level (high, medium, low), estimated completion time in days, and an ID.
    Format output strictly as a JSON list.
    """
    
    response = call_gemini_api(prompt)
    
    try:
        return json.loads(response) if response else []
    except json.JSONDecodeError:
        return []

# Assign deadlines dynamically to tasks in the checklist
def assign_deadlines(checklist, start_date=datetime.now()):
    for task in checklist:
        task["deadline"] = str(start_date + timedelta(days=task.get("estimated_days", 0)))
    return checklist

# Mark a task as completed
def mark_task_completed(checklist, task_id):
    for task in checklist:
        if task.get("id") == task_id:
            task["completed"] = True
            task["completed_on"] = str(datetime.now())
            return checklist
    return checklist

# Assign tasks to team members
def assign_task_to_member(checklist, task_id, member_name):
    for task in checklist:
        if task.get("id") == task_id:
            task["assigned_to"] = member_name
            return checklist
    return checklist

# Predict business growth using AI
def predict_business_growth(user_input):
    prompt = f"""
    The user is running a business with the following details: {user_input}
    Predict the business growth over the next 12 months and provide a percentage growth rate.
    Output only a numerical value (e.g., 12.5 for 12.5% growth).
    """
    
    response = call_gemini_api(prompt)
    
    try:
        return float(response.strip('%')) / 100 if "%" in response else float(response) / 100
    except ValueError:
        return 0.0  # Return default growth if parsing fails
