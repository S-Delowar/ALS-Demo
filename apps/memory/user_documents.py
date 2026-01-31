from weaviate.classes.query import Filter
from .weaviate_client import get_weaviate_client
from .embeddings import embed_text

# Save a chunk of a user document
# Accepts 'client' to reuse connection from tasks
def save_document_chunk(
    client, 
    text: str,
    user_id: int,
    document_id: int,
    session_id: int | None,
):
    vector = embed_text(text)
    collection = client.collections.get("UserDocuments")

    collection.data.insert(
        properties={
            "text": text,
            "user_id": user_id,
            "document_id": document_id,
            "session_id": session_id or -1,
        },
        vector=vector,
    )

# Retrieve document chunks
def search_user_documents(
    query: str,
    user_id: int,
    session_id: int | None = None,
    limit: int = 4,
    client = None # Optional: pass client if already open
):
    # Helper to run the logic
    def _search(active_client):
        vector = embed_text(query)
        collection = active_client.collections.get("UserDocuments")

        # Build Filters
        filters = Filter.by_property("user_id").equal(user_id)
        
        if session_id is not None:
            # Combine filters using '&' (AND)
            filters = filters & Filter.by_property("session_id").equal(session_id)

        result = collection.query.near_vector(
            near_vector=vector,
            limit=limit,
            filters=filters,
            return_properties=["text"]
        )

        return [o.properties["text"] for o in result.objects]

    # Use passed client OR create a temporary one
    if client:
        return _search(client)
    else:
        with get_weaviate_client() as local_client:
            return _search(local_client)