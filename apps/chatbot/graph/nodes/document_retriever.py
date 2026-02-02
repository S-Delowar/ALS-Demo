from apps.chatbot.graph.state import ChatState
from apps.memory.user_documents import search_user_documents
from apps.memory.weaviate_client import get_weaviate_client


weaviate_client = get_weaviate_client()

def document_node(state: ChatState) -> ChatState:
    
    print("======*********** Document Retrieval Node Called **************======")
    
    state["documents"] = search_user_documents(
        query=state["message"],
        user_id=state["user_id"],
        session_id=state["session_id"],
        limit=4,
        client=weaviate_client,
    )
    return state
