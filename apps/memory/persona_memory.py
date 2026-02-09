import logging
from weaviate.classes.query import Filter
from .weaviate_client import get_weaviate_client
from .embeddings import embed_text

logger = logging.getLogger(__name__)

def save_persona_memory(
    text: str,
    user_id: int,
    confidence: float,
    memory_type: str,
    client = None 
):
    vector = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
    
    print("=====******\n====Text Embedding done, saving to Weaviate...\n=====******=======")
    
    def _save(active_client):
        collection = active_client.collections.get("PersonaMemory")
        collection.data.insert(
            properties={
                "text": text,
                "user_id": user_id,
                "confidence": confidence,
                "type": memory_type,
            },
            vector=vector,
        )
        
        print(f"====\nSaved persona memory to Weaviate:====\n{text}")

    if client:
        _save(client)
    else:
        with get_weaviate_client() as local_client:
            _save(local_client)


def search_persona_memory(
    query: str,
    user_id: int,
    limit: int = 3,
    client = None
):
    def _search(active_client):
        vector = embed_text(query, task_type="RETRIEVAL_QUERY")
        
        collection = active_client.collections.get("PersonaMemory")

        result = collection.query.near_vector(
            near_vector=vector,
            limit=limit,
            filters=Filter.by_property("user_id").equal(user_id),
            return_properties=["text", "confidence", "type"]
        )
        
        # Return list of dicts to match previous return format
        return [o.properties for o in result.objects]

    if client:
        return _search(client)
    else:
        with get_weaviate_client() as local_client:
            return _search(local_client)