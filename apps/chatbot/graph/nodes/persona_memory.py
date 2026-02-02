from apps.chatbot.graph.state import ChatState
from apps.memory.persona_memory import search_persona_memory
from apps.memory.weaviate_client import get_weaviate_client


weaviate_client = get_weaviate_client()

def persona_memory_node(state: ChatState) -> ChatState:
    
    print("======*********** Persona Memory Node Called **************======")
    state["persona_memory"] = search_persona_memory(
        query=state["message"],
        user_id=state["user_id"],
        limit=3,
        client=weaviate_client,
    )
    return state
