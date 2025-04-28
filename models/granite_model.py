import json
import re
import requests
import os
from config import GEMINI_API_KEY
from together import Together
import time
from typing import List, Dict, Any
from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer
from datetime import datetime

class MemoryManager:
    def __init__(self, uri: str, token: str, dim: int = 384):
        self.dim = dim
        self.uri = uri
        self.token = token
        self.client = MilvusClient(uri=uri, token=token)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def _ensure_collection(self, user_id: str):
        # Dynamically set the collection name based on user_id
        collection_name = f"memory_{user_id}"
        if self.client.has_collection(collection_name): return
        schema = self.client.create_schema()
        schema.add_field("memory_id", DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field("text", DataType.VARCHAR, max_length=10000)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=self.dim)
        schema.add_field("user_id", DataType.VARCHAR, max_length=100)
        schema.add_field("timestamp", DataType.INT64)
        schema.add_field("type", DataType.VARCHAR, max_length=100)
        index_params = self.client.prepare_index_params()
        index_params.add_index("embedding", metric_type="L2")
        self.client.create_collection(collection_name, schema=schema, index_params=index_params, enable_dynamic_field=True)

    def insert_memories(self, texts: List[str], user_id: str, memory_type: str = "thought"):
        self._ensure_collection(user_id)  # Ensure the collection for the user exists
        collection_name = f"memory_{user_id}"
        embeddings = self.embedder.encode(texts).tolist()
        timestamp = int(datetime.utcnow().timestamp())
        rows = [{"text": t, "embedding": e, "user_id": user_id, "timestamp": timestamp, "type": memory_type} for t, e in zip(texts, embeddings)]
        self.client.insert(collection_name, rows)
        self.client.flush(collection_name)

    def search_memory(self, query: str, top_k: int = 3, user_id: str = None) -> List[Dict[str, Any]]:
        if user_id is None:
            raise ValueError("user_id must be provided for search.")
        
        collection_name = f"memory_{user_id}"
        q_emb = self.embedder.encode([query])[0].tolist()
        results = self.client.search(
            collection_name,
            data=[q_emb],
            anns_field="embedding",
            search_params={"metric_type": "L2", "params": {"nprobe": 10}},
            output_fields=["memory_id", "text", "user_id", "timestamp", "type"],
            limit=top_k
        )
        hits = [{
            "id": hit["entity"]["memory_id"],
            "distance": hit["distance"],
            "text": hit["entity"]["text"],
            "user_id": hit["entity"].get("user_id", ""),
            "timestamp": hit["entity"].get("timestamp", 0),
            "type": hit["entity"].get("type", "")
        } for hit in results[0]]
        return hits







memory_tool = MemoryManager()

client = Together(
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
