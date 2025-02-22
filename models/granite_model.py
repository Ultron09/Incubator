import json
from datetime import datetime, timedelta
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini API Key
genai.configure(api_key=GEMINI_API_KEY)

import json
import re

def clean_ai_response(raw_response):
    """Removes backticks and ensures valid JSON format"""
    json_match = re.search(r'```json\s*(\{.*\})\s*```', raw_response, re.DOTALL)
    if json_match:
        return json_match.group(1)  # Extract clean JSON content
    return raw_response  # Return original if no match found

def chat_with_ai(user_message):
    raw_response = call_gemini_api(user_message)
    
    # Clean AI response
    cleaned_response = clean_ai_response(raw_response)

    # Ensure AI response is valid JSON
    try:
        response_data = json.loads(cleaned_response)
        return response_data.get("response", ""), response_data.get("updated_checklist", [])
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}, Raw response: {raw_response}")
        return "Error parsing AI response", []


# AI-powered Business Consultant Chatbot
def chat_with_ai(user_message, checklist=None):
    if checklist is None:
        checklist = []

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

    raw_response = call_gemini_api(prompt)
    
    # Ensure AI response is valid JSON
    try:
        response_data = json.loads(raw_response)
        if not isinstance(response_data, dict):  # Ensure it's a dictionary
            raise ValueError("Invalid JSON structure")
        
        return response_data.get("response", ""), response_data.get("updated_checklist", [])
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing AI response: {e}, Raw response: {raw_response}")
        return "Error parsing AI response", []

# Function to validate checklist format
def validate_checklist(checklist):
    """
    Ensures the checklist is a list of dictionaries with required keys.
    Example valid checklist item:
    {{"id": 1, "task": "Register business", "priority": "high"}}
    """
    if not isinstance(checklist, list):
        return False

    for item in checklist:
        if not isinstance(item, dict) or "id" not in item or "task" not in item or "priority" not in item:
            return False

    return True

# Function to update the checklist based on AI suggestions
def update_checklist(existing_checklist, new_checklist):
    """
    Merges the existing checklist with the AI-generated checklist, avoiding duplicates.
    """
    existing_tasks = {item["task"]: item for item in existing_checklist}
    
    for item in new_checklist:
        if item["task"] not in existing_tasks:
            existing_tasks[item["task"]] = item

    return list(existing_tasks.values())

