import json
import re
import requests
import os
from config import GEMINI_API_KEY
import openai
from openai import OpenAI
from memory_manager import MemoryTool
memory_tool = MemoryTool()
client = openai.OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.getenv("TOGETHER_API_KEY"),
)
def build_system_context(query):
    results = memory_tool.search_memory(query, top_k=5, user_id="1to1help")
    return results

def call_gemini_api(user_input):
    system_prompt = f"You are a psychologist I will give u relveant context You need to help user reach a satisfied mental state ,{context} "
    completion = client.chat.completions.create(
  model="meta-llama/Llama-Vision-Free",
  messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
      ],
    )
    return completion.choices[0].message.content


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

    prompt =user_message

    raw_response = call_gemini_api(prompt)

    # Clean and process AI response
    cleaned_response = clean_ai_response(raw_response)

    try:
        response_data = json.loads(cleaned_response)
        return response_data.get("response", ""), response_data.get("updated_checklist", []), None
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}, Raw response: {raw_response}")
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
