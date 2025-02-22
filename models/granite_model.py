import json
from datetime import datetime, timedelta
import requests
from config import IBM_GRANITE_API_KEY, IBM_GRANITE_URL, IBM_WML_PROJECT_ID

# Ensure all credentials are set
if not IBM_GRANITE_API_KEY or not IBM_GRANITE_URL or not IBM_WML_PROJECT_ID:
    raise ValueError("IBM Granite API Key, URL, or Project ID is missing.")

# API Call Function
def call_granite_api(prompt):
    url = f"{IBM_GRANITE_URL}/v1/watson/generative-models/granite/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IBM_GRANITE_API_KEY}"
    }
    data = {"messages": [{"role": "user", "content": prompt}]}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

# AI-powered Business Consultant Chatbot
def chat_with_ai(user_message, checklist):
    prompt = f"""
    The user is running a business and has the following query: {user_message}
    - Provide business guidance on the next step they should take.
    - Suggest any updates to their current checklist.
    - If necessary, modify task deadlines based on new priorities.
    - Respond as a strategic business consultant.
    Format output as JSON containing `response` (advice text) and `updated_checklist` (task list with modifications).
    """
    
    response = call_granite_api(prompt)
    try:
        response_data = json.loads(response) if response else {}
        return response_data.get("response", ""), response_data.get("updated_checklist", [])
    except json.JSONDecodeError:
        return "Error parsing AI response", []

# AI-generated business checklist
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
    Format output as JSON.
    """
    response = call_granite_api(prompt)
    try:
        return json.loads(response) if response else []
    except json.JSONDecodeError:
        return []

# Assign deadlines dynamically
def assign_deadlines(checklist, start_date=datetime.now()):
    for task in checklist:
        task["deadline"] = str(start_date + timedelta(days=task.get("estimated_days", 0)))
    return checklist

# Mark task as completed
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
    """
    response = call_granite_api(prompt)
    try:
        return float(response.strip('%')) / 100 if "%" in response else float(response) / 100
    except ValueError:
        return 0.0  # Default growth if parsing fails
