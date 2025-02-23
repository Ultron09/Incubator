import json
import re
import requests
import os
from config import GEMINI_API_KEY

# Load the API key from environment variables (if not already loaded)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"


def call_gemini_api(user_input):
    """
    Calls the Gemini AI API with the given user input and returns the response.
    
    Parameters:
        user_input (str): The user's message to be processed by Gemini AI.

    Returns:
        dict: The response from the Gemini API.
    """
    if not GEMINI_API_KEY:
        return {"error": "Missing GEMINI_API_KEY. Set it in environment variables."}
    
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{"parts": [{"text": user_input}]}]
    }

    response = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API call failed with status {response.status_code}", "details": response.text}


def clean_ai_response(raw_response):
    """Removes backticks and ensures valid JSON format."""
    json_match = re.search(r'```json\s*(\{.*\})\s*```', raw_response, re.DOTALL)
    if json_match:
        return json_match.group(1)  # Extract clean JSON content
    return raw_response  # Return original if no match found


import json  # Make sure to import json if not already

def chat_with_ai(user_message, checklist=None):
    """
    Calls the AI to get business guidance and an updated checklist.
    
    Parameters:
        user_message (str): The user's business-related question.
        checklist (list, optional): Current checklist of tasks.

    Returns:
        tuple: (AI response as a string, Updated checklist as a list, Function call as None)
    """
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

    # Ensure raw_response is a dictionary and extract text safely
    if isinstance(raw_response, dict) and "candidates" in raw_response:
        try:
            ai_text = raw_response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return "Error: Unexpected API response structure", [], None
    else:
        return "Error: Unexpected API response format", [], None

    # Clean and process AI response
    cleaned_response = clean_ai_response(ai_text)

    try:
        response_data = json.loads(cleaned_response)
        return response_data.get("response", ""), response_data.get("updated_checklist", []), None
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}, Raw response: {ai_text}")
        return "Error parsing AI response", [], None


def validate_checklist(checklist):
    """
    Ensures the checklist is a list of dictionaries with required keys.
    """
    if not isinstance(checklist, list):
        return False

    for item in checklist:
        if not isinstance(item, dict) or "id" not in item or "task" not in item or "priority" not in item:
            return False

    return True


def update_checklist(existing_checklist, new_checklist):
    """
    Merges the existing checklist with the AI-generated checklist, avoiding duplicates.
    """
    existing_tasks = {item["task"]: item for item in existing_checklist}
    
    for item in new_checklist:
        if item["task"] not in existing_tasks:
            existing_tasks[item["task"]] = item

    return list(existing_tasks.values())
