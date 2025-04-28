# tools/memory_manager.py
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


"""
if __name__ == "__main__":
    # — hard‑coded credentials for now —  
    URI   = "https://in03-74809fbebdd4930.serverless.gcp-us-west1.cloud.zilliz.com"
    TOKEN = "99db0548cad592ed8c1dcf1523085d92924aee7a470d4f9f42693f3cab97d8c90f70d703b28699af0cd6fc210933d8f05fd5abf4"

    mem = MemoryManager(uri=URI, token=TOKEN)

    # Demo insert & search
    demo_texts = [f"memory example {i}" for i in range(5)]
    user_id = "user123"
    mem.insert_memories(demo_texts, user_id)

    hits = mem.search_memory("memory example 2", top_k=2, user_id=user_id)
    for h in hits:
        print(f"✅ ID: {h['id']}, Distance: {h['distance']:.3f}, Text: {h['text']}")
"""

