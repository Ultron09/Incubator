import json
from datetime import datetime, timedelta
from ibm_watson_machine_learning.foundation_models import Model
import os
from config import IBM_GRANITE_API_KEY  # Ensure config.py is properly imported

# Ensure the API key is set
if not IBM_GRANITE_API_KEY:
    raise ValueError("IBM_GRANITE_API_KEY is missing. Please check your environment variables.")

granite_model = Model.from_pretrained(
    model_id="granite-13b-chat",
    api_key=IBM_GRANITE_API_KEY
)

# AI-powered Business Consultant Chatbot
def chat_with_ai(user_message, checklist):
    prompt = f"""
    The user is running a business and has the following query: {user_message}
    - Provide business guidance on the next step they should take.
    - Suggest any updates to their current checklist.
    - If necessary, modify task deadlines based on new priorities.
    - Respond as a strategic business consultant.
    Format output as JSON containing `response` (advice text), `updated_checklist` (task list with modifications).
    """
    
    response = granite_model.generate_text(prompt=prompt)
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
    
    response = granite_model.generate_text(prompt=prompt)
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
    response = granite_model.generate_text(prompt=prompt)
    
    try:
        return float(response.strip('%')) / 100 if "%" in response else float(response) / 100
    except ValueError:
        return 0.0  # Default growth if parsing fails
