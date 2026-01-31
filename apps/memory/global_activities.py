from .weaviate_client import get_weaviate_client
from .embeddings import embed_text

def save_global_activity(
    text: str, 
    profession: str, 
    version="v1", 
    client=None
):
    vector = embed_text(text)
    
    def _save(active_client):
        collection = active_client.collections.get("GlobalActivities")
        collection.data.insert(
            properties={
                "text": text,
                "profession": profession,
                "version": version,
            },
            vector=vector,
        )

    if client:
        _save(client)
    else:
        with get_weaviate_client() as local_client:
            _save(local_client)