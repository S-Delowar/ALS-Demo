from apps.chatbot.graph.state import ChatState
from apps.persona.models import UserPersona


def persona_loader(state: ChatState) -> ChatState:
    persona = UserPersona.objects.get(user_id=state["user_id"])

    state["persona"] = {
        "profession": persona.profession,
        "level": persona.level,
        "preferences": persona.preferences,
    }

    return state
