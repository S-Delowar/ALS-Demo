from apps.chatbot.graph.state import ChatState
from apps.memory.global_activities import search_global_activities
from apps.persona.models import UserPersona
from apps.memory.weaviate_client import get_weaviate_client


weaviate_client = get_weaviate_client()

def global_activities_node(state: ChatState) -> ChatState:
    persona = UserPersona.objects.get(user_id=state["user_id"])

    if persona.profession:
        state["global_activities"] = search_global_activities(
            query=state["message"],
            profession=persona.profession,
            limit=3,
            client=weaviate_client
        )
    else:
        state["global_activities"] = []

    return state
