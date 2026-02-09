from weaviate.classes.query import Filter

from apps.memory.embeddings import embed_text
from apps.memory.weaviate_client import get_weaviate_client

weaviate_client = get_weaviate_client()

def save_global_activity(
    text: str, 
    profession: str, 
    version="v1", 
    client=None
):
    vector = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
    
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
    
    

# Search function
def search_global_activities(
    query: str,
    profession: str,
    client=weaviate_client,
    limit: int = 3,
):
    """
    Semantic search for global activities scoped by profession.
    Used by RAG in the chatbot.
    """    
    def _search(active_client):
        query_vector = embed_text(query, task_type="RETRIEVAL_QUERY")
        
        collection = active_client.collections.get("PersonaMemory")

        result = collection.query.near_vector(
            near_vector=query_vector,
            filters=Filter.by_property("profession").equal(profession),
            limit=limit,
        )
        
        # Return list of dicts to match previous return format
        return [o.properties for o in result.objects]

    if client:
        return _search(client)
    else:
        with get_weaviate_client() as local_client:
            return _search(local_client)