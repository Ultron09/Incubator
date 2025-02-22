import json
from datetime import datetime, timedelta
import requests
from config import GEMINI_API_KEY, GEMINI_API_URL
import genai


# Ensure all credentials are set
if not GEMINI_API_KEY or not GEMINI_API_URL:
    raise ValueError("Gemini API Key or URL is missing.")

# API Call Function to interact with Gemini API
def call_gemini_api(prompt):
    # Create the client instance using the API key from environment
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Send the prompt to Gemini API model
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Assuming model name is "gemini-2.0-flash"
            contents=prompt
        )
        
        # If response is successful, return the text from the response
        if response and response.text:
            return response.text
        else:
            return "No response from Gemini API."
    except Exception as e:
        print(f"Error while calling Gemini API: {e}")
        return "Error calling Gemini API"

# AI-powered Business Consultant Chatbot
def chat_with_ai(user_message, checklist=None):
    prompt = f"""
    The user is running a business and has the following query: {user_message}
    - Provide business guidance on the next step they should take.
    - Suggest any updates to their current checklist.
    - If necessary, modify task deadlines based on new priorities.
    - Respond as a strategic business consultant.
    Format output as JSON containing `response` (advice text) and `updated_checklist` (task list with modifications).
    """
    
    response = call_gemini_api(prompt)
    
    # Attempt to parse the response, if it's in JSON format
    try:
        response_data = json.loads(response)
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
    
    response = call_gemini_api(prompt)
    
    # Try to parse the response as JSON and return the checklist
    try:
        return json.loads(response) if response else []
    except json.JSONDecodeError:
        return []

# Assign deadlines dynamically to tasks in the checklist
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
    
    response = call_gemini_api(prompt)
    
    # Try to parse the growth prediction and return the growth rate
    try:
        # Strip out the percentage sign and convert to float
        return float(response.strip('%')) / 100 if "%" in response else float(response) / 100
    except ValueError:
        return 0.0  # Return default growth if parsing fails
