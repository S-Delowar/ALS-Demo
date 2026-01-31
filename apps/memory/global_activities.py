from weaviate.classes.query import Filter

from apps.memory.embeddings import embed_text
from apps.memory.weaviate_client import get_weaviate_client

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
            
            

def activities_exist_for_profession(profession: str) -> bool:
    """
    Checks if activities exist using Weaviate V4 syntax
    """
    with get_weaviate_client() as client:
        collection = client.collections.get("GlobalActivities")
        
        # V4 Query Syntax: fetch objects with a filter
        result = collection.query.fetch_objects(
            filters=Filter.by_property("profession").equal(profession),
            limit=1
        )
        
        # If we found at least 1 object, return True
        return len(result.objects) > 0