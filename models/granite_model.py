import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
from ibm_watson_machine_learning.foundation_models import Model
import os
from config import IBM_GRANITE_API_KEY  # Ensure config.py is properly imported
# Ensure the API key is provided correctly
if not IBM_GRANITE_API_KEY:
    raise ValueError("IBM_GRANITE_API_KEY is missing. Please check your environment variables.")

# Initialize the model with credentials
granite_model = Model(model_id="granite-13b-chat", credentials={"apikey": IBM_GRANITE_API_KEY})
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
    response = granite_model.generate(prompt)
    response_data = json.loads(response)
    return response_data["response"], response_data["updated_checklist"]

# AI-generated business checklist based on user input
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
    
    response = granite_model.generate(prompt)
    checklist = json.loads(response)
    return checklist

# Assign deadlines dynamically
def assign_deadlines(checklist, start_date=datetime.now()):
    for task in checklist:
        task["deadline"] = str(start_date + timedelta(days=task["estimated_days"]))
    return checklist

# Mark task as completed
def mark_task_completed(checklist, task_id):
    for task in checklist:
        if task["id"] == task_id:
            task["completed"] = True
            task["completed_on"] = str(datetime.now())
            return checklist
    return checklist

# Assign tasks to team members
def assign_task_to_member(checklist, task_id, member_name):
    for task in checklist:
        if task["id"] == task_id:
            task["assigned_to"] = member_name
            return checklist
    return checklist

# Predict business growth using AI
def predict_business_growth(user_input):
    prompt = f"""
    The user is running a business with the following details: {user_input}
    Predict the business growth over the next 12 months and provide a percentage growth rate.
    """
    response = granite_model.generate(prompt)
    return float(response.strip('%')) / 100

# Generate business growth prediction graph
def plot_business_growth_prediction(months, growth_rate):
    x = list(range(1, months + 1))
    y = [100 * (1 + growth_rate) ** i for i in x]  # Assuming initial value of 100
    
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker='o', linestyle='-', color='b')
    plt.xlabel("Months")
    plt.ylabel("Business Growth (%)")
    plt.title("Projected Business Growth")
    plt.grid(True)
    plt.show()
